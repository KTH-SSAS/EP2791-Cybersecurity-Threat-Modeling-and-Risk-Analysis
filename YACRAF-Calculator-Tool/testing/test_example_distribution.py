import os
import pickle
import sys
import types
import unittest


TOOL_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, TOOL_DIRECTORY)
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "src", "blocks_calculation"))
sys.path.insert(0, os.path.join(TOOL_DIRECTORY, "config"))

# The saved metamodel contains references to value/calculation classes. Its
# statistical engine can be imported without initializing the Tk GUI.
sys.modules.setdefault("config", types.ModuleType("config"))
from general_calculations import (  # noqa: E402
    CalculationTypeAND,
    CalculationTypeMultiplication,
    CalculationTypeSampleTriangle,
    _distribution_from_input,
    configure_pos_calculation,
    reset_distribution_sampling_cache,
)
from main import DEFAULT_SAVE_NAME, get_save_name  # noqa: E402


EXAMPLE_DIRECTORY = os.path.join(TOOL_DIRECTORY, "saves", DEFAULT_SAVE_NAME)


class TestDistributionExample(unittest.TestCase):
    def setUp(self):
        reset_distribution_sampling_cache(seed=11)
        configure_pos_calculation("ratio")

    def test_no_argument_launch_selects_distribution_example(self):
        self.assertEqual(get_save_name(["main.py"]), "example_distribution")
        self.assertEqual(get_save_name(["main.py", "custom"]), "custom")

    def test_example_loads_both_linked_metamodel_views(self):
        view_paths_file = os.path.join(EXAMPLE_DIRECTORY, "view_file_paths.txt")
        with open(view_paths_file, "r") as file_with_paths:
            view_paths = [line.strip() for line in file_with_paths]

        self.assertEqual(
            view_paths,
            [
                "configurations/YACRAF 1.pickle",
                "configurations/YACRAF 2.pickle",
                "setups/Distribution example.pickle",
            ],
        )

        second_configuration_path = os.path.join(
            EXAMPLE_DIRECTORY, "configurations", "YACRAF 2.pickle"
        )
        with open(second_configuration_path, "rb") as configuration_file:
            _, configuration_classes, configuration_inputs = pickle.load(
                configuration_file
            )

        self.assertEqual(
            [item["name"] for item in configuration_classes],
            ["Attack event AND", "Attack event OR"],
        )
        self.assertTrue(any(
            item["calculation_type"] == CalculationTypeSampleTriangle
            for item in configuration_inputs
        ))

        # Linked configuration classes accumulate their calculation inputs
        # across both metamodel views. Verify that every operation with a fixed
        # arity is complete after those views are combined.
        configured_inputs = {}
        calculation_types = {}

        for relative_path in view_paths[:2]:
            configuration_path = os.path.join(EXAMPLE_DIRECTORY, relative_path)
            with open(configuration_path, "rb") as configuration_file:
                _, classes, inputs = pickle.load(configuration_file)

            attributes_by_id = {}
            possible_output_positions = []
            for class_index, configuration_class in enumerate(classes):
                group_number = configuration_class["linked_group_number"]
                if group_number is None:
                    class_key = (relative_path, class_index)
                else:
                    class_key = ("linked", group_number)

                for attribute_index, attribute in enumerate(
                        configuration_class["configuration_attributes_gui"]):
                    attribute_key = (class_key, attribute_index)
                    attributes_by_id[attribute["configuration_attribute_gui"]] = attribute_key
                    attribute_y = configuration_class["y"] + attribute_index + 1
                    possible_output_positions.extend([
                        (configuration_class["x"] - 1, attribute_y, attribute_key),
                        (configuration_class["x"] + 6, attribute_y, attribute_key),
                    ])

            for configuration_input in inputs:
                output_x = configuration_input["x"]
                output_y = configuration_input["y"]
                nearest_output = min(
                    possible_output_positions,
                    key=lambda position: ((position[0] - output_x) ** 2 +
                                          (position[1] - output_y) ** 2),
                )
                distance_squared = ((nearest_output[0] - output_x) ** 2 +
                                    (nearest_output[1] - output_y) ** 2)
                self.assertLess(distance_squared, 0.01)
                output_key = nearest_output[2]
                calculation_types[output_key] = configuration_input["calculation_type"]
                configured_inputs.setdefault(output_key, set()).update(
                    attributes_by_id[connection["start_block"]]
                    for connection in configuration_input["connections"]
                )

        for output_key, calculation_type in calculation_types.items():
            required_inputs = calculation_type.number_of_inputs()
            if required_inputs is not None:
                self.assertEqual(len(configured_inputs[output_key]), required_inputs)

    def test_example_contains_the_screenshot_graph(self):
        configuration_path = os.path.join(
            EXAMPLE_DIRECTORY, "configurations", "YACRAF 1.pickle"
        )
        setup_path = os.path.join(
            EXAMPLE_DIRECTORY, "setups", "Distribution example.pickle"
        )

        with open(configuration_path, "rb") as configuration_file:
            _, configuration_classes, _ = pickle.load(configuration_file)
        class_names = {
            item["configuration_class_gui"]: item["name"]
            for item in configuration_classes
        }

        with open(setup_path, "rb") as setup_file:
            _, is_excluded, setup_classes, connections = pickle.load(setup_file)

        self.assertFalse(is_excluded)
        self.assertEqual(
            [(class_names[item["configuration_class_gui"]], item["name"])
             for item in setup_classes],
            [
                ("Abuse case", "Example abuse case"),
                ("Attack event AND", "Combined attack"),
                ("Attack event OR", "Normal-cost route"),
                ("Attack event OR", "Triangular-cost route"),
                ("Loss event", "Example loss"),
            ],
        )

        values = {
            item["name"]: [attribute["value"]
                           for attribute in item["setup_attributes_gui"]]
            for item in setup_classes
        }
        self.assertEqual(values["Example abuse case"][8],
                         ("triangular", 20.0, 25.0, 30.0))
        self.assertEqual(values["Combined attack"][1], ("uniform", 1.0, 3.0))
        self.assertEqual(values["Normal-cost route"][1], ("normal", 10.0, 2.0))
        self.assertEqual(values["Triangular-cost route"][1],
                         ("triangular", 5.0, 10.0, 15.0))
        self.assertEqual(values["Example loss"][1],
                         ("triangular", 100.0, 500.0, 1000.0))

        def class_at_connection_endpoint(coordinate):
            x, y = coordinate
            matches = []

            for setup_class in setup_classes:
                class_x = setup_class["x"]
                class_y = setup_class["y"]
                class_width = 11
                class_height = 1 + len(setup_class["setup_attributes_gui"])
                beside = (x in (class_x - 1, class_x + class_width) and
                          class_y <= y < class_y + class_height)
                above_or_below = (y in (class_y - 1, class_y + class_height) and
                                  class_x <= x < class_x + class_width)

                if beside or above_or_below:
                    matches.append(setup_class["name"])

            self.assertEqual(len(matches), 1)
            return matches[0]

        edges = [
            (class_at_connection_endpoint((connection["start_block"]["x"],
                                           connection["start_block"]["y"])),
             class_at_connection_endpoint((connection["end_block"]["x"],
                                           connection["end_block"]["y"])))
            for connection in connections
        ]
        self.assertEqual(
            edges,
            [
                ("Example abuse case", "Combined attack"),
                ("Normal-cost route", "Combined attack"),
                ("Triangular-cost route", "Combined attack"),
                ("Combined attack", "Example loss"),
                ("Example abuse case", "Example loss"),
            ],
        )

    def test_example_parameters_produce_distributed_cost_and_risk(self):
        setup_path = os.path.join(
            EXAMPLE_DIRECTORY, "setups", "Distribution example.pickle"
        )
        with open(setup_path, "rb") as setup_file:
            _, _, setup_classes, _ = pickle.load(setup_file)

        values = {
            item["name"]: [attribute["value"]
                           for attribute in item["setup_attributes_gui"]]
            for item in setup_classes
        }
        sample_count = 5000
        normal_route = _distribution_from_input(
            values["Normal-cost route"][1], sample_count, "normal-route"
        )
        triangular_route = _distribution_from_input(
            values["Triangular-cost route"][1], sample_count, "triangular-route"
        )
        combined_local = _distribution_from_input(
            values["Combined attack"][1], sample_count, "combined-local"
        )
        global_cost = CalculationTypeAND.calculate_output_value(
            [normal_route, triangular_route, combined_local], sample_count
        )
        effort = _distribution_from_input(
            values["Example abuse case"][8], sample_count, "effort"
        )
        probability_of_success = CalculationTypeSampleTriangle.calculate_output_value(
            [effort, global_cost], sample_count
        )[0]
        magnitude = _distribution_from_input(
            values["Example loss"][1], sample_count, "magnitude"
        )
        abuse_values = values["Example abuse case"]
        probability_of_contact = 0.1 * sum(value[0] for value in abuse_values[:2]) / 2
        action_factors = [
            abuse_values[4][0],
            abuse_values[5][0],
            10 - abuse_values[2][0],
            10 - abuse_values[3][0],
        ]
        probability_of_action = 0.1 * sum(action_factors) / len(action_factors)
        threat_event_probability = probability_of_contact * probability_of_action
        loss_probability = threat_event_probability * probability_of_success
        risk = CalculationTypeMultiplication.calculate_output_value(
            [magnitude, loss_probability], sample_count
        )

        self.assertEqual(len(global_cost.get_samples()), sample_count)
        self.assertAlmostEqual(global_cost.get_samples().mean(), 22.0, delta=0.4)
        self.assertGreater(probability_of_success, 0)
        self.assertLess(probability_of_success, 1)
        self.assertAlmostEqual(probability_of_contact, 0.4)
        self.assertAlmostEqual(probability_of_action, 0.5)
        self.assertAlmostEqual(threat_event_probability, 0.2)
        self.assertAlmostEqual(loss_probability,
                               0.2 * probability_of_success)
        self.assertNotAlmostEqual(loss_probability, probability_of_success)
        self.assertEqual(len(risk.get_samples()), sample_count)
        self.assertTrue((risk.get_samples() >= 0).all())


if __name__ == "__main__":
    unittest.main()
