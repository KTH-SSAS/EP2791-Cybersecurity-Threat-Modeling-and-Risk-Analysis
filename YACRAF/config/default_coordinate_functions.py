from helper_functions_general import convert_actual_coordinate_to_grid
from config import *

def get_block_start_coordinates(length_unit, num_coordinates=1):
    """
    Returns the default grid coordinates when creating new blocks, where subsequent values are used when multiple blocks are created at the same time to avoid stacking
    """
    grid_x, grid_y = convert_actual_coordinate_to_grid(settings.get_canvas_width()/3, settings.get_canvas_height()/3, length_unit)
    grid_coordinates = [(grid_x, grid_y)]
    
    for i in range(1, num_coordinates):
        grid_coordinates.append((grid_x+2*i, grid_y+2*i))
        
    return grid_coordinates
    
def get_save_coordinate(length_unit):
    """
    Returns the grid coordinate of the save button
    """
    return 0, settings.get_canvas_height() / length_unit - SETTINGS_HEIGHT - SAVE_HEIGHT
    
def get_settings_coordinate(length_unit):
    """
    Returns the grid coordinate of the settings button
    """
    return 0, settings.get_canvas_height() / length_unit - SETTINGS_HEIGHT
    
def get_change_configuration_view_start_coordinate(length_unit):
    """
    Returns the grid coordinate of the first configuration view button
    """
    return settings.get_canvas_width() / length_unit - 2 * CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT
    
def get_change_setup_view_start_coordinate(length_unit):
    """
    Returns the grid coordinate of the first setup view button
    """
    return settings.get_canvas_width() / length_unit - CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT
    
def get_create_class_coordinate(length_unit):
    """
    Returns the grid coordinate of the button creating a new configuration class
    """
    return 0, 0
    
def get_create_input_coordinate(length_unit):
    """
    Returns the grid coordinate of the button creating a new input block
    """
    return 0, ADD_CLASS_HEIGHT
    
def get_to_setup_start_coordinate(length_unit):
    """
    Returns the grid coordinate of the first button that adds the setup version of a configuration class to a setup view
    """
    return 0, 0
    
def get_create_connection_coordinate(length_unit):
    """
    Returns the grid coordinate of the button creating a directional connection in a setup view
    """
    return settings.get_canvas_width() / (2 * length_unit) - ADD_CONNECTION_WIDTH, 0
    
def get_calculate_values_coordinate(length_unit):
    """
    Returns the grid coordinate of the button calculating all attribute values in the setup views
    """
    return settings.get_canvas_width() / (2 * length_unit), 0
    
def get_create_attribute_offset():
    """
    Returns the grid offset from the last attribute that the button for creating another attribute is positioned
    """
    return (ATTRIBUTE_WIDTH - ADD_ATTRIBUTE_WIDTH) / 2, 0
    
def get_create_configuration_view_offset():
    """
    Returns the grid offset from the last button changing to configuration views that the button for creating another configuration view is positioned
    """
    return (CHANGE_VIEW_WIDTH - ADD_CHANGE_VIEW_WIDTH) / 2, 0
    
def get_create_setup_view_offset():
    """
    Returns the grid offset from the last button changing to setup views that the button for creating another setup view is positioned
    """
    return (CHANGE_VIEW_WIDTH - ADD_CHANGE_VIEW_WIDTH) / 2, 0
    
def get_run_script_start_coordinate(length_unit):
    """
    Returns the grid coordinate of the button running or clearing scripts
    """
    return settings.get_canvas_width() / length_unit - RUN_SCRIPT_WIDTH, settings.get_canvas_height() / length_unit - RUN_SCRIPT_HEIGHT
    
def get_options_coordinate(length_unit):
    """
    Returns the grid coordinate top center of options
    """
    return settings.get_canvas_width() / (2 * length_unit), 2
