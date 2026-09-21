import os
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np


TOOL_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src", "blocks_calculation"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src", "blocks_calculation", "setup"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "config"))

# general_calculations imports GUI configuration constants, but the statistical
# engine itself has no GUI dependency. A blank module keeps these tests headless.
sys.modules.setdefault("config", types.ModuleType("config"))

from general_calculations import (  # noqa: E402
    CalculationTypeAND,
    CalculationTypeMultiplication,
    CalculationTypeOR,
    CalculationTypeSampleTriangle,
    DistributionValue,
    ValueTypeDistribution,
    ValueTypeNumber,
    ValueTypeProbability,
    ValueTypeTriangleDistribution,
    _distribution_from_input,
    calculate_independent_probability_union,
    combine_values,
    configure_distribution_display,
    configure_pos_calculation,
    is_distribution_valued_attribute,
    materialize_probability_override,
    parse_distribution_spec,
    reset_distribution_sampling_cache,
)
from settings import Settings  # noqa: E402
from setup_class_calculation import SetupClass  # noqa: E402
from setup_attribute_calculation import SetupAttribute  # noqa: E402
import setup_attribute_calculation  # noqa: E402
from script_interface import ScriptInterface  # noqa: E402
import helper_functions_general  # noqa: E402
from yacraf_notation import format_parameter_name, get_parameter_abbreviation  # noqa: E402


class InputAttribute:
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = (value,)

    def get_value_type(self):
        return self.value_type

    def get_current_value(self):
        return self.value


class ManualInputAttribute(InputAttribute):
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = value


class OutputAttribute:
    @staticmethod
    def get_input_scalar():
        return 1

    @staticmethod
    def get_input_offset():
        return 0


class ProbabilityConfigurationAttributeStub:
    def __init__(self, name, *, value_type=ValueTypeProbability,
                 calculation_type=CalculationTypeMultiplication,
                 input_attributes=()):
        self.name = name
        self.value_type = value_type
        self.calculation_type = calculation_type
        self.input_attributes = {
            input_attribute: True for input_attribute in input_attributes
        }

    def get_name(self):
        return self.name

    def get_value_type(self):
        return self.value_type

    def get_calculation_type(self):
        return self.calculation_type

    def get_input_configuration_attributes(self):
        return self.input_attributes

    @staticmethod
    def get_input_scalar():
        return 1

    @staticmethod
    def get_input_offset():
        return 0

    @staticmethod
    def is_hidden():
        return False


class ProbabilitySetupClassStub:
    def __init__(self, configuration_name="Abuse case"):
        self.configuration_name = configuration_name
        self.attributes = []

    def get_configuration_name(self):
        return self.configuration_name

    def get_setup_attributes(self):
        return self.attributes

    @staticmethod
    def get_input_setup_classes():
        return {}


class SetupClassStub:
    def __init__(self, configuration_name, predecessors=()):
        self.configuration_name = configuration_name
        self.predecessors = {predecessor: None for predecessor in predecessors}

    def get_configuration_name(self):
        return self.configuration_name

    def get_input_setup_classes(self):
        return self.predecessors


class ConnectedInputAttribute(InputAttribute):
    def __init__(self, value_type, value, name, setup_class):
        super().__init__(value_type, value)
        self.name = name
        self.setup_class = setup_class

    def get_name(self):
        return self.name

    def get_setup_class(self):
        return self.setup_class


class ConfigurationClassStub:
    @staticmethod
    def get_name():
        return "Loss event"

    @staticmethod
    def get_configuration_attributes():
        return []


class LossProbabilityOutputAttribute(OutputAttribute):
    @staticmethod
    def get_name():
        return "Probability"

    @staticmethod
    def get_configuration_class():
        return ConfigurationClassStub()


class TestDistributionSpecifications(unittest.TestCase):
    def setUp(self):
        reset_distribution_sampling_cache(seed=7)
        configure_distribution_display((0.05, 0.5, 0.95))
        configure_pos_calculation("ratio")

    def sampled(self, specification):
        return _distribution_from_input(specification, 20000, object()).get_samples()

    def test_supported_distributions(self):
        uniform = self.sampled(("uniform", 2.0, 5.0))
        triangular = self.sampled(("triangular", 2.0, 3.0, 5.0))
        normal = self.sampled(("normal", 2.0, 3.0))
        lognormal = self.sampled(("lognormal", 4.0, 1.5))
        exponential = self.sampled(("exponential", 3.0))

        self.assertTrue(np.all((uniform >= 2) & (uniform <= 5)))
        self.assertTrue(np.all((triangular >= 2) & (triangular <= 5)))
        self.assertTrue(np.all(normal >= 0))
        self.assertTrue(np.all(lognormal > 0))
        self.assertTrue(np.all(exponential >= 0))
        self.assertAlmostEqual(float(np.median(lognormal)), 4.0, delta=0.1)
        self.assertAlmostEqual(float(np.mean(exponential)), 3.0, delta=0.1)
        self.assertEqual(
            parse_distribution_spec(("exponential", 3.0)),
            ("exponential", 3.0),
        )

    def test_fixed_value_is_a_degenerate_distribution(self):
        self.assertEqual(parse_distribution_spec((2.0,)), ("constant", 2.0))
        self.assertTrue(ValueTypeDistribution.is_correct_input_value((2.0,)))
        self.assertTrue(ValueTypeTriangleDistribution.is_correct_input_value((2.0,)))
        np.testing.assert_array_equal(self.sampled((2.0,)), np.full(20000, 2.0))

    def test_system_connection_scalars_are_ignored(self):
        source = SetupClass("source", ConfigurationClassStub())
        target = SetupClass("target", ConfigurationClassStub())

        target.set_input_setup_class(source, (7.0,))

        self.assertIsNone(target.get_input_setup_classes()[source])

    def test_connection_endpoint_has_no_removed_scalar_indicator_hook(self):
        source_path = os.path.join(
            TOOL_DIRECTORY,
            "src",
            "blocks_gui",
            "connection",
            "connection_blocks_gui.py",
        )
        with open(source_path, encoding="utf-8") as source_file:
            source = source_file.read()

        self.assertNotIn("correct_scalars_indicator_location", source)

    def test_legacy_triangle_is_accepted(self):
        self.assertEqual(parse_distribution_spec((1.0, 2.0, 3.0)),
                         ("triangular", 1.0, 2.0, 3.0))

    def test_legacy_triangle_field_accepts_named_triangular_syntax(self):
        specification = helper_functions_general.convert_string_to_value(
            "triangular / 1 / 2 / 3"
        )

        self.assertEqual(
            parse_distribution_spec(specification, triangle_only=True),
            ("triangular", 1.0, 2.0, 3.0),
        )
        self.assertTrue(ValueTypeTriangleDistribution.is_correct_input_value(
            specification
        ))

    def test_defense_triangle_distribution_propagates_into_global_difficulty(self):
        global_difficulty = combine_values(
            ValueTypeDistribution,
            CalculationTypeAND,
            [ManualInputAttribute(
                 ValueTypeDistribution, ("uniform", 2.0, 2.0)
             ),
             ManualInputAttribute(
                 ValueTypeTriangleDistribution,
                 ("triangular", 1.0, 2.0, 3.0),
             )],
            [None, None],
            OutputAttribute(),
            1000,
        )[0]

        self.assertIsInstance(global_difficulty, DistributionValue)
        self.assertTrue(np.all(global_difficulty.get_samples() >= 3))
        self.assertTrue(np.all(global_difficulty.get_samples() <= 5))

    def test_non_negative_shift_is_added_to_distribution_samples(self):
        specification = helper_functions_general.convert_string_to_value("1 + lognormal / 5 / 2")

        self.assertEqual(
            parse_distribution_spec(specification),
            ("shifted", 1.0, "lognormal", 5.0, 2.0),
        )

        samples = self.sampled(specification)
        self.assertTrue(np.all(samples >= 1))
        self.assertAlmostEqual(float(np.median(samples)), 6.0, delta=0.15)

    def test_distribution_shift_is_whitespace_tolerant(self):
        self.assertEqual(
            parse_distribution_spec(helper_functions_general.convert_string_to_value("2.5+exponential / 3")),
            ("shifted", 2.5, "exponential", 3.0),
        )

    def test_invalid_cost_distributions_are_rejected(self):
        for specification in (("uniform", -1.0, 2.0),
                              ("triangular", 1.0, 3.0, 2.0),
                              ("normal", 1.0, -1.0),
                              ("lognormal", 0.0, 1.5),
                              ("exponential", 0.0),
                              ("exponential", 1.0, 2.0),
                              ("-1 + lognormal", 5.0, 2.0),
                              ("minimum + lognormal", 5.0, 2.0),
                              ("1 + 2 + lognormal", 5.0, 2.0),
                              ("1 + ", 5.0, 2.0),
                              (-1.0,),
                              (float("inf"),),
                              (float("nan"),)):
            with self.subTest(specification=specification):
                with self.assertRaises(ValueError):
                    parse_distribution_spec(specification)

    def test_display_percentiles_are_configurable(self):
        distribution = DistributionValue.empirical([1, 2, 3, 4])

        configure_distribution_display((0, 0.5, 1))
        self.assertEqual(str(distribution), "P0=1 / P50=2.5 / P100=4")

        configure_distribution_display((0.05, 0.5, 0.95))
        self.assertEqual(str(distribution), "P5=1.15 / P50=2.5 / P95=3.85")

    def test_sampling_settings_are_validated(self):
        sampling_settings = Settings()
        sampling_settings.set_num_samples(0)
        self.assertEqual(sampling_settings.get_num_samples(), 1)

        sampling_settings.set_percentile_range(0)
        self.assertEqual(sampling_settings.get_distribution_percentiles(), (0, 0.5, 1))
        sampling_settings.set_percentile_range(7)
        self.assertEqual(sampling_settings.get_distribution_percentiles(), (0.05, 0.5, 0.95))

        sampling_settings.set_pos_calculation_mode("distribution")
        self.assertEqual(sampling_settings.get_pos_calculation_mode(), "distribution")
        sampling_settings.set_pos_calculation_mode("unsupported")
        self.assertEqual(sampling_settings.get_pos_calculation_mode(), "ratio")

    def test_fixed_arity_warning_names_the_actual_calculation(self):
        with patch("builtins.print") as print_warning:
            is_valid = ValueTypeProbability.correctly_connected(
                CalculationTypeSampleTriangle, [object()]
            )

        self.assertFalse(is_valid)
        print_warning.assert_called_once_with(
            "Warning: Calculation type T requires exactly 2 input attributes "
            "in the configuration"
        )

    def test_long_percentile_text_is_wrapped_and_fitted(self):
        class Canvas:
            @staticmethod
            def itemcget(label, option):
                return "Arial 11"

        class Font:
            def __init__(self, family, size, weight):
                self.size = size

            def measure(self, text):
                return len(text) * self.size

        config_module = sys.modules["config"]
        config_module.LENGTH_UNIT = 25
        config_module.FONT = ("Arial", 11)
        config_module.FONT_DECREASE_LINE_BREAK = 3
        config_module.OUTLINE_WIDTH = 1
        config_module.DECIMALS_WHEN_ROUNDING = 3

        percentile_text = "P5=123456.789 / P50=234567.891 / P95=345678.912"
        with patch.object(helper_functions_general.tkfont, "Font", Font):
            fitted_text, fitted_font = helper_functions_general.get_text_that_fits(
                Canvas(), object(), percentile_text, 5, False, 25
            )

        maximum_width = 5 * 25 - 2
        self.assertIn("\n", fitted_text)
        self.assertLessEqual(
            max(len(line) * fitted_font[1] for line in fitted_text.split("\n")),
            maximum_width,
        )

    def test_numeric_setting_value_is_accepted_by_text_fitting(self):
        class Canvas:
            @staticmethod
            def itemcget(label, option):
                return "Arial 11"

        class Font:
            def __init__(self, family, size, weight):
                self.size = size

            def measure(self, text):
                return len(text) * self.size

        config_module = sys.modules["config"]
        config_module.LENGTH_UNIT = 25
        config_module.FONT = ("Arial", 11)
        config_module.FONT_DECREASE_LINE_BREAK = 3
        config_module.OUTLINE_WIDTH = 1
        config_module.DECIMALS_WHEN_ROUNDING = 3

        with patch.object(helper_functions_general.tkfont, "Font", Font):
            fitted_text, _ = helper_functions_general.get_text_that_fits(
                Canvas(), object(), 10000, 7, False, 25
            )

        self.assertEqual(fitted_text, "10000")

    def test_every_distribution_value_type_is_plottable_regardless_of_object(self):
        self.assertTrue(is_distribution_valued_attribute(ValueTypeDistribution, None))
        self.assertTrue(is_distribution_valued_attribute(ValueTypeTriangleDistribution, None))
        self.assertTrue(is_distribution_valued_attribute(
            ValueTypeProbability,
            (DistributionValue.empirical([0.2, 0.8]),),
        ))
        self.assertFalse(is_distribution_valued_attribute(ValueTypeNumber, (4.0,)))

    def test_model_labels_use_parameter_notation_instead_of_value_types(self):
        expected_abbreviations = {
            ("Abuse case", "Accessability to attack surface"): "AtAS",
            ("Abuse case", "Window of opportunity"): "WoO",
            ("Abuse case", "Ability to repudiate"): "AtR",
            ("Abuse case", "Perceived deterrence"): "PD",
            ("Abuse case", "Perceived ease of attack"): "PEoA",
            ("Abuse case", "Perceived benefit of success"): "PBoS",
            ("Abuse case", "Threat event probability"): "TEP",
            ("Abuse case", "Probability of contact"): "PoC",
            ("Abuse case", "Effort spent"): "ES",
            ("Abuse case", "Probability of action"): "PoA",
            ("Attacker", "Personal risk tolerance"): "RT",
            ("Attacker", "Concern for collateral damage"): "CfCD",
            ("Attacker", "Skill"): "Sk",
            ("Attacker", "Resources"): "Res",
            ("Attacker", "Sponsorship"): "Sp",
            ("Attacker", "Threat capability"): "TC",
            ("Attack event AND", "Local difficulty"): "LD",
            ("Attack event OR", "Global difficulty"): "GD",
            ("Attack event AND", "Probability of success"): "PoS",
            ("Loss event", "Magnitude"): "LM",
            ("Loss event", "Probability"): "LP",
            ("Loss event", "Risk"): "LR",
            ("Actor", "Risk"): "AR",
            ("Defense mechanism", "Cost"): "DMC",
            ("Defense mechanism", "Impact"): "DMI",
            ("Defense mechanism", "Existence"): "DME",
        }
        for parameter, abbreviation in expected_abbreviations.items():
            self.assertEqual(get_parameter_abbreviation(*parameter), abbreviation)

        self.assertEqual(
            format_parameter_name("Attack event AND", "Global difficulty"),
            "Global difficulty (GD)",
        )
        self.assertEqual(
            format_parameter_name("Custom class", "Unmapped distribution"),
            "Unmapped distribution",
        )


class TestProbabilityOverrides(unittest.TestCase):
    def setUp(self):
        reset_distribution_sampling_cache(seed=17)

    @staticmethod
    def attribute(name, *, configuration_name="Abuse case",
                  value_type=ValueTypeProbability):
        setup_class = ProbabilitySetupClassStub(configuration_name)
        input_configuration = ProbabilityConfigurationAttributeStub(
            "Assessment input", value_type=ValueTypeNumber
        )
        configuration_attribute = ProbabilityConfigurationAttributeStub(
            name, value_type=value_type, input_attributes=(input_configuration,)
        )
        input_attribute = SetupAttribute(setup_class, input_configuration)
        input_attribute.set_value((0.5,))
        setup_attribute = SetupAttribute(setup_class, configuration_attribute)
        setup_class.attributes.extend((input_attribute, setup_attribute))
        return setup_attribute

    @staticmethod
    def abuse_case_probability_graph():
        setup_class = ProbabilitySetupClassStub()
        assessment_configuration = ProbabilityConfigurationAttributeStub(
            "Assessment input", value_type=ValueTypeNumber
        )
        contact_configuration = ProbabilityConfigurationAttributeStub(
            "Probability of contact",
            input_attributes=(assessment_configuration,),
        )
        action_configuration = ProbabilityConfigurationAttributeStub(
            "Probability of action",
            input_attributes=(assessment_configuration,),
        )
        tep_configuration = ProbabilityConfigurationAttributeStub(
            "Threat event probability",
            input_attributes=(contact_configuration, action_configuration),
        )
        contact = SetupAttribute(setup_class, contact_configuration)
        action = SetupAttribute(setup_class, action_configuration)
        tep = SetupAttribute(setup_class, tep_configuration)
        setup_class.attributes.extend((contact, action, tep))
        return contact, action, tep

    @staticmethod
    def calculate(attribute, num_samples=100):
        sampling_settings = Settings()
        sampling_settings.set_num_samples(num_samples)
        with patch.object(
            setup_attribute_calculation,
            "settings",
            sampling_settings,
            create=True,
        ):
            attribute.calculate_value()

    def test_scalar_probability_override_accepts_closed_interval_bounds(self):
        self.assertEqual(
            materialize_probability_override((0,), 5, "lower-bound"),
            (0.0,),
        )
        self.assertEqual(
            materialize_probability_override((1,), 5, "upper-bound"),
            (1.0,),
        )
        self.assertEqual(
            materialize_probability_override((0.375,), 5, "interior"),
            (0.375,),
        )

    def test_scalar_probability_override_rejects_values_outside_bounds(self):
        for invalid_value in (-0.001, 1.001, float("nan"), float("inf")):
            with self.subTest(invalid_value=invalid_value):
                with self.assertRaises(ValueError):
                    materialize_probability_override(
                        (invalid_value,), 5, "invalid-scalar"
                    )

    def test_persistent_override_rejects_materialized_samples(self):
        samples = DistributionValue.empirical([0.2, 0.4, 0.6])

        with self.assertRaises(ValueError):
            materialize_probability_override(
                (samples,), 3, "already-materialized"
            )

    def test_named_probability_distribution_is_sampled_and_clipped(self):
        override = materialize_probability_override(
            ("uniform", 1.2, 1.5), 37, "clipped-uniform"
        )

        self.assertEqual(len(override), 1)
        self.assertIsInstance(override[0], DistributionValue)
        self.assertEqual(len(override[0].get_samples()), 37)
        np.testing.assert_array_equal(
            override[0].get_samples(), np.ones(37)
        )

    def test_only_abuse_case_poc_and_poa_allow_user_overrides(self):
        self.assertTrue(self.attribute("Probability of contact").allows_user_override())
        self.assertTrue(self.attribute("Probability of action").allows_user_override())
        self.assertFalse(self.attribute(
            "Threat event probability"
        ).allows_user_override())
        self.assertFalse(self.attribute(
            "Probability of action", configuration_name="Attacker"
        ).allows_user_override())
        self.assertFalse(self.attribute(
            "Probability of contact", value_type=ValueTypeNumber
        ).allows_user_override())

        setup_class = ProbabilitySetupClassStub()
        manual_configuration = ProbabilityConfigurationAttributeStub(
            "Probability of contact", calculation_type=None
        )
        manual_attribute = SetupAttribute(setup_class, manual_configuration)
        setup_class.attributes.append(manual_attribute)
        self.assertFalse(manual_attribute.allows_user_override())

    def test_user_override_lifecycle_preserves_the_input_specification(self):
        attribute = self.attribute("Probability of contact")
        specification = ("triangular", 0.1, 0.4, 1.3)

        self.assertFalse(attribute.has_user_override())
        self.assertIsNone(attribute.get_user_override())

        attribute.set_user_override(specification)
        self.assertTrue(attribute.has_user_override())
        self.assertEqual(attribute.get_user_override(), specification)

        attribute.reset_user_override()
        self.assertFalse(attribute.has_user_override())
        self.assertIsNone(attribute.get_user_override())

    def test_unsupported_attribute_rejects_a_user_override(self):
        attribute = self.attribute("Threat event probability")

        with self.assertRaises(ValueError):
            attribute.set_user_override((0.5,))

    def test_temporary_script_override_takes_precedence(self):
        attribute = self.attribute("Probability of action")
        attribute.set_user_override((0.4,))

        self.calculate(attribute)
        self.assertEqual(attribute.get_current_value(), (0.4,))

        attribute.set_override_value((0.9,))
        attribute.attempt_to_reset_value()

        self.calculate(attribute)
        self.assertEqual(attribute.get_current_value(), (0.9,))
        self.assertIsNone(attribute.get_value())
        self.assertEqual(attribute.get_user_override(), (0.4,))

        attribute.reset_override_value()
        self.calculate(attribute)
        self.assertEqual(attribute.get_current_value(), (0.4,))

    def test_manual_value_is_retained_beneath_temporary_script_override(self):
        setup_class = ProbabilitySetupClassStub()
        configuration = ProbabilityConfigurationAttributeStub(
            "Manual probability", calculation_type=None
        )
        attribute = SetupAttribute(setup_class, configuration)
        setup_class.attributes.append(attribute)
        attribute.set_value((0.6,))
        attribute.set_override_value((0.9,))

        attribute.attempt_to_reset_value()

        self.assertEqual(attribute.get_value(), (0.6,))
        self.assertEqual(attribute.get_current_value(), (0.9,))

    def test_granular_script_reset_recalculates_once_after_batch(self):
        class AttributeGUI:
            def __init__(self):
                self.reset_count = 0

            def attempt_to_reset_override_value(self):
                self.reset_count += 1
                return True

        class Helper:
            @staticmethod
            def check_type(values, expected_type):
                return None

            def __init__(self, attributes):
                self.attributes = attributes

            def get_setup_attributes_gui(self, *args):
                return self.attributes

        class Model:
            def __init__(self):
                self.calculate_count = 0

            def calculate_values(self):
                self.calculate_count += 1

        attributes = [AttributeGUI(), AttributeGUI()]
        model = Model()
        interface = ScriptInterface.__new__(ScriptInterface)
        interface._ScriptInterface__model = model
        interface._ScriptInterface__script_helper = Helper(attributes)

        interface.reset_override_attribute_values(class_type="Abuse case")

        self.assertEqual([item.reset_count for item in attributes], [1, 1])
        self.assertEqual(model.calculate_count, 1)

    def test_scalar_overrides_propagate_into_tep_multiplication(self):
        contact, action, tep = self.abuse_case_probability_graph()
        contact.set_user_override((0.4,))
        action.set_user_override((0.75,))

        self.calculate(tep)

        self.assertAlmostEqual(tep.get_current_value()[0], 0.3)

    def test_distribution_override_propagates_into_tep_multiplication(self):
        contact, action, tep = self.abuse_case_probability_graph()
        contact.set_user_override(("uniform", 0.2, 0.8))
        action.set_user_override((0.5,))

        self.calculate(tep, num_samples=53)

        contact_samples = contact.get_current_value()[0].get_samples()
        tep_value = tep.get_current_value()[0]
        self.assertIsInstance(tep_value, DistributionValue)
        self.assertEqual(len(tep_value.get_samples()), 53)
        np.testing.assert_allclose(
            tep_value.get_samples(), contact_samples * 0.5
        )

        loss_probability = CalculationTypeMultiplication.calculate_output_value(
            [tep_value, np.array([0.4])], 53
        )
        loss_risk = CalculationTypeMultiplication.calculate_output_value(
            [loss_probability, np.array([100.0])], 53
        )
        np.testing.assert_allclose(
            loss_probability.get_samples(), contact_samples * 0.5 * 0.4
        )
        np.testing.assert_allclose(
            loss_risk.get_samples(), contact_samples * 0.5 * 0.4 * 100
        )

    def test_reset_user_override_recalculates_the_formula(self):
        setup_class = ProbabilitySetupClassStub()
        first_configuration = ProbabilityConfigurationAttributeStub("Assessment A")
        second_configuration = ProbabilityConfigurationAttributeStub("Assessment B")
        action_configuration = ProbabilityConfigurationAttributeStub(
            "Probability of action",
            input_attributes=(first_configuration, second_configuration),
        )
        first = SetupAttribute(setup_class, first_configuration)
        second = SetupAttribute(setup_class, second_configuration)
        action = SetupAttribute(setup_class, action_configuration)
        setup_class.attributes.extend((first, second, action))
        first.set_value((0.2,))
        second.set_value((0.4,))

        self.calculate(action)
        self.assertAlmostEqual(action.get_current_value()[0], 0.08)

        action.set_user_override((0.75,))
        self.calculate(action)
        self.assertEqual(action.get_current_value(), (0.75,))

        # Formula inputs may change while hidden by the analyst override.
        first.set_value((0.5,))
        action.reset_user_override()
        self.assertIsNone(action.get_current_value())
        self.calculate(action)
        self.assertAlmostEqual(action.get_current_value()[0], 0.2)

    def test_distribution_override_uses_the_current_sample_count(self):
        attribute = self.attribute("Probability of contact")
        specification = ("uniform", 0.2, 0.8)
        attribute.set_user_override(specification)

        self.calculate(attribute, num_samples=7)
        first_materialization = attribute.get_current_value()[0]
        self.assertEqual(len(first_materialization.get_samples()), 7)

        reset_distribution_sampling_cache(seed=23)
        attribute.attempt_to_reset_value()
        self.calculate(attribute, num_samples=13)
        second_materialization = attribute.get_current_value()[0]

        self.assertEqual(attribute.get_user_override(), specification)
        self.assertEqual(len(second_materialization.get_samples()), 13)
        self.assertIsNot(first_materialization, second_materialization)


class TestAttackPlanAggregation(unittest.TestCase):
    def setUp(self):
        configure_pos_calculation("ratio")

    def atomic(self, key, samples):
        return DistributionValue.atomic(np.asarray(samples, dtype=float), key)

    def test_or_is_selected_per_sample(self):
        route_a = self.atomic("A", [6, 20])
        route_b = self.atomic("B", [14, 5])
        local_c = self.atomic("C", [2, 2])

        entry = CalculationTypeOR.calculate_output_value([route_a, route_b], 2)
        foothold = CalculationTypeAND.calculate_output_value([entry, local_c], 2)

        np.testing.assert_allclose(foothold.get_samples(), [8, 7])

    def test_shared_prerequisites_are_counted_once(self):
        # The nine-node example from the README. The two samples make a
        # different entry route cheapest, while all later local costs are fixed.
        a = self.atomic("A", [6, 20])
        b = self.atomic("B", [14, 5])
        c = self.atomic("C", [2, 2])
        d = self.atomic("D", [10, 10])
        e = self.atomic("E", [4, 4])
        f = self.atomic("F", [8, 8])
        g = self.atomic("G", [12, 12])
        h = self.atomic("H", [5, 5])
        i = self.atomic("I", [7, 7])

        entry = DistributionValue.combine_and([DistributionValue.combine_or([a, b]), c])
        privilege = DistributionValue.combine_and([entry, d])
        discovery = DistributionValue.combine_and([entry, e])
        credentials = DistributionValue.combine_and([privilege, f])
        monitoring = DistributionValue.combine_and([privilege, g])
        staging = DistributionValue.combine_and([discovery, credentials, h])
        exfiltration = DistributionValue.combine_and([staging, monitoring, i])

        # Sample 1 uses A: 6+2+10+4+8+12+5+7 = 54.
        # Sample 2 uses B: 5+2+10+4+8+12+5+7 = 53.
        np.testing.assert_allclose(exfiltration.get_samples(), [54, 53])
        self.assertEqual(len(exfiltration.get_plans()), 2)
        self.assertTrue(all(len(plan) == 8 for plan in exfiltration.get_plans()))

    def test_probability_of_success_compares_aligned_samples(self):
        effort = DistributionValue.empirical([40, 60, 80, 30])
        global_cost = DistributionValue.empirical([50, 55, 70, 45])

        probability = CalculationTypeSampleTriangle.calculate_output_value(
            [effort, global_cost], 4
        )
        np.testing.assert_allclose(probability, [0.5])

    def test_probability_of_success_can_return_a_distribution(self):
        effort = DistributionValue.empirical([2, 4, 6, 8])
        global_cost = DistributionValue.empirical([3, 5, 7, 9])
        configure_pos_calculation("distribution")

        probability = CalculationTypeSampleTriangle.calculate_output_value(
            [effort, global_cost], 4
        )

        self.assertIsInstance(probability, DistributionValue)
        np.testing.assert_allclose(probability.get_samples(), [0.75, 0.5, 0.25, 0])

    def test_triangular_conditional_pos_example(self):
        # These empirical effort samples have the exact survival counts of a
        # symmetric Triangular(2, 5, 8) example at g = 3, 5, and 7.
        effort = DistributionValue.empirical([3] + [4] * 8 + [6] * 8 + [8])
        global_cost = DistributionValue.empirical([3] * 6 + [5] * 6 + [7] * 6)
        configure_pos_calculation("distribution")

        probability = CalculationTypeSampleTriangle.calculate_output_value(
            [effort, global_cost], 18
        ).get_samples()

        np.testing.assert_allclose(probability[:6], 17 / 18)
        np.testing.assert_allclose(probability[6:12], 1 / 2)
        np.testing.assert_allclose(probability[12:], 1 / 18)

    def test_probability_value_type_keeps_the_pos_distribution(self):
        configure_pos_calculation("distribution")

        probability = combine_values(
            ValueTypeProbability,
            CalculationTypeSampleTriangle,
            [InputAttribute(ValueTypeDistribution, DistributionValue.empirical([2, 4, 6, 8])),
             InputAttribute(ValueTypeDistribution, DistributionValue.empirical([3, 5, 7, 9]))],
            [None, None],
            OutputAttribute(),
            4,
        )[0]

        self.assertIsInstance(probability, DistributionValue)
        np.testing.assert_allclose(probability.get_samples(), [0.75, 0.5, 0.25, 0])

    def test_independent_probability_union(self):
        probability = calculate_independent_probability_union(
            [np.asarray([0.1]), np.asarray([0.12])], 1
        )
        np.testing.assert_allclose(probability, [0.208])

    def test_loss_probability_unions_each_abuse_case_contribution(self):
        abuse_a = SetupClassStub("Abuse case")
        abuse_b = SetupClassStub("Abuse case")
        terminal_a = SetupClassStub("Attack event AND", (abuse_a,))
        terminal_b = SetupClassStub("Attack event OR", (abuse_b,))
        attributes = [
            ConnectedInputAttribute(
                ValueTypeProbability, 0.2,
                "Threat event probability", abuse_a,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.3,
                "Threat event probability", abuse_b,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.5,
                "Probability of success", terminal_a,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.4,
                "Probability of success", terminal_b,
            ),
        ]

        probability = combine_values(
            ValueTypeProbability,
            CalculationTypeMultiplication,
            attributes,
            [None] * len(attributes),
            LossProbabilityOutputAttribute(),
            1,
        )

        # p_a = 0.2 * 0.5 = 0.10; p_b = 0.3 * 0.4 = 0.12.
        # P(A union B) = 1 - (1 - 0.10)(1 - 0.12) = 0.208.
        np.testing.assert_allclose(probability, [0.208])

    def test_loss_probability_union_preserves_empirical_samples(self):
        abuse_a = SetupClassStub("Abuse case")
        abuse_b = SetupClassStub("Abuse case")
        terminal_a = SetupClassStub("Attack event AND", (abuse_a,))
        terminal_b = SetupClassStub("Attack event OR", (abuse_b,))
        attributes = [
            ConnectedInputAttribute(
                ValueTypeProbability, 0.2,
                "Threat event probability", abuse_a,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.4,
                "Threat event probability", abuse_b,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability,
                DistributionValue.empirical([0.1, 0.5, 0.9]),
                "Probability of success", terminal_a,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.5,
                "Probability of success", terminal_b,
            ),
        ]

        probability = combine_values(
            ValueTypeProbability,
            CalculationTypeMultiplication,
            attributes,
            [None] * len(attributes),
            LossProbabilityOutputAttribute(),
            3,
        )[0]

        self.assertIsInstance(probability, DistributionValue)
        np.testing.assert_allclose(
            probability.get_samples(), [0.216, 0.28, 0.344]
        )

    def test_loss_probability_rejects_ambiguous_abuse_terminal_pairing(self):
        abuse = SetupClassStub("Abuse case")
        terminal_a = SetupClassStub("Attack event AND", (abuse,))
        terminal_b = SetupClassStub("Attack event OR", (abuse,))
        attributes = [
            ConnectedInputAttribute(
                ValueTypeProbability, 0.2,
                "Threat event probability", abuse,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.5,
                "Probability of success", terminal_a,
            ),
            ConnectedInputAttribute(
                ValueTypeProbability, 0.4,
                "Probability of success", terminal_b,
            ),
        ]

        with patch("builtins.print") as warning:
            probability = combine_values(
                ValueTypeProbability,
                CalculationTypeMultiplication,
                attributes,
                [None] * len(attributes),
                LossProbabilityOutputAttribute(),
                1,
            )

        self.assertEqual(probability, ("SETUP ERROR",))
        self.assertIn("exactly one terminal attack event", warning.call_args.args[0])

    def test_loss_risk_keeps_the_full_sample_distribution(self):
        magnitude = DistributionValue.empirical([100, 200, 300])
        probability = np.asarray([0.1])

        risk = CalculationTypeMultiplication.calculate_output_value(
            [magnitude, probability], 3
        )
        np.testing.assert_allclose(risk.get_samples(), [10, 20, 30])

    def test_probability_distribution_propagates_into_loss_risk(self):
        magnitude = DistributionValue.empirical([100, 200, 300])
        probability = DistributionValue.empirical([0.2, 0.5, 0.8])

        risk = combine_values(
            ValueTypeDistribution,
            CalculationTypeMultiplication,
            [InputAttribute(ValueTypeDistribution, magnitude),
             InputAttribute(ValueTypeProbability, probability)],
            [None, None],
            OutputAttribute(),
            3,
        )[0]

        np.testing.assert_allclose(risk.get_samples(), [20, 100, 240])


if __name__ == "__main__":
    unittest.main()
