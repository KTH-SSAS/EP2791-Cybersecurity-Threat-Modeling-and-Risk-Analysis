def script_logic(script_if):
    # Insert logic here
    script_if.calculate_values()
    
    # Write all class instances of the given types to CSV format that can be converted to a table used in a report
    for class_type_name in ("Loss event", "Abuse case", "Attacker"):
        headers = [class_type_name]
        rows = []
        
        # For each unique class instance found among the class types
        for i, class_instance_name in enumerate(script_if.get_class_instance_names(class_type_name)):
            row = [class_instance_name]
            
            # For each attribute type that the current class type has
            for attribute_name in script_if.get_attribute_names(class_type_name):
                if i == 0:
                    headers.append(attribute_name)
                    
                attribute_values = script_if.get_attribute_values(class_type_name, class_instance_name, attribute_name)
                
                if len(attribute_values) > 1:
                    print(f"Warning: Multiple attributes found when searching for {class_type_name}, {class_instance_name}, and {attribute_name}, using the attribute value of the first encountered")
                    
                row.append(script_if.convert_value_to_string(attribute_values[0]))
                
            rows.append(row)
            
        # Currently prints the results
        print("--------------------------------------------------")
        print(",".join(headers))
        
        for row in rows:
            print(",".join(row))
            
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
