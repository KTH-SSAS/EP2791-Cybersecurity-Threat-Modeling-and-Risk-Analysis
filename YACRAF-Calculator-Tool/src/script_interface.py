import numpy as np
from helper_functions_general import convert_value_to_string, convert_string_to_value
    
class ScriptInterface:
    """
    Methods that scripts can interact with to manipulate the program
    
    Meaning of values passed to methods for finding/matching blocks in setup views, where None matches with all of the specific type:
    class_type: Name of class type (for example, Attack event)
    class_instance: Name of class instance (for example, DoS attack)
    attribute: Name of attribute (for example, Local difficulty)
    view: Setup view name to consider
    """
    def __init__(self, model):
        self.__model = model
        self.__script_helper = ScriptHelper(model)
        
    def get_current_view_name(self):
        """
        Returns the name of the current view
        """
        return self.__model.get_current_view().get_name()
        
    def get_class_type_names(self, view=None):
        """
        Returns a list of class names (those specified in configuration views) found in the specified setup views
        """
        self.__script_helper.check_type([view], str)
        return list(set(setup_class_gui.get_configuration_name() for setup_class_gui in self.__script_helper.get_setup_classes_gui(view, None)))
        
    def get_class_instance_names(self, class_type, view=None):
        """
        Returns a list of class instance names (those specified in setup views) found in the specified setup views
        """
        self.__script_helper.check_type([view, class_type], str)
        return [setup_class_gui.get_name() for setup_class_gui in self.__script_helper.get_instances_setup_class_gui(view, class_type, None)]
        
    def get_attribute_names(self, class_type):
        """
        Returns a list of attribute names for a specific class type
        """
        self.__script_helper.check_type([class_type], str)
        setup_class_gui = self.__script_helper.get_first_setup_class_gui(class_type)
        
        if setup_class_gui == None:
            return []
            
        return [setup_attribute_gui.get_name() for setup_attribute_gui in setup_class_gui.get_setup_attributes_gui()]
        
    def get_input_class_names(self, class_type, class_instance, *, input_class_type=None, input_class_instance=None, view=None):
        """
        input_class_type: Name of class type (for example, Attack event) that should only be considered when finding connected input classes, None considering all
        input_class_instance: Name of class instance (for example, DoS attack) that should only be considered when finding connected input classes, None considering all
        
        Returns a list of tuples (input_class_type, input_class_instance) including the class type and class instance names of all classes which the specified setup class instance takes input from
        """
        self.__script_helper.check_type([class_type, class_instance, input_class_type, input_class_instance, view], str)
        input_class_names = []
        
        for setup_class_gui in self.__script_helper.get_instances_setup_class_gui(view, class_type, class_instance):
            # Add any newly found input class name that had not been previously added
            for input_setup_class in setup_class_gui.get_setup_class().get_input_setup_classes():
                if input_class_type in (None, input_setup_class.get_configuration_name()) and input_class_instance in (None, input_setup_class.get_instance_name()):
                    to_add = (input_setup_class.get_configuration_name(), input_setup_class.get_instance_name())
                    
                    if not to_add in input_class_names:
                        input_class_names.append(to_add)
                        
        return input_class_names
        
    def get_attribute_values(self, class_type, class_instance, attribute, view=None):
        """
        Returns a list of displayed values by the specified setup attributes, each value in turn represented by a list of individual values
        """
        self.__script_helper.check_type([class_type, class_instance, attribute, view], str)
        attributes_values = []
        
        for setup_attribute_gui in self.__script_helper.get_setup_attributes_gui(view, class_type, class_instance, attribute):
            attributes_values.append(setup_attribute_gui.get_setup_attribute().get_current_value())
            
        return attributes_values
        
    def convert_value_to_string(self, attribute_value):
        """
        Converts the specified tuple attribute value into a formatted string
        """
        self.__script_helper.check_type([attribute_value], tuple)
        
        return convert_value_to_string(attribute_value)
        
    def override_attribute_values(self, override_value, class_type, *, class_instance=None, attribute=None, view=None):
        """
        Overrides the displayed value of matching attributes with a temporary one
        """
        self.__script_helper.check_type([class_type, class_instance, attribute, view], str)
        self.__script_helper.check_convert_to_type(override_value, str)
        
        override_value = convert_string_to_value(str(override_value))
        
        for setup_attribute_gui in self.__script_helper.get_setup_attributes_gui(view, class_type, class_instance, attribute):
            setup_attribute_gui.get_setup_attribute().set_override_value(override_value)
            
    def reset_override_attribute_values(self, *, class_type=None, class_instance=None, attribute=None, view=None):
        """
        Resets any override value of matching attributes
        """
        self.__script_helper.check_type([class_type, class_instance, attribute, view], str)
        
        for setup_attribute_gui in self.__script_helper.get_setup_attributes_gui(view, class_type, class_instance, attribute):
            setup_attribute_gui.attempt_to_reset_override_value()
            
    def set_class_marker(self, value, color, *, class_type=None, class_instance=None, view=None):
        """
        Adds a visual marker on all matching class instances
        """
        self.__script_helper.check_type([class_type, class_instance, view], str)
        self.__script_helper.check_convert_to_type(value, str)
        
        for setup_class_gui in self.__script_helper.get_instances_setup_class_gui(view, class_type, class_instance):
            setup_class_gui.create_script_marker_indicator(value, color)
            
    def calculate_values(self):
        """
        Calculates all attribute values in the setup views based on the current configuration
        """
        self.__model.calculate_values()
        
    def reset_script_changes(self):
        """
        Reset any changes made by scripts, such as override values and markers
        """
        self.__model.reset_script_changes()
        
class ScriptHelper:
    def __init__(self, model):
        self.__model = model
        self.__cache = {} # To improve performance when getting the same elements multiple times
        
    def get_from_cache(self, identifier):
        if identifier in self.__cache:
            return self.__cache[identifier]
            
        return None
        
    def get_setup_views(self, view):
        cache_result = self.get_from_cache(view)
        
        if cache_result != None:
            return cache_result
            
        setup_views = []
        
        for setup_view in self.__model.get_setup_views():
            if view in (None, setup_view.get_name()):
                if not setup_view.is_excluded():
                    setup_views.append(setup_view)
                    
        return setup_views
        
    def get_setup_classes_gui(self, view, class_type):
        cache_result = self.get_from_cache((view, class_type))
        
        if cache_result != None:
            return cache_result
            
        setup_classes_gui = []
        seen_setup_classes = set()
        
        for setup_view in self.get_setup_views(view):
            for setup_class_gui in setup_view.get_setup_classes_gui():
                if class_type in (None, setup_class_gui.get_configuration_name()):
                    setup_class = setup_class_gui.get_setup_class()
                    
                    if not setup_class in seen_setup_classes:
                        setup_classes_gui.append(setup_class_gui)
                        seen_setup_classes.add(setup_class)
                        
        return setup_classes_gui
        
    def get_first_setup_class_gui(self, class_type):
        cache_result = self.get_from_cache(class_type)
        
        if cache_result != None:
            return cache_result
            
        for setup_view in self.get_setup_views(None):
            for setup_class_gui in setup_view.get_setup_classes_gui():
                if class_type in (None, setup_class_gui.get_configuration_name()):
                    return setup_class_gui
                    
        return None
        
    def get_instances_setup_class_gui(self, view, class_type, class_instance):
        cache_result = self.get_from_cache((view, class_type, class_instance))
        
        if cache_result != None:
            return cache_result
            
        instance_setup_classes_gui = []
        
        for setup_class_gui in self.get_setup_classes_gui(view, class_type):
            if class_type in (None, setup_class_gui.get_configuration_name()) and class_instance in (None, setup_class_gui.get_name()):
                instance_setup_classes_gui.append(setup_class_gui)
                
        return instance_setup_classes_gui
        
    def get_setup_attributes_gui(self, view, class_type, class_instance, attribute):
        cache_result = self.get_from_cache((view, class_type, class_instance, attribute))
        
        if cache_result != None:
            return cache_result
            
        setup_attributes_gui = []
        
        for setup_class_gui in self.get_instances_setup_class_gui(view, class_type, class_instance):
            if class_instance in (None, setup_class_gui.get_name()):
                for setup_attribute_gui in setup_class_gui.get_setup_attributes_gui():
                    if attribute in (None, setup_attribute_gui.get_name()):
                        setup_attributes_gui.append(setup_attribute_gui)
                        
        return setup_attributes_gui
        
    def check_type(self, list_to_check, type_to_check):
        """
        Checks if each element in a list is of a specified type
        
        list_to_check: List of elements to check
        types_to_check: Type or tuple of types
        """
        for element_to_check in list_to_check:
            if element_to_check != None and not isinstance(element_to_check, type_to_check):
                raise TypeError(f"Expected type {type_to_check}, but {element_to_check} was {type(element_to_check)}")
                
    def check_convert_to_type(self, to_check, type_to_convert_to):
        """
        Checks if a variable can be converted to a specified type
        
        to_check: Variable to check if it can be correctly converted
        type_to_convert_to: Type or tuple of types
        """
        try:
            converted_value = type_to_convert_to(to_check)
        except (TypeError, ValueError):
            raise TypeError(f"Cannot convert {to_check} of type {type(to_check)} to {type_to_convert_to}")
