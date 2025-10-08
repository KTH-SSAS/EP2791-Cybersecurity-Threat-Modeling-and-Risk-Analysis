def script_logic(script_if):
    # Insert logic here
    
    # Loops through all defense mechanism instances
    for defense_mechanism_name in script_if.get_class_instance_names("Defense mechanism"):
        current_value = script_if.get_attribute_values("Defense mechanism", defense_mechanism_name, "Impact")[0]
        override_value = " / ".join(["0"] * len(current_value)) # Override value with zeros, where the number of zeros is according to the value type
        
        script_if.override_attribute_values(override_value, \
                                            "Defense mechanism", \
                                            class_instance=defense_mechanism_name, \
                                            attribute="Impact")
        
    script_if.calculate_values()
    
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
