import os
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np


TOOL_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src", "blocks_calculation"))
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
    ValueTypeProbability,
    _distribution_from_input,
    combine_values,
    configure_distribution_display,
    configure_pos_calculation,
    parse_distribution_spec,
    reset_distribution_sampling_cache,
)
from settings import Settings  # noqa: E402
import helper_functions_general  # noqa: E402


class InputAttribute:
    def __init__(self, value_type, value):
        self.value_type = value_type
        self.value = (value,)

    def get_value_type(self):
        return self.value_type

    def get_current_value(self):
        return self.value


class OutputAttribute:
    @staticmethod
    def get_input_scalar():
        return 1

    @staticmethod
    def get_input_offset():
        return 0


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

        self.assertTrue(np.all((uniform >= 2) & (uniform <= 5)))
        self.assertTrue(np.all((triangular >= 2) & (triangular <= 5)))
        self.assertTrue(np.all(normal >= 0))
        self.assertTrue(np.all(lognormal > 0))
        self.assertAlmostEqual(float(np.median(lognormal)), 4.0, delta=0.1)

    def test_legacy_triangle_is_accepted(self):
        self.assertEqual(parse_distribution_spec((1.0, 2.0, 3.0)),
                         ("triangular", 1.0, 2.0, 3.0))

    def test_invalid_cost_distributions_are_rejected(self):
        for specification in (("uniform", -1.0, 2.0),
                              ("triangular", 1.0, 3.0, 2.0),
                              ("normal", 1.0, -1.0),
                              ("lognormal", 0.0, 1.5)):
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
