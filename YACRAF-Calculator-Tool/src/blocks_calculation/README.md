# Code structure

Found in the `configuration` directory are all blocks used strictly in setting up the configuration of the threat model and in the `setup` directory those for defining and calculating the values of the system model according to the configuration.

`general_calculations.py` contains the classes and functions used for performing the calculations of attribute values, but also checking that the current configuration and setup is valid for each of the calculation and value types. This is the primary file to consider while implementing any additional calculation or value types.

The authoritative description of calculation semantics, equations, statistical assumptions, and extensions is [Yacraf calculations and statistical extensions](../../../Course-material/lectures/Yacraf-calculations.md). Keep this source-level README focused on code organization so the mathematical behavior is documented in one place.

`ValueTypeDistribution` and `DistributionValue` in `general_calculations.py` are the primary implementation types for distribution-valued inputs and results. The setup calculation classes call those operations while traversing configured attribute inputs.
