import os
import importlib.util
from general_gui import GUIModelingBlock
from script_interface import ScriptInterface
from helper_functions_general import convert_grid_coordinate_to_actual
from default_coordinate_functions import get_save_coordinate, get_settings_coordinate, get_change_configuration_view_start_coordinate, get_change_setup_view_start_coordinate, get_create_class_coordinate, get_create_input_coordinate, get_to_setup_start_coordinate, get_create_connection_coordinate, get_calculate_values_coordinate, get_create_attribute_offset, get_create_configuration_view_offset, get_create_setup_view_offset, get_run_script_start_coordinate
from config import *

class Button(GUIModelingBlock):
    """
    Class managing a custom button
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, command, *, ignore_zoom=False, text_width=None, label_text_x=None, additional_pressable_items=None, tags_rect=(), tags_text=()):
        super().__init__(model, view, text, width, height, fill_color, position=(x, y), text_width=text_width, label_text_x=label_text_x, ignore_zoom=ignore_zoom, additional_pressable_items=additional_pressable_items, bind_left=MOUSE_DRAG, tags_rect=tags_rect, tags_text=tags_text)
        self.__command = command
        self.__fill_color = fill_color
        
        self.__completed_command = False
        self.__was_released = False
        
    def left_pressed(self, event):
        self.change_to_select_color()
        
        if self.__command != None:
            self.__command()
            
        self.__completed_command = True
        self.reset_select_color()
        
    def left_dragged(self, event):
        pass
        
    def left_released(self, event):
        self.__was_released = True
        self.reset_select_color()
        
    def change_to_select_color(self):
        super().set_fill_color(SELECT_COLOR)
        
    def reset_select_color(self):
        if self.__completed_command and self.__was_released:
            super().set_fill_color(self.__fill_color)
            
            self.__completed_command = False
            self.__was_released = False
            
    def set_fill_color(self, fill_color):
        self.__fill_color = fill_color
        super().set_fill_color(fill_color)
        
class TouchButton(Button):
    """
    Class managing custom button that is triggered ones per press
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, command, *, ignore_zoom=False, tags_rect=(TAG_BUTTON,), tags_text=(TAG_BUTTON_TEXT,)):
        super().__init__(model, view, text, x, y, width, height, fill_color, command, ignore_zoom=ignore_zoom, tags_rect=tags_rect, tags_text=tags_text)
        
    @staticmethod
    def add_attribute(model, view, configuration_class_gui):
        """
        Button for adding an attribute to a specific configuration attribute
        """
        offset_x, offset_y = get_create_attribute_offset()
        x = configuration_class_gui.get_x() + offset_x
        y = configuration_class_gui.get_y() + CLASS_HEIGHT + len(configuration_class_gui.get_configuration_attributes_gui()) * ATTRIBUTE_HEIGHT
        command = lambda: configuration_class_gui.create_attribute()
        return TouchButton(model, view, "+", x, y, ADD_ATTRIBUTE_WIDTH, ADD_ATTRIBUTE_HEIGHT, ADD_ATTRIBUTE_COLOR, command, tags_rect=(), tags_text=())
        
    @staticmethod
    def add_view(model, view, is_configuration_view):
        """
        Button for adding another view
        """
        if is_configuration_view:
            offset_x, offset_y = get_create_configuration_view_offset()
            x, y = get_change_configuration_view_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
            command = lambda: model.create_view(True, "New configuration")
            
        else:
            offset_x, offset_y = get_create_setup_view_offset()
            x, y = get_change_setup_view_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
            command = lambda: model.create_view(False, "New setup")
            
        x += offset_x
        y += offset_y
        
        return TouchButton(model, view, "+", x, y, ADD_CHANGE_VIEW_WIDTH, ADD_CHANGE_VIEW_HEIGHT, ADD_CHANGE_VIEW_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def save(model, view):
        """
        Button for saving all views
        """
        x, y = get_save_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: model.save()
        return TouchButton(model, view, "Save", x, y, SAVE_WIDTH, SAVE_HEIGHT, SAVE_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def settings(model, view):
        """
        Button for opening the general settings of the program
        """
        from options import Options
        
        x, y = get_settings_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: Options.settings(model, view)
        return TouchButton(model, view, "Settings", x, y, SETTINGS_WIDTH, SETTINGS_HEIGHT, SETTINGS_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def change_view(model, view, view_name, view_to_change_to, is_configuration_view, current_number_of_buttons):
        """
        Button for changing to a specified view
        """
        if view == view_to_change_to:
            color = CHANGE_VIEW_SELECTED_COLOR # Appear selected if it changes to the existing view
            command = None # No need to make any changes when pressed
        else:
            color = CHANGE_VIEW_COLOR
            command = lambda: model.change_view(view_to_change_to)
            
        if is_configuration_view:
            x, y = get_change_configuration_view_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        else:
            x, y = get_change_setup_view_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
            
        y += current_number_of_buttons * CHANGE_VIEW_HEIGHT
        return TouchButton(model, view, view_name, x, y, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, color, command, ignore_zoom=True)
        
    @staticmethod
    def add_configuration_class(model, view):
        """
        Button for creating a new configuration class
        """
        x, y = get_create_class_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: view.create_configuration_class_gui()
        return TouchButton(model, view, "Add class", x, y, ADD_CLASS_WIDTH, ADD_CLASS_HEIGHT, ADD_CLASS_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def add_input(model, view):
        """
        Button for adding an input block
        """
        x, y = get_create_input_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: view.create_configuration_input_gui()
        return TouchButton(model, view, "Add input", x, y, ADD_INPUT_WIDTH, ADD_INPUT_HEIGHT, ADD_INPUT_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def add_to_setup(model, view, configuration_class_gui, current_number_of_buttons):
        """
        Button for creating a setup version of a configuration class
        """
        x, y = get_to_setup_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        y += current_number_of_buttons * ADD_TO_SETUP_HEIGHT
        command = lambda: view.create_setup_class_gui(configuration_class_gui=configuration_class_gui)
        
        to_setup_button = TouchButton(model, view, configuration_class_gui.get_name(), x, y, ADD_TO_SETUP_WIDTH, ADD_TO_SETUP_HEIGHT, ADD_TO_SETUP_COLOR, command, ignore_zoom=True)
        configuration_class_gui.add_to_setup_button(view, to_setup_button)
        
        return to_setup_button
        
    @staticmethod
    def create_connection(model, view):
        """
        Button for creating a directional setup connection
        """
        x, y = get_create_connection_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: view.create_connection_with_blocks()
        return TouchButton(model, view, "Add connection", x, y, ADD_CONNECTION_WIDTH, ADD_CONNECTION_HEIGHT, ADD_CONNECTION_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def calculate_values(model, view):
        """
        Button for calculating the values of all setup attributes
        """
        x, y = get_calculate_values_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: model.calculate_values()
        return TouchButton(model, view, "Calculate", x, y, CALCULATE_VALUES_WIDTH, CALCULATE_VALUES_HEIGHT, CALCULATE_VALUES_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def run_script(model, view, script_path, script_name, num_script_buttons):
        """
        Button for running the corrosponding script
        """
        # Import the module of the script
        spec = importlib.util.spec_from_file_location(script_name, os.path.join(script_path, f"{script_name}.py"))
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)
        
        x, y = get_run_script_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        y -= num_script_buttons * RUN_SCRIPT_HEIGHT
        
        script_interface = ScriptInterface(model)
        command = lambda: script_module.script_control(script_interface)
        return TouchButton(model, view, script_name, x, y, RUN_SCRIPT_WIDTH, RUN_SCRIPT_HEIGHT, RUN_SCRIPT_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def clear_script(model, view):
        """
        Button for resetting any changes made by scripts
        """
        x, y = get_run_script_start_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        command = lambda: model.reset_script_changes()
        return TouchButton(model, view, "Clear script", x, y, RUN_SCRIPT_WIDTH, RUN_SCRIPT_HEIGHT, RUN_SCRIPT_CLEAR_COLOR, command, ignore_zoom=True)
        
    @staticmethod
    def options(model, view, text, x, y, fill_color, command):
        """
        Button used within option windows
        """
        return TouchButton(model, view, text, x, y, OPTIONS_GRID_WIDTH, OPTIONS_GRID_HEIGHT, fill_color, command, ignore_zoom=True, tags_rect=(TAG_OPTIONS,), tags_text=(TAG_OPTIONS_TEXT,))
        
class RadioButton(Button):
    """
    Class that manages a custom radio button, where exactly one out of multiple alternatives is selected at a time
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, is_selected, command, *, ignore_zoom=False, linked_radio_buttons=None, tags_rect=(TAG_OPTIONS,), tags_text=(TAG_OPTIONS_TEXT,)):
        if ignore_zoom:
            length_unit = LENGTH_UNIT
        else:
            length_unit = view.get_length_unit()
            
        actual_x, actual_y = convert_grid_coordinate_to_actual(x, y, length_unit)
        offset, size = convert_grid_coordinate_to_actual((height - BUTTON_SELECT_INDICATOR_SIZE) / 2, BUTTON_SELECT_INDICATOR_SIZE, length_unit)
        
        self.__selected_indicator = view.get_canvas().create_oval(actual_x+offset, \
                                                                  actual_y+offset, \
                                                                  actual_x+offset+size, \
                                                                  actual_y+offset+size, \
                                                                  width=OUTLINE_WIDTH, \
                                                                  outline=OUTLINE_COLOR, \
                                                                  fill=BUTTON_SELECT_INDICATOR_COLOR, \
                                                                  tags=(TAG_OPTIONS_TEXT,))
        
        super().__init__(model, view, text, x, y, width, height, fill_color, None, ignore_zoom=ignore_zoom, text_width=width-1, label_text_x=x+width/2+0.5, additional_pressable_items=[self.__selected_indicator], tags_rect=tags_rect, tags_text=tags_text)
        
        self.__command = command
        self.__tags_rect = tags_rect
        self.__tags_text = tags_text
        self.__is_selected = is_selected
        self.__fill_color = fill_color
        
        # When one radio button among a set of linked ones is pressed, all others should be unselected
        if linked_radio_buttons == None:
            self.__linked_radio_buttons = [] # New group
        else:
            self.__linked_radio_buttons = linked_radio_buttons # This button is added as part of an existing group
            
        self.__linked_radio_buttons.append(self)
        
        self.update_selected_indicator_color()
        
    @staticmethod
    def options(model, view, text, x, y, fill_color, is_selected, command):
        """
        Radio button used within option windows
        """
        return RadioButton(model, view, text, x, y, OPTIONS_GRID_WIDTH, OPTIONS_GRID_HEIGHT, fill_color, is_selected, command, ignore_zoom=True)
        
    def left_pressed(self, event):
        if not self.__is_selected:
            self.set_selected(True)
            
    def update_selected_indicator_color(self):
        """
        Update the color of the circular indicator showing whether it has been selected
        """
        if self.__is_selected:
            color = BUTTON_SELECT_INDICATOR_COLOR_SELECTED
        else:
            color = BUTTON_SELECT_INDICATOR_COLOR
            
        self.get_canvas().itemconfig(self.__selected_indicator, fill=color)
        
    def set_selected(self, is_selected):
        """
        Select this radio button
        """
        self.__is_selected = is_selected
        
        if is_selected:
            self.__is_selected = True
            self.__command()
            
            # Unselect linked radio buttons
            for linked_radio_button in self.__linked_radio_buttons:
                if linked_radio_button != self:
                    linked_radio_button.set_selected(False)
                    
        self.update_selected_indicator_color()
        
    def create_linked_radio_button(self, text, is_selected, command):
        """
        Returns a newly created radio button that is linked to this one
        """
        new_radio_button = RadioButton(self.get_model(), \
                                       self.get_view(), \
                                       text, \
                                       self.get_x(), \
                                       self.get_y() + len(self.__linked_radio_buttons) * OPTIONS_GRID_HEIGHT, \
                                       self.get_width(), \
                                       self.get_height(), \
                                       self.__fill_color, \
                                       is_selected, \
                                       command, \
                                       ignore_zoom=self.ignores_zoom(), \
                                       linked_radio_buttons=self.__linked_radio_buttons, \
                                       tags_rect=self.__tags_rect, \
                                       tags_text=self.__tags_text)
        
        return new_radio_button
        
class ToggleButton(Button):
    """
    Class that manages a custom toggle button that can be toggled on and off
    """
    def __init__(self, model, view, text, x, y, width, height, fill_color, is_selected, command_select, command_unselect, *, ignore_zoom=False, tags_rect=(TAG_OPTIONS,), tags_text=(TAG_OPTIONS_TEXT,)):
        if ignore_zoom:
            length_unit = LENGTH_UNIT
        else:
            length_unit = view.get_length_unit()
            
        actual_x, actual_y = convert_grid_coordinate_to_actual(x, y, length_unit)
        offset, size = convert_grid_coordinate_to_actual((height - BUTTON_SELECT_INDICATOR_SIZE) / 2, BUTTON_SELECT_INDICATOR_SIZE, length_unit)
        
        self.__selected_indicator = view.get_canvas().create_rectangle(actual_x+offset, \
                                                                       actual_y+offset, \
                                                                       actual_x+offset+size, \
                                                                       actual_y+offset+size, \
                                                                       width=OUTLINE_WIDTH, \
                                                                       outline=OUTLINE_COLOR, \
                                                                       fill=BUTTON_SELECT_INDICATOR_COLOR, \
                                                                       tags=(TAG_OPTIONS_TEXT,))
        
        super().__init__(model, view, text, x, y, width, height, fill_color, None, ignore_zoom=ignore_zoom, text_width=width-1, label_text_x=x+width/2+0.5, additional_pressable_items=[self.__selected_indicator], tags_rect=tags_rect, tags_text=tags_text)
        
        self.__command_select = command_select # Command to run when toggled on
        self.__command_unselect = command_unselect # Command to run when toggled off
        self.__is_selected = is_selected
        
        self.update_selected_indicator_color()
        
    @staticmethod
    def options(model, view, text, x, y, fill_color, is_selected, command_select, command_unselect):
        """
        Toggle button used within option windows
        """
        return ToggleButton(model, view, text, x, y, OPTIONS_GRID_WIDTH, OPTIONS_GRID_HEIGHT, fill_color, is_selected, command_select, command_unselect, ignore_zoom=True)
        
    def left_pressed(self, event):
        self.set_selected(not self.__is_selected)
        
    def update_selected_indicator_color(self):
        """
        Update the square indicator showing whether the button is toggled on or off
        """
        if self.__is_selected:
            color = BUTTON_SELECT_INDICATOR_COLOR_SELECTED
        else:
            color = BUTTON_SELECT_INDICATOR_COLOR
            
        self.get_canvas().itemconfig(self.__selected_indicator, fill=color)
        
    def set_selected(self, is_selected):
        """
        Toggles the button to a specified state
        """
        self.__is_selected = is_selected
        
        if is_selected:
            self.__command_select()
        else:
            self.__command_unselect()
            
        self.update_selected_indicator_color()
