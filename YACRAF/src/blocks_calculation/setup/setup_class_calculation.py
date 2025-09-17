from setup_attribute_calculation import SetupAttribute
from config import *

class SetupClass:
    def __init__(self, instance_name, configuration_class):
        self.__instance_name = instance_name
        self.__configuration_class = configuration_class
        self.__setup_attributes = []
        self.__input_setup_classes = {} # Key: Setup class, Value: List of input scalars
        
        # Create setup versions of each configuration attribute in the specified configuration class
        for configuration_attribute in configuration_class.get_configuration_attributes():
            self.create_setup_attribute(configuration_attribute)
            
    def get_instance_name(self):
        return self.__instance_name
        
    def set_instance_name(self, instance_name):
        self.__instance_name = instance_name
        
    def get_configuration_name(self):
        return self.__configuration_class.get_name()
        
    def calculate_values(self):
        """
        Calculate the final value of all setup attributes of this setup class
        """
        for attribute in self.__setup_attributes:
            attribute.calculate_value()
            
    def get_setup_attributes(self):
        return self.__setup_attributes
        
    def create_setup_attribute(self, configuration_attribute):
        """
        Creates a setup version of a configuration attribute
        """
        setup_attribute = SetupAttribute(self, configuration_attribute)
        self.__setup_attributes.append(setup_attribute)
        
        return setup_attribute
        
    def remove_setup_attribute(self, configuration_attribute):
        """
        Removes a setup attribute based on its configuration attribute
        """
        for setup_attribute in self.__setup_attributes:
            if setup_attribute.has_configuration_attribute(configuration_attribute):
                self.__setup_attributes.remove(setup_attribute)
                break
        
    def get_input_setup_classes(self):
        return self.__input_setup_classes
        
    def set_input_setup_class(self, input_class, input_setup_class_scalars=None):
        """
        Sets a setup class as input during calculations of attribute values
        
        input_class: Setup class to add as input during calculations
        input_setup_class_scalars: List of scalars to consider when performing calculations using values from the input class
        """
        if input_setup_class_scalars == None:
            input_setup_class_scalars = [1]
            
        self.__input_setup_classes[input_class] = input_setup_class_scalars
        
    def remove_input_setup_class(self, input_class):
        if input_class in self.__input_setup_classes:
            self.__input_setup_classes.pop(input_class)
