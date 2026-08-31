# Code structure

Found in the `configuration` directory are all blocks used strictly in setting up the configuration of the threat model and in the `setup` directory those for defining and calculating the values of the system model according to the configuration.

`general_calculations.py` contains the classes and functions used for performing the calculations of attribute values, but also checking that the current configuration and setup is valid for each of the calculation and value types. This is the primary file to consider while implementing any additional calculation or value types.

`ValueTypeDistribution` represents non-negative uniform, triangular, truncated-normal, and lognormal inputs with Monte Carlo samples. Its `DistributionValue` result also retains feasible attack plans as sets of atomic local-cost source identifiers. Distribution-valued `AND` takes unions of prerequisite plans, distribution-valued `OR` retains alternative plans, and strict plan supersets are pruned. Shared prerequisite sources are consequently included once when a downstream `AND` combines branches.
