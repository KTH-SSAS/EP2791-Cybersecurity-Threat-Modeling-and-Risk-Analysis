from general_calculations import combine_values
from config import *

class SetupAttribute:
    def __init__(self, setup_class, configuration_attribute):
        self.__setup_class = setup_class
        self.__configuration_attribute = configuration_attribute
        self.__value = None # None or a tuple
        self.__override_value = None # None or a tuple
        
    def has_setup_class(self, setup_class):
        return self.__setup_class == setup_class
        
    def get_attribute_index(self):
        return self.__setup_class.get_setup_attributes().index(self)
        
    def get_value(self):
        return self.__value
        
    def set_value(self, value):
        self.__value = value
        
    def clear_value(self):
        self.__value = None
        
    def attempt_to_reset_value(self):
        """
        Reset value so that the program knows it should calculate a new one, but only if there is no override value and there are input attributes as this attribute otherwise should take a manual input
        """
        if not self.has_override_value():
            self.clear_value()
            
    def get_override_value(self):
        return self.__override_value
        
    def set_override_value(self, override_value):
        self.__override_value = override_value
        
    def has_override_value(self):
        return self.__override_value != None
        
    def reset_override_value(self):
        self.__override_value = None
        
    def get_current_value(self):
        if self.has_override_value():
            return self.__override_value
            
        return self.__value
        
    def has_connected_setup_attributes(self):
        return len(self.get_connected_setup_attributes()) > 0
        
    def calculate_value(self):
        """
        Calculates the value based on input attributes
        """
        if self.__value != None:
            return
            
        connected_setup_attributes = []
        setup_input_scalars_per_attribute = []
        
        # First calculate any dependent connected setup attributes
        for connected_setup_attribute, input_setup_scalars in self.get_connected_setup_attributes().items():
            connected_setup_attributes.append(connected_setup_attribute)
            setup_input_scalars_per_attribute.append(input_setup_scalars)
            
            connected_setup_attribute.calculate_value()
            
        # Then calculate the value of this setup attribute considering all dependent connected setup attributes
        input_configuration_attributes = list(self.__configuration_attribute.get_input_configuration_attributes().keys())
        value_type = self.__configuration_attribute.get_value_type()
        calculation_type = self.__configuration_attribute.get_calculation_type()
        
        if value_type.correctly_connected(calculation_type, input_configuration_attributes):
            self.__value = combine_values(value_type, \
                                          calculation_type, \
                                          connected_setup_attributes, \
                                          setup_input_scalars_per_attribute, \
                                          self.__configuration_attribute, \
                                          settings.get_num_samples())
        else:
            self.__value = ("CONFIGURATION ERROR",)
            
    def get_value_type(self):
        return self.__configuration_attribute.get_value_type()
        
    def has_configuration_attribute(self, configuration_attribute):
        return self.__configuration_attribute == configuration_attribute
        
    def get_name(self):
        return self.__configuration_attribute.get_name()
        
    def is_hidden(self):
        return self.__configuration_attribute.is_hidden()
        
    def get_connected_setup_attributes(self):
        """
        Returns all setup classes that are connected through connected setup classes, considering the connections between specific attributes made in the configuration
        """
        filtered_connected_setup_attributes = {}
        connected_setup_classes = self.__setup_class.get_input_setup_classes() | {self.__setup_class: None}
        
        # Go through all connected configuration attributes
        for connected_configuration_attribute, is_internal in self.__configuration_attribute.get_input_configuration_attributes().items():
            # Go through all connected setup classes
            for connected_setup_class, input_scalars in connected_setup_classes.items():
                found_internal_connection = is_internal and connected_setup_class == self.__setup_class
                found_external_connection = not is_internal and connected_setup_class != self.__setup_class
                
                # If a setup class corresponding to the configuration class with the connected configuration attribute is currently connected
                if found_internal_connection or found_external_connection:
                    # Go through all setup attributes of the connected setup class to find the one with the correct configuration attribute
                    for connected_setup_attribute in connected_setup_class.get_setup_attributes():
                        if connected_setup_attribute.has_configuration_attribute(connected_configuration_attribute):
                            filtered_connected_setup_attributes[connected_setup_attribute] = input_scalars
                            
        return filtered_connected_setup_attributes
