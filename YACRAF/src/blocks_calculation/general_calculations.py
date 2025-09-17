import os
import numpy as np
from helper_functions_general import convert_value_to_string, convert_string_to_value
from config import *

def combine_values(value_type, calculation_type, input_setup_attributes, setup_input_scalars_per_attribute, configuration_attribute, num_samples):
    """
    Returns a string of the calculated value by combining the value of all input setup attributes according to the calculation type
    """
    calculated_value = value_type.default_value()
    input_values = []
    
    number_of_inputs = calculation_type.number_of_inputs()
    
    # Missing connected setup attributes for the given calculation type to be correctly calculated
    if number_of_inputs != None and len(input_setup_attributes) != number_of_inputs:
        return ("-",)
        
    for i, input_setup_attribute in enumerate(input_setup_attributes):
        input_value_type = input_setup_attribute.get_value_type()
        input_value = input_setup_attribute.get_current_value()
        
        # If an input value could not previously be calculated, this value cannot be calculated either
        if input_value in (("-",), ("SETUP ERROR",)):
            return input_value
            
        # Could not extract input value
        if not input_value_type.is_correct_input_value(input_value):
            return ("SETUP ERROR",)
            
        input_value = np.array(input_value)
        setup_input_scalars = setup_input_scalars_per_attribute[i]
        
        # Apply input scalars
        if setup_input_scalars != None:
            input_value = apply_setup_input_scalars(input_value, np.array(setup_input_scalars), input_value_type.allowed_number_of_scalars())
            
        input_values.append(input_value)
        
    if len(input_values) > 0:
        calculated_value = calculation_type.calculate_output_value(input_values, num_samples) * configuration_attribute.get_input_scalar() + configuration_attribute.get_input_offset()
        calculated_value = value_type.adjust_to_range(calculated_value)
        
    return tuple(calculated_value)
    
def get_attribute_value_types(configuration_attributes):
    """
    Returns a list of value types corresponding to each input configuration attribute
    """
    value_types = []
    
    for configuration_attribute in configuration_attributes:
        value_types.append(configuration_attribute.get_value_type())
        
    return value_types
    
def apply_setup_input_scalars(values, input_scalars, allowed_scalar_values):
    """
    Applies setup input scalars to the specified value, but also checks if the number of scalars are allowed
    """
    if len(input_scalars) in allowed_scalar_values:
        values *= input_scalars
    else:
        print(f"Warning: Could not apply input setup scalars {input_scalars} to {values}, expected a number of values equal to a value in {allowed_scalar_values}")
        
    return values
    
class ValueType:
    """
    Class representing the type of value in an attribute, for example a single value or a distribution
    """
    @staticmethod
    def symbol():
        return None
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        """
        Checks if the configuration is correct considering a specific calculation type and its input configuration attributes
        """
        number_of_inputs = calculation_type.number_of_inputs()
        
        if number_of_inputs != None and len(input_configuration_attributes) != number_of_inputs:
            print(f"Warning: Calculation type {CalculationTypeDivision.symbol()} require exactly {number_of_inputs} input attributes in the configuration")
            return False
            
        return True
        
    @staticmethod
    def is_correct_input_value(input_value):
        """
        Returns whether the input value was correctly formatted
        """
        return True
        
    @staticmethod
    def adjust_to_range(value):
        """
        Adjusts the specified value to fit within the allowed range of the value type
        """
        return value
        
class ValueTypeString(ValueType):
    @staticmethod
    def explaination():
        return "Simple text (no calculations)"
        
    @staticmethod
    def default_text():
        return "Text"
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if calculation_type in (None, CalculationTypeQualitative):
            return True
            
        print(f"Warning: Attribute value type \"Simple text\" does not support calculation type {calculation_type.symbol()}")
        return False
        
class ValueTypeNumber(ValueType):
    @staticmethod
    def symbol():
        return "N"
        
    @staticmethod
    def explaination():
        return "Number (integer or decimal number)"
        
    @staticmethod
    def default_text():
        return "Number"
        
    @staticmethod
    def default_value():
        return np.zeros(1)
        
    @staticmethod
    def allowed_number_of_scalars():
        return (1,)
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if not ValueType.correctly_connected(calculation_type, input_configuration_attributes):
            return False
            
        elif calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type in (CalculationTypeMean, CalculationTypeAND, CalculationTypeOR, CalculationTypeMultiplication, CalculationTypeDivision):
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if input_value_type not in (ValueTypeNumber, ValueTypeProbability):
                    print(f"Warning: Attribute value type {ValueTypeNumber.symbol()} does not support {input_value_type.symbol()} as input for the calculation type {calculation_type.symbol()}")
                    return False
                    
            return True
            
        elif calculation_type == CalculationTypeSampleTriangle:
            print(f"Warning: Attribute value type {ValueTypeNumber.symbol()} does not support calculation type {calculation_type.symbol()}")
            return False
            
        print(f"Error: Could not match calculation type {calculation_type} in value type {ValueTypeNumber.symbol()}")
        return True
        
    @staticmethod
    def is_correct_input_value(input_value):
        if len(input_value) != 1:
            print(f"Warning: The input {input_value} did not contain exactly one value for the attribute value type {ValueTypeNumber.symbol()}")
            return False
            
        elif not isinstance(input_value[0], float):
            print(f"Warning: The input {input_value[0]} could not be converted to a float for the attribute value type {ValueTypeNumber.symbol()}")
            return False
            
        return True
        
class ValueTypeProbability(ValueType):
    @staticmethod
    def symbol():
        return "P"
        
    @staticmethod
    def explaination():
        return "Probability, value in [0, 1]"
        
    @staticmethod
    def default_text():
        return "Probability"
        
    @staticmethod
    def default_value():
        return np.zeros(1)
        
    @staticmethod
    def allowed_number_of_scalars():
        return (1,)
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if not ValueType.correctly_connected(calculation_type, input_configuration_attributes):
            return False
            
        elif calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type in (CalculationTypeMean, CalculationTypeAND, CalculationTypeOR, CalculationTypeMultiplication, CalculationTypeDivision, CalculationTypeSampleTriangle):
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if (calculation_type != CalculationTypeSampleTriangle and input_value_type not in (ValueTypeNumber, ValueTypeProbability)) or \
                   (calculation_type == CalculationTypeSampleTriangle and input_value_type != ValueTypeTriangleDistribution):
                    print(f"Warning: Attribute value type {ValueTypeProbability.symbol()} does not support {input_value_type.symbol()} as input for the calculation type {calculation_type.symbol()}")
                    return False
                    
            return True
            
        print(f"Error: Could not match calculation type {calculation_type} in value type {ValueTypeProbability.symbol()}")
        return True
        
    @staticmethod
    def is_correct_input_value(input_value):
        if len(input_value) != 1:
            print(f"Warning: The input {input_value} did not contain exactly one value for the attribute value type {ValueTypeProbability.symbol()}")
            return False
            
        elif not isinstance(input_value[0], float):
            print(f"Warning: The input {input_value[0]} could not be converted to a float for the attribute value type {ValueTypeProbability.symbol()}")
            return False
            
        elif input_value[0] < 0 or input_value[0] > 1:
            print(f"Warning: The input {input_value[0]} at the attribute value type {ValueTypeProbability.symbol()} is not in [0, 1]")
            return False
            
        return True
                
    @staticmethod
    def adjust_to_range(value):
        if value[0] < 0:
            value[0] = 0
            
        elif value[0] > 1:
            value[0] = 1
            
        return value
        
class ValueTypeTriangleDistribution(ValueType):
    @staticmethod
    def symbol():
        return "T"
        
    @staticmethod
    def explaination():
        return "Triangle distribution (a / b / c)"
        
    @staticmethod
    def default_text():
        return "a / b / c"
        
    @staticmethod
    def default_value():
        return np.zeros(3)
        
    @staticmethod
    def allowed_number_of_scalars():
        return (1, 3)
        
    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if not ValueType.correctly_connected(calculation_type, input_configuration_attributes):
            return False
            
        elif calculation_type == CalculationTypeQualitative:
            return True
            
        elif calculation_type in (CalculationTypeMean, CalculationTypeAND, CalculationTypeOR):
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if input_value_type != ValueTypeTriangleDistribution:
                    print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} does not support {input_value_type.symbol()} as input for the calculation type {calculation_type.symbol()}")
                    return False
                    
            return True
            
        elif calculation_type == CalculationTypeMultiplication:
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if input_value_type == ValueTypeTriangleDistribution:
                    return True
                    
            print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} with the calculation type {calculation_type.symbol()} requires at least one input to be of type {ValueTypeTriangleDistribution.symbol()}")
            return False
            
        elif calculation_type == CalculationTypeDivision:
            first_value_type, second_value_type = get_attribute_value_types(input_configuration_attributes)
            
            if first_value_type != ValueTypeTriangleDistribution:
                print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} with the calculation type {calculation_type.symbol()} does not support value type {first_value_type.symbol()} as its first input")
                return False
                
            elif second_value_type not in (ValueTypeNumber, ValueTypeProbability, ValueTypeTriangleDistribution):
                print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} with the calculation type {calculation_type.symbol()} does not support value type {first_value_type.symbol()} as its second input")
                return False
                
            return True
                    
        elif calculation_type == CalculationTypeSampleTriangle:
            print(f"Warning: Attribute value type {ValueTypeTriangleDistribution.symbol()} does not support calculation type {calculation_type.symbol()}")
            return False
            
        print(f"Error: Could not match calculation type {calculation_type} in value type {ValueTypeTriangleDistribution.symbol()}")
        return True
        
    @staticmethod
    def is_correct_input_value(input_value):
        if len(input_value) != 3:
            print(f"Warning: The input {input_value} did not contain exactly three values for the attribute value type {ValueTypeProbability.symbol()}")
            return False
            
        for value in input_value:
            if not isinstance(value, float):
                print(f"Warning: The value {value} in the input {input_value} could not be converted to a float for the attribute value type {ValueTypeProbability.symbol()}")
                return False
                
        return True
        
class CalculationType:
    """
    Class representing the mathematical operation performed between input attributes, such as AND, OR, etc
    """
    @staticmethod
    def number_of_inputs():
        """
        Returns the number of inputs this calculation type requires, where the order of inputs also matters (the appearing number at each connection)
        Returns None if the inputs are not enumerated and their order does not matter
        """
        return None
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        """
        input_values: List of NumPy arrays representing input values from each input attribute
        num_samples: Number of samples to perform, if applicaple to the calculation type
        
        Returns the calculated value based on the list of input values
        """
        return None
        
class CalculationTypeMean(CalculationType):
    @staticmethod
    def symbol():
        return "M"
        
    @staticmethod
    def explaination():
        return "Mean"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.mean(np.stack(input_values), axis=0)
        
class CalculationTypeAND(CalculationType):
    @staticmethod
    def symbol():
        return "&"
        
    @staticmethod
    def explaination():
        return "AND (addition)"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.sum(np.stack(input_values), axis=0)
        
class CalculationTypeOR(CalculationType):
    @staticmethod
    def symbol():
        return "|"
        
    @staticmethod
    def explaination():
        return "OR (minimum)"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return np.min(np.stack(input_values), axis=0)
        
class CalculationTypeMultiplication(CalculationType):
    @staticmethod
    def symbol():
        return "*"
        
    @staticmethod
    def explaination():
        return "Multiplication"
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        output_value = np.ones(1)
        
        for input_value in input_values:
            # Found a value that is not a scalar, need to change the format of the output value
            if len(output_value) == 1 and len(input_value) > 1:
                output_value = np.ones(len(input_value)) * output_value
                
            output_value *= input_value
            
        return output_value
        
class CalculationTypeDivision(CalculationType):
    @staticmethod
    def symbol():
        return "/"
        
    @staticmethod
    def explaination():
        return "Division between two values, (1) / (2)"
        
    @staticmethod
    def number_of_inputs():
        return 2
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        return input_values[0] / input_values[1]
        
class CalculationTypeSampleTriangle(CalculationType):
    @staticmethod
    def symbol():
        return "T"
        
    @staticmethod
    def explaination():
        return "Sample two triangle distributions, ratio of (1) > (2)"
        
    @staticmethod
    def number_of_inputs():
        return 2
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        sampled_values = []
        
        for input_value in input_values:
            a, b, c = input_value
            
            # If all values are equal, make one slightly different to avoid errors
            if a == b == c:
                a -= 1e-10
                
            # Sample current triangle distribution
            sampled_values.append(np.random.triangular(a, b, c, num_samples))
            
        # Compare samples
        return np.array([np.array(np.sum(sampled_values[0] > sampled_values[1]) / num_samples)])
        
class CalculationTypeQualitative(CalculationType):
    @staticmethod
    def symbol():
        return "Q"
        
    @staticmethod
    def explaination():
        return "Manual and qualitative evaluation"
