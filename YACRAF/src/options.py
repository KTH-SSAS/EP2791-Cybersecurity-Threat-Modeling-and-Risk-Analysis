import tkinter as tk
from general_gui import GUIBlock, GUIModelingBlock
from buttons_gui import TouchButton, RadioButton, ToggleButton
from helper_functions_general import convert_value_to_string, convert_string_to_value, convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_font, delete_all
from default_coordinate_functions import get_options_coordinate
from pressable_entry import PressableEntry
from config import *

class Options:
    """
    Manages the options that pops up when editing an object
    """
    def __init__(self, model, view, rows, columns, text):
        self.__model = model
        self.__view = view
        
        width = columns * OPTIONS_GRID_WIDTH
        height = rows * OPTIONS_GRID_HEIGHT
        
        canvas_width, canvas_height = convert_actual_coordinate_to_grid(settings.get_canvas_width(), settings.get_canvas_height(), LENGTH_UNIT)
        
        self.__x, self.__y = get_options_coordinate(LENGTH_UNIT) # Uses LENGTH_UNIT as zoom is ignored
        self.__x -= width / 2
        self.__y += OPTIONS_GRID_HEIGHT # Account for title
        
        actual_x1, actual_y1 = convert_grid_coordinate_to_actual(self.__x, self.__y, LENGTH_UNIT)
        actual_x2, actual_y2 = convert_grid_coordinate_to_actual(self.__x+width, self.__y+height, LENGTH_UNIT)
        
        self.__background_rect = view.get_canvas().create_rectangle(actual_x1, actual_y1, actual_x2, actual_y2, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=OPTIONS_BACKGROUND_COLOR, tags=(TAG_OPTIONS_BACKGROUND,))
        self.__background_block = GUIBlock(model, view, [self.__background_rect], self.__x, self.__y, width, height, ignore_zoom=True)
        
        self.add_label(-1, columns/2-0.5, f"Options: {text}", color=OPTIONS_TITLE_COLOR) # Title
        self.add_button(rows, columns/2-0.5, "Close", self.delete) # Close button
        
        self.__background_block.highlight(HIGHLIGHT_OPTIONS, highlight_border_width=2*HIGHLIGHT_BORDER_WIDTH, highlight_tags=(TAG_OPTIONS_HIGHLIGHT))
        
        view.set_currently_open_options(self)
        
    @staticmethod
    def view(model, view):
        """
        Options for configuration and setup views
        """
        from setup_view import SetupView
        
        is_setup_view = isinstance(view, SetupView)
        
        if is_setup_view:
            columns = 5
        else:
            columns = 3
        
        options = Options(model, view, 3, columns, "View")
        
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Name:", view.get_name(), lambda: view.set_name(entry_text.get()), entry_text)
        
        options.add_move_buttons(0, 1, "Move view button:", lambda: model.swap_view_places(view, True), lambda: model.swap_view_places(view, False))
        
        current_column = 2
        
        if is_setup_view:
            options.add_label(0, current_column, "Copy view:")
            options.add_button(1, current_column, "Copy", lambda: view.create_copy())
            
            current_column += 1
            
            options.add_label(0, current_column, "Exclude view from calculations:")
            options.add_toggle_button(1, current_column, "Exclude", view.is_excluded(), lambda: view.set_excluded(True), lambda: view.set_excluded(False))
            
            current_column += 1
            
        options.add_label(0, current_column, "Delete view:")
        options.add_button(1, current_column, "Delete", lambda: model.delete_view(view))
        
    @staticmethod
    def settings(model, view):
        """
        Options for general settings to the program
        """
        options = Options(model, view, 2, 2, "General settings")
        
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Number of samples when sampling distributions:", settings.get_num_samples(), lambda: set_num_samples(entry_text.get()), entry_text)
        
        options.add_label(0, 1, "Warn for duplicate class instance names:")
        options.add_toggle_button(1, 1, "Print warnings", settings.warns_duplicate_names(), lambda: settings.set_warn_duplicate_names(True), lambda: settings.set_warn_duplicate_names(False))
        
    @staticmethod
    def configuration_class(model, view, configuration_class_gui, configuration_views):
        """
        Options for configuration classes
        """
        options = Options(model, view, max(2, 1+len(configuration_views)), 2, "Class")
        
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Name:", configuration_class_gui.get_name(), lambda: configuration_class_gui.set_name(entry_text.get()), entry_text)
        
        options.add_label(0, 1, "Add linked copy to metamodel view:")
        
        # Buttons to create a linked copy in each respective configuration view
        for i, configuration_view in enumerate(configuration_views):
            link_button = options.add_button(i+1, \
                                             1, \
                                             configuration_view.get_name(), \
                                             lambda configuration_view=configuration_view: model.create_linked_configuration_class_gui(configuration_class_gui, configuration_view))
            
    @staticmethod
    def configuration_attribute(model, view, configuration_class_gui, configuration_attribute_gui):
        """
        Options for configuration attributes
        """
        value_type = configuration_attribute_gui.get_configuration_attribute().get_value_type()
        
        options = Options(model, view, max(2, 1+len(VALUE_TYPES)), 4, "Attribute")
        
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Name:", configuration_attribute_gui.get_name(), lambda: configuration_attribute_gui.set_name(entry_text.get()), entry_text)
        
        options.add_move_buttons(0, 1, "Move view button", \
                                 lambda: configuration_class_gui.swap_attribute_places(configuration_attribute_gui, True), \
                                 lambda: configuration_class_gui.swap_attribute_places(configuration_attribute_gui, False))
        
        options.add_label(0, 2, "Value type:")
        initial_radio_button = None
        
        for i, value_type in enumerate(VALUE_TYPES):
            text = value_type.explaination()
            is_selected = value_type == configuration_attribute_gui.get_value_type()
            
            if i == 0:
                initial_radio_button = options.add_radio_button(1, 2, text, is_selected, lambda value_type=value_type: configuration_attribute_gui.set_value_type(value_type))
            else:
                options.add_linked_radio_button(initial_radio_button, text, is_selected, lambda value_type=value_type: configuration_attribute_gui.set_value_type(value_type))
                
        options.add_label(0, 3, "Hide from system views:")
        options.add_toggle_button(1, 3, "Hide", configuration_attribute_gui.is_hidden(), \
                                                                 lambda: configuration_attribute_gui.set_hidden(True), \
                                                                 lambda: configuration_attribute_gui.set_hidden(False))
        
    @staticmethod
    def configuration_input(model, view, configuration_input):
        """
        Options for configuration inputs
        """
        options = Options(model, view, max(1+len(CALCULATION_TYPES), 2), 3, "Input")
        
        options.add_label(0, 0, "Operation:")
        
        for i, calculation_type in enumerate(CALCULATION_TYPES):
            text = calculation_type.explaination()
            is_selected = calculation_type == configuration_input.get_calculation_type()
            
            if i == 0:
                initial_radio_button = options.add_radio_button(1, 0, text, is_selected, lambda calculation_type=calculation_type: configuration_input.set_calculation_type(calculation_type))
            else:
                options.add_linked_radio_button(initial_radio_button, text, is_selected, lambda calculation_type=calculation_type: configuration_input.set_calculation_type(calculation_type))
                
        # Add an entry field where the input scalar is specified, and set its default value
        attached_configuration_attribute_gui = configuration_input.get_attached_configuration_attribute_gui()
        
        if attached_configuration_attribute_gui != None:
            text_scalar = convert_value_to_string((attached_configuration_attribute_gui.get_input_scalar(),))
            text_offset = convert_value_to_string((attached_configuration_attribute_gui.get_input_offset(),))
        else:
            text_scalar = "1"
            text_offset = "0"
            
        entry_text_scalar = tk.StringVar()
        options.add_entry(0, 1, "Scalar (float or integer):", text_scalar, lambda: set_configuration_scalar(configuration_input, entry_text_scalar.get()), entry_text_scalar)
        
        entry_text_offset = tk.StringVar()
        options.add_entry(0, 2, "Offset (float or integer):", text_offset, lambda: set_configuration_offset(configuration_input, entry_text_offset.get()), entry_text_offset)
        
    @staticmethod
    def setup_class(model, view, setup_class_gui, setup_views):
        """
        Options for setup classes
        """
        options = Options(model, view, max(2, 1+len(setup_views)), 2, "Class")
        
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Name:", setup_class_gui.get_name(), lambda: setup_class_gui.set_name(entry_text.get()), entry_text)
        
        options.add_label(0, 1, "Add linked copy to system view:")
        
        # Buttons to create a linked copy in each respective setup view
        for i, setup_view in enumerate(setup_views):
            link_button = options.add_button(i+1, \
                                             1, \
                                             setup_view.get_name(), \
                                             lambda setup_view=setup_view: model.create_linked_setup_class_gui(setup_class_gui, setup_view))
            
    @staticmethod
    def connection(model, view, connection):
        """
        Options for connections between blocks in configuration views
        """
        options = Options(model, view, 1, 1, "Connection")
        options.add_toggle_button(0, 0, "External connection", connection.is_external(), lambda: connection.set_external(True), lambda: connection.set_external(False))
        
    @staticmethod
    def connection_with_blocks(model, view, connection):
        """
        Options for directional connection in setup views
        """
        options = Options(model, view, 2, 1, "Connection")
        default_text = connection.get_input_scalars_string()
        
        if default_text == None:
            default_text = "1"
            
        entry_text = tk.StringVar()
        options.add_entry(0, 0, "Scalar (number or a / b / c):", default_text, lambda: set_setup_scalars(connection, entry_text.get()), entry_text)
        
    def get_grid_coordinate(self, row, column):
        """
        Returns the grid coordinate that is represented by the top left square in the specified row and column
        """
        x = self.__x + column * OPTIONS_GRID_WIDTH
        y = self.__y + row * OPTIONS_GRID_HEIGHT
        
        return x, y
        
    def add_label(self, row, column, text, color=OPTIONS_HEADER_COLOR):
        """
        Adds a text fields
        """
        position = self.get_grid_coordinate(row, column)
        self.__background_block.add_attached_block(GUIModelingBlock(self.__model, self.__view, text, OPTIONS_GRID_WIDTH, OPTIONS_GRID_HEIGHT, color, position=position, ignore_zoom=True, tags_rect=(TAG_OPTIONS,), tags_text=(TAG_OPTIONS_TEXT,)))
        
    def add_entry(self, row, column, text, default_text, command, entry_text=None):
        """
        Adds a field for entrering text with a text field above that explains what should be entered
        """
        self.add_label(row, column, text)
        
        x, y = self.get_grid_coordinate(row+1, column)
        self.__background_block.add_attached_block(PressableEntry(self.__model, self.__view, x, y, OPTIONS_GRID_WIDTH, OPTIONS_GRID_HEIGHT, command, text=default_text, entry_text=entry_text, ignore_zoom=True, tags_rect=(TAG_OPTIONS,), tags_text=(TAG_OPTIONS_TEXT,)))
        
    def add_button(self, row, column, text, command):
        """
        Adds a pressable button
        """
        x, y = self.get_grid_coordinate(row, column)
        self.__background_block.add_attached_block(TouchButton.options(self.__model, self.__view, text, x, y, OPTIONS_BUTTON_COLOR, command))
        
    def add_move_buttons(self, row, column, text, command_up, command_down):
        """
        Adds buttons to change the order of objects
        """
        self.add_label(row, column, text)
        self.add_button(row+1, column, "Up", command_up)
        self.add_button(row+2, column, "Down", command_down)
        
    def add_radio_button(self, row, column, text, is_selected, command):
        """
        Adds a new unlinked radio button
        """
        x, y = self.get_grid_coordinate(row, column)
        radio_button = RadioButton.options(self.__model, self.__view, text, x, y, OPTIONS_BUTTON_COLOR, is_selected, command)
        self.__background_block.add_attached_block(radio_button)
        
        return radio_button
        
    def add_linked_radio_button(self, existing_radio_button, text, is_selected, command):
        """
        Adds a new linked radio button, where any other linked one will be unselected if this is selected or vice versa
        """
        self.__background_block.add_attached_block(existing_radio_button.create_linked_radio_button(text, is_selected, command))
        
    def add_toggle_button(self, row, column, text, is_selected, command_select, command_unselect):
        """
        Adds a toggable button (on or off state)
        """
        x, y = self.get_grid_coordinate(row, column)
        self.__background_block.add_attached_block(ToggleButton.options(self.__model, self.__view, text, x, y, OPTIONS_BUTTON_COLOR, is_selected, command_select, command_unselect))
        
    def move(self, move_x, move_y):
        """
        Moves the option window
        """
        self.__background_block.move_block(move_x, move_y)
        
    def delete(self):
        self.__background_block.delete()
        self.__view.reset_currently_open_options()
        
def set_configuration_scalar(configuration_input, input_scalar_string):
    try:
        input_scalar = convert_string_to_value(input_scalar_string)[0]
    except:
        input_scalar = 1
        
    configuration_input.set_input_scalar(input_scalar)
    
def set_configuration_offset(configuration_input, input_offset_string):
    try:
        input_offset = convert_string_to_value(input_offset_string)[0]
    except:
        input_offset = 0
        
    configuration_input.set_input_offset(input_offset)
    
def set_setup_scalars(connection, input_scalars_string):
    try:
        connection.set_input_scalars(convert_string_to_value(input_scalars_string))
    except:
        connection.reset_input_scalars()

def set_num_samples(num_samples_string):
    try:
        settings.set_num_samples(abs(int(num_samples_string)))
    except:
        settings.set_num_samples(1)
