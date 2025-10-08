import numpy as np
import tkinter.font as tkfont

def convert_value_to_string(value):
    """
    Takes a NumPy array or list as input and converts it to a string
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    if not isinstance(value, tuple):
        print(f"Error: Could not convert {value} to string, as it was not a tuple")
        return None
        
    final_value = []
    
    for element in value:
        try:
            rounded_value = round(float(element), DECIMALS_WHEN_ROUNDING)
            
            # If the float does not have any decimal numbers, convert it to an integer for a better looking output
            if rounded_value == int(rounded_value):
                rounded_value = int(rounded_value)
        except:
            rounded_value = element
            
        final_value.append(str(rounded_value))
        
    return " / ".join(final_value)
    
def convert_string_to_value(string):
    """
    Takes a string as input and converts it to a tuple, where each value is attempted to be converted to a float
    """
    values = []
    
    for value_string in string.split("/"):
        value = value_string.strip()
        
        try:
            values.append(float(value))
        except:
            values.append(value)
            
    return tuple(values)
    
def convert_grid_coordinate_to_actual(grid_x, grid_y, length_unit):
    """
    Converts/scales a coordinate in the grid to one based on pixels
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    actual_x = round(grid_x * length_unit, DECIMALS_WHEN_ROUNDING)
    actual_y = round(grid_y * length_unit, DECIMALS_WHEN_ROUNDING)
    
    return actual_x, actual_y
    
def convert_actual_coordinate_to_grid(actual_x, actual_y, length_unit):
    """
    Converts/scales a coordinate based on pixels to one based on the grid
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    grid_x = round(actual_x / length_unit, DECIMALS_WHEN_ROUNDING)
    grid_y = round(actual_y / length_unit, DECIMALS_WHEN_ROUNDING)
    
    return grid_x, grid_y
    
def get_actual_coordinates_after_scale(actual_coordinates_before_scale, new_length_unit, last_length_unit):
    """
    actual_coordinates_before_scale: A sequence of x and y values (for example, a tuple (x1, y1, x2, y2)) before the coordinate was scaled
    new_length_unit: The length unit before the scaling
    last_length_unit: The length unit after the scaling
    
    Converts the pixel values before scaling (such as zooming a view) to the corresponding ones after the scaling
    """
    adjusted_actual_coordinates = []
    
    for i in range(0, len(actual_coordinates_before_scale), 2):
        previous_actual_x = actual_coordinates_before_scale[i]
        previous_actual_y = actual_coordinates_before_scale[i+1]
        
        # Convert to grid coordinates using the length unit before the scaling
        previous_grid_x, previous_grid_y = convert_actual_coordinate_to_grid(previous_actual_x, previous_actual_y, last_length_unit)
        
        # Convert the grid coordinates back to pixel coordinates using the new length unit after the zoom
        for value in convert_grid_coordinate_to_actual(previous_grid_x, previous_grid_y, new_length_unit):
            adjusted_actual_coordinates.append(value)
            
    return adjusted_actual_coordinates
    
def distance_to_closest_grid_intersection(view, grid_x, grid_y):
    """
    Find the distance from a grid coordinate to the closest grid intersection considering the offset of the grid due to panning/zooming
    The x and y distances are in the range [-0.5, 0.5)
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    grid_offset_x, grid_offset_y = view.get_grid_offset()
    
    grid_distance_x = round(int(grid_x + 0.5 - grid_offset_x) - grid_x + grid_offset_x, DECIMALS_WHEN_ROUNDING)
    grid_distance_y = round(int(grid_y + 0.5 - grid_offset_y) - grid_y + grid_offset_y, DECIMALS_WHEN_ROUNDING)
    
    if grid_x <= -0.5:
        grid_distance_x -= 1
        
    if grid_y <= -0.5:
        grid_distance_y -= 1
        
    return grid_distance_x, grid_distance_y
    
def get_grid_mid_x(view, grid_x):
    """
    Get the x coordinate in the middle of the current grid square considering the offset of the grid due to panning/zooming
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    grid_offset_x, _ = view.get_grid_offset()
    
    grid_mid_x = round(int(grid_x - grid_offset_x + 0.5) + grid_offset_x, DECIMALS_WHEN_ROUNDING)
    
    return grid_mid_x
    
def get_grid_mid_y(view, grid_y):
    """
    Get the y cooridinate in the middle of the current grid square considering the offset of the grid due to panning/zooming
    """
    from config import DECIMALS_WHEN_ROUNDING
    
    _, grid_offset_y = view.get_grid_offset()
    
    grid_mid_y = round(int(grid_y - grid_offset_y + 0.5) + grid_offset_y, DECIMALS_WHEN_ROUNDING)
    
    return grid_mid_y
    
def get_max_directions_movement(allowed_movement_directions):
    """
    allowed_movement_directions: A list of directions that a block cannot move in
    
    Returns a list of the maximum distance a block can move in any direction, where None means no limit
    """
    max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = [None] * 4
    
    if "RIGHT" not in allowed_movement_directions:
        max_positive_move_x = 0
        
    if "LEFT" not in allowed_movement_directions:
        max_negative_move_x = 0
        
    if "DOWN" not in allowed_movement_directions:
        max_positive_move_y = 0
        
    if "UP" not in allowed_movement_directions:
        max_negative_move_y = 0
        
    return max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y
    
def convert_direction_to_vector(direction):
    """
    direction: Tuple (x, y, direction)
    
    Returns a normalized vector converted from a specified direction
    """
    if direction == "UP":
        return np.array([0, -1])
    elif direction == "RIGHT":
        return np.array([1, 0])
    elif direction == "DOWN":
        return np.array([0, 1])
    elif direction == "LEFT":
        return np.array([-1, 0])
        
    print(f"Error: Did not recognize direction {direction}")
    
def get_font(length_unit, *, canvas_and_label=None, has_line_break=False):
    """
    canvas_and_label: Tuple (canvas, label)
    has_line_break: Whether the text should line break
    
    Returns the font size that should be used in a text field on the canvas given considering the current scaling (zoom) level and whether there is a line break (need to lower font size further)
    """
    from config import LENGTH_UNIT, FONT, FONT_DECREASE_LINE_BREAK
    
    new_font_size = int(FONT[1] * length_unit / LENGTH_UNIT + 0.5)
    
    if has_line_break:
        new_font_size -= FONT_DECREASE_LINE_BREAK
        
    if new_font_size < 1:
        new_font_size = 1
        
    if canvas_and_label == None:
        return (FONT[0], new_font_size)
        
    canvas, label = canvas_and_label
    
    # Get existing attributes of the font
    current_font = canvas.itemcget(label, "font").split()
    
    if len(current_font) == 2:
        updated_font = (current_font[0], new_font_size)
        
    elif len(current_font) == 3:
        updated_font = (current_font[0], new_font_size, current_font[2])
        
    else:
        return (FONT[0], new_font_size)
        
    return updated_font
    
def get_text_that_fits(canvas, label, text, text_width, is_bold, length_unit):
    """
    Returns the text and its corresponding font required for the specified text to fit within the specified grid text width
    """
    from config import OUTLINE_WIDTH
    
    actual_maximum_text_width = convert_grid_coordinate_to_actual(text_width, 0, length_unit)[0] - 2 * OUTLINE_WIDTH
    font = get_font(length_unit, canvas_and_label=(canvas, label))
    
    if is_bold:
        font = (font[0], font[1], "bold")
        actual_text_width = tkfont.Font(family=font[0], size=font[1], weight=font[2]).measure(text)
    else:
        font = (font[0], font[1])
        actual_text_width = tkfont.Font(family=font[0], size=font[1]).measure(text)
        
    # Should add line break and lower font size
    if actual_text_width >= actual_maximum_text_width:
        has_line_break_text = True
        
        # Find the space that is closest to the middle and line break there
        words = text.split()
        mid_index = len(text) // 2
        current_number_of_characters = 0
        
        for i, word in enumerate(words):
            current_number_of_characters += len(word) + 1
            
            if current_number_of_characters >= mid_index:
                if current_number_of_characters - mid_index < len(word) // 2:
                    text = " ".join(words[:i+1]) + "\n" + " ".join(words[i+1:])
                else:
                    text = " ".join(words[:i]) + "\n" + " ".join(words[i:])
                    
                break
                
    else:
        has_line_break_text = False
        
    font = get_font(length_unit, canvas_and_label=(canvas, label), has_line_break=has_line_break_text)
    
    if is_bold:
        font = (font[0], font[1], "bold")
    else:
        font = (font[0], font[1])
        
    return text, font
    
def delete_all(to_delete_list, manual_delete=False):
    """
    Calls the delete method of all elements in to_delete_list
    """
    from configuration_attribute_gui import GUIConfigurationAttribute
    from connection_blocks_gui import GUIConnectionCorner, GUIConnectionScalarsIndicator
    
    for i in range(len(to_delete_list)-1, -1, -1):
        if manual_delete and isinstance(to_delete_list[i], (GUIConfigurationAttribute, GUIConnectionCorner, GUIConnectionScalarsIndicator)):
            to_delete_list[i].delete(True)
        else:
            to_delete_list[i].delete()
