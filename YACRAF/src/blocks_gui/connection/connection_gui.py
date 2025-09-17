import tkinter as tk
import numpy as np
from connection_blocks_gui import GUIConnectionCorner, GUIConnectionTriangle
from circle_indicator_gui import GUICircleIndicator
from helper_functions_general import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_scale, get_grid_mid_x, get_grid_mid_y, convert_direction_to_vector
from options import Options
from config import *

class GUIConnection:
    """
    Connects two blocks by lines
    """
    def __init__(self, model, view, start_block, start_direction, *, end_block=None, \
                                                                     end_direction=None, \
                                                                     corner_coordinates=None, \
                                                                     is_external=False, \
                                                                     mouse_location=None):
        self.__model = model
        self.__view = view
        
        self.__start_block = start_block
        self.__start_direction = start_direction # Direction which the first line goes out from the start block
        
        self.__end_block = end_block
        self.__end_direction = end_direction # Direction which the last line goes out from the end block
        
        self.__corners = []
        self.__lines = []
        
        # Indicator for which order connections are considered when calculating values (only applying to relevant calculation types)
        self.__num_order = None
        self.__num_order_indicator = None
        
        self.__is_external = is_external
        self.__is_deleted = False
        
        start_block.add_connection(self)
        
        # End block was specified
        if end_block != None:
            end_block.add_connection(self)
            
        self.create_new_lines(mouse_location)
        
        # Specific coordinates for corners were specified
        if corner_coordinates != None:
            for i, corner in enumerate(self.__corners):
                move_x = corner_coordinates[i][0] - corner.get_x()
                move_y = corner_coordinates[i][1] - corner.get_y()
                
                corner.move_block(move_x, move_y)
                
            self.adjust_lines_to_dragged_corners()
            
    def scale(self, new_length_unit, last_length_unit):
        """
        Scales items on the canvas when zooming
        """
        # Scale lines
        for line in self.__lines:
            adjusted_actual_coordinates = get_actual_coordinates_after_scale(self.__view.get_canvas().coords(line), new_length_unit, last_length_unit)
            x1, y1, x2, y2 = adjusted_actual_coordinates
            self.__view.get_canvas().coords(line, x1, y1, x2, y2)
            
        # Scale corners        
        for corner in self.__corners:
            corner.scale(new_length_unit, last_length_unit)
            
        # Scale connection order indicator
        if self.__num_order_indicator != None:
            self.__num_order_indicator.scale(new_length_unit, last_length_unit)
            
    def open_options(self):
        return Options.connection(self.__model, self.__view, self)
            
    def get_start_block(self):
        return self.__start_block
        
    def get_start_direction(self):
        return self.__start_direction
        
    def get_end_block(self):
        return self.__end_block
        
    def get_end_direction(self):
        return self.__end_direction
        
    def set_end_location(self, block, direction):
        """
        Connects the connection to an end block
        """
        self.__end_block = block
        self.__end_direction = direction
        
        self.__end_block.add_connection(self)
        
        self.create_new_lines()
        self.__view.update_shown_order()
        
    def update_direction(self, affected_block, new_direction):
        """
        Updates the direction which the line goes out from a block
        """
        if affected_block == self.__start_block:
            self.__start_direction = new_direction
            
        elif affected_block == self.__end_block:
            self.__end_direction = new_direction
            
        self.create_new_lines()
        
    def create_new_lines(self, mouse_location=None):
        """
        Deletes existing lines and corners, creating new ones
        """
        self.remove_corners()
        self.remove_lines()
        
        start_x, start_y = self.__start_block.get_connection_grid_start(self.__start_direction)
        
        # The lines should follow the mouse around as it has not been connected to a block yet
        if mouse_location != None:
            end_x, end_y = convert_actual_coordinate_to_grid(mouse_location[0], mouse_location[1], self.__view.get_length_unit())
            
            # Direction which the line should attach to the mouse
            if end_x > start_x:
                self.__end_direction = "LEFT"
                end_x -= 0.5
            else:
                self.__end_direction = "RIGHT"
                end_x += 0.5
        else:
            end_x, end_y = self.__end_block.get_connection_grid_start(self.__end_direction)
            
        corner_coordinates = self.create_corners(start_x, start_y, end_x, end_y)
        
        # Create corners
        for corner_x, corner_y in corner_coordinates:
            self.__corners.append(GUIConnectionCorner(self.__model, self.__view, self, corner_x, corner_y))
            
        # Draw lines based on the created corners
        if mouse_location != None:
            self.create_lines_from_corners((end_x, end_y+0.5))
        else:
            self.create_lines_from_corners()
            
    def adjust_lines_to_dragged_corners(self):
        """
        Corrects the lines to match the new position of corners as they have been dragged around
        """
        self.remove_lines()
        self.create_lines_from_corners()
        
    def get_corners(self):
        return self.__corners
                
    def get_adjacent_corners(self, corner):
        """
        Returns list of corners that are adjacent to the specified corner (directly connected to it)
        """
        corner_index = self.__corners.index(corner)
        adjacent_corners = []
        
        # Previous corner
        if corner_index > 0:
            adjacent_corners.append(self.__corners[corner_index-1])
            
        # Next corner
        if corner_index < len(self.__corners) - 1:
            adjacent_corners.append(self.__corners[corner_index+1])
            
        return adjacent_corners
        
    def allowed_corner_movement_directions(self, corner):
        """
        Returns a list of directions that the specified corner can be moved (other directions would require additional corners to be added)
        """
        adjacent_corners = self.get_adjacent_corners(corner)
        allowed_directions = set()
        
        for adjacent_corner in adjacent_corners:
            # Adjacent corner is above or below
            if adjacent_corner.get_x() == corner.get_x():
                allowed_directions.update({"LEFT", "RIGHT"})
                
            # Adjacent corner is to the left or the right
            elif adjacent_corner.get_y() == corner.get_y():
                allowed_directions.update({"UP", "DOWN"})
                
        return list(allowed_directions)
        
    def move_lines(self, move_x, move_y):
        """
        Attempts to move all lines and corners without recreating the path, but will resort to creating an entirely new path if necessary
        """
        # If currently panning or zooming, only move lines and corners
        if self.__view.is_panning() or self.__view.is_zooming():
            for corner in self.__corners:
                corner.move_block(move_x, move_y)
                
            for line in self.__lines:
                actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(move_x, move_y, self.__view.get_length_unit())
                self.__view.get_canvas().move(line, actual_move_x, actual_move_y)
                
            if self.__num_order_indicator != None:
                self.__num_order_indicator.move(move_x, move_y)
                
            return True
            
        # If not panning, need to create completely new lines and corners
        else:
            self.create_new_lines()
            
            return False
            
    def attempt_to_create_number_indicator(self):
        """
        Will add an indicator for the order which this connection has been connected to a specific input block (important for some mathematical operations) if it has a specific number
        """
        if self.__num_order != None:
            num_order_x, num_order_y = self.__start_block.get_connection_grid_start(self.__start_direction)
            
            if self.__start_direction == "LEFT":
                num_order_x += 1
                
            num_order_y += 0.5
            
            self.__num_order_indicator = GUICircleIndicator(self.__view, num_order_x, num_order_y, NUM_ORDER_CIRCLE_RADIUS, NUM_ORDER_CIRCLE_COLOR, NUM_ORDER_CIRCLE_OUTLINE, self.__num_order)
            
    def attempt_to_remove_number_indicator(self):
        """
        Removes indicator for which order the connection has been connected to a specific input block if such an indicator exists
        """
        if self.__num_order_indicator != None:
            self.__num_order_indicator.remove()
            self.__num_order_indicator = None
            
    def create_lines_from_corners(self, end_grid_location=None):
        """
        Creates the lines that connect previously created corners
        """
        actual_coordinates = [self.__start_block.get_connection_actual_start(self.__start_direction)]
        
        # Get the coordinate of each existing corner
        for corner in self.__corners:
            actual_corner_x, actual_corner_y = convert_grid_coordinate_to_actual(corner.get_x()+0.5, corner.get_y()+0.5, self.__view.get_length_unit())
            actual_coordinates.append((actual_corner_x, actual_corner_y))
            
        if end_grid_location != None:
            actual_coordinates.append(convert_grid_coordinate_to_actual(end_grid_location[0], end_grid_location[1], self.__view.get_length_unit()))
        else:
            actual_coordinates.append(self.__end_block.get_connection_actual_start(self.__end_direction))
            
        # Draw lines between each corner coordinate
        for i in range(1, len(actual_coordinates)):
            from_x = actual_coordinates[i-1][0]
            from_y = actual_coordinates[i-1][1]
            to_x = actual_coordinates[i][0]
            to_y = actual_coordinates[i][1]
            
            # Draw a dashed line if an external connection
            if self.__is_external:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH, dash=CONNECTION_DASH, tags=(TAG_CONNECTION_LINE,))
            else:
                line = self.__view.get_canvas().create_line(from_x, from_y, to_x, to_y, fill=CONNECTION_COLOR, width=CONNECTION_WIDTH, tags=(TAG_CONNECTION_LINE,))
                
            self.__lines.append(line)
            
        self.attempt_to_create_number_indicator()
        
    def positions_dot_product(self, current_position, final_position):
        """
        current_position: Tuple (x, y, direction)
        final_position: Tuple (x, y, direction)
        
        Returns the dot product between a normalized vector from current_position to final_position with the normalized vector that is created based on the direction out from current_position
        """
        vector_to_final_position = np.array([final_position[0] - current_position[0], final_position[1] - current_position[1]])
        vector_direction = convert_direction_to_vector(current_position[2])
        
        vector_to_final_position_norm = np.linalg.norm(vector_to_final_position)
        
        if vector_to_final_position_norm != 0:
            vector_to_final_position = vector_to_final_position / vector_to_final_position_norm
            
        return np.dot(vector_to_final_position, vector_direction)
        
    def get_position_after_turn(self, current_position, final_position):
        """
        current_position: Tuple (x, y, direction)
        final_position: Tuple (x, y, direction)
        
        Returns a tuple (x, y, direction) of a corner position, where the direction has been changed according to which direction the connection should turn next
        """
        current_direction = current_position[2]
        current_x, current_y, _ = current_position
        new_direction = ""
        
        if current_direction == "UP":
            if final_position[0] < current_position[0]:
                new_direction = "LEFT"
            else:
                new_direction = "RIGHT"
                
        elif current_direction == "RIGHT":
            if final_position[1] < current_position[1]:
                new_direction = "UP"
            else:
                new_direction = "DOWN"
                
        elif current_direction == "DOWN":
            if final_position[0] > current_position[0]:
                new_direction = "RIGHT"
            else:
                new_direction = "LEFT"
                
        elif current_direction == "LEFT":
            if final_position[1] > current_position[1]:
                new_direction = "DOWN"
            else:
                new_direction = "UP"
        
        else:
            print(f"Error: Did not recognize direction {current_direction}")
            
        return (current_x, current_y, new_direction)
        
    def create_corners(self, start_x, start_y, end_x, end_y):
        """
        Returns a list of corners between the start and end coordinates
        """
        sorted_directions = tuple(sorted([self.__start_direction, self.__end_direction]))
        
        # No corners are necessary if the end points point directly toward each other
        if (sorted_directions == ("DOWN", "UP") and abs(start_x - end_x) < 0.1) or \
           (sorted_directions == ("LEFT", "RIGHT") and abs(start_y - end_y) < 0.1):
            return []
            
        corners_from_start = []
        corners_from_end = []
        
        position_start = (start_x, start_y, self.__start_direction)
        position_end = (end_x, end_y, self.__end_direction)
        
        while True:
            # Dot product between current direction and the direction to the other end
            start_dot_product = self.positions_dot_product(position_start, position_end)
            end_dot_product = self.positions_dot_product(position_end, position_start)
            
            # Both ends point at most 90 degrees wrong toward each other
            if start_dot_product >= 0 and end_dot_product >= 0:
                start_x, start_y, _ = self.get_position_after_turn(position_start, position_end)
                end_x, end_y, _ = self.get_position_after_turn(position_end, position_start)
                
                # Parallel
                if abs(np.dot(convert_direction_to_vector(position_start[2]), convert_direction_to_vector(position_end[2]))) == 1:
                    if position_start[2] in ("DOWN", "UP"):
                        mid_y = get_grid_mid_y(self.__view, (start_y + end_y) / 2)
                        corners_from_start.append((start_x, mid_y))
                        corners_from_end.append((end_x, mid_y))
                        
                    else:
                        mid_x = get_grid_mid_x(self.__view, (start_x + end_x) / 2)                           
                        corners_from_start.append((mid_x, start_y))
                        corners_from_end.append((mid_x, end_y))
                        
                # Intersecting
                else:
                    if position_start[2] in ("DOWN", "UP"):
                        corners_from_start.append((start_x, end_y))
                        
                    else:
                        corners_from_start.append((end_x, start_y))
                        
                break
                
            # The end point whose current corner has the currently sharpest required turn toward the other end point's current corner should turn first
            if start_dot_product <= end_dot_product:
                position_start = self.get_position_after_turn(position_start, position_end)
                corners_from_start.append((position_start[0], position_start[1]))
                
            else:
                position_end = self.get_position_after_turn(position_end, position_start)
                corners_from_end.append((position_end[0], position_end[1]))
                
            if len(corners_from_start + corners_from_end) >= 10:
                break
                
        # To order the corners from the starting point to the end point
        corners_from_end.reverse()
        
        return corners_from_start + corners_from_end
        
    def remove_corners(self):
        for corner in self.__corners:
            corner.delete(False)
            
        self.__corners.clear()
        
    def remove_lines(self):
        for line in self.__lines:
            self.__view.get_canvas().delete(line)
            
        self.attempt_to_remove_number_indicator()
        
        self.__lines.clear()
        
    def set_num_order(self, num_order):
        """
        Sets the number which is displayed to indicate which order connections have been connected to an input block
        """
        self.__num_order = num_order
        self.attempt_to_remove_number_indicator()
        self.attempt_to_create_number_indicator()
        
    def reset_num_order(self):
        self.set_num_order(None)
        
    def is_external(self):
        """
        Returns whether the connection is considered external (only takes input from other class instances of the same class type and not itself)
        """
        return self.__is_external
        
    def set_external(self, is_external):
        """
        Sets whether the connection is considered external (only takes input from other class instances of the same class type and not itself)
        """
        self.__is_external = is_external
        self.__end_block.get_attached_configuration_attribute_gui().get_configuration_attribute().add_input_configuration_attribute(self.__start_block.get_configuration_attribute(), \
                                                                                                                                    not is_external)
        
        self.create_new_lines()
        self.__view.update_shown_order()
        
    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            
            self.__start_block.remove_connection(self)
            
            if self.__end_block != None:
                self.__end_block.remove_connection(self)
                attached_configuration_attribute_gui = self.__end_block.get_attached_configuration_attribute_gui()
                
                # Update the input value type of all setup attributes of the configuration class which this connection is removed from
                if attached_configuration_attribute_gui != None:
                    attached_configuration_attribute_gui.get_configuration_class_gui().update_value_input_types()
                    
            self.remove_corners()
            self.remove_lines()
            
    def save_state(self):
        saved_states = {"start_block": str(self.__start_block), \
                        "start_direction": self.__start_direction, \
                        "end_direction": self.__end_direction, \
                        "corner_coordinates": [], \
                        "is_external": self.__is_external}
        
        for corner in self.__corners:
            saved_states["corner_coordinates"].append((corner.get_x(), corner.get_y()))
            
        return saved_states
