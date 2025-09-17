def mark_easiest_previous_attack(script_if, view, attack_event_type, attack_event_instance, color, value_index=None):
    """
    Adds a marker on the attack event that is easiest to perform
    
    attack_event_type: Type of attack event to consider
    attack_event_instance: Attack event instance to consider when finding the easiest previous attack
    color: Color of marker
    value_index: The index of the value to find the easiest previous attack for, applicable for distributions with multiple values
    """
    input_classes = script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event AND", view=view) + \
                    script_if.get_input_class_names(attack_event_type, attack_event_instance, input_class_type="Attack event OR", view=view)
    
    current_global_difficulties = script_if.get_attribute_values(attack_event_type, attack_event_instance, "Global difficulty", view)
    
    if len(current_global_difficulties) > 1:
        print(f"Warning: Multiple attributes found when searching for {attack_event_type} and {attack_event_instance}, using the attribute value of the first encountered")
        
    # Find unique path for each individual value displayed by the attribute
    for i in range(len(current_global_difficulties[0])):
        if value_index == None or i == value_index:
            script_if.set_class_marker(i+1, color, class_type=attack_event_type, class_instance=attack_event_instance, view=view)
            
            current_easiest_previous_attack = None
            current_lowest_difficulty = None
            
            # Check all input classes
            for input_class_name, input_class_instance in input_classes:
                global_difficulties = script_if.get_attribute_values(input_class_name, input_class_instance, "Global difficulty", view)
                
                if len(global_difficulties) > 1:
                    print(f"Warning: Multiple attributes found when searching for {input_class_name} and {input_class_instance}, using the attribute value of the first encountered")
                    
                global_difficulty = global_difficulties[0]
                
                # Found a new easiest previous attack
                if current_lowest_difficulty == None or global_difficulty[i] < current_lowest_difficulty:
                    current_easiest_previous_attack = (input_class_name, input_class_instance)
                    current_lowest_difficulty = global_difficulty[i]
                    
            # Recursively mark the next easiest attack
            if current_easiest_previous_attack != None:
                mark_easiest_previous_attack(script_if, view, current_easiest_previous_attack[0], current_easiest_previous_attack[1], color, i)
                
def script_logic(script_if):
    # Insert logic here
    script_if.calculate_values()
    
    view = script_if.get_current_view_name()
    
    num_input_to_per_instance = {} # How many attack events each attack event is connected to, Key: Tuple (class_type, class_instance), Value: number attack events that takes it as input
    colors = ("red", "light blue", "green", "yellow", "orange", "magenta", "gray")
    
    # Find the number of attack events each attack event is connected to, considering both types of attack events
    for attack_event_type in ("Attack event AND", "Attack event OR"):
        # For each attack event instance among both types
        for attack_event_instance in script_if.get_class_instance_names(attack_event_type, view=view):
            if (attack_event_type, attack_event_instance) not in num_input_to_per_instance:
                num_input_to_per_instance[(attack_event_type, attack_event_instance)] = 0
                
            # For each input class
            for input_class_names in script_if.get_input_class_names(attack_event_type, \
                                                                     attack_event_instance, \
                                                                     input_class_type="Attack event AND", \
                                                                     view=view) + \
                                     script_if.get_input_class_names(attack_event_type, \
                                                                     attack_event_instance, \
                                                                     input_class_type="Attack event OR", \
                                                                     view=view):
                
                if input_class_names not in num_input_to_per_instance:
                    num_input_to_per_instance[input_class_names] = 1
                else:
                    num_input_to_per_instance[input_class_names] += 1
                    
    current_end_point = 0
    
    # Mark the easeist path for all attack events that are not input for another (are at the top of the attack event tree)
    for class_names, num_input_to in num_input_to_per_instance.items():
        if num_input_to == 0:
            input_class_type, input_class_instance = class_names
            
            mark_easiest_previous_attack(script_if, view, input_class_type, input_class_instance, colors[current_end_point])
            current_end_point += 1
            
def script_control(script_if):
    script_if.reset_script_changes()
    script_logic(script_if)
