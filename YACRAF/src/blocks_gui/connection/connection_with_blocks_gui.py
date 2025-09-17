from options import Options
from connection_gui import GUIConnection
from connection_blocks_gui import GUIConnectionTriangle, GUIConnectionScalarsIndicator
from helper_functions_general import convert_value_to_string, distance_to_closest_grid_intersection
from config import *

class GUIConnectionWithBlocks(GUIConnection):
    """
    Manages directional connection with already attached triangle blocks found in setup views
    """
    def __init__(self, model, view, *, start_coordinate=None, end_coordinate=None, input_scalars=None, input_scalars_indicator_coordinate=None):
        self.__model = model
        self.__view = view
        self.__input_scalars = (1,)
        self.__input_scalars_indicator = None
        
        start_block = GUIConnectionTriangle(model, view, "RIGHT", False) # Points out from class
        end_block = GUIConnectionTriangle(model, view, "RIGHT", True) # Points into class
        
        super().__init__(model, view, start_block, "RIGHT", end_block=end_block, end_direction="LEFT")
        
        self.__is_deleted = False
        
        # Move start block to specified coordinate
        if start_coordinate != None:
            start_block.move_block(start_coordinate[0] - start_block.get_x(), \
                                   start_coordinate[1] - start_block.get_y())
            start_block.put_down_block()
            
        # Move end block to specified coordinate
        if end_coordinate != None:
            end_block.move_block(end_coordinate[0] - end_block.get_x(), \
                                 end_coordinate[1] - end_block.get_y())
            end_block.put_down_block()
            
        if input_scalars != None:
            self.set_input_scalars(input_scalars)
            
        if self.__input_scalars_indicator != None and input_scalars_indicator_coordinate != None:
            self.__input_scalars_indicator.move_block(input_scalars_indicator_coordinate[0] - self.__input_scalars_indicator.get_x(), \
                                                      input_scalars_indicator_coordinate[1] - self.__input_scalars_indicator.get_y())
            
        
    def scale(self, new_length_unit, last_length_unit):
        super().scale(new_length_unit, last_length_unit)
        
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.scale(new_length_unit, last_length_unit)
            
    def create_new_lines(self, mouse_location=None):
        super().create_new_lines()
        
        self.update_input_scalars_indicator()
        
    def move_lines(self, move_x, move_y):
        only_moved = super().move_lines(move_x, move_y)
        
        if only_moved and self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.move_block(move_x, move_y)
    
    def open_options(self):
        return Options.connection_with_blocks(self.__model, self.__view, self)
        
    def get_start_setup_class_gui(self):
        """
        Returns the GUI setup class that one of the triangle block points out from
        """
        return self.get_start_block().get_attached_setup_class_gui()
    
    def get_end_setup_class_gui(self):
        """
        Returns the GUI setup class that one of the triangle block points into
        """
        return self.get_end_block().get_attached_setup_class_gui()
    
    def get_start_setup_class(self):
        """
        Returns the setup class without a GUI that one of the triangle blocks points out from
        """
        start_attached_setup_class_gui = self.get_start_block().get_attached_setup_class_gui()
        
        if start_attached_setup_class_gui == None:
            return None
        
        return start_attached_setup_class_gui.get_setup_class()
        
    def get_end_setup_class(self):
        """
        Returns the setup class without a GUI that one of the triangle blocks points into
        """
        end_attached_setup_class_gui = self.get_end_block().get_attached_setup_class_gui()
        
        if end_attached_setup_class_gui == None:
            return None
            
        return end_attached_setup_class_gui.get_setup_class()
        
    def get_movable_items(self):
        """
        Returns all items that are directly moved around the view, such as during panning
        """
        movable_items = []
        
        for potential_block in [self.get_start_block(), self.get_end_block()]:
            if not potential_block.is_attached():
                movable_items.append(potential_block)
                
        return movable_items
        
    def adjust_lines_to_dragged_corners(self):
        super().adjust_lines_to_dragged_corners()
        
        self.update_input_scalars_indicator()
        
    def get_input_scalars(self):
        return self.__input_scalars
        
    def set_input_scalars(self, input_scalars):
        should_reset = True
        
        for input_scalar in input_scalars:
            if input_scalar != 1:
                should_reset = False
                break
                
        if should_reset:
            input_scalars = (1,)
            
        self.__input_scalars = input_scalars
        
        start_setup_class_gui = self.get_start_setup_class_gui()
        end_setup_class_gui = self.get_end_setup_class_gui()
        
        if start_setup_class_gui != None and end_setup_class_gui != None:
            end_setup_class_gui.get_setup_class().set_input_setup_class(start_setup_class_gui.get_setup_class(), input_scalars) # Update input scalars
            
        self.update_input_scalars_indicator()
        
    def reset_input_scalars(self):
        self.set_input_scalars([1])
        
    def get_input_scalars_string(self):
        """
        Returns the input scalars as a formatted string
        """
        return convert_value_to_string(self.__input_scalars)
        
    def update_input_scalars_indicator(self):
        """
        Updates the input scalars indicator (removing it, adding it, or updating its text)
        """
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.delete()
            
        # Show indicator unless default value
        if self.__input_scalars != (1,):
            self.__input_scalars_indicator = GUIConnectionScalarsIndicator(self.__model, self.__view, self)
            self.correct_scalars_indicator_location()
            
    def correct_scalars_indicator_location(self):
        """
        Adjusts the position of the input scalars indicator to align with the grid, if the indicator exists
        """
        if self.__input_scalars_indicator != None:
            self.__input_scalars_indicator.snap_to_grid()
            
    def get_input_scalars_coordinate(self):
        if self.__input_scalars_indicator == None:
            return None
            
        return (self.__input_scalars_indicator.get_x(), self.__input_scalars_indicator.get_y())
        
    def get_scalars_indicator_start_coordinate(self):
        """
        Returns the default start coordinate of the input scalars indicator
        """
        corners = self.get_corners()
        end_x, end_y = self.get_end_block().get_connection_grid_start(self.get_end_direction())
        
        if len(corners) > 0:
            start_x, start_y = corners[-1].get_x(), corners[-1].get_y()
            
        else:
            start_x, start_y = self.get_start_block().get_connection_grid_start(self.get_start_direction())
            
        indicator_x = abs(start_x + end_x) / 2
        indicator_y = abs(start_y + end_y) / 2
        
        indicator_x -= INPUT_SCALARS_INDICATOR_WIDTH // 2
        indicator_y -= INPUT_SCALARS_INDICATOR_HEIGHT // 2
        
        return indicator_x, indicator_y
        
    def allowed_scalars_indicator_movement_directions(self):
        """
        Returns a list of directions that the input scalars indicator can move (can only move along the lines of the connection)
        """
        allowed_directions = []
        
        # Coordinate in the middle of the indicator
        indicator_pos = (self.__input_scalars_indicator.get_x()+self.__input_scalars_indicator.get_width()//2, \
                         self.__input_scalars_indicator.get_y()+self.__input_scalars_indicator.get_height()//2)
        
        start_x, start_y = self.get_start_block().get_connection_grid_start(self.get_start_direction())
        end_x, end_y = self.get_end_block().get_connection_grid_start(self.get_end_direction())
        corners = self.get_corners()
        
        # Coordinates of all corners and end points
        coordinates = [(start_x, start_y)] + [(corner.get_x(), corner.get_y()) for corner in corners] + [(end_x, end_y)]
        
        # Find between which two coordinates of corners or end points that the indicator is
        for i in range(1, len(coordinates)):
            first_pos, second_pos = coordinates[i-1], coordinates[i]
            
            for j in range(2):
                if max(abs(indicator_pos[j] - first_pos[j]), \
                       abs(first_pos[j] - second_pos[j]), \
                       abs(second_pos[j] - indicator_pos[j])) < 0.01:
                    # Vertically aligned
                    if j == 0:
                        if indicator_pos[1] > min(first_pos[1], second_pos[1]):
                            allowed_directions.append("UP")
                            
                        if indicator_pos[1] < max(first_pos[1], second_pos[1]):
                            allowed_directions.append("DOWN")
                            
                    # Horizontally aligned
                    if j == 1:
                        if indicator_pos[0] > min(first_pos[0], second_pos[0]):
                            allowed_directions.append("LEFT")
                            
                        if indicator_pos[0] < max(first_pos[0], second_pos[0]):
                            allowed_directions.append("RIGHT")
                            
        return allowed_directions
        
    def is_deleted(self):
        return self.__is_deleted()
        
    def delete(self):
        if not self.__is_deleted:
            self.__is_deleted = True
            
            if self.__input_scalars_indicator != None:
                self.__input_scalars_indicator.delete()
                
            self.remove_corners()
            self.remove_lines()
            self.__view.remove_connection_with_blocks(self)
            
            self.get_start_block().delete()
            self.get_end_block().delete()
            
    def save_state(self):
        saved_states = {"start_block": self.get_start_block().save_state(), "end_block": self.get_end_block().save_state(), "input_scalars": self.__input_scalars}
        
        if self.__input_scalars_indicator == None:
            saved_states["input_scalars_indicator_coordinate"] = None
        else:
            saved_states["input_scalars_indicator_coordinate"] = self.get_input_scalars_coordinate()
            
        return saved_states
