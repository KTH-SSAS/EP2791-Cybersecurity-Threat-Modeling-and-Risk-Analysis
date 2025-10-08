from configuration_attribute_calculation import ConfigurationAttribute
from setup_class_calculation import SetupClass
from config import *

class ConfigurationClass:
    """
    Configuration class used for calculations
    """
    def __init__(self, name):
        self.__name = name
        self.__configuration_attributes = []
        self.__setup_class_versions = []
        
    def get_name(self):
        return self.__name
        
    def set_name(self, name):
        self.__name = name
        
    def get_configuration_attributes(self):
        return self.__configuration_attributes
        
    def create_attribute(self, attribute_name):
        """
        Creates and adds a new configuration attribute, creating a corresponding setup attribute for all setup class versions
        """
        configuration_attribute = ConfigurationAttribute(attribute_name, self)
        self.__configuration_attributes.append(configuration_attribute)
        
        for setup_class_version in self.__setup_class_versions:
            setup_class_version.create_setup_attribute(configuration_attribute)
        
        return configuration_attribute
        
    def remove_attribute(self, configuration_attribute):
        if configuration_attribute in self.__configuration_attributes:
            self.__configuration_attributes.remove(configuration_attribute)
            
            for setup_class_version in self.__setup_class_versions:
                setup_class_version.remove_setup_attribute(configuration_attribute)
                
    def create_setup_version(self):
        setup_class = SetupClass("New instance", self)
        self.__setup_class_versions.append(setup_class)
        
        return setup_class
