from general_gui import GUIBlock, GUIModelingBlock
from helper_functions_general import convert_grid_coordinate_to_actual, get_max_directions_movement, convert_direction_to_vector
from default_coordinate_functions import get_block_start_coordinates
from config import *

def get_triangle_coordinates(view, x, y, direction, is_end_block):
    """
    Returns the corner coordinates of a triangle based on the direction which the triangle should point in
    """
    center_x = x + 0.5
    center_y = y + 0.5
    from_center = CONNECTION_END_WIDTH / 2
    
    # Default coordinates for each corner in a square
    upper_left = [center_x - from_center, center_y - from_center]
    upper_right = [center_x + from_center, center_y - from_center]
    lower_left = [center_x - from_center, center_y + from_center]
    lower_right = [center_x + from_center, center_y + from_center]
    
    to_adjust = convert_direction_to_vector(direction) * (1 - CONNECTION_END_WIDTH) / 2
    
    if not is_end_block:
        to_adjust *= -1
        
    # Combine two of the corners from a square with the point of the triangle that points in the specified direction
    if direction == "UP":
        coordinates = [center_x, center_y - from_center] + lower_right + lower_left
    elif direction == "RIGHT":
        coordinates = upper_left + [center_x + from_center, center_y] + lower_left
    elif direction == "DOWN":
        coordinates = upper_left + upper_right + [center_x, center_y + from_center]
    elif direction == "LEFT":
        coordinates = upper_right + lower_right + [center_x - from_center, center_y]
        
    for i in range(1, len(coordinates), 2):
        coordinates[i-1] += to_adjust[0]
        coordinates[i] += to_adjust[1]
        
    # Convert the grid coordinates to pixel coordinates
    actual_coordinates = []
    
    for i in range(0, len(coordinates), 2):
        actual_x, actual_y = convert_grid_coordinate_to_actual(coordinates[i], coordinates[i+1], view.get_length_unit())
        actual_coordinates += [actual_x, actual_y]
        
    return actual_coordinates
    
class GUIConnectionCorner(GUIBlock):
    """
    Manages the block on a corner of a connection
    """
    def __init__(self, model, view, connection, x, y):
        actual_x, actual_y = convert_grid_coordinate_to_actual(x+0.5-CORNER_WIDTH/2, y+0.5-CORNER_HEIGHT/2, view.get_length_unit())
        actual_width, actual_height = convert_grid_coordinate_to_actual(CORNER_WIDTH, CORNER_HEIGHT, view.get_length_unit())
        self.__rect = view.get_canvas().create_rectangle(actual_x, \
                                                         actual_y, \
                                                         actual_x+actual_width, \
                                                         actual_y+actual_height, \
                                                         width=OUTLINE_WIDTH, \
                                                         outline=OUTLINE_COLOR, \
                                                         fill=CORNER_COLOR, \
                                                         tags=(TAG_CONNECTION_CORNER,))
        
        super().__init__(model, view, [self.__rect], x, y, CORNER_WIDTH, CORNER_HEIGHT, bind_left=MOUSE_DRAG)
        self.__connection = connection
        self.__was_dragged = False
        
    def left_dragged(self, event):
        self.__was_dragged = True
        
        allowed_movement_directions = self.__connection.allowed_corner_movement_directions(self)
        max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = get_max_directions_movement(allowed_movement_directions)
        
        last_grid_x, last_grid_y = self.get_x(), self.get_y()
        
        move_x, move_y = super().left_dragged(event, \
                                              max_positive_move_x=max_positive_move_x, \
                                              max_negative_move_x=max_negative_move_x, \
                                              max_positive_move_y=max_positive_move_y, \
                                              max_negative_move_y=max_negative_move_y, \
                                              single_direction=True)
        
        # Move adjacent corners that need to follow the dragged corner
        for adjacent_corner in self.__connection.get_adjacent_corners(self):
            # Horizontally aligned
            if adjacent_corner.get_y() == last_grid_y:
                adjacent_corner.move_block(0, move_y)
                
            # Vertically aligned
            elif adjacent_corner.get_x() == last_grid_x:
                adjacent_corner.move_block(move_x, 0)
                
        self.__connection.adjust_lines_to_dragged_corners()
        
    def left_released(self, event):
        super().left_released(event, False)
        
        if self.__was_dragged:
            for adjacent_corner in self.__connection.get_adjacent_corners(self):
                adjacent_corner.snap_to_grid()
                
            # Adjust lines to match the new position of corners after they have snapped to the grid
            self.__connection.adjust_lines_to_dragged_corners()
            
            self.get_view().update_shown_order()
            
    def open_options(self):
        self.__connection.open_options()
        
    def delete(self, manual_delete=False):
        if not self.is_deleted():
            super().delete()
            
            if manual_delete:
                self.__connection.delete()
                
class GUIConnectionTriangle(GUIBlock):
    """
    Manages the triangle block found at each end of a directional connection in setup views
    """
    def __init__(self, model, view, direction, is_end_block, position=None):
        if position == None:
            coordinates = get_block_start_coordinates(view.get_length_unit(), 2)
            
            if not is_end_block:
                x, y = coordinates[0]
            else:
                x, y = coordinates[1]
                
        else:
            x, y = position
            
        self.__is_end_block = is_end_block # This block points into a setup class
        self.__triangle = view.get_canvas().create_polygon(get_triangle_coordinates(view, x, y, direction, is_end_block), \
                                                           width=OUTLINE_WIDTH, \
                                                           outline=OUTLINE_COLOR, \
                                                           fill=CONNECTION_END_COLOR, \
                                                           tags=(TAG_CONNECTION_CORNER,))
        
        super().__init__(model, view, [self.__triangle], x, y, CONNECTION_END_WIDTH, CONNECTION_END_WIDTH, bind_left=MOUSE_DRAG)
        self.__connection = None
        self.__attached_setup_class_gui = None
        
    def left_dragged(self, event):
        super().left_dragged(event)
        
        # Disconnect from class
        if self.__attached_setup_class_gui != None:
            self.attempt_to_detach_from_class()
            
    def left_released(self, event):
        if super().left_released(event, False):
            self.put_down_block()
            
        self.get_view().update_shown_order()
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        # If panning or zooming, only the start block should move the lines
        if (not self.get_view().is_panning() and not self.get_view().is_zooming()) or not self.__is_end_block:
            self.__connection.move_lines(move_x, move_y)
            
    def scale(self, new_length_unit, last_length_unit):
        super().scale(new_length_unit, last_length_unit)
        
        # Scale the connection between the triangle blocks if this is the start block
        if not self.__is_end_block:
            self.__connection.scale(new_length_unit, last_length_unit)
            
    def open_options(self):
        self.__connection.open_options()
            
    def put_down_block(self):
        """
        When releasing the block after dragging it, attempt to attach to an adjacent setup class
        """
        for setup_class_gui in self.get_view().get_setup_classes_gui():
            is_adjacent, direction = setup_class_gui.is_adjacent([(self.get_x(), self.get_y())])
            
            # Attach to class
            if is_adjacent:
                # If this connection is redundant (another already exist between these two setup classes), delete it
                if (self.__is_end_block and \
                    self.__connection.get_start_setup_class() in setup_class_gui.get_setup_class().get_input_setup_classes()) \
                   or \
                   (not self.__is_end_block and \
                    self.__connection.get_end_setup_class() != None and \
                    setup_class_gui.get_setup_class() in self.__connection.get_end_setup_class().get_input_setup_classes()):
                    self.delete()
                    return
                    
                setup_class_gui.add_connection(self.__connection)
                setup_class_gui.add_attached_block(self)
                self.__attached_setup_class_gui = setup_class_gui
                
                self.__connection.update_direction(self, direction)
                self.rotate_triangle(direction)
                
                self.attempt_to_enable_calculation_connection() # If both ends are connected, the connection is now used for calculations
                
                break
                
        self.__connection.correct_scalars_indicator_location()
        
    def rotate_triangle(self, new_direction):
        """
        Rotates the triangle to point in the specified direction
        """
        if self.__is_end_block:
            directions = ["UP", "RIGHT", "DOWN", "LEFT"]
            new_direction = directions[(directions.index(new_direction) + 2) % len(directions)]
            
        new_coordinates = get_triangle_coordinates(self.get_view(), self.get_x(), self.get_y(), new_direction, self.__is_end_block)
        self.get_view().get_canvas().coords(self.__triangle, new_coordinates)
        
        # Update the highlight to point in the same direction
        self.update_highlight(HIGHLIGHT_SELECTED_COLOR)
        
    def get_connection_actual_start(self, direction):
        """
        Returns the pixel coordinate that a connection line should start from
        """
        # Center of block as default
        x = self.get_x() + 0.5
        y = self.get_y() + 0.5
        
        # Correct one of the values to get the correct coordinate considering the direction which the line goes out from the block
        if direction == "UP":
            y = self.get_y() + (1 - self.get_height())
        elif direction == "DOWN":
            y = self.get_y() + self.get_height()
        elif direction == "LEFT":
            x = self.get_x() + (1 - self.get_width())
        elif direction == "RIGHT":
            x = self.get_x() + self.get_width()
            
        actual_x, actual_y = convert_grid_coordinate_to_actual(x, y, self.get_view().get_length_unit())
        
        return actual_x, actual_y
        
    def add_connection(self, connection):
        self.__connection = connection
        
    def get_attached_setup_class_gui(self):
        return self.__attached_setup_class_gui
        
    def is_attached(self):
        """
        Returns whether the block is currently attached to a setup class
        """
        return self.__attached_setup_class_gui != None
        
    def attempt_to_detach_from_class(self):
        """
        Detaches from connected class if connected to one
        """
        if self.__attached_setup_class_gui != None:
            self.attempt_to_disable_calculation_connection() # Connection is no longer used for calculations, if it previously was
            
            self.__attached_setup_class_gui.remove_connection(self.__connection)
            self.__attached_setup_class_gui.remove_attached_block(self)
            
            # Update value input type of setup class that takes input from previously connected setup class
            if self.__connection.get_end_setup_class_gui() != None:
                self.__connection.get_end_setup_class_gui().update_value_input_types()
                
            self.__attached_setup_class_gui = None
            
    def attempt_to_enable_calculation_connection(self):
        """
        Attempts to connect the calculation blocks without GUI when both GUI end blocks have been connected
        """
        if not self.get_view().is_excluded():
            start_setup_class = self.__connection.get_start_setup_class()
            end_setup_class = self.__connection.get_end_setup_class()
            
            if start_setup_class != None and end_setup_class != None:
                end_setup_class.set_input_setup_class(start_setup_class, self.__connection.get_input_scalars())
                self.__connection.get_end_setup_class_gui().update_value_input_types()
                
    def attempt_to_disable_calculation_connection(self):
        """
        Attempt to disconnect the calculation blocks without GUI
        """
        end_setup_class = self.__connection.get_end_setup_class()
        
        # Remove start setup class as input from the end setup class
        if end_setup_class != None:
            end_setup_class.remove_input_setup_class(self.__connection.get_start_setup_class())
            
    def delete(self):
        if not self.is_deleted():
            self.attempt_to_detach_from_class()
            self.__connection.delete()
            
        super().delete()
        
class GUIConnectionScalarsIndicator(GUIModelingBlock):
    """
    Manages indicator that shows the input scalars for a directional connection in setup views
    """
    def __init__(self, model, view, connection):
        super().__init__(model, view, connection.get_input_scalars_string(), \
                                      INPUT_SCALARS_INDICATOR_WIDTH, \
                                      INPUT_SCALARS_INDICATOR_HEIGHT, \
                                      INPUT_SCALARS_INDICATOR_COLOR, \
                                      position=connection.get_scalars_indicator_start_coordinate(), \
                                      bind_left=MOUSE_DRAG, \
                                      tags_rect=(TAG_INDICATOR,), \
                                      tags_text=(TAG_INDICATOR_TEXT,))
        self.__connection = connection
        
    def left_dragged(self, event):
        allowed_movement_directions = self.__connection.allowed_scalars_indicator_movement_directions()
        max_positive_move_x, max_negative_move_x, max_positive_move_y, max_negative_move_y = get_max_directions_movement(allowed_movement_directions)
        
        super().left_dragged(event, \
                             max_positive_move_x=max_positive_move_x, \
                             max_negative_move_x=max_negative_move_x, \
                             max_positive_move_y=max_positive_move_y, \
                             max_negative_move_y=max_negative_move_y, \
                             single_direction=True)
        
    def open_options(self):
        return self.__connection.open_options()
        
    def update_displayed_input_scalars(self):
        self.set_text(self.__connection.get_input_scalars_string())
        
    def delete(self, manual_delete=False):
        super().delete()
        
        if manual_delete:
            self.__connection.reset_input_scalars()
