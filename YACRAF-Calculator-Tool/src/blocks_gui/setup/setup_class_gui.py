import tkinter as tk
import numpy as np
from general_gui import GUIClass
from setup_attribute_gui import GUISetupAttribute
from circle_indicator_gui import GUICircleIndicator
from options import Options
from config import *

class GUISetupClass(GUIClass):
    """
    Manages a GUI setup class
    """
    def __init__(self, model, view, setup_class, configuration_class_gui, *, position=None, linked_group_number=None):
        self.__setup_class = setup_class
        self.__configuration_class_gui = configuration_class_gui
        self.__setup_attributes_gui = []
        self.__connections = [] # Directional connections between setup classes
        self.__script_marker_indicators = [] # Indicators created by scripts
        
        super().__init__(model, view, self.__setup_class.get_instance_name(), CLASS_WIDTH+SETUP_WIDTH_ADDITION, CLASS_HEIGHT, False, position=position, linked_group_number=linked_group_number)
        
        configuration_class_gui.add_setup_class_gui(self)
        
        # Create all GUI setup attributes, with the exception of hidden ones
        for setup_attribute, configuration_attribute_gui in zip(self.__setup_class.get_setup_attributes(), self.__configuration_class_gui.get_configuration_attributes_gui()):
            if not configuration_attribute_gui.is_hidden():
                self.create_setup_attribute_gui(setup_attribute, configuration_attribute_gui)
                
        self.update_text()
        
    @staticmethod
    def new(model, view, configuration_class_gui, position=None):
        setup_class = configuration_class_gui.get_configuration_class().create_setup_version()
        return GUISetupClass(model, view, setup_class, configuration_class_gui, position=position)
        
    @staticmethod
    def linked_copy(view, setup_class_gui, position=None):
        return GUISetupClass(setup_class_gui.get_model(), \
                             view, \
                             setup_class_gui.get_setup_class(), \
                             setup_class_gui.get_configuration_class_gui(), \
                             position=position, \
                             linked_group_number=setup_class_gui.get_linked_group_number())
        
    def open_options(self):
        return Options.setup_class(self.get_model(), self.get_view(), self, self.get_model().get_setup_views())
        
    def move_block(self, move_x, move_y):
        super().move_block(move_x, move_y)
        
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.move(move_x, move_y)
            
    def scale(self, new_length_unit, last_length_unit):
        super().scale(new_length_unit, last_length_unit)
        
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.scale(new_length_unit, last_length_unit)
            
    def is_adjacent(self, coordinates):
        """
        Returns whether any of the specified grid coordinates are adjacent to this block, and in such cases returns the direction which the adjacent coordinates goes out from the block
        """
        # Above or below
        for coordinate in coordinates:
            coordinate_to_check = np.array(coordinate)
            
            for i in range(self.get_width()):
                coordinate_up = np.array((self.get_x() + i, self.get_y() - 1))
                
                # Above class
                if np.linalg.norm(coordinate_to_check - coordinate_up) < 0.5:
                    return True, "UP"
                    
                if len(self.__setup_attributes_gui) == 0:
                    coordinate_down = np.array((self.get_x() + i, self.get_y() + self.get_height()))
                else:
                    last_attribute = self.__setup_attributes_gui[-1]
                    coordinate_down = np.array((last_attribute.get_x() + i, last_attribute.get_y() + last_attribute.get_height()))
                    
                # Below last attribute
                if np.linalg.norm(coordinate_to_check - coordinate_down) < 0.5:
                    return True, "DOWN"
                    
        # Sides of class
        is_adjacent_side, direction = super().is_adjacent(coordinates)
        
        if is_adjacent_side:
            return True, direction 
            
        for i, attribute in enumerate(self.__setup_attributes_gui):
            # Sides of attribute
            is_adjacent_side, direction = attribute.is_adjacent(coordinates)
            
            if is_adjacent_side:
                return True, direction
                
        return False, ""
        
    def create_setup_attribute_gui(self, setup_attribute, configuration_attribute_gui):
        """
        Creates and adds a GUI version of a setup attribute
        """
        setup_attribute_gui = GUISetupAttribute(self.get_model(), \
                                                self.get_view(), \
                                                setup_attribute, \
                                                self, \
                                                configuration_attribute_gui)
        
        self.__setup_attributes_gui.append(setup_attribute_gui)
        self.add_attached_block(setup_attribute_gui)
        
        return setup_attribute_gui
        
    def update_setup_attribute_gui_order(self):
        """
        Updates the shown order of GUI setup attributes according to the order in the calculation setup attribute without a GUI
        """
        # Map each setup attribute (in their current order) to an index value to be sorted according to
        index_map = {value: index for index, value in enumerate(self.__setup_class.get_setup_attributes())}
        
        sorted_setup_attributes_gui = sorted(self.__setup_attributes_gui, key=lambda attribute_gui: index_map[attribute_gui.get_setup_attribute()])
        
        # Move position of GUI blocks
        for i, setup_attribute_gui in enumerate(sorted_setup_attributes_gui):
            steps_moved = i - self.__setup_attributes_gui.index(setup_attribute_gui)
            setup_attribute_gui.move_block(0, steps_moved)
            
        self.__setup_attributes_gui = sorted_setup_attributes_gui
        
    def get_connected_setup_attributes_gui(self, setup_attribute):
        """
        Returns all GUI setup attributes that the specified setup attribute currently takes as input
        """
        connected_setup_attributes_gui = []
        
        for connected_setup_attribute in setup_attribute.get_connected_setup_attributes():
            for connected_setup_class_gui in self.get_connected_setup_classes_gui() + [self]:
                # Found the setup class that has the currently sought connected setup attribute
                if connected_setup_attribute.has_setup_class(connected_setup_class_gui.get_setup_class()):
                    if not connected_setup_attribute.is_hidden():
                        for i, setup_attribute_gui in enumerate(connected_setup_class_gui.get_setup_attributes_gui()):
                            if setup_attribute_gui.get_setup_attribute() == connected_setup_attribute:
                                connected_setup_attributes_gui.append(connected_setup_class_gui.get_setup_attributes_gui()[i])
                                break
                                
                    # Adds the attributes connected to the hidden one
                    else:
                        connected_setup_attributes_gui += connected_setup_class_gui.get_connected_setup_attributes_gui(connected_setup_attribute)
                        
        return connected_setup_attributes_gui
        
    def get_setup_class(self):
        return self.__setup_class
        
    def get_configuration_class_gui(self):
        return self.__configuration_class_gui
        
    def get_setup_attributes_gui(self):
        return self.__setup_attributes_gui
        
    def remove_setup_attribute_gui(self, setup_attribute_gui_to_remove):
        index_first_move_up = self.__setup_attributes_gui.index(setup_attribute_gui_to_remove)
        self.__setup_attributes_gui.remove(setup_attribute_gui_to_remove)
        self.remove_attached_block(setup_attribute_gui_to_remove)
        
        # Move up all GUI setup attributes after the removed one
        for setup_attribute_gui in self.__setup_attributes_gui[index_first_move_up:]:
            setup_attribute_gui.move_block(0, -ATTRIBUTE_HEIGHT)
            
    def add_connection(self, connection):
        self.__connections.append(connection)
        
    def remove_connection(self, connection):
        if connection in self.__connections:
            self.__connections.remove(connection)
            
    def get_connected_setup_classes_gui(self):
        """
        Returns all setup classes currently connected to this GUI setup class
        """
        connected_setup_classes_gui = []
        
        for connection in self.__connections:
            setup_class_gui = connection.get_start_setup_class_gui()
            
            # Do not include connections that are not connected to any other class or those connected to itself
            if setup_class_gui not in (None, self):
                connected_setup_classes_gui.append(setup_class_gui)
                
        return connected_setup_classes_gui
        
    def create_script_marker_indicator(self, text, color, update_linked=True):
        """
        Indicator that is added by scripts to mark classes
        """
        self.__script_marker_indicators.append(GUICircleIndicator(self.get_view(), \
                                                                  self.get_x()+2*SCRIPT_MARKER_CIRCLE_RADIUS*(0.5+len(self.__script_marker_indicators)), \
                                                                  self.get_y()-SCRIPT_MARKER_CIRCLE_RADIUS, \
                                                                  SCRIPT_MARKER_CIRCLE_RADIUS, \
                                                                  color, \
                                                                  SCRIPT_MARKER_CIRCLE_OUTLINE, text))
        
        # Add to linked copies
        if update_linked:
            for linked_setup_class_gui in self.get_model().get_linked_setup_classes_gui(self):
                linked_setup_class_gui.create_script_marker_indicator(text, color, False)
                
    def reset_changes_by_scripts(self):
        """
        Remove any changes or additions made by scripts
        """
        # Reset override values
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.attempt_to_reset_override_value()
            
        # Remove markers placed by scripts
        for script_marker_indicator in self.__script_marker_indicators:
            script_marker_indicator.remove()
            
        self.__script_marker_indicators = []
        
    def update_value_input_types(self, *, specific_attribute_index=None, update_linked=True):
        """
        Updates the input value type of all setup attributes of this setup class (manual entry field or based on calculated value)
        
        specific_attribute_index: Index of attribute to refresh input type
        update_linked: Whether linked copies also should be updated
        """
        for i, setup_attribute_gui in enumerate(self.__setup_attributes_gui):
            # Update the attribute of the specified index, or all if None
            if specific_attribute_index == None or i == specific_attribute_index:
                setup_attribute_gui.update_value_input_type()
                
        if update_linked:
            for linked_setup_class_gui in self.get_model().get_linked_setup_classes_gui(self):
                linked_setup_class_gui.update_value_input_types(specific_attribute_index=specific_attribute_index, update_linked=False)
                
    def calculate_values(self):
        """
        Calculates and shows the values of all setup attributes of this setup class
        """
        self.__setup_class.calculate_values()
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            setup_attribute_gui.display_calculated_value()
            
    def reset_calculated_values(self):
        """
        Resets the calculated value of all setup attributes so that the program knows which ones should be recalculated later
        """
        # Reset values
        for setup_attribute in self.__setup_class.get_setup_attributes():
            setup_attribute.attempt_to_reset_value()
            
        # Sets the value to that of the manual entry field where there is one
        for setup_attribute_gui in self.__setup_attributes_gui:
            if setup_attribute_gui.has_manually_entered_value():
                setup_attribute_gui.add_entered_value_to_attribute()
                
    def get_configuration_name(self):
        """
        Returns the name of the corresponding configuration class name
        """
        return self.__configuration_class_gui.get_name()
        
    def get_name(self):
        """
        Returns the name of the setup class instance
        """
        return self.__setup_class.get_instance_name()
        
    def set_name(self, name):
        """
        Sets the name of the setup class instance
        """
        self.__setup_class.set_instance_name(name)
        self.update_text()
        
    def update_text(self, update_linked=True):
        """
        Updates the displayed text according to the set configuration class and setup class names
        """
        self.set_text(f"{self.__configuration_class_gui.get_name()}: {self.__setup_class.get_instance_name()}")
        
        if update_linked:
            for linked_setup_class_gui in self.get_model().get_linked_setup_classes_gui(self):
                linked_setup_class_gui.update_text(False)
                
    def delete(self):
        super().delete()
        
        self.__configuration_class_gui.remove_setup_class_gui(self)
        self.get_view().remove_setup_class_gui(self)
        
    def save_state(self):
        saved_states = super().save_state() | {"name": self.get_name(), "configuration_class_gui": str(self.__configuration_class_gui), "setup_attributes_gui": []}
        
        for setup_attribute_gui in self.__setup_attributes_gui:
            saved_states["setup_attributes_gui"].append(setup_attribute_gui.save_state())
            
        return saved_states
