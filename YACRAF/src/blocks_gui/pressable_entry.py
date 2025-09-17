import tkinter as tk
from general_gui import GUIModelingBlock
from helper_functions_general import convert_grid_coordinate_to_actual, get_actual_coordinates_after_scale, get_font
from config import *

class PressableEntry(GUIModelingBlock):
    """
    Custom entry field that creates an Entry when pressed and removes it when unfocused
    """
    def __init__(self, model, view, x, y, width, height, command, *, text="", entry_text=None, ignore_zoom=False, tags_rect=(), tags_text=()):
        super().__init__(model, view, text, width, height, ENTRY_COLOR, position=(x, y), ignore_zoom=ignore_zoom, bind_left=MOUSE_PRESS, tags_rect=tags_rect, tags_text=tags_text)
        self.__command = command
        
        if entry_text == None:
            self.__entry_text = tk.StringVar()
        else:
            self.__entry_text = entry_text
            
        self.__entry_text.set(text)
        
        self.__entry = None # Entry field that appears when pressed
        self.__entry_window = None # Window that the Entry field is placed within so that it can be drawn on the canvas of the specified view
        
        self.__entry_text.trace("w", lambda *args: self.write()) # Updated whenever writing in the Entry
        
    def left_pressed(self, event):
        self.get_view().focus()
        
        # Create an Entry if it does not exist
        if self.__entry_window == None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = convert_grid_coordinate_to_actual(self.get_x(), self.get_y(), self.get_length_unit())
            
            # Create Entry and Window to put the Entry in to allow it be put inside the Canvas
            self.__entry = tk.Entry(self.get_view(), textvariable=self.__entry_text, font=get_font(self.get_length_unit()))
            self.__entry_window = self.get_canvas().create_window((actual_x+OUTLINE_WIDTH, \
                                                                   actual_y+OUTLINE_WIDTH), \
                                                                   window=self.__entry, \
                                                                   anchor="nw", \
                                                                   width=actual_width, \
                                                                   height=actual_height)
                                                                   
            self.set_text("") # To ensure that the text on the block does not show underneath the Entry
            
            # When starting to edit the entered value, unselect all blocks
            self.get_view().unselect_all_items()
                        
            self.__entry.bind("<FocusOut>", lambda *args: self.remove_entry()) # Remove the Entry when unfocused
            self.__entry.focus()
            self.__entry.icursor(tk.END)
            
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        if self.__entry_window != None:
            actual_move_x, actual_move_y = convert_grid_coordinate_to_actual(move_x, move_y, self.get_length_unit())
            new_actual_x, new_actual_y = self.get_view().get_canvas().coords(self.__entry_window)
            new_actual_x += actual_move_x
            new_actual_y += actual_move_y
            
            self.get_canvas().coords(self.__entry_window, new_actual_x, new_actual_y)
            
    def scale(self, new_length_unit, last_length_unit):
        super().scale(new_length_unit, last_length_unit)
        
        if self.__entry_window != None:
            actual_width, actual_height = self.get_entry_size()
            actual_x, actual_y = get_actual_coordinates_after_scale(self.get_view().get_canvas().coords(self.__entry_window), \
                                                                                                        new_length_unit, \
                                                                                                        last_length_unit)
            
            self.__entry.config(font=get_font(self.get_length_unit()))
            self.get_view().get_canvas().coords(self.__entry_window, (actual_x, actual_y))
            self.get_view().get_canvas().itemconfig(self.__entry_window, width=actual_width, height=actual_height)
            
    def remove_entry(self):
        """
        Removes the Entry field that appeared
        """
        if self.__entry_window != None:
            self.set_text(self.__entry_text.get()) # Update text in the label on the block, which was previously removed when the Entry appeared
            
            self.get_canvas().delete(self.__entry_window)
            self.__entry_window = None
            self.__entry = None
            
    def write(self):
        self.__command()
        
    def get_entry_text(self):
        return self.__entry_text.get()
        
    def set_entry_text(self, text):
        self.__entry_text.set(text)
        self.set_text(text) # Text in the label on the block
        
    def get_entry_size(self):
        """
        Returns the pixel width and height that an entry field should have
        """
        width, height = convert_grid_coordinate_to_actual(self.get_width(), self.get_height(), self.get_length_unit())
        width -= OUTLINE_WIDTH
        height -= OUTLINE_WIDTH * 2
        
        return width, height
        
    def delete(self):
        self.remove_entry()
        super().delete()
