import tkinter as tk
import tkinter.font as tkfont
import numpy as np
from circle_indicator_gui import GUICircleIndicator
from helper_functions_general import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid, get_actual_coordinates_after_scale, distance_to_closest_grid_intersection, get_font, get_text_that_fits, delete_all
from default_coordinate_functions import get_block_start_coordinates
from config import *

class GUIBlock:
    """
    Class managing blocks/buttons shown in views
    """
    def __init__(self, model, view, pressable_items, x, y, width, height, *, ignore_zoom=False, bind_left=None, bind_right=None):
        self.__model = model
        self.__view = view
        self.__pressable_items = pressable_items
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__ignore_zoom = ignore_zoom
        self.__shapes_highlight = []
        self.__attached_blocks = [] # Blocks that are attached to this one, also affected by moving, scaling, highlighting, etc
        
        self.__draggable = bind_left == MOUSE_DRAG
        self.__pick_up_actual_coordinate = (0, 0)
        
        canvas = view.get_canvas()
        
        # Bind mouse actions to the block
        for pressable_item in self.__pressable_items:
            if bind_left in (MOUSE_PRESS, MOUSE_DRAG):
                canvas.tag_bind(pressable_item, MOUSE_LEFT_PRESS, self.left_pressed)
                
            if bind_left == MOUSE_DRAG:
                canvas.tag_bind(pressable_item, MOUSE_LEFT_DRAG, self.left_dragged)
                canvas.tag_bind(pressable_item, MOUSE_LEFT_RELEASE, self.left_released)
                
            if bind_right == MOUSE_PRESS:
                canvas.tag_bind(pressable_item, MOUSE_RIGHT_PRESS, self.right_pressed)
                
        self.__was_dragged = False
        self.__is_deleted = False
        
        from connection_blocks_gui import GUIConnectionCorner
        
        # Do not update shown order of items if corner of a connection as they are recreated often when changing the path of connections
        if not isinstance(self, GUIConnectionCorner):
            view.update_shown_order()
            
    def left_pressed(self, event):
        """
        Pressing the left mouse button on the block
        """
        self.__view.select_item(self)
        
        # Pick up block
        if self.__draggable:
            self.__pick_up_actual_coordinate = (event.x, event.y)
            
    def left_dragged(self, event, *, max_positive_move_x=None, max_negative_move_x=None, max_positive_move_y=None, max_negative_move_y=None, single_direction=False):
        """
        Dragging the block with the left mouse button
        """
        if self.__draggable:
            self.__was_dragged = True
            move_x, move_y = convert_actual_coordinate_to_grid(event.x-self.__pick_up_actual_coordinate[0], event.y-self.__pick_up_actual_coordinate[1], self.get_length_unit())
            
            if max_positive_move_x != None and move_x > max_positive_move_x:
                move_x = max_positive_move_x
            elif max_negative_move_x != None and move_x < max_negative_move_x:
                move_x = max_negative_move_x
                
            if max_positive_move_y != None and move_y > max_positive_move_y:
                move_y = max_positive_move_y
            elif max_negative_move_y != None and move_y < max_negative_move_y:
                move_y = max_negative_move_y
                
            # If the block can only be dragged in one direction at a time, pick the one that is moved the most
            if single_direction:
                if abs(move_x) >= abs(move_y):
                    move_y = 0
                else:
                    move_x = 0
                    
            self.move_block(move_x, move_y)
            
            self.__pick_up_actual_coordinate = (event.x, event.y)
            
            return move_x, move_y
            
        return 0, 0
        
    def left_released(self, event, update_shown_order=True):
        """
        Releasing the left mouse button on the block
        """
        did_put_down_block = False
        
        # Put down block, where it needs to have been dragged to correct its position to avoid always drawing new connection lines that reset custom paths
        if self.__draggable and self.__was_dragged:
            self.snap_to_grid()
            did_put_down_block = True
            
            if update_shown_order:
                self.__view.update_shown_order()
                
        self.__was_dragged = False
        
        return did_put_down_block
        
    def right_pressed(self, event):
        pass
        
    def scale(self, new_length_unit, last_length_unit):
        """
        Scales the block, typical when zooming
        """
        for pressable_item in self.__pressable_items + self.__shapes_highlight:
            item_type = self.get_canvas().type(pressable_item)
            adjusted_actual_coordinates = get_actual_coordinates_after_scale(self.get_canvas().coords(pressable_item), new_length_unit, last_length_unit)
            
            # Scales different items on the canvas differently
            if item_type == "rectangle":
                x1, y1, x2, y2 = adjusted_actual_coordinates
                self.get_canvas().coords(pressable_item, x1, y1, x2, y2)
                
            elif item_type == "polygon":
                x1, y1, x2, y2, x3, y3 = adjusted_actual_coordinates
                self.get_canvas().coords(pressable_item, x1, y1, x2, y2, x3, y3)
                
            elif item_type == "text":
                x, y = adjusted_actual_coordinates
                has_line_break = "\n" in self.get_canvas().itemcget(pressable_item, "text")
                
                self.get_canvas().coords(pressable_item, x, y)
                self.get_canvas().itemconfig(pressable_item, font=get_font(new_length_unit, \
                                                                           canvas_and_label=(self.get_canvas(), pressable_item), \
                                                                           has_line_break=has_line_break))
                
        for attached_block in self.__attached_blocks:
            attached_block.scale(new_length_unit, last_length_unit)
            
    def highlight(self, color, *, highlight_border_width=HIGHLIGHT_BORDER_WIDTH, update_shown_order=True, highlight_tags=()):
        """
        Create a highlight around the block
        """
        GUIBlock.unhighlight(self)
        
        # Creates a slightly larger version of each shape and place it behind
        for pressable_item in self.__pressable_items:
            item_type = self.get_canvas().type(pressable_item)
            actual_coordinates = self.get_canvas().coords(pressable_item)
            
            if item_type == "rectangle":
                x1, y1, x2, y2 = actual_coordinates
                rect = self.get_canvas().create_rectangle(x1-highlight_border_width, \
                                                          y1-highlight_border_width, \
                                                          x2+highlight_border_width, \
                                                          y2+highlight_border_width, \
                                                          width=0, \
                                                          fill=color, \
                                                          tags=highlight_tags)
                
                self.__shapes_highlight.append(rect)
                
            elif item_type == "polygon":
                actual_coordinate_pairs = list(zip(actual_coordinates[0::2], actual_coordinates[1::2]))
                actual_center_x = sum(x for x, y in actual_coordinate_pairs) / 3
                actual_center_y = sum(y for x, y in actual_coordinate_pairs) / 3
                
                new_actual_coordinate_pairs = []
                
                for x, y in actual_coordinate_pairs:
                    vector_from_center = (x - actual_center_x, y - actual_center_y)
                    magnitude = (vector_from_center[0] ** 2 + vector_from_center[1] ** 2) ** 0.5
                    
                    for vector_value, old_actual_value in zip(vector_from_center, (x, y)):
                        new_actual_coordinate_pairs.append(old_actual_value + (vector_value / magnitude) * highlight_border_width * 2)
                        
                x1, y1, x2, y2, x3, y3 = new_actual_coordinate_pairs
                triangle = self.get_canvas().create_polygon(x1, y1, x2, y2, x3, y3, width=0, fill=color)
                
                self.__shapes_highlight.append(triangle)
                
        if highlight_tags == ():
            for shape in self.__shapes_highlight:
                self.get_canvas().tag_lower(shape)
                
        for attached_block in self.__attached_blocks:
            attached_block.highlight(color, highlight_border_width=highlight_border_width, update_shown_order=False, highlight_tags=highlight_tags)
            
        if highlight_tags != () and update_shown_order:
            self.__view.update_shown_order()
            
    def unhighlight(self):
        """
        Removes shapes that are used as highlight around the block
        """
        for shape_highlight in self.__shapes_highlight:
            self.get_canvas().delete(shape_highlight)
            
        self.__shapes_highlight.clear()
        
        for attached_block in self.__attached_blocks:
            attached_block.unhighlight()
        
    def update_highlight(self, color):
        """
        Refreshes the highlighy by removing and then recreating it
        """
        if len(self.__shapes_highlight) > 0:
            self.unhighlight()
            self.highlight(color)
            
    def snap_to_grid(self):
        """
        Snaps the block to align with the grid
        """
        move_x, move_y = distance_to_closest_grid_intersection(self.__view, self.__x, self.__y)
        
        self.move_block(move_x, move_y)
         
    def move_block(self, move_x, move_y):
        """
        Moves the block on the canvas based on coordinates of the grid
        """
        if self.__ignore_zoom:
            length_unit = LENGTH_UNIT
        else:
            length_unit = self.__view.get_length_unit()
            
        if move_x != 0 or move_y != 0:
            move_actual_x, move_actual_y = convert_grid_coordinate_to_actual(move_x, move_y, length_unit)
            
            # Move block
            for pressable_item in self.__pressable_items:
                self.get_canvas().move(pressable_item, move_actual_x, move_actual_y)
                
            # Move highlight of the block
            for shape_highlight in self.__shapes_highlight:
                self.get_canvas().move(shape_highlight, move_actual_x, move_actual_y)
                
            self.__x = round(self.__x + move_x, DECIMALS_WHEN_ROUNDING)
            self.__y = round(self.__y + move_y, DECIMALS_WHEN_ROUNDING)
            
        for block in self.__attached_blocks:
            if block != self:
                block.move_block(move_x, move_y)
                
    def get_connection_grid_start(self, direction):
        """
        Returns the grid coordinate that a connection line should start from
        """
        # Center of block as default
        x = self.__x + int(0.5 * self.__width)
        y = self.__y + int(0.5 * self.__height)
        
        # Correct one of the values to get the correct coordinate considering the direction which the line goes out from the block
        if direction == "UP":
            y = self.__y - 1
        elif direction == "DOWN":
            y = self.__y + int(self.__height + 0.98) # Round up to make sure blocks less than one length unit selects the correct coordinate
        elif direction == "LEFT":
            x = self.__x - 1
        elif direction == "RIGHT":
            x = self.__x + int(self.__width + 0.98)
            
        return x, y
        
    def get_connection_actual_start(self, direction):
        """
        Returns the pixel coordinate that a connection line should start from
        """
        # Center of block as default
        x = self.__x + 0.5 * self.__width
        y = self.__y + 0.5 * self.__height
        
        # Correct one of the values to get the correct coordinate considering the direction which the line goes out from the block
        if direction == "UP":
            y = self.__y
        elif direction == "DOWN":
            y = self.__y + self.__height # Round up to make sure blocks less than one length unit selects the correct coordinate
        elif direction == "LEFT":
            x = self.__x
        elif direction == "RIGHT":
            x = self.__x + self.__width
            
        actual_x, actual_y = convert_grid_coordinate_to_actual(x, y, self.__view.get_length_unit())
        
        return actual_x, actual_y
        
    def get_model(self):
        return self.__model
        
    def get_view(self):
        return self.__view
        
    def get_canvas(self):
        return self.__view.get_canvas()
        
    def get_x(self):
        return self.__x
        
    def get_y(self):
        return self.__y
        
    def get_width(self):
        return self.__width
        
    def get_height(self):
        return self.__height
        
    def ignores_zoom(self):
        return self.__ignore_zoom
        
    def get_length_unit(self):
        if self.__ignore_zoom:
            return LENGTH_UNIT
        else:
            return self.__view.get_length_unit()
            
    def add_attached_block(self, block):
        self.__attached_blocks.append(block)
        
    def remove_attached_block(self, block):
        self.__attached_blocks.remove(block)
        
    def has_attached_block(self, block):
        return block in self.__attached_blocks
        
    def get_text_width(self):
        return self.__text_width
        
    def get_direction(self, mouse_x, mouse_y):
        """
        Returns the direction out from a block based on the closes edge from the mouse
        """
        direction = "RIGHT"
        actual_mid_x = convert_grid_coordinate_to_actual(self.get_x()+self.get_width()//2, 0, self.__view.get_length_unit())[0]
        
        if mouse_x < actual_mid_x:
            direction = "LEFT"
            
        return direction
        
    def is_deleted(self):
        return self.__is_deleted
        
    def delete(self):
        self.__is_deleted = True
        self.get_view().unselect_item(self)
        
        delete_all(self.__attached_blocks)
        
        for pressable_items in self.__pressable_items:
            self.get_canvas().delete(pressable_items)
            
        GUIBlock.unhighlight(self)
        
    def save_state(self):
        return {"x": self.__x, "y": self.__y}
        
class GUIModelingBlock(GUIBlock):
    """
    Class for block with text
    """
    def __init__(self, model, view, text, width, height, fill_color, *, position=None, \
                                                                        text_width=None, \
                                                                        label_text_x=None, \
                                                                        ignore_zoom=False, \
                                                                        additional_pressable_items=None, \
                                                                        bind_left=None, \
                                                                        bind_right=None, \
                                                                        tags_rect=(), \
                                                                        tags_text=()):
        
        if position == None:
            x, y = get_block_start_coordinates(view.get_length_unit())[0]
        else:
            x, y = position
            
        if ignore_zoom:
            length_unit = LENGTH_UNIT
        else:
            length_unit = view.get_length_unit()
            
        canvas = view.get_canvas()
        actual_rect_x1, actual_rect_y1 = convert_grid_coordinate_to_actual(x, y, length_unit)
        actual_rect_x2, actual_rect_y2 = convert_grid_coordinate_to_actual(x+width, y+height, length_unit)
        
        self.__rect = canvas.create_rectangle(actual_rect_x1, actual_rect_y1, actual_rect_x2, actual_rect_y2, width=OUTLINE_WIDTH, outline=OUTLINE_COLOR, fill=fill_color, tags=tags_rect)
        
        if label_text_x == None:
            label_text_x = x + width / 2
            
        actual_label_text_x, actual_label_text_y = convert_grid_coordinate_to_actual(label_text_x, y+height/2, length_unit)
        self.__label_text = canvas.create_text(actual_label_text_x, actual_label_text_y, text="", font=FONT, anchor="center", justify="center", tags=tags_text)
        
        pressable_items = [self.__rect, self.__label_text]
        
        if additional_pressable_items != None:
            for additional_pressable_item in additional_pressable_items:
                canvas.tag_raise(additional_pressable_item)
                
            pressable_items += additional_pressable_items
            
        super().__init__(model, view, pressable_items, x, y, width, height, ignore_zoom=ignore_zoom, bind_left=bind_left, bind_right=bind_right)
        self.__text = text
        
        if text_width != None:
            self.__text_width = text_width
        else:
            self.__text_width = width
            
        self.set_text(text) # Ensure line break
        
    def is_adjacent(self, coordinates):
        """
        Returns whether any of the specified grid coordinates are considered adjacent to this block, and in such cases which direction goes out from the block
        """
        for coordinate in coordinates:
            coordinate_to_check = np.array(coordinate)
            
            for i in range(self.get_height()):
                coordinate_left = np.array((self.get_x() - 1, self.get_y() + i))
                coordinate_right = np.array((self.get_x() + self.get_width(), self.get_y() + i))
                
                if np.linalg.norm(coordinate_to_check - coordinate_left) < 0.5:
                    return True, "LEFT"
                    
                elif np.linalg.norm(coordinate_to_check - coordinate_right) < 0.5:
                    return True, "RIGHT"
                    
        return False, ""
        
    def get_text(self):
        """
        Returns the text on the block
        """
        return self.__text
        
    def set_text(self, text, is_bold=False):
        """
        Sets the text on the block
        """
        text, font = get_text_that_fits(self.get_canvas(), self.__label_text, text, self.__text_width, is_bold, self.get_length_unit())
        
        self.__text = text
        self.get_canvas().itemconfig(self.__label_text, text=text, font=font, fill=TEXT_COLOR)
        
    def get_text_width(self):
        return self.__text_width
        
    def set_fill_color(self, fill_color):
        self.get_canvas().itemconfig(self.__rect, fill=fill_color)
        self.get_canvas().update_idletasks() # Ensure that the color is changed immediately and not after other
        
class GUIClass(GUIModelingBlock):
    """
    Manages a configuration or setup class
    """
    def __init__(self, model, view, text, width, height, is_configuration_class, *, position=None, linked_group_number=None):
        super().__init__(model, view, text, width, height, CLASS_COLOR, position=position, bind_left=MOUSE_DRAG)
        self.__is_configuration_class = is_configuration_class
        self.__linked_group_number = linked_group_number # If the class belongs to a group of linked copies
        self.__linked_group_indicator = None
        
        if self.__linked_group_number != None:
            self.update_linked_group_indicator()
            
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.move(move_x, move_y)
            
    def scale(self, new_length_unit, last_length_unit):
        super().scale(new_length_unit, last_length_unit)
        
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.scale(new_length_unit, last_length_unit)
            
    def is_linked(self):
        return self.__linked_group_number != None
        
    def get_linked_group_number(self):
        return self.__linked_group_number
        
    def set_linked_group_number(self, linked_group_number):
        self.__linked_group_number = linked_group_number
        self.update_linked_group_indicator()
                
    def update_linked_group_indicator(self):
        # Remove any existing indicator
        if self.__linked_group_indicator != None:
            self.__linked_group_indicator.remove()
                
        # Add or update indicator
        if self.__linked_group_number != None:
            # Create new indicator
            if self.__linked_group_indicator == None:
                self.__linked_group_indicator = GUICircleIndicator(self.get_view(), \
                                                                   self.get_x()+self.get_width(), \
                                                                   self.get_y(), \
                                                                   LINKED_GROUP_CIRCLE_RADIUS, \
                                                                   LINKED_GROUP_CIRCLE_COLOR, \
                                                                   LINKED_GROUP_CIRCLE_OUTLINE, \
                                                                   self.__linked_group_number)
            # Update existing one
            else:
                self.__linked_group_indicator.create(self.__linked_group_number)
        else:
            self.__linked_group_indicator = None
            
    def delete(self):
        super().delete()
        
        # Remove linked group indicator if it exists
        if self.__linked_group_number != None:
            self.__linked_group_indicator.remove()
            self.get_model().remove_class_gui_from_linked_group(self, self.__is_configuration_class)
                    
    def save_state(self):
        return super().save_state() | {"linked_group_number": self.__linked_group_number}

