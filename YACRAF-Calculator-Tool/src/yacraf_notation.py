"""Display abbreviations for parameters in the bundled YACRAF metamodel.

These abbreviations identify a parameter's meaning. They deliberately do not
describe its implementation value type: for example, ``GD`` remains global
difficulty whether its value is scalar or distribution-valued.
"""


_PARAMETER_ABBREVIATIONS = {
    "attack event": {
        "local difficulty": "LD",
        "global difficulty": "GD",
        "probability of success": "PoS",
    },
    "abuse case": {
        # Existing saves contain the first spelling; accept both forms.
        "accessability to attack surface": "AtAS",
        "accessibility to attack surface": "AtAS",
        "window of opportunity": "WoO",
        "ability to repudiate": "AtR",
        "perceived deterrence": "PD",
        "perceived ease of attack": "PEoA",
        "perceived benefit of success": "PBoS",
        "threat event probability": "TEP",
        "probability of contact": "PoC",
        "effort spent": "ES",
        "probability of action": "PoA",
    },
    "attacker": {
        "personal risk tolerance": "RT",
        "risk tolerance": "RT",
        "concern for collateral damage": "CfCD",
        "skill": "Sk",
        "resources": "Res",
        "sponsorship": "Sp",
        "threat capability": "TC",
    },
    "loss event": {
        "magnitude": "LM",
        "probability": "LP",
        "risk": "LR",
    },
    "actor": {
        "risk": "AR",
    },
    "defense mechanism": {
        "cost": "DMC",
        "impact": "DMI",
        "existence": "DME",
    },
}


def _normalized_class_name(class_name):
    normalized_name = str(class_name).strip().casefold()
    if normalized_name.startswith("attack event "):
        return "attack event"
    return normalized_name


def get_parameter_abbreviation(class_name, attribute_name):
    """Return the semantic YACRAF abbreviation, or ``None`` if unknown."""
    class_parameters = _PARAMETER_ABBREVIATIONS.get(
        _normalized_class_name(class_name), {}
    )
    return class_parameters.get(str(attribute_name).strip().casefold())


def format_parameter_name(class_name, attribute_name):
    """Format a model label without exposing internal value-type symbols."""
    abbreviation = get_parameter_abbreviation(class_name, attribute_name)
    if abbreviation is None:
        return str(attribute_name)
    return f"{attribute_name} ({abbreviation})"
