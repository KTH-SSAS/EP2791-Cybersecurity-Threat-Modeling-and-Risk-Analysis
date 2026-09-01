import os
import numpy as np
from helper_functions_general import convert_value_to_string, convert_string_to_value
from config import *


_distribution_rng = np.random.default_rng()
_distribution_sample_cache = {}
_distribution_display_percentiles = (0.05, 0.5, 0.95)
_pos_calculation_mode = "ratio"


def reset_distribution_sampling_cache(seed=None):
    """Start a new, internally consistent Monte Carlo calculation run."""
    global _distribution_rng

    _distribution_sample_cache.clear()

    if seed is not None:
        _distribution_rng = np.random.default_rng(seed)


def configure_distribution_display(percentiles):
    """Configure the three quantiles shown for sampled results."""
    global _distribution_display_percentiles

    percentiles = tuple(float(percentile) for percentile in percentiles)
    if len(percentiles) != 3 or percentiles[1] != 0.5 or \
       not 0 <= percentiles[0] <= percentiles[1] <= percentiles[2] <= 1:
        raise ValueError("Display percentiles must be lower / 0.5 / upper")

    _distribution_display_percentiles = percentiles


def get_distribution_display_percentiles():
    return _distribution_display_percentiles


def configure_pos_calculation(mode):
    """Choose whether probability-of-success returns a ratio or distribution."""
    global _pos_calculation_mode

    mode = str(mode).strip().lower()
    if mode not in ("ratio", "distribution"):
        raise ValueError("PoS calculation mode must be ratio or distribution")

    _pos_calculation_mode = mode


def get_pos_calculation_mode():
    return _pos_calculation_mode


class DistributionValue:
    """
    Monte Carlo representation of a non-negative quantity.

    A value is either an empirical sample vector or a collection of feasible
    attack plans. Attack plans retain their atomic local-cost sources so that
    AND gates can take set unions without charging shared prerequisites twice.
    """
    def __init__(self, samples=None, *, source_samples=None, plans=None, sample_count=None):
        self.__samples = None if samples is None else np.asarray(samples, dtype=float)
        self.__source_samples = source_samples
        self.__plans = None if plans is None else self.__minimal_plans(plans)
        self.__sample_count = sample_count

        if self.__samples is None and (self.__source_samples is None or self.__plans is None):
            raise ValueError("A distribution value requires samples or attack plans")

        if self.__samples is None and len(self.__source_samples) == 0 and self.__sample_count is None:
            raise ValueError("An empty attack plan requires a sample count")

    @staticmethod
    def __minimal_plans(plans):
        unique_plans = sorted(set(frozenset(plan) for plan in plans), key=len)
        minimal_plans = []

        # Local costs are non-negative, so a strict superset can never be the
        # cheapest plan and is safe to discard.
        for plan in unique_plans:
            if not any(existing_plan < plan for existing_plan in minimal_plans):
                minimal_plans.append(plan)

        return tuple(minimal_plans)

    @classmethod
    def empirical(cls, samples):
        return cls(samples=np.asarray(samples, dtype=float))

    @classmethod
    def atomic(cls, samples, source_key):
        samples = np.asarray(samples, dtype=float)
        return cls(source_samples={source_key: samples}, plans=({source_key},))

    @classmethod
    def empty_plan(cls, num_samples):
        return cls(source_samples={}, plans=(frozenset(),), sample_count=num_samples)

    def is_plan_aware(self):
        return self.__source_samples is not None and self.__plans is not None

    def get_samples(self):
        if self.__samples is None:
            if len(self.__source_samples) == 0:
                # The empty plan is the additive identity used at root nodes.
                self.__samples = np.zeros(self.__sample_count)
            else:
                sample_count = len(next(iter(self.__source_samples.values())))
                plan_costs = []

                for plan in self.__plans:
                    cost = np.zeros(sample_count)
                    for source_key in plan:
                        cost += self.__source_samples[source_key]
                    plan_costs.append(cost)

                self.__samples = np.min(np.stack(plan_costs), axis=0)

        return self.__samples

    def get_plans(self):
        return self.__plans

    def get_source_samples(self):
        return self.__source_samples

    def get_quantiles(self, probabilities=None):
        if probabilities is None:
            probabilities = get_distribution_display_percentiles()
        return np.quantile(self.get_samples(), probabilities)

    def apply_affine(self, scalar, offset=0):
        scalar = float(scalar)
        offset = float(offset)

        if scalar == 1 and offset == 0:
            return self

        # An affine transform of a complete path no longer has atomic source
        # provenance. Default YACRAF cost aggregation uses scalar=1, offset=0.
        return DistributionValue.empirical(self.get_samples() * scalar + offset)

    def clip_nonnegative(self):
        if np.all(self.get_samples() >= 0):
            return self
        return DistributionValue.empirical(np.maximum(self.get_samples(), 0))

    def clip_probability(self):
        samples = self.get_samples()
        if np.all((samples >= 0) & (samples <= 1)):
            return self
        return DistributionValue.empirical(np.clip(samples, 0, 1))

    @staticmethod
    def __merge_sources(distribution_values):
        merged_sources = {}

        for distribution_value in distribution_values:
            for source_key, samples in distribution_value.get_source_samples().items():
                if source_key in merged_sources:
                    existing_samples = merged_sources[source_key]
                    if existing_samples.shape != samples.shape or not np.array_equal(existing_samples, samples):
                        raise ValueError("A shared local-cost source was sampled inconsistently")
                else:
                    merged_sources[source_key] = samples

        return merged_sources

    @classmethod
    def combine_and(cls, distribution_values):
        if all(value.is_plan_aware() for value in distribution_values):
            plans = [frozenset()]

            for distribution_value in distribution_values:
                plans = [current_plan | input_plan
                         for current_plan in plans
                         for input_plan in distribution_value.get_plans()]

            sample_count = len(distribution_values[0].get_samples())
            return cls(source_samples=cls.__merge_sources(distribution_values), plans=plans, sample_count=sample_count)

        samples = np.sum(np.stack([value.get_samples() for value in distribution_values]), axis=0)
        return cls.empirical(samples)

    @classmethod
    def combine_or(cls, distribution_values):
        if all(value.is_plan_aware() for value in distribution_values):
            plans = [plan
                     for distribution_value in distribution_values
                     for plan in distribution_value.get_plans()]
            sample_count = len(distribution_values[0].get_samples())
            return cls(source_samples=cls.__merge_sources(distribution_values), plans=plans, sample_count=sample_count)

        samples = np.min(np.stack([value.get_samples() for value in distribution_values]), axis=0)
        return cls.empirical(samples)

    def __float__(self):
        return float(self.get_quantiles((0.5,))[0])

    def __lt__(self, other):
        return float(self) < float(other)

    def __str__(self):
        probabilities = get_distribution_display_percentiles()
        quantiles = self.get_quantiles(probabilities)
        formatted = []

        for probability, value in zip(probabilities, quantiles):
            rounded_value = round(float(value), 3)
            if rounded_value == int(rounded_value):
                rounded_value = int(rounded_value)
            percentile = round(probability * 100)
            formatted.append(f"P{percentile}={rounded_value}")

        return " / ".join(formatted)

    def to_display_string(self):
        return str(self)


def _is_number(value):
    return isinstance(value, (int, float, np.integer, np.floating))


def parse_distribution_spec(input_value, *, triangle_only=False):
    """Validate and normalize a GUI-entered distribution specification."""
    if len(input_value) == 1 and isinstance(input_value[0], DistributionValue):
        return input_value[0]

    if triangle_only:
        if len(input_value) != 3 or not all(_is_number(value) for value in input_value):
            raise ValueError("A triangular distribution requires minimum / mode / maximum")
        distribution_name = "triangular"
        parameters = tuple(float(value) for value in input_value)
    elif len(input_value) == 3 and all(_is_number(value) for value in input_value):
        # Backward compatibility for the existing example_triangle saves.
        distribution_name = "triangular"
        parameters = tuple(float(value) for value in input_value)
    else:
        if len(input_value) == 0 or not isinstance(input_value[0], str):
            raise ValueError("A distribution must start with its name")
        distribution_name = input_value[0].strip().lower()
        parameters = tuple(input_value[1:])

        if not all(_is_number(value) for value in parameters):
            raise ValueError("Distribution parameters must be numbers")
        parameters = tuple(float(value) for value in parameters)

    if distribution_name == "uniform":
        if len(parameters) != 2:
            raise ValueError("Uniform requires minimum / maximum")
        minimum, maximum = parameters
        if minimum < 0 or maximum < minimum:
            raise ValueError("Uniform requires 0 <= minimum <= maximum")
    elif distribution_name == "triangular":
        if len(parameters) != 3:
            raise ValueError("Triangular requires minimum / mode / maximum")
        minimum, mode, maximum = parameters
        if minimum < 0 or not minimum <= mode <= maximum:
            raise ValueError("Triangular requires 0 <= minimum <= mode <= maximum")
    elif distribution_name == "normal":
        if len(parameters) != 2:
            raise ValueError("Normal requires mean / standard deviation")
        mean, standard_deviation = parameters
        if mean < 0 or standard_deviation < 0:
            raise ValueError("Normal cost requires a non-negative mean and standard deviation")
    elif distribution_name == "lognormal":
        if len(parameters) != 2:
            raise ValueError("Lognormal requires median / geometric standard deviation")
        median, geometric_standard_deviation = parameters
        if median <= 0 or geometric_standard_deviation < 1:
            raise ValueError("Lognormal requires median > 0 and geometric standard deviation >= 1")
    else:
        raise ValueError(f"Unsupported distribution {distribution_name}")

    return (distribution_name,) + parameters


def _sample_distribution_spec(distribution_spec, num_samples):
    distribution_name, *parameters = distribution_spec

    if distribution_name == "uniform":
        minimum, maximum = parameters
        if minimum == maximum:
            return np.full(num_samples, minimum)
        return _distribution_rng.uniform(minimum, maximum, num_samples)

    if distribution_name == "triangular":
        minimum, mode, maximum = parameters
        if minimum == maximum:
            return np.full(num_samples, minimum)
        return _distribution_rng.triangular(minimum, mode, maximum, num_samples)

    if distribution_name == "normal":
        mean, standard_deviation = parameters
        if standard_deviation == 0:
            return np.full(num_samples, mean)

        # Costs cannot be negative, so this is a normal distribution truncated
        # at zero (rejection sampling, without an additional SciPy dependency).
        samples = _distribution_rng.normal(mean, standard_deviation, num_samples)
        negative = samples < 0
        while np.any(negative):
            samples[negative] = _distribution_rng.normal(mean, standard_deviation, np.sum(negative))
            negative = samples < 0
        return samples

    if distribution_name == "lognormal":
        median, geometric_standard_deviation = parameters
        if geometric_standard_deviation == 1:
            return np.full(num_samples, median)
        return _distribution_rng.lognormal(np.log(median), np.log(geometric_standard_deviation), num_samples)

    raise ValueError(f"Unsupported distribution {distribution_name}")


def _distribution_from_input(input_value, num_samples, source_key, *, triangle_only=False):
    parsed_value = parse_distribution_spec(input_value, triangle_only=triangle_only)
    if isinstance(parsed_value, DistributionValue):
        return parsed_value

    cache_key = (source_key, parsed_value, num_samples)
    if cache_key not in _distribution_sample_cache:
        samples = _sample_distribution_spec(parsed_value, num_samples)
        _distribution_sample_cache[cache_key] = DistributionValue.atomic(samples, source_key)

    return _distribution_sample_cache[cache_key]


def distribution_from_input(input_value, num_samples, source_key):
    """Return aligned samples for a manual distribution-valued attribute."""
    return _distribution_from_input(input_value, num_samples, source_key)


def _as_distribution_value(value, num_samples):
    if isinstance(value, DistributionValue):
        samples = value.get_samples()
        if len(samples) == 1 and num_samples != 1:
            return DistributionValue.empirical(np.full(num_samples, samples[0]))
        return value

    values = np.asarray(value, dtype=float)
    if values.size == 1:
        values = np.full(num_samples, values.item())
    elif values.size != num_samples:
        raise ValueError("A sampled distribution input has an unexpected number of samples")
    return DistributionValue.empirical(values)

def combine_values(value_type, calculation_type, input_setup_attributes, setup_input_scalars_per_attribute, configuration_attribute, num_samples):
    """
    Returns a string of the calculated value by combining the value of all input setup attributes according to the calculation type
    """
    calculated_value = value_type.calculation_default(num_samples)
    input_values = []
    use_distribution_sampling = value_type == ValueTypeDistribution or any(
        input_setup_attribute.get_value_type() == ValueTypeDistribution or
        (input_setup_attribute.get_current_value() is not None and
         len(input_setup_attribute.get_current_value()) == 1 and
         isinstance(input_setup_attribute.get_current_value()[0], DistributionValue))
        for input_setup_attribute in input_setup_attributes
    )
    
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
            
        if len(input_value) == 1 and isinstance(input_value[0], DistributionValue):
            input_value = input_value[0]
        elif use_distribution_sampling and input_value_type == ValueTypeDistribution:
            input_value = _distribution_from_input(input_value, num_samples, id(input_setup_attribute))
        elif use_distribution_sampling and input_value_type == ValueTypeTriangleDistribution:
            input_value = _distribution_from_input(input_value, num_samples, id(input_setup_attribute), triangle_only=True)
        else:
            input_value = np.array(input_value)
        setup_input_scalars = setup_input_scalars_per_attribute[i]
        
        # Apply input scalars
        if setup_input_scalars != None:
            input_value = apply_setup_input_scalars(input_value, np.array(setup_input_scalars), input_value_type.allowed_number_of_scalars())
            
        input_values.append(input_value)
        
    if len(input_values) > 0:
        calculated_value = calculation_type.calculate_output_value(input_values, num_samples)

        if isinstance(calculated_value, DistributionValue):
            calculated_value = calculated_value.apply_affine(configuration_attribute.get_input_scalar(), configuration_attribute.get_input_offset())
        else:
            calculated_value = calculated_value * configuration_attribute.get_input_scalar() + configuration_attribute.get_input_offset()

        calculated_value = value_type.adjust_to_range(calculated_value)

    if isinstance(calculated_value, DistributionValue):
        return (calculated_value,)

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
    if isinstance(values, DistributionValue):
        if len(input_scalars) == 1:
            return values.apply_affine(input_scalars[0])
        print(f"Warning: Could not apply input setup scalars {input_scalars} to a distribution; expected one scalar")
    elif len(input_scalars) in allowed_scalar_values:
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

    @classmethod
    def calculation_default(cls, num_samples):
        return cls.default_value()
        
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
                   (calculation_type == CalculationTypeSampleTriangle and input_value_type not in (ValueTypeTriangleDistribution, ValueTypeDistribution)):
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

        elif isinstance(input_value[0], DistributionValue):
            samples = input_value[0].get_samples()
            if np.any((samples < 0) | (samples > 1)):
                print("Warning: The probability distribution in the input is not in [0, 1]")
                return False
            return True
            
        elif not isinstance(input_value[0], float):
            print(f"Warning: The input {input_value[0]} could not be converted to a float for the attribute value type {ValueTypeProbability.symbol()}")
            return False
            
        elif input_value[0] < 0 or input_value[0] > 1:
            print(f"Warning: The input {input_value[0]} at the attribute value type {ValueTypeProbability.symbol()} is not in [0, 1]")
            return False
            
        return True
                
    @staticmethod
    def adjust_to_range(value):
        if isinstance(value, DistributionValue):
            return value.clip_probability()

        if value[0] < 0:
            value[0] = 0
            
        elif value[0] > 1:
            value[0] = 1
            
        return value


class ValueTypeDistribution(ValueType):
    @staticmethod
    def symbol():
        return "D"

    @staticmethod
    def explaination():
        return "Distribution (uniform, triangular, normal, or lognormal)"

    @staticmethod
    def default_text():
        return "triangular / 0 / 0.5 / 1"

    @staticmethod
    def default_value():
        return np.zeros(1)

    @staticmethod
    def calculation_default(num_samples):
        return DistributionValue.empty_plan(num_samples)

    @staticmethod
    def allowed_number_of_scalars():
        return (1,)

    @staticmethod
    def correctly_connected(calculation_type, input_configuration_attributes):
        if not ValueType.correctly_connected(calculation_type, input_configuration_attributes):
            return False

        if calculation_type == CalculationTypeQualitative:
            return True

        if calculation_type in (CalculationTypeMean, CalculationTypeAND, CalculationTypeOR, CalculationTypeMultiplication):
            allowed_value_types = (ValueTypeNumber, ValueTypeProbability, ValueTypeTriangleDistribution, ValueTypeDistribution)
            for input_value_type in get_attribute_value_types(input_configuration_attributes):
                if input_value_type not in allowed_value_types:
                    print(f"Warning: Attribute value type {ValueTypeDistribution.symbol()} does not support {input_value_type.symbol()} as input for {calculation_type.symbol()}")
                    return False
            return True

        if calculation_type == CalculationTypeDivision:
            first_value_type, second_value_type = get_attribute_value_types(input_configuration_attributes)
            allowed_value_types = (ValueTypeNumber, ValueTypeProbability, ValueTypeTriangleDistribution, ValueTypeDistribution)
            return first_value_type in allowed_value_types and second_value_type in allowed_value_types

        print(f"Warning: Attribute value type {ValueTypeDistribution.symbol()} does not support calculation type {calculation_type.symbol()}")
        return False

    @staticmethod
    def is_correct_input_value(input_value):
        try:
            parse_distribution_spec(input_value)
            return True
        except ValueError as error:
            print(f"Warning: {error}")
            return False

    @staticmethod
    def adjust_to_range(value):
        if isinstance(value, DistributionValue):
            return value.clip_nonnegative()
        return np.maximum(value, 0)


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
        if any(isinstance(value, DistributionValue) for value in input_values):
            sampled_values = [_as_distribution_value(value, num_samples).get_samples() for value in input_values]
            return DistributionValue.empirical(np.mean(np.stack(sampled_values), axis=0))
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
        if any(isinstance(value, DistributionValue) for value in input_values):
            return DistributionValue.combine_and([_as_distribution_value(value, num_samples) for value in input_values])
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
        if any(isinstance(value, DistributionValue) for value in input_values):
            return DistributionValue.combine_or([_as_distribution_value(value, num_samples) for value in input_values])
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
        if any(isinstance(value, DistributionValue) for value in input_values):
            output_value = np.ones(num_samples)
            for input_value in input_values:
                output_value *= _as_distribution_value(input_value, num_samples).get_samples()
            return DistributionValue.empirical(output_value)

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
        if any(isinstance(value, DistributionValue) for value in input_values):
            numerator = _as_distribution_value(input_values[0], num_samples).get_samples()
            denominator = _as_distribution_value(input_values[1], num_samples).get_samples()
            return DistributionValue.empirical(numerator / denominator)
        return input_values[0] / input_values[1]
        
class CalculationTypeSampleTriangle(CalculationType):
    @staticmethod
    def symbol():
        return "T"
        
    @staticmethod
    def explaination():
        return "Compare effort (1) > cost (2), using the configured PoS mode"
        
    @staticmethod
    def number_of_inputs():
        return 2
        
    @staticmethod
    def calculate_output_value(input_values, num_samples):
        sampled_values = []
        
        for input_value in input_values:
            if isinstance(input_value, DistributionValue):
                sampled_values.append(_as_distribution_value(input_value, num_samples).get_samples())
                continue

            a, b, c = input_value
            
            # If all values are equal, make one slightly different to avoid errors
            if a == b == c:
                a -= 1e-10
                
            # Sample current triangle distribution
            sampled_values.append(np.random.triangular(a, b, c, num_samples))
            
        effort_samples, global_cost_samples = sampled_values

        if get_pos_calculation_mode() == "distribution":
            # Conditional PoS for every plausible global cost. The empirical
            # effort survival function assumes effort and cost are independent.
            sorted_effort = np.sort(effort_samples)
            num_effort_samples = len(sorted_effort)
            num_greater = num_effort_samples - np.searchsorted(
                sorted_effort, global_cost_samples, side="right"
            )
            return DistributionValue.empirical(num_greater / num_effort_samples)

        # Existing scalar estimator based on aligned success/failure samples.
        return np.array([np.array(np.sum(effort_samples > global_cost_samples) / num_samples)])
        
class CalculationTypeQualitative(CalculationType):
    @staticmethod
    def symbol():
        return "Q"
        
    @staticmethod
    def explaination():
        return "Manual and qualitative evaluation"
