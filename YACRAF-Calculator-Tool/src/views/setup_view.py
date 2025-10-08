import os
import pickle
from view import View
from setup_class_gui import GUISetupClass
from buttons_gui import TouchButton
from connection_gui import GUIConnection
from connection_with_blocks_gui import GUIConnectionWithBlocks
from helper_functions_general import delete_all
from config import *

class SetupView(View):
    """
    Class managing a setup view
    """
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__setup_classes_gui = []
        self.__connections_with_blocks = []
        self.__to_setup_buttons = []
        self.__is_excluded = False
        
        self.__create_connection_button = TouchButton.create_connection(model, self)
        self.__calculate_value_button = TouchButton.calculate_values(model, self)
        
        self.__run_script_buttons = []
        
        # Add buttons to run scripts
        for file_name_full in os.listdir(SCRIPTS_PATH):
            # Find all .py files
            if file_name_full.strip()[-3:] == ".py":
                file_name = file_name_full.strip().replace(".py", "")
                
                # Skip the template file
                if file_name != "SCRIPT_TEMPLATE":
                    # If at least one script, add a button for resetting any changes made by scripts
                    if len(self.__run_script_buttons) == 0:
                        self.__run_script_buttons.append(TouchButton.clear_script(model, self))
                        
                    self.__run_script_buttons.append(TouchButton.run_script(model, self, SCRIPTS_PATH, file_name, len(self.__run_script_buttons)))
                    
    def on_resize(self, event):
        """
        When changing the size of the window, also move setup view specific buttons
        """
        move_x, move_y = super().on_resize(event)
        
        self.__create_connection_button.move_block(move_x/2, 0)
        self.__calculate_value_button.move_block(move_x/2, 0)
        
        for run_script_button in self.__run_script_buttons:
            run_script_button.move_block(move_x, move_y)
            
    def create_copy(self):
        """
        Creates a new setup view and sets it up to match this one
        """
        setup_view_copy = self.get_model().create_view(False, self.get_name())
        
        grid_offset = self.get_grid_offset()
        setup_view_copy.set_grid_offset(grid_offset[0], grid_offset[1])
        
        for setup_class_gui in self.__setup_classes_gui:
            linked_group_number = setup_class_gui.get_linked_group_number()
            position = (setup_class_gui.get_x(), setup_class_gui.get_y())
            
            if linked_group_number != None:
                self.get_model().create_linked_setup_class_gui(setup_class_gui, \
                                                               setup_view_copy, \
                                                               linked_group_number=linked_group_number, \
                                                               position=position)
            else:
                setup_class_gui_copy = setup_view_copy.create_setup_class_gui(configuration_class_gui=setup_class_gui.get_configuration_class_gui(), \
                                                                              position=position)
                setup_class_gui_copy.set_name(setup_class_gui.get_name())
                
                for setup_attribute_gui, setup_attribute_gui_copy in zip(setup_class_gui.get_setup_attributes_gui(), \
                                                                         setup_class_gui_copy.get_setup_attributes_gui()):
                    setup_attribute_gui_copy.set_displayed_value(convert_value_to_string(setup_attribute_gui.get_setup_attribute().get_value()))
                    
        for connection_with_blocks in self.__connections_with_blocks:
            start_block = connection_with_blocks.get_start_block()
            end_block = connection_with_blocks.get_end_block()
            
            setup_view_copy.create_connection_with_blocks(start_coordinate=(start_block.get_x(), start_block.get_y()), \
                                                          end_coordinate=(end_block.get_x(), end_block.get_y()), \
                                                          input_scalars=connection_with_blocks.get_input_scalars(), \
                                                          input_scalars_indicator_coordinate=connection_with_blocks.get_input_scalars_coordinate())
            
    def create_setup_class_gui(self, *, configuration_class_gui=None, setup_class_gui_to_copy=None, position=None):
        """
        Creates a GUI setup class that is drawn on the canvas in the view
        """
        if not((configuration_class_gui == None and setup_class_gui_to_copy != None) or \
               (configuration_class_gui != None and setup_class_gui_to_copy == None)):
            print("Error: Exactly one of configuration_class_gui and setup_class_gui_to_copy need to be specified")
            return
            
        if setup_class_gui_to_copy != None:
            setup_class_gui = GUISetupClass.linked_copy(self, setup_class_gui_to_copy, position)
            
        elif configuration_class_gui != None:
            setup_class_gui = GUISetupClass.new(self.get_model(), self, configuration_class_gui, position)
            
        self.__setup_classes_gui.append(setup_class_gui)
        
        return setup_class_gui
        
    def get_setup_classes_gui(self):
        return self.__setup_classes_gui
        
    def remove_setup_class_gui(self, setup_class_gui):
        self.__setup_classes_gui.remove(setup_class_gui)
        
    def get_movable_items(self):
        """
        Returns all items that can be directly moved around the view, such as during panning
        """
        movable_items = self.__setup_classes_gui.copy() # All setup classes
        
        # Relevant blocks from directional connections
        for connection in self.__connections_with_blocks:
            movable_items += connection.get_movable_items()
            
        return movable_items
        
    def reset_override_values(self):
        """
        Reset the override values of all attributes in all setup classes in the view
        """
        for setup_class_gui in self.__setup_classes_gui:
            setup_class_gui.reset_override_value()
            
    def get_matching_setup_classes_gui(self, *, class_configuration_name=None, class_instance_name=None):
        """
        Returns a list of all GUI setup classes whose name matches the specified ones, where None matches all
        """
        matching_setup_classes_gui = []
        
        for setup_class_gui in self.__setup_classes_gui:
            if class_configuration_name == None or setup_class_gui.get_configuration_name() == class_configuration_name:
                if class_instance_name == None or setup_class_gui.get_name() == class_instance_name:
                    matching_setup_classes_gui.append(setup_class_gui)
                    
        return matching_setup_classes_gui
        
    def create_connection_with_blocks(self, *, start_coordinate=None, end_coordinate=None, input_scalars=None, input_scalars_indicator_coordinate=None):
        """
        Creates a new directional connection with already attached triangle blocks on either side
        """
        connection_with_blocks = GUIConnectionWithBlocks(self.get_model(), \
                                                         self, \
                                                         start_coordinate=start_coordinate, \
                                                         end_coordinate=end_coordinate, \
                                                         input_scalars=input_scalars, \
                                                         input_scalars_indicator_coordinate=input_scalars_indicator_coordinate)
        self.__connections_with_blocks.append(connection_with_blocks)
        
        return connection_with_blocks
        
    def remove_connection_with_blocks(self, connection):
        """
        Remove directional connection with attached triangle blocks on either side
        """
        self.__connections_with_blocks.remove(connection)
        
    def create_add_to_setup_button(self, configuration_class_gui):
        """
        Creates a button for adding a class from a configuration view to this setup view
        """
        self.__to_setup_buttons.append(TouchButton.add_to_setup(self.get_model(), self, configuration_class_gui, len(self.__to_setup_buttons)))
        self.update_add_to_setup_button_order()
        
    def remove_add_to_setup_button(self, to_setup_button):
        """
        Removes a specified button adding a class from a configuration view to this setup view, typically due to removing the configuration class
        """
        to_setup_button.delete()
        
        button_index = self.__to_setup_buttons.index(to_setup_button)
        self.__to_setup_buttons.remove(to_setup_button)
        
        # Move up all buttons after the removed button
        for to_setup_button_to_move in self.__to_setup_buttons[button_index:]:
            to_setup_button_to_move.move_block(0, -ADD_TO_SETUP_HEIGHT)
            
    def update_add_to_setup_button_order(self):
        """
        Updates the stored and displayed order of buttons creating a setup class from a configuration class
        """
        to_setup_buttons_with_index = list(enumerate(self.__to_setup_buttons)) # List of tuples (index, to_setup_button)
        sorted_to_setup_buttons = sorted(to_setup_buttons_with_index, key=lambda x: x[1].get_text())
        
        for i, to_setup_button_with_index in enumerate(sorted_to_setup_buttons):
            previous_index, to_setup_button = to_setup_button_with_index
            
            to_setup_button.move_block(0, (i - previous_index) * CHANGE_VIEW_HEIGHT)
            
        self.__to_setup_buttons = [to_setup_button for _, to_setup_button in sorted_to_setup_buttons]
        
    def is_excluded(self):
        """
        Returns whether the view has been excluded from current calculations
        """
        return self.__is_excluded
        
    def set_excluded(self, is_excluded):
        if is_excluded == self.__is_excluded:
            return
            
        self.__is_excluded = is_excluded
        
        # Change background color
        if is_excluded:
            self.set_background_color(VIEW_EXCLUDED_COLOR)
        else:
            self.set_background_color(VIEW_BACKGROUND_COLOR)
            
        # Change color on the button changing to this view from other views
        for setup_view in self.get_model().get_configuration_views() + self.get_model().get_setup_views():
            if setup_view != self:
                if is_excluded:
                    setup_view.set_color_change_view_button(self, VIEW_EXCLUDED_COLOR)
                else:
                    setup_view.set_color_change_view_button(self, CHANGE_VIEW_COLOR)
                    
        for connection_with_blocks in self.__connections_with_blocks:
            # Disable connections in the view
            if is_excluded:
                connection_with_blocks.get_start_block().attempt_to_disable_calculation_connection()
            # Enable connections in the view
            else:
                connection_with_blocks.get_start_block().attempt_to_enable_calculation_connection()
                
    def save(self):
        """
        Saves the state of the view
        """
        # Save the state of all blocks
        saved_states_setup_classes_gui = [class_gui.save_state() for class_gui in self.__setup_classes_gui]
        saved_states_connections_with_blocks = [connection.save_state() for connection in self.__connections_with_blocks]
        
        file_path = os.path.join(SETUP_SAVES_DIRECTORY, f"{self.get_name()}.pickle")
        
        # Save grid offset and block states to file
        with open(os.path.join(SAVES_PATH, file_path), "wb") as file_pickle:
            pickle.dump((self.get_grid_offset(), self.is_excluded(), saved_states_setup_classes_gui, saved_states_connections_with_blocks), file_pickle)
            
        return file_path
        
    def restore_save(self, file_path, mapping_configuration_class_gui, linked_groups_per_number):
        """
        Adds blocks and configures this view according to a previous save
        
        file_path: Path to the file save
        mapping_configuration_class_gui: Mapping between IDs of blocks from the save to those recreated in this new view instance
        linked_groups_per_number: Dictionary (Key: Group number, Value: List of GUI setup classes) for setup class copies linked to each other
        """
        is_excluded = False
        
        try:
            with open(os.path.join(SAVES_PATH, file_path), "rb") as file_pickle:
                grid_offset, is_excluded, saved_states_setup_classes_gui, saved_states_connections_with_blocks = pickle.load(file_pickle)
                self.set_grid_offset(grid_offset[0], grid_offset[1])
                
                # Restore setup classes
                for saved_states_setup_class_gui in saved_states_setup_classes_gui:
                    position = (saved_states_setup_class_gui["x"], saved_states_setup_class_gui["y"])
                    linked_group_number = saved_states_setup_class_gui["linked_group_number"]
                    
                    # Should bind to already existing setup class
                    if linked_group_number != None and linked_group_number in linked_groups_per_number:
                        setup_class_gui = self.get_model().create_linked_setup_class_gui(linked_groups_per_number[linked_group_number][0], \
                                                                                         self, \
                                                                                         linked_group_number=linked_group_number, \
                                                                                         position=position)
                        
                    else:
                        configuration_class_gui = mapping_configuration_class_gui[saved_states_setup_class_gui["configuration_class_gui"]]
                        setup_class_gui = self.create_setup_class_gui(configuration_class_gui=configuration_class_gui, position=position)
                        
                        if linked_group_number != None:
                            linked_groups_per_number[linked_group_number] = [setup_class_gui]
                        
                    # Set setup class data
                    setup_class_gui.set_name(saved_states_setup_class_gui["name"])
                    
                    for saved_states_setup_attribute_gui, setup_attribute_gui in zip(saved_states_setup_class_gui["setup_attributes_gui"], setup_class_gui.get_setup_attributes_gui()):
                        setup_attribute_gui.set_displayed_value(convert_value_to_string(saved_states_setup_attribute_gui["value"]))
                        
                # Restore setup connections
                for saved_states_connection_with_blocks in saved_states_connections_with_blocks:
                    saved_states_start_block = saved_states_connection_with_blocks["start_block"]
                    saved_states_end_block = saved_states_connection_with_blocks["end_block"]
                    
                    start_coordinate = (saved_states_start_block["x"], saved_states_start_block["y"])
                    end_coordinate = (saved_states_end_block["x"], saved_states_end_block["y"])
                    
                    connection_with_blocks = self.create_connection_with_blocks(start_coordinate=start_coordinate, \
                                                                                end_coordinate=end_coordinate, \
                                                                                input_scalars=saved_states_connection_with_blocks["input_scalars"], \
                                                                                input_scalars_indicator_coordinate=saved_states_connection_with_blocks["input_scalars_indicator_coordinate"])
                    
        except FileNotFoundError as e:
            print(f"Could not find setup view {file_path}: {e}")
            
        return is_excluded
        
    def delete(self):
        delete_all(self.__setup_classes_gui)
        delete_all(self.__connections_with_blocks)
        
        super().delete()
