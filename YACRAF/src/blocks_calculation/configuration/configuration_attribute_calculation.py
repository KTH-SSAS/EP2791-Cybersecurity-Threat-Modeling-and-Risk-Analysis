from config import *

class ConfigurationAttribute:
    """
    Configuration attribute used for calculations
    """
    def __init__(self, name, configuration_class):
        self.__name = name
        self.__configuration_class = configuration_class
        self.__value_type = ValueTypeString
        self.__calculation_type = None
        self.__input_configuration_attributes = {} # Key: input_configuration_attribute, Value: is_internal
        self.__input_scalar = 1 # Float or integer
        self.__input_offset = 0 # Float or integer
        self.__is_hidden = False
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        
    def get_configuration_class(self):
        return self.__configuration_class
        
    def get_value_type(self):
        return self.__value_type
        
    def set_value_type(self, value_type):
        self.__value_type = value_type
        
    def get_calculation_type(self):
        return self.__calculation_type
        
    def set_calculation_type(self, calculation_type):
        self.__calculation_type = calculation_type
        
    def get_input_configuration_attributes(self):
        return self.__input_configuration_attributes
        
    def has_input_configuration_attributes(self):
        return len(self.__input_configuration_attributes) > 0
        
    def add_input_configuration_attribute(self, input_configuration_attribute, is_internal):
        """
        input_configuration_attribute: Configuration attribute to add as an input
        is_internal: Whether the configuration attribute added as an input is connected internally (within the same class instance)
        """
        self.__input_configuration_attributes[input_configuration_attribute] = is_internal
        
    def remove_input_configuration_attribute(self, input_configuration_attribute):
        self.__input_configuration_attributes.pop(input_configuration_attribute)
        
    def get_input_scalar(self):
        return self.__input_scalar
        
    def set_input_scalar(self, input_scalar):
        self.__input_scalar = input_scalar
        
    def reset_input_scalar(self):
        self.__input_scalar = 1
        
    def get_input_offset(self):
        return self.__input_offset
        
    def set_input_offset(self, input_offset):
        self.__input_offset = input_offset
        
    def reset_input_offset(self):
        self.__input_offset = 0
        
    def is_hidden(self):
        return self.__is_hidden
        
    def set_hidden(self, is_hidden):
        self.__is_hidden = is_hidden
