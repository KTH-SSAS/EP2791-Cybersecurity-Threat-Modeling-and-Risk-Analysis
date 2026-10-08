import importlib.util
import os
import pickle
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


TOOL_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIRECTORY = os.path.join(TOOL_DIRECTORY, "src")
SETUP_VIEW_PATH = os.path.join(SRC_DIRECTORY, "views", "setup_view.py")
sys.path.insert(0, SRC_DIRECTORY)


class SetupAttributeGUIStub:
    def __init__(self):
        self.displayed_values = []
        self.restored_overrides = []

    def set_displayed_value(self, value):
        self.displayed_values.append(value)

    def restore_user_override(self, value):
        self.restored_overrides.append(value)


class SetupClassGUIStub:
    def __init__(self, setup_attribute_gui):
        self.setup_attribute_gui = setup_attribute_gui
        self.names = []

    def set_name(self, value):
        self.names.append(value)

    def get_setup_attributes_gui(self):
        return [self.setup_attribute_gui]


class TestSetupViewRestore(unittest.TestCase):
    def test_restore_save_formats_persisted_attribute_value(self):
        """A persisted value must be displayable while a setup view loads."""
        dependency_modules = {}
        for module_name, attribute_name in (
            ("setup_class_gui", "GUISetupClass"),
            ("buttons_gui", "TouchButton"),
            ("connection_gui", "GUIConnection"),
            ("connection_with_blocks_gui", "GUIConnectionWithBlocks"),
        ):
            dependency_module = types.ModuleType(module_name)
            setattr(dependency_module, attribute_name, object)
            dependency_modules[module_name] = dependency_module

        view_module = types.ModuleType("view")
        view_module.View = object
        dependency_modules["view"] = view_module

        with tempfile.TemporaryDirectory() as temporary_directory:
            config = types.ModuleType("config")
            config.SAVES_PATH = temporary_directory
            config.DECIMALS_WHEN_ROUNDING = 3
            dependency_modules["config"] = config

            saved_state = (
                (0, 0),
                False,
                [
                    {
                        "x": 1,
                        "y": 2,
                        "linked_group_number": None,
                        "configuration_class_gui": "configuration-id",
                        "name": "Restored instance",
                        "setup_attributes_gui": [
                            {"value": (0.375,), "user_override": None}
                        ],
                    }
                ],
                [],
            )
            save_path = os.path.join(temporary_directory, "restored.pickle")
            with open(save_path, "wb") as save_file:
                pickle.dump(saved_state, save_file)

            with patch.dict(sys.modules, dependency_modules):
                spec = importlib.util.spec_from_file_location(
                    "setup_view_under_test", SETUP_VIEW_PATH
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                setup_attribute_gui = SetupAttributeGUIStub()
                setup_class_gui = SetupClassGUIStub(setup_attribute_gui)
                setup_view = object.__new__(module.SetupView)
                setup_view.set_grid_offset = lambda _x, _y: None
                setup_view.create_setup_class_gui = (
                    lambda **_kwargs: setup_class_gui
                )

                is_excluded = setup_view.restore_save(
                    "restored.pickle",
                    {"configuration-id": object()},
                    {},
                )

        self.assertFalse(is_excluded)
        self.assertEqual(setup_class_gui.names, ["Restored instance"])
        self.assertEqual(setup_attribute_gui.displayed_values, ["0.375"])
        self.assertEqual(setup_attribute_gui.restored_overrides, [None])


if __name__ == "__main__":
    unittest.main()
