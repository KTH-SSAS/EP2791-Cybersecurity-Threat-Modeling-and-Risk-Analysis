from general_gui import GUIModelingBlock
from helper_functions_general import convert_grid_coordinate_to_actual, get_font, get_text_that_fits
from pressable_entry import PressableEntry
from config import *

class GUISetupAttribute(GUIModelingBlock):
    """
    Manages a GUI setup attribute
    """
    def __init__(self, model, view, setup_attribute, setup_class_gui, configuration_attribute_gui):
        self.__setup_attribute = setup_attribute
        self.__setup_class_gui = setup_class_gui
        self.__configuration_attribute_gui = configuration_attribute_gui
        
        width = ATTRIBUTE_WIDTH + SETUP_WIDTH_ADDITION
        height = ATTRIBUTE_HEIGHT
        text_width = ATTRIBUTE_WIDTH
        
        attribute_x = setup_class_gui.get_x()
        attribute_y = setup_class_gui.get_y() + CLASS_HEIGHT + len(setup_class_gui.get_setup_attributes_gui()) * ATTRIBUTE_HEIGHT
        
        actual_label_value_x, actual_label_value_y = convert_grid_coordinate_to_actual(attribute_x+ATTRIBUTE_WIDTH+SETUP_WIDTH_ADDITION/2, \
                                                                                       attribute_y+height/2, view.get_length_unit())
        self.__label_value = view.get_canvas().create_text(actual_label_value_x, \
                                                           actual_label_value_y, \
                                                           text="-", \
                                                           font=get_font(view.get_length_unit()), \
                                                           anchor="center", \
                                                           justify="center")
        
        super().__init__(model, \
                         view, \
                         configuration_attribute_gui.get_name(), \
                         width, \
                         height, \
                         ATTRIBUTE_COLOR, \
                         position=(attribute_x, attribute_y), \
                         text_width=text_width, \
                         label_text_x=attribute_x+ATTRIBUTE_WIDTH/2, \
                         additional_pressable_items=[self.__label_value], \
                         bind_left=MOUSE_PRESS)
        
        self.__entry_value = None # Manual entry field
        
        configuration_attribute_gui.add_setup_attribute_gui(self)
        self.update_text()
        
        # If setup_attribute does not have any value, clear and potentially set default value
        if setup_attribute.get_value() == None:
            self.update_value_input_type()
            
        # If setup_attribute already has a value (for example, if this is a linked copy), do not clear it and update the displayed value so that it shows
        else:
            self.update_value_input_type(False)
            self.display_calculated_value()
            
    def left_pressed(self, event):
        super().left_pressed(event)
        self.set_input_attributes_highlight(True)
         
    def open_options(self):
        pass
        
    def unhighlight(self):
        super().unhighlight()
        self.set_input_attributes_highlight(False)
        
    def set_input_attributes_highlight(self, highlight):
        """
        Sets the current highlight of all connected setup attributes that this one currently takes as input
        """
        for connected_setup_attribute_gui in self.__setup_class_gui.get_connected_setup_attributes_gui(self.__setup_attribute):
            if not self.get_view().is_selected_item(connected_setup_attribute_gui):
                # Set highlight
                if highlight:
                    connected_setup_attribute_gui.highlight(HIGHLIGHT_INPUT_COLOR)
                    
                # Remove highlight
                else:
                    connected_setup_attribute_gui.unhighlight()
                    
    def update_value_input_type(self, clear_value=True):
        """
        Update the input value type (manual entry field or calculated value) of this setup attribute based on whether there are connected input attributes
        """
        has_currently_connected_inputs = self.__setup_attribute.has_connected_setup_attributes()
        
        # No manual entry as it takes input from connected attributes
        if has_currently_connected_inputs and \
           self.__configuration_attribute_gui.get_configuration_attribute().get_calculation_type() != CalculationTypeQualitative:
            self.switch_to_value_label(clear_value)
        else:
            self.switch_to_value_entry(clear_value)
            
    def switch_to_value_label(self, clear_value=True):
        """
        Switches to no manual input
        """
        if self.__entry_value != None:
            self.remove_attached_block(self.__entry_value)
            self.__entry_value.delete()
            self.__entry_value = None
            
            # Reset any manually entered value
            if clear_value:
                self.__setup_attribute.clear_value()
                self.set_displayed_value("-")
                
    def switch_to_value_entry(self, clear_value=True):
        """
        Switches to manual entry input field
        """
        if self.__entry_value == None:
            self.__entry_value = PressableEntry(self.get_model(), self.get_view(), self.get_x()+ATTRIBUTE_WIDTH, self.get_y(), SETUP_WIDTH_ADDITION, self.get_height(), lambda: self.update_linked_entry_text())
            self.add_attached_block(self.__entry_value)
            
            # Reset any calculated value as the input now should be entered manually, where a default value is entered
            if clear_value:
                value_type = self.__configuration_attribute_gui.get_value_type()
                
                if value_type != None:
                    value = value_type.default_text()
                else:
                    value = "Value"
                    
                self.__setup_attribute.set_value((value,))
                
            self.display_calculated_value()
            
    def update_linked_entry_text(self):
        for linked_setup_attribute_gui in self.get_model().get_linked_setup_attributes_gui(self):
        	linked_setup_attribute_gui.set_displayed_value(self.__entry_value.get_entry_text())
        	
    def has_manually_entered_value(self):
        return self.__entry_value != None
        
    def get_setup_attribute(self):
        return self.__setup_attribute
        
    def get_setup_class_gui(self):
        return self.__setup_class_gui
        
    def add_entered_value_to_attribute(self):
        """
        Sets the value of the setup attribute to that entered in the entry
        """
        self.__setup_attribute.set_value(convert_string_to_value(self.__entry_value.get_entry_text()))
        
    def set_displayed_value(self, text, color=None):
        """
        Sets the value that is displayed either as the resulting calculated value or that in an entry field
        """
        if color == None:
            color = TEXT_COLOR
            
        if text == None:
            text = "ERROR"
            
        # Set value in Label
        if self.__entry_value == None:
            text, font = get_text_that_fits(self.get_canvas(), self.__label_value, text, self.get_text_width(), False, self.get_length_unit())
            self.get_view().get_canvas().itemconfig(self.__label_value, text=text, font=font, fill=color)
            
        # Set value in Entry
        else:
            self.__entry_value.set_entry_text(text)
            
    def display_calculated_value(self):
        """
        Updates the currently shown value to match the calculated value, where an override value is shown if it exists
        """
        if self.__setup_attribute.has_override_value():
            self.switch_to_value_label(False)
            self.set_displayed_value(convert_value_to_string(self.__setup_attribute.get_override_value()), "red")
        else:
            self.set_displayed_value(convert_value_to_string(self.__setup_attribute.get_value()))
            
    def attempt_to_reset_override_value(self):
        """
        Remove the override value if it exists and update the displayed value accordingly
        """
        if self.__setup_attribute.has_override_value():
            self.__setup_attribute.reset_override_value()
            
            # Update the displayed value for all linked copies
            for setup_attribute_gui in [self] + self.get_model().get_linked_setup_attributes_gui(self):
                setup_attribute_gui.update_value_input_type(False)
                setup_attribute_gui.display_calculated_value()
                
            return True
            
        return False
        
    def get_name(self):
        return self.__configuration_attribute_gui.get_name()
        
    def update_text(self):
        text, is_bold = self.__configuration_attribute_gui.get_attribute_text()
        self.set_text(text, is_bold)
        
    def delete(self):
        super().delete()
        
        self.__configuration_attribute_gui.remove_setup_attribute_gui(self)
        self.__setup_class_gui.remove_setup_attribute_gui(self)
        
    def save_state(self):
        return super().save_state() | {"value": self.__setup_attribute.get_value()}
