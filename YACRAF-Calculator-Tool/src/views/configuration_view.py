import os
import pickle
from view import View
from configuration_class_gui import GUIConfigurationClass
from configuration_input_gui import GUIConfigurationInput
from buttons_gui import TouchButton
from connection_gui import GUIConnection
from helper_functions_general import delete_all
from config import *

class ConfigurationView(View):
    """
    Class managing a configuration view
    """
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__configuration_classes_gui = []
        self.__configuration_inputs_gui = []
        self.__held_connection = None
        
        self.__add_configuration_class_button = TouchButton.add_configuration_class(model, self) # Button to create a new configuration class
        self.__add_input_button = TouchButton.add_input(model, self) # Button to create a new input block
        
        self.get_canvas().bind(MOUSE_MOTION, self.move_held_connection)
        
    def create_configuration_class_gui(self, *, configuration_class_gui_to_copy=None, position=None):
        """
        Create a new GUI configuration class that is drawn on the canvas in the view
        """
        # Create new
        if configuration_class_gui_to_copy == None:
            configuration_class_gui = GUIConfigurationClass.new(self.get_model(), self, position)
            self.get_model().create_add_to_setup_buttons(configuration_class_gui) # Add buttons to add the setup class version
            
        # Create linked copy
        else:
            configuration_class_gui = GUIConfigurationClass.linked_copy(self, configuration_class_gui_to_copy, position)
            
        self.__configuration_classes_gui.append(configuration_class_gui)
        
        return configuration_class_gui
        
    def remove_configuration_class_gui(self, configuration_class_gui):
        self.__configuration_classes_gui.remove(configuration_class_gui)
        
    def get_configuration_classes_gui(self):
        return self.__configuration_classes_gui
        
    def create_configuration_input_gui(self, position=None):
        """
        Create an input block and add it to the view
        """
        configuration_input_gui = GUIConfigurationInput(self.get_model(), self, position)
        self.__configuration_inputs_gui.append(configuration_input_gui)
        
        return configuration_input_gui
        
    def remove_configuration_input_gui(self, configuration_input_gui):
        self.__configuration_inputs_gui.remove(configuration_input_gui)
        
    def get_configuration_inputs_gui(self):
        return self.__configuration_inputs_gui
        
    def create_connection(self, block, direction, mouse_location=None):
        """
        Creates a new held connection that is connected to the specified block and ends at the current mouse location
        """
        connection = GUIConnection(self, block.get_view(), block, direction, mouse_location=mouse_location)
        self.set_held_connection(connection)
        
        return connection
        
    def move_held_connection(self, event):
        if self.__held_connection != None:
            self.__held_connection.create_new_lines((event.x, event.y))
            
    def get_held_connection(self):
        return self.__held_connection
        
    def set_held_connection(self, connection):
        self.__held_connection = connection
        
    def reset_held_connection(self, remove_connection=False):
        if remove_connection and self.__held_connection != None:
            self.__held_connection.delete()
            
        self.__held_connection = None
        
    def get_movable_items(self):
        """
        Returns all items that can be moved around the view, such as during panning
        """
        movable_items = self.__configuration_classes_gui.copy() # All configuration classes
        
        # All input blocks that are not attached to a configuration attribute, avoiding including them twice as they are moved with their corresponding configuration class
        for configuration_input_gui in self.__configuration_inputs_gui:
            if not configuration_input_gui.is_attached():
                movable_items.append(configuration_input_gui)
        
        return movable_items
        
    def save(self):
        """
        Saves the state of the view
        """
        # Save the state of all blocks
        saved_states_configuration_classes_gui = [class_gui.save_state() for class_gui in self.__configuration_classes_gui]
        saved_states_configuration_inputs_gui = [input_gui.save_state() for input_gui in self.__configuration_inputs_gui]
        
        file_path = os.path.join(CONFIGURATION_SAVES_DIRECTORY, f"{self.get_name()}.pickle")
        
        # Save grid offset and block states to file
        with open(os.path.join(SAVES_PATH, file_path), "wb") as file_pickle:
            pickle.dump((self.get_grid_offset(), saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui), file_pickle)
            
        return file_path
        
    def restore_save(self, file_path, linked_groups_per_number):
        """
        Adds blocks and configures this view according to a previous save
        
        file_path: Path to the file save
        linked_groups_per_number: Dictionary (Key: Group number, Value: List of GUI configuration classes) for configuation class copies linked to each other
        
        Returns mapping between IDs of blocks from the save to those recreated in this new view instance
        """
        try:
            with open(os.path.join(SAVES_PATH, file_path), "rb") as file_pickle:
                grid_offset, saved_states_configuration_classes_gui, saved_states_configuration_inputs_gui = pickle.load(file_pickle)
                self.set_grid_offset(grid_offset[0], grid_offset[1])
                
                mapping_configuration_class_gui = {} # Maps class IDs of GUI configuration classes from previous save to the IDs of the newly created classes
                mapping_configuration_attribute_gui = {} # Maps class IDs of GUI configuration attributes from previous save to the IDs of the newly created classes
                
                # Restore configuration classes
                for saved_states_configuration_class_gui in saved_states_configuration_classes_gui:
                    linked_group_number = saved_states_configuration_class_gui["linked_group_number"]
                    position = (saved_states_configuration_class_gui["x"], saved_states_configuration_class_gui["y"])
                    
                    # Should bind to already existing configuration class
                    if linked_group_number != None and linked_group_number in linked_groups_per_number:
                        configuration_class_gui = self.get_model().create_linked_configuration_class_gui(linked_groups_per_number[linked_group_number][0], \
                                                                                                         self, \
                                                                                                         linked_group_number=linked_group_number, \
                                                                                                         position=position)
                    else:
                        configuration_class_gui = self.create_configuration_class_gui(position=position)
                        
                        if linked_group_number != None:
                            linked_groups_per_number[linked_group_number] = [configuration_class_gui]
                            
                        # Set configuration class data
                        configuration_class_gui.set_name(saved_states_configuration_class_gui["name"])
                        
                        # Restore configuration attributes
                        for saved_states_configuration_attribute_gui in saved_states_configuration_class_gui["configuration_attributes_gui"]:
                            # Create configuration attribute
                            configuration_class_gui.create_attribute()
                            configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[-1]
                            
                            # Set configuration attribute data
                            configuration_attribute_gui.set_name(saved_states_configuration_attribute_gui["name"])
                            configuration_attribute_gui.set_value_type(saved_states_configuration_attribute_gui["value_type"])
                            configuration_attribute_gui.set_input_scalar(saved_states_configuration_attribute_gui["input_scalar"])
                            configuration_attribute_gui.set_input_offset(saved_states_configuration_attribute_gui["input_offset"])
                            configuration_attribute_gui.set_hidden(saved_states_configuration_attribute_gui["is_hidden"])
                            
                    mapping_configuration_class_gui[saved_states_configuration_class_gui["configuration_class_gui"]] = configuration_class_gui
                    
                    for saved_states_configuration_attribute_gui, configuration_attribute_gui in zip(saved_states_configuration_class_gui["configuration_attributes_gui"], configuration_class_gui.get_configuration_attributes_gui()):
                        mapping_configuration_attribute_gui[saved_states_configuration_attribute_gui["configuration_attribute_gui"]] = configuration_attribute_gui
                    
                # Restore configuration inputs
                for saved_states_configuration_input_gui in saved_states_configuration_inputs_gui:
                    # Create configuration input
                    configuration_input_gui = self.create_configuration_input_gui(position=(saved_states_configuration_input_gui["x"], saved_states_configuration_input_gui["y"]))
                    
                    # Set configuration input data
                    configuration_input_gui.attempt_to_attach_to_attribute()
                    calculation_type = saved_states_configuration_input_gui["calculation_type"]
                    
                    if calculation_type != "":
                        configuration_input_gui.set_calculation_type(calculation_type)
                        
                    # Restore configuration connections
                    for saved_states_connection in saved_states_configuration_input_gui["connections"]:
                        connection = GUIConnection(self.get_model(), \
                                                   self, \
                                                   mapping_configuration_attribute_gui[saved_states_connection["start_block"]], \
                                                   saved_states_connection["start_direction"], \
                                                   end_block=configuration_input_gui, \
                                                   end_direction=saved_states_connection["end_direction"], \
                                                   corner_coordinates=saved_states_connection["corner_coordinates"], \
                                                   is_external=saved_states_connection["is_external"])
                        
                return mapping_configuration_class_gui
                
        except FileNotFoundError as e:
            print(f"Could not find configuration view {file_path}: {e}")
            
        return {}
        
    def delete(self):
        delete_all(self.__configuration_classes_gui)
        delete_all(self.__configuration_inputs_gui)
        
        super().delete()
