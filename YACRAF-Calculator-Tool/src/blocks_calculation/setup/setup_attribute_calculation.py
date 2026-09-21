from general_calculations import (combine_values,
                                  CalculationTypeQualitative,
                                  materialize_probability_override,
                                  validate_probability_override,
                                  ValueTypeProbability)
from config import *

class SetupAttribute:
    def __init__(self, setup_class, configuration_attribute):
        self.__setup_class = setup_class
        self.__configuration_attribute = configuration_attribute
        self.__value = None # None or a tuple
        self.__override_value = None # Temporary script override; None or a tuple
        self.__user_override = None # Persistent analyst override specification
        
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
        Reset the calculated/materialized value before a new calculation run.

        Temporary script overrides remain stored separately and still take
        precedence. Calculated values are still cleared beneath them so a
        formula result or user-distribution sample cannot become stale. A
        manually entered value is retained while its entry is temporarily
        hidden by a script override.
        """
        if not self.has_override_value() or self.has_user_override() or \
           self.has_connected_setup_attributes():
            self.clear_value()
            
    def get_override_value(self):
        return self.__override_value
        
    def set_override_value(self, override_value):
        self.__override_value = override_value
        
    def has_override_value(self):
        return self.__override_value != None
        
    def reset_override_value(self):
        self.__override_value = None

    def allows_user_override(self):
        """Return whether this is a bundled calculated PoC or PoA attribute."""
        return self.__setup_class.get_configuration_name().strip().casefold() == "abuse case" and \
               self.get_name().strip().casefold() in (
                   "probability of contact", "probability of action"
               ) and \
               self.get_value_type() == ValueTypeProbability and \
               self.__configuration_attribute.get_calculation_type() not in (
                   None, CalculationTypeQualitative
               ) and \
               len(self.__configuration_attribute.get_input_configuration_attributes()) > 0

    def get_user_override(self):
        return self.__user_override

    def set_user_override(self, user_override):
        """Persist a validated scalar or distribution PoC/PoA specification."""
        if not self.allows_user_override():
            raise ValueError(
                "Only abuse-case Probability of contact and Probability of action "
                "support analyst overrides"
            )

        self.__user_override = validate_probability_override(user_override)
        self.clear_value()

    def has_user_override(self):
        return self.__user_override is not None

    def reset_user_override(self):
        self.__user_override = None
        self.clear_value()
        
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

        # A temporary script override takes precedence over a persistent user
        # override. It is already returned by get_current_value(), and no
        # underlying value needs to be materialized until the script override
        # is removed.
        if self.has_override_value():
            return

        if self.has_user_override():
            try:
                self.__value = materialize_probability_override(
                    self.__user_override,
                    settings.get_num_samples(),
                    id(self)
                )
            except ValueError as error:
                print(f"Warning: {error}")
                self.__value = ("SETUP ERROR",)
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

    def get_setup_class(self):
        return self.__setup_class
        
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
