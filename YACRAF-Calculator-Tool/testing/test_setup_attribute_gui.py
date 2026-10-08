import importlib.util
import os
import sys
import types
import unittest
from unittest.mock import patch


TOOL_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIRECTORY = os.path.join(TOOL_DIRECTORY, "src")
SETUP_GUI_PATH = os.path.join(
    SRC_DIRECTORY, "blocks_gui", "setup", "setup_attribute_gui.py"
)
sys.path.insert(0, SRC_DIRECTORY)


class SetupAttributeStub:
    @staticmethod
    def has_override_value():
        return False

    @staticmethod
    def has_user_override():
        return False

    @staticmethod
    def get_value():
        return (0.375,)


class TestSetupAttributeGUI(unittest.TestCase):
    def test_display_calculated_value_formats_restored_value(self):
        """A restored value must be displayable while the GUI is initialized."""
        general_gui = types.ModuleType("general_gui")
        general_gui.GUIModelingBlock = object

        pressable_entry = types.ModuleType("pressable_entry")
        pressable_entry.PressableEntry = object

        config = types.ModuleType("config")
        config.DECIMALS_WHEN_ROUNDING = 3

        with patch.dict(
            sys.modules,
            {
                "general_gui": general_gui,
                "pressable_entry": pressable_entry,
                "config": config,
            },
        ):
            spec = importlib.util.spec_from_file_location(
                "setup_attribute_gui_under_test", SETUP_GUI_PATH
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            gui = object.__new__(module.GUISetupAttribute)
            gui._GUISetupAttribute__setup_attribute = SetupAttributeStub()

            displayed_values = []
            gui.set_displayed_value = (
                lambda text, color=None: displayed_values.append((text, color))
            )

            gui.display_calculated_value()

        self.assertEqual(displayed_values, [("0.375", None)])


if __name__ == "__main__":
    unittest.main()
