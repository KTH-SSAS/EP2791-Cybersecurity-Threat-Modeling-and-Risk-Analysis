import tkinter as tk
from general_gui import GUIModelingBlock
from buttons_gui import TouchButton
from connection_with_blocks_gui import GUIConnectionWithBlocks
from options import Options
from helper_functions_general import convert_actual_coordinate_to_grid
from default_coordinate_functions import get_change_configuration_view_start_coordinate, get_change_setup_view_start_coordinate
from config import *

class View(tk.Frame):
    """
    Class managing all objects in a view and the canvas that the corresponding items are drawn on
    """
    def __init__(self, model, name):
        super().__init__()
        self.__model = model
        self.__name = name
        self.__view_headers = [] # Title headers above the configuration and setup view buttons
        self.__configuration_change_view_buttons = {} # View and corresponding button
        self.__setup_change_view_buttons = {} # View and corersponding button
        self.__selected_items = set() # Items that are highlighted by pressing on them
        
        self.__is_panning = False
        self.__is_zooming = False
        self.__panning_last_mouse_coordinate = (0, 0)
        self.__length_unit_difference = 0 # How much the length unit has been changed from LENGTH_UNIT
        self.__grid_offset = (0, 0) # How much items are offset from the grid in the range [0, 1) due to panning/zooming
        
        self.__canvas = tk.Canvas(self, width=settings.get_canvas_width(), height=settings.get_canvas_height(), bg=VIEW_BACKGROUND_COLOR)
        self.__canvas_size = (settings.get_canvas_width(), settings.get_canvas_height())
        self.__add_change_configuration_view_button = TouchButton.add_view(model, self, True)
        self.__add_change_setup_view_button = TouchButton.add_view(model, self, False)
        self.__save_button = TouchButton.save(model, self)
        self.__settings_button = TouchButton.settings(model, self)
        
        self.__currently_open_options = None
        
        # Add the headers above the buttons that change between views
        for text, position in [("Metamodel:", get_change_configuration_view_start_coordinate(LENGTH_UNIT)), ("System:", get_change_setup_view_start_coordinate(LENGTH_UNIT))]:
            x, y = position
            y -= CHANGE_VIEW_HEIGHT
            self.__view_headers.append(GUIModelingBlock(model, self, text, CHANGE_VIEW_WIDTH, CHANGE_VIEW_HEIGHT, CHANGE_VIEW_HEADER_COLOR, position=(x, y), ignore_zoom=True, tags_rect=(TAG_BUTTON,), tags_text=(TAG_BUTTON_TEXT,)))
            
        self.__canvas.bind(MOUSE_LEFT_PRESS, self.pan_start)
        self.__canvas.bind(MOUSE_LEFT_DRAG, self.pan_move)
        self.__canvas.bind(MOUSE_LEFT_RELEASE, self.pan_stop)
        
        # Binds two variations to account for Linux, macOS, and Windows
        self.__canvas.bind(MOUSE_WHEEL_UP, self.zoom_in)
        self.__canvas.bind(MOUSE_WHEEL_DOWN, self.zoom_out)
        self.__canvas.bind(MOUSE_WHEEL, lambda event: self.zoom_in(event) if event.delta > 0 else self.zoom_out(event))
        
        # Changing the window size
        self.__canvas.bind("<Configure>", self.on_resize)
        
        self.__canvas.pack(expand=True, fill="both")
        
    def pan_start(self, event):
        """
        When starting to pan by pressing the canvas background
        """
        closest_item = self.__canvas.find_closest(event.x, event.y)
        actual_coords_closest_item = self.__canvas.bbox(closest_item)
        
        # Item on the canvas was pressed
        if actual_coords_closest_item != None:
            x1, y1, x2, y2 = actual_coords_closest_item
            self.__is_panning = not (x1 <= event.x <= x2 and y1 <= event.y <= y2)
            
        # Pressed on background
        else:
            self.__is_panning = True
            
        self.focus()
        
        if self.__is_panning:
            self.unselect_all_items()
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_move(self, event):
        """
        When dragging on the canvas background to pan the view
        """
        if self.__is_panning:
            # How much to move each item
            move_x, move_y = convert_actual_coordinate_to_grid(event.x-self.__panning_last_mouse_coordinate[0], event.y-self.__panning_last_mouse_coordinate[1], self.get_length_unit())
            
            self.update_grid_offset(move_x, move_y)
            
            for movable_item in self.get_movable_items():
                movable_item.move_block(move_x, move_y)
                
            self.__panning_last_mouse_coordinate = (event.x, event.y)
            
    def pan_stop(self, event):
        """
        When stopping to pan by releasing the mouse button
        """
        self.__is_panning = False
        
    def zoom_in(self, event):
        if self.get_length_unit() < LENGTH_UNIT_ZOOM_LIMITS[1]:
            self.zoom(event, 1)
        
    def zoom_out(self, event):
        if self.get_length_unit() > LENGTH_UNIT_ZOOM_LIMITS[0]:
            self.zoom(event, -1)
        
    def zoom(self, event, length_unit_difference):
        """
        Zooming in or out the view
        
        length_unit_difference: The difference in length unit per grid square due to zooming
        """
        self.__is_zooming = True
        
        last_length_unit = self.get_length_unit()
        self.__length_unit_difference += length_unit_difference
        
        scale_origin_x, scale_origin_y = convert_actual_coordinate_to_grid(event.x, event.y, self.get_length_unit()) # Zoom around where the mouse is
        length_unit_change = last_length_unit / self.get_length_unit() - 1
        
        move_x = scale_origin_x * length_unit_change
        move_y = scale_origin_y * length_unit_change
        
        self.update_grid_offset(move_x, move_y)
        
        for movable_item in self.get_movable_items():
            movable_item.scale(self.get_length_unit(), last_length_unit) # Scales the size of the grid and all its components
            movable_item.move_block(move_x, move_y) # Moves all components on the grid to simulate zooming in at the coordinates of the mouse
            
        self.__is_zooming = False
        
    def on_resize(self, event):
        """
        Changing the window size
        """
        self.__canvas.config(width=event.width, height=event.height)
        
        actual_move_x = event.width - self.__canvas_size[0]
        actual_move_y = event.height - self.__canvas_size[1]
        move_x, move_y = convert_actual_coordinate_to_grid(actual_move_x, actual_move_y, LENGTH_UNIT)
        
        self.__canvas_size = (event.width, event.height)
        
        # Buttons and their accompanying headers to move so that they do not end up outside the window
        for item_to_move_x in self.__view_headers + \
                              list(self.__configuration_change_view_buttons.values()) + \
                              list(self.__setup_change_view_buttons.values()) + \
                              [self.__add_change_configuration_view_button, self.__add_change_setup_view_button]:
            item_to_move_x.move_block(move_x, 0)
            
        self.__save_button.move_block(0, move_y)
        self.__settings_button.move_block(0, move_y)
        
        if self.__currently_open_options != None:
            self.__currently_open_options.move(move_x/2, 0)
        
        settings.set_canvas_size(event.width, event.height)
        
        return move_x, move_y
        
    def update_shown_order(self):
        """
        Refreshes the order that items should be shown in to make sure some are shown on top of others
        """
        for tag in (TAG_INPUT, TAG_INPUT_TEXT, TAG_CONNECTION_LINE, TAG_CONNECTION_CORNER, TAG_INDICATOR, TAG_INDICATOR_TEXT, TAG_BUTTON, TAG_BUTTON_TEXT, TAG_OPTIONS_HIGHLIGHT, TAG_OPTIONS_BACKGROUND, TAG_OPTIONS, TAG_OPTIONS_TEXT):
            self.__canvas.tag_raise(tag)
            
    def open_options(self):
        return Options.view(self.get_model(), self)
        
    def get_model(self):
        return self.__model
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        self.__model.set_text_change_view_buttons(self, name) # Need to update the text of the change view buttons in all views
        
    def get_canvas(self):
        return self.__canvas
        
    def set_background_color(self, color):
        self.__canvas.config(bg=color)
        
    def add_change_view_button(self, view_to_change_to, is_configuration_view):
        """
        Adds a button to change to a specified view
        """
        # Move down the button that adds another view
        if is_configuration_view:
            self.__configuration_change_view_buttons[view_to_change_to] = TouchButton.change_view(self.__model, self, view_to_change_to.get_name(), view_to_change_to, True, len(self.__configuration_change_view_buttons))
            self.__add_change_configuration_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
        else:
            self.__setup_change_view_buttons[view_to_change_to] = TouchButton.change_view(self.__model, self, view_to_change_to.get_name(), view_to_change_to, False, len(self.__setup_change_view_buttons))
            self.__add_change_setup_view_button.move_block(0, CHANGE_VIEW_HEIGHT)
            
    def remove_change_view_button(self, view_to_remove):
        """
        Removes a button that changes to a specified view
        """
        from configuration_view import ConfigurationView
        from setup_view import SetupView
        
        # Move up the button that adds another view
        if isinstance(view_to_remove, ConfigurationView):
            change_view_buttons = self.__configuration_change_view_buttons
            self.__add_change_configuration_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        elif isinstance(view_to_remove, SetupView):
            change_view_buttons = self.__setup_change_view_buttons
            self.__add_change_setup_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
            
        button_to_remove = change_view_buttons[view_to_remove]
        
        # Move up all buttons that change view that are after the removed button
        for change_view_button in change_view_buttons.values():
            if change_view_button.get_y() > button_to_remove.get_y():
                change_view_button.move_block(0, -CHANGE_VIEW_HEIGHT)
                
        # Remove the button to change view
        button_to_remove.delete()
        change_view_buttons.pop(view_to_remove)
        
    def move_change_view_button(self, view_to_move, up):
        """
        Moves a change view button up or down a step
        """
        to_move = CHANGE_VIEW_HEIGHT
        
        if up:
            to_move *= -1
            
        from configuration_view import ConfigurationView
        from setup_view import SetupView
        
        if isinstance(view_to_move, ConfigurationView):
            self.__configuration_change_view_buttons[view_to_move].move_block(0, to_move)
            
        elif isinstance(view_to_move, SetupView):
            self.__setup_change_view_buttons[view_to_move].move_block(0, to_move)
            
    def set_color_change_view_button(self, view, color):
        from configuration_view import ConfigurationView
        from setup_view import SetupView
        
        if isinstance(view, ConfigurationView):
            self.__configuration_change_view_buttons[view].set_fill_color(color)
            
        elif isinstance(view, SetupView):
            self.__setup_change_view_buttons[view].set_fill_color(color)
            
    def set_text_change_view_button(self, view_with_changed_name, text):
        """
        Change the text of a specific change view button within this view
        """
        if view_with_changed_name in self.__configuration_change_view_buttons:
            self.__configuration_change_view_buttons[view_with_changed_name].set_text(text)
            
        elif view_with_changed_name in self.__setup_change_view_buttons:
            self.__setup_change_view_buttons[view_with_changed_name].set_text(text)
            
    def get_selected_items(self):
        return self.__selected_items
        
    def is_selected_item(self, selected_item):
        return selected_item in self.__selected_items
        
    def select_item(self, selected_item):
        # Unselect other items if not selecting multiple ones
        if not (self.get_model().is_currently_pressing_key("Shift_L") or self.get_model().is_currently_pressing_key("Shift_R")):
            self.unselect_all_items()
            
        # Highlight selected item
        if selected_item not in self.__selected_items:
            selected_item.highlight(HIGHLIGHT_SELECTED_COLOR)
            self.__selected_items.add(selected_item)
            
    def unselect_item(self, unselected_item):
        if unselected_item in self.__selected_items:
            unselected_item.unhighlight()
            self.__selected_items.remove(unselected_item)
            
    def unselect_all_items(self):
        for selected_item in self.__selected_items:
            selected_item.unhighlight()
            
        self.__selected_items.clear()
        
    def is_zooming(self):
        return self.__is_zooming
        
    def is_panning(self):
        return self.__is_panning
        
    def get_length_unit(self):
        """
        Returns the current length unit, including any difference due to zooming
        """
        return LENGTH_UNIT + self.__length_unit_difference
        
    def update_grid_offset(self, move_x, move_y):
        """
        Update the current offset of the grid due to panning/zooming
        """
        # Set the offset of each value to be within [0, 1)
        grid_offset_x = (self.__grid_offset[0] + move_x) % 1
        grid_offset_y = (self.__grid_offset[1] + move_y) % 1
        
        self.__grid_offset = (grid_offset_x, grid_offset_y)
        
    def get_grid_offset(self):
        return self.__grid_offset
        
    def set_grid_offset(self, offset_x, offset_y):
        self.__grid_offset = (offset_x, offset_y)
        
    def set_currently_open_options(self, currently_open_options):
        # Already open
        if self.__currently_open_options == currently_open_options:
            return
            
        # Close existing
        if self.__currently_open_options != None:
            self.__currently_open_options.delete()
            
        self.__currently_open_options = currently_open_options
        
    def reset_currently_open_options(self):
        self.__currently_open_options = None
        
    def delete(self):
        self.destroy()
