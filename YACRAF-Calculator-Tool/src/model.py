import os
from configuration_view import ConfigurationView
from setup_view import SetupView
from setup_attribute_gui import GUISetupAttribute
from connection_gui import GUIConnection
from helper_functions_general import delete_all
from config import *

class Model:
    """
    Class that tracks all views and other objects that spans multiple views
    """
    def __init__(self, root, *, force_new_save=False, num_configuration_views=1, num_setup_views=3):
        self.__root = root
        self.__configuration_views = []
        self.__setup_views = []
        self.__current_view = None
        
        self.__currently_pressed_keys = set()
        
        self.__linked_configuration_groups_per_number = {}
        self.__linked_setup_groups_per_number = {}
        
        self.__root.title("Canvas")
        self.__root.geometry(f"{settings.get_canvas_width()}x{settings.get_canvas_height()}")
        self.__root.rowconfigure(0, weight=1)
        self.__root.columnconfigure(0, weight=1)
        
        excluded_setup_views = []
        
        # Create new views
        if not os.path.exists(FILE_PATHS_SAVES_PATH) or force_new_save:
            for i in range(num_configuration_views):
                self.create_view(True, "Metamodel")
                
            for i in range(num_setup_views):
                self.create_view(False, f"System {i+1}")
                
        # Restore saved views
        else:
            with open(FILE_PATHS_SAVES_PATH, "r") as file_with_paths:
                mapping_configuration_class_gui = {} # Used to map configuration class IDs from the saves to newly created ones
                
                for line in file_with_paths:
                    file_path = line.strip()
                    view_directory, view_name = os.path.split(file_path)
                    view_name = view_name.replace(".pickle", "")
                    
                    view_directory = os.path.split(view_directory)[1]
                    
                    # Restore saved configuration view
                    if view_directory == CONFIGURATION_SAVES_DIRECTORY:
                        configuration_view = self.create_view(True, view_name)
                        mapping_configuration_class_gui.update(configuration_view.restore_save(file_path, self.__linked_configuration_groups_per_number))
                        
                    # Restore saved setup view
                    elif view_directory == SETUP_SAVES_DIRECTORY:
                        setup_view = self.create_view(False, view_name)
                        is_excluded = setup_view.restore_save(file_path, mapping_configuration_class_gui, self.__linked_setup_groups_per_number)
                        
                        if is_excluded:
                            excluded_setup_views.append(setup_view)
                            
                for view in self.__configuration_views + self.__setup_views:
                    view.update_shown_order()
                    
        # Attempt to find and set a suitable default view
        if len(self.__configuration_views) > 0:
            self.change_view(self.__configuration_views[0])
            
        elif len(self.__setup_views) > 0:
            self.change_view(self.__setup_views[0])
            
        for setup_view in excluded_setup_views:
            setup_view.set_excluded(True)
            
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)
        
        self.calculate_values()
        
    def on_key_press(self, event):
        """
        When pressing a key on the keyboard
        """
        key = event.keysym
        self.__currently_pressed_keys.add(key.lower())
        
        # If the view or nothing (only root) is in focus (not typing in an entry)
        if self.__root.focus_get() in (self.__root, self.__current_view):
            # Delete a selected block
            if key == "BackSpace":
                items_to_delete = []
                
                for selected_item in list(self.__current_view.get_selected_items()):
                    if not isinstance(selected_item, GUISetupAttribute):
                        items_to_delete.append(selected_item)
                        
                delete_all(items_to_delete, True)
                
            # Reset a held connection
            elif key == "Escape":
                if isinstance(self.__current_view, ConfigurationView):
                    self.__current_view.reset_held_connection(True)
                    
            # Edit a selected block, or the current view if no block is selected
            elif key.lower() == "e":
                selected_items = list(self.__current_view.get_selected_items())
                
                # Open the options for the selected block
                if len(selected_items) > 0:
                    for selected_item in selected_items:
                        selected_item.open_options()
                        
                # Open the options for the view
                else:
                    self.__current_view.open_options()
                    
    def on_key_release(self, event):
        """
        When releasing a key on the keyboard
        """
        key = event.keysym
        
        # Remove the released key from the set of currently pressed ones
        if key.lower() in self.__currently_pressed_keys:
            self.__currently_pressed_keys.remove(key.lower())
            
    def is_currently_pressing_key(self, key):
        return key.lower() in self.__currently_pressed_keys
        
    def create_add_to_setup_buttons(self, configuration_class_gui):
        """
        Creates and adds the button used to create a setup version of a configuration class to each existing setup view
        """
        for existing_setup_view in self.__setup_views:
            existing_setup_view.create_add_to_setup_button(configuration_class_gui)
            
    def remove_add_to_setup_buttons(self, to_setup_buttons):
        """
        Removes the button used to create a setup version of a configuration class from each existing setup view, typically due to the configuration class being deleted
        """
        for to_setup_button in to_setup_buttons:
            to_setup_button.get_view().remove_add_to_setup_button(to_setup_button)
            
    def get_linked_configuration_classes_gui(self, configuration_class_gui):
        """
        Returns a list of all configuration classes that are linked copies of the specified one
        """
        linked_group_number = configuration_class_gui.get_linked_group_number()
        
        if linked_group_number == None:
            return []
            
        linked_configuration_classes_gui = self.__linked_configuration_groups_per_number[linked_group_number].copy()
        
        if configuration_class_gui in linked_configuration_classes_gui:
            linked_configuration_classes_gui.remove(configuration_class_gui) # Do not include itself
            
        return linked_configuration_classes_gui
        
    def create_linked_configuration_class_gui(self, configuration_class_gui_to_copy, view_to_copy_to, *, linked_group_number=None, position=None):
        """
        Creates a linked copy of a configuration class in a specified view
        """
        # Create a new linked group if it does not exist
        self.attempt_to_create_linked_group(configuration_class_gui_to_copy, view_to_copy_to, self.__linked_configuration_groups_per_number, linked_group_number)
        
        # Create new linked copy and add it to the group
        linked_configuration_class_gui = view_to_copy_to.create_configuration_class_gui(configuration_class_gui_to_copy=configuration_class_gui_to_copy, position=position)
        self.__linked_configuration_groups_per_number[linked_configuration_class_gui.get_linked_group_number()].append(linked_configuration_class_gui)
        
        return linked_configuration_class_gui
        
    def get_linked_configuration_attributes_gui(self, configuration_attribute_gui):
        """
        Returns a list of all configuration attributes that are linked copies of the specified one
        """
        if configuration_attribute_gui.get_configuration_class_gui().get_linked_group_number() == None:
            return []
            
        # Index that the specified attribute has in its class
        try:
            attribute_index = configuration_attribute_gui.get_configuration_class_gui().get_configuration_attributes_gui().index(configuration_attribute_gui)
        except:
            return []
            
        linked_configuration_attributes_gui = []
        
        # Find the corresponding attribute of each linked configuration class
        for linked_configuration_class_gui in self.get_linked_configuration_classes_gui(configuration_attribute_gui.get_configuration_class_gui()):
            linked_configuration_attributes_gui.append(linked_configuration_class_gui.get_configuration_attributes_gui()[attribute_index])
            
        return linked_configuration_attributes_gui
        
    def get_linked_setup_classes_gui(self, setup_class_gui):
        """
        Returns a list of all setup classes that are linked copies of the specified one
        """
        linked_group_number = setup_class_gui.get_linked_group_number()
        
        if linked_group_number == None:
            return []
            
        linked_setup_classes_gui = self.__linked_setup_groups_per_number[linked_group_number].copy()
        
        try:
            linked_setup_classes_gui.remove(setup_class_gui) # Do not include itself
        except:
            pass
            
        return linked_setup_classes_gui
        
    def create_linked_setup_class_gui(self, setup_class_gui_to_copy, view_to_copy_to, *, linked_group_number=None, position=None):
        """
        Creates a linked copy of a setup class in a specified view
        """
        # Create a new linked group if it does not exist
        self.attempt_to_create_linked_group(setup_class_gui_to_copy, view_to_copy_to, self.__linked_setup_groups_per_number, linked_group_number)
        
        # Create new linked copy and add it to the group
        linked_setup_class_gui = view_to_copy_to.create_setup_class_gui(setup_class_gui_to_copy=setup_class_gui_to_copy, position=position)
        self.__linked_setup_groups_per_number[linked_setup_class_gui.get_linked_group_number()].append(linked_setup_class_gui)
        
        return linked_setup_class_gui
        
    def get_linked_setup_attributes_gui(self, setup_attribute_gui):
        """
        Returns a list of all setup attributes that are linked copies of the specified one
        """
        if setup_attribute_gui.get_setup_class_gui().get_linked_group_number() == None:
            return []
            
        # Index that the specified attribute has in its class
        try:
            attribute_index = setup_attribute_gui.get_setup_class_gui().get_setup_attributes_gui().index(setup_attribute_gui)
        except:
            return []
            
        linked_setup_attributes_gui = []
        
        # Find the corresponding attribute of each linked configuration class
        for linked_setup_class_gui in self.get_linked_setup_classes_gui(setup_attribute_gui.get_setup_class_gui()):
            linked_setup_attributes_gui.append(linked_setup_class_gui.get_setup_attributes_gui()[attribute_index])
            
        return linked_setup_attributes_gui
        
    def attempt_to_create_linked_group(self, class_gui_to_copy, view_to_copy_to, linked_groups_per_number, linked_group_number=None):
        """
        Create a new linked group if it does not exist
        """
        if class_gui_to_copy.get_linked_group_number() == None:
            if linked_group_number == None:
                linked_group_number = len(linked_groups_per_number)
                
            linked_groups_per_number[linked_group_number] = [class_gui_to_copy]
            class_gui_to_copy.set_linked_group_number(linked_group_number)
            
    def remove_class_gui_from_linked_group(self, linked_class_gui, is_configuration_view):
        linked_group_number = linked_class_gui.get_linked_group_number()
        
        if is_configuration_view:
            linked_groups_per_number = self.__linked_configuration_groups_per_number
        else:
            linked_groups_per_number = self.__linked_setup_groups_per_number
        
        linked_groups_per_number[linked_group_number].remove(linked_class_gui)
        
        # Should remove group as there is at most only one class in it
        if len(linked_groups_per_number[linked_group_number]) <= 1:
            for class_gui in linked_groups_per_number[linked_group_number]:
                class_gui.set_linked_group_number(None)
                
            linked_groups_per_number.pop(linked_group_number)
            
            # Decrement all group numbers above the removed one
            for group_number in sorted(linked_groups_per_number.keys()):
                if group_number > linked_group_number:
                    # Remove and add again with new number
                    group = linked_groups_per_number.pop(group_number)
                    linked_groups_per_number[group_number-1] = group
                    
                    # Set the new number in each setup class
                    for class_gui in group:
                        class_gui.set_linked_group_number(group_number-1)
                        
    def get_root(self):
        return self.__root
        
    def get_configuration_views(self):
        return self.__configuration_views
        
    def get_setup_views(self):
        return self.__setup_views
        
    def swap_view_places(self, view_to_move, move_up):
        """
        Switches the order that two views are stored and the order their buttons appear based on whether a specified view should move up or down
        """
        views_to_consider_moving = []
        
        # Select all configuration or setup views
        if view_to_move in self.__configuration_views:
            views_to_consider_moving = self.__configuration_views
            
        elif view_to_move in self.__setup_views:
            views_to_consider_moving = self.__setup_views
            
        view_index = views_to_consider_moving.index(view_to_move)
        
        if move_up:
            view_to_swap_with_index = view_index - 1
        else:
            view_to_swap_with_index = view_index + 1
            
        # Swap views if there is a view to swap position with
        if (move_up and view_index > 0) or (not move_up and view_index < len(views_to_consider_moving) - 1):
            for view in self.__configuration_views + self.__setup_views:
                view.move_change_view_button(views_to_consider_moving[view_index], move_up)
                view.move_change_view_button(views_to_consider_moving[view_to_swap_with_index], not move_up)
                
            views_to_consider_moving[view_index], views_to_consider_moving[view_to_swap_with_index] = views_to_consider_moving[view_to_swap_with_index], views_to_consider_moving[view_index]
            
    def update_add_to_setup_button_order(self):
        for setup_view in self.__setup_views:
            setup_view.update_add_to_setup_button_order()
            
    def create_view(self, is_configuration_view, view_name):
        """
        Creates a new view, including buttons to navigate to the new view from existing ones
        """
        if is_configuration_view:
            new_view = ConfigurationView(self, view_name)
        else:
            new_view = SetupView(self, view_name)
            
        new_view.grid(row=0, column=0, sticky="nswe")
        
        # Add button to change to other view from the new view
        for configuration_view in self.__configuration_views:
            new_view.add_change_view_button(configuration_view, True)
            
        for setup_view in self.__setup_views:
            new_view.add_change_view_button(setup_view, False)
            
        # Add the new view to the list of existing ones
        if is_configuration_view:
            self.__configuration_views.append(new_view)
        else:
            self.__setup_views.append(new_view)
            
        # Add button to change to the new view from existing views
        for view in self.__configuration_views + self.__setup_views:
            view.add_change_view_button(new_view, is_configuration_view)
            
        # If setup view, add buttons to add classes from configuration views to the setup view 
        if not is_configuration_view:
            seen_configuration_classes = set() # To ensure a button for every linked copy of a configuration class is not added
            
            for configuration_view in self.__configuration_views:
                for configuration_class_gui in configuration_view.get_configuration_classes_gui():
                    configuration_class = configuration_class_gui.get_configuration_class()
                    
                    if configuration_class not in seen_configuration_classes:
                        new_view.create_add_to_setup_button(configuration_class_gui)
                        seen_configuration_classes.add(configuration_class_gui.get_configuration_class())
                        
        self.change_view(self.__current_view)
        
        return new_view
        
    def delete_view(self, view_to_delete):
        """
        Deletes a view and removes the buttons to navigate to it from the remaining views
        """
        # Check that there will be at least one view left
        if len(self.__configuration_views) + len(self.__setup_views) <= 1:
            print("Cannot delete the view, at least one view needs to exist")
            return
            
        view_to_delete.delete()
        
        # Remove button to change to the deleted view from all other views
        for view in self.__configuration_views + self.__setup_views:
            if view != view_to_delete:
                view.remove_change_view_button(view_to_delete)
                
        # Remove reference to button to convert each configuration class to a setup class from each configuration class
        for configuration_view in self.__configuration_views:
            if configuration_view != view_to_delete:
                for configuration_class_gui in configuration_view.get_configuration_classes_gui():
                    configuration_class_gui.remove_to_setup_button(view_to_delete)
                    
        # Remove reference to view
        if view_to_delete in self.__configuration_views:
            self.__configuration_views.remove(view_to_delete)
            
            # Change to the first configuration view if it exists
            if len(self.__configuration_views) > 0:
                self.change_view(self.__configuration_views[0])
            # Otherwise, change to the first setup view
            else:
                self.change_view(self.__setup_views[0])
                
        elif view_to_delete in self.__setup_views:
            self.__setup_views.remove(view_to_delete)
            
            # Change to the first setup view if it exists
            if len(self.__setup_views) > 0:
                self.change_view(self.__setup_views[0])
            # Otherwise, change to the first configuration view
            else:
                self.change_view(self.__configuration_views[0])
                
    def get_current_view(self):
        return self.__current_view
        
    def change_view(self, view):
        """
        Moves the specified view to the top of all views so that it is shown
        """
        if view == None:
            return
            
        self.__current_view = view
        view.tkraise()
        
    def get_num_configuration_classes(self):
        """
        Returns the total number of configuration classes across all configuration views
        """
        num_configuration_classes = 0
        
        for view in self.__configuration_views:
            num_configuration_classes += len(view.get_configuration_classes_gui())
            
        return num_configuration_classes
        
    def reset_script_changes(self):
        """
        Resets any changes or additions made by scripts to all setup views
        """
        for setup_view in self.__setup_views:
            for setup_class_gui in setup_view.get_setup_classes_gui():
                setup_class_gui.reset_changes_by_scripts()
                
        self.calculate_values()
        
    def calculate_values(self):
        """
        Calculates the values of setup attributes
        """
        seen_instances = {} # Key: Instance name, Value: List of GUI setup classes
        seen_linked_groups = set()
        
        # Reset all values that do not have a manual entry field
        for setup_view in self.__setup_views:
            for setup_class_gui in setup_view.get_setup_classes_gui():
                if not setup_view.is_excluded():
                    setup_class_gui.reset_calculated_values()
                    
                # Used for finding duplicate names
                if settings.warns_duplicate_names():
                    instance_name = setup_class_gui.get_name()
                    linked_group_number = setup_class_gui.get_linked_group_number()
                    
                    if instance_name not in seen_instances:
                        seen_instances[instance_name] = [setup_class_gui]
                        
                        if linked_group_number != None:
                            seen_linked_groups.add(linked_group_number)
                    else:
                        if linked_group_number == None or linked_group_number not in seen_linked_groups:
                            seen_instances[instance_name].append(setup_class_gui)
                            
        for instance_name, setup_classes_gui in seen_instances.items():
            if len(setup_classes_gui) > 1:
                print(f"Warning: Found duplicate of class instance name {instance_name} for class type {setup_classes_gui[0].get_configuration_name()} (not a problem, but might cause confusion)")
                print("\tYou can turn off this warning in the settings")
                print("\tFound duplicates in the following views:")
                
                for setup_class_gui in setup_classes_gui:
                    text_linked_group = ""
                    
                    if setup_class_gui.get_linked_group_number() != None:
                        text_linked_group = f" (linked number identifier {setup_class_gui.get_linked_group_number()})"
                        
                    print(f"\t\t{setup_class_gui.get_view().get_name()}{text_linked_group}")
                    
        # Calculates the values of any attribute that had its value reset
        for setup_view in self.__setup_views:
            for setup_class_gui in setup_view.get_setup_classes_gui():
                if not setup_view.is_excluded():
                    setup_class_gui.calculate_values()
                    
    """
    def get_setup_view_names(self):
        return [view.get_name() for view in self.__setup_views]
    """
    
    def set_text_change_view_buttons(self, view_with_changed_name, text):
        """
        Sets the text shown on all buttons changing to the specified view in all views
        """
        for view in self.__configuration_views + self.__setup_views:
            view.set_text_change_view_button(view_with_changed_name, text)
            
    def update_duplicate_view_name(self, view, existing_view_names):
        """
        Adds a number to the name of the specified view if it overlaps with snother view
        """
        added_number = 1
        
        while view.get_name() in existing_view_names:
            view.set_name(f"{view.get_name()} ({added_number})")
        
    def save(self):
        """
        Saves all configuration and setup views
        """
        self.calculate_values()
        
        for directory in [CONFIGURATION_SAVES_DIRECTORY, SETUP_SAVES_DIRECTORY]:
            os.makedirs(os.path.join(SAVES_PATH, directory), exist_ok=True)
            
        configuration_view_names = set()
        setup_view_names = set()
        
        # Create file where the path and view type of each saved view is stored, also storing the order of the views
        with open(FILE_PATHS_SAVES_PATH, "w") as file_with_paths:
            # Need to store configuration views first as they need to be restored before setup views so that they can use the configurations
            for configuration_view in self.__configuration_views:
                self.update_duplicate_view_name(configuration_view, configuration_view_names)
                configuration_view_names.add(configuration_view.get_name())
                
                file_path = configuration_view.save()
                file_with_paths.write(f"{file_path}\n")
                
            for setup_view in self.__setup_views:
                self.update_duplicate_view_name(setup_view, setup_view_names)
                setup_view_names.add(setup_view.get_name())
                
                file_path = setup_view.save()
                file_with_paths.write(f"{file_path}\n")
                
        settings.save()
