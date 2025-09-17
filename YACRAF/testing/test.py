import unittest
import tkinter as tk
import sys
import os
import time
from tkinter import font
from io import StringIO

sys.path.append(os.path.join("..", "config"))
from program_paths import IMPORT_PATHS

for path in IMPORT_PATHS:
    sys.path.append(os.path.join("..", path))
    
from model import Model
from script_interface import ScriptInterface
from configuration_class_calculation import ConfigurationClass
from helper_functions_general import convert_grid_coordinate_to_actual, convert_actual_coordinate_to_grid
from default_coordinate_functions import get_block_start_coordinates
from config import *

# sys.stdout = StringIO() # Suppress prints

def process_changes(root):
    """
    Manually process changes made to the GUI
    """
    root.update_idletasks()
    root.update()
    time.sleep
    
def perform_action(block, action, grid_x, grid_y, length_unit=None):
    """
    Simulates an event at a specific coordinate
    """
    if length_unit == None:
        length_unit = block.get_view().get_length_unit()
        
    x, y = convert_grid_coordinate_to_actual(grid_x, grid_y, length_unit)
    
    event = tk.Event()
    event.x = x
    event.y = y
    
    action(event)
    process_changes(block.get_view().get_model().get_root())
    
    time.sleep(0.005)
    
def drag_to(block, grid_x, grid_y, length_unit=None):
    """
    Drag a block to a specific coordinate
    """
    perform_action(block, block.left_pressed, block.get_x(), block.get_y(), length_unit=length_unit)
    perform_action(block, block.left_dragged, grid_x, grid_y, length_unit=length_unit)
    perform_action(block, block.left_released, grid_x, grid_y, length_unit=length_unit)
    
def drag_and_attach_input(configuration_input, configuration_attribute_gui, attached_side, length_unit=None):
    """
    Drag and attach an input block to a specific side of a configuration attribute
    """
    if attached_side == "LEFT":
        x = configuration_attribute_gui.get_x() - INPUT_WIDTH
        y = configuration_attribute_gui.get_y()
    elif attached_side == "RIGHT":
        x = configuration_attribute_gui.get_x() + CLASS_WIDTH
        y = configuration_attribute_gui.get_y()
    else:
        print(f"Error: Did not recognize the side {attached_side}")
        
    drag_to(configuration_input, x, y, length_unit)
    
def configuration_connection(configuration_attribute_gui, attribute_side, configuration_input):
    """
    Creates a connection between a configuration attribute and an input block
    """
    if attribute_side == "LEFT":
        attribute_x = configuration_attribute_gui.get_x()
    elif attribute_side == "RIGHT":
        attribute_x = configuration_attribute_gui.get_x() + configuration_attribute_gui.get_width() - 1
    else:
        print(f"Error: Did not recognize the side {attribute_side}")
        
    perform_action(configuration_attribute_gui, configuration_attribute_gui.right_pressed, attribute_x, configuration_attribute_gui.get_y())
    perform_action(configuration_input, configuration_input.right_pressed, configuration_input.get_x(), configuration_input.get_y())
    
    return configuration_attribute_gui._GUIConfigurationAttribute__connections[-1]
    
def setup_connection(output_setup_class, output_side, input_setup_class, input_side):
    """
    Creates and drags a setup connection between two setup classes according to the specified side of the classes where the triangle blocks should end up
    """
    connection = output_setup_class.get_view().create_connection_with_blocks()
    
    for setup_class, side, connection_end in [(output_setup_class, output_side, connection.get_start_block()), (input_setup_class, input_side, connection.get_end_block())]:
        x = setup_class.get_x() + setup_class.get_width() // 2
        y = setup_class.get_y() + setup_class.get_height() // 2
        
        if side == "UP":
            y = setup_class.get_y() - 1
        elif side == "RIGHT":
            x = setup_class.get_x() + setup_class.get_width()
        elif side == "DOWN":
            y = setup_class.get_y() + setup_class.get_height()
        elif side == "LEFT":
            x = setup_class.get_x() - 1
            
        drag_to(connection_end, x, y)
        
    return connection
    
class Test(unittest.TestCase):
    def setUp(self, *, num_configuration_views=2, num_setup_views=4):
        """
        Creates the default model and views used during testing
        """
        self.root = tk.Tk()
        self.model = Model(self.root, force_new_save=True, num_configuration_views=num_configuration_views, num_setup_views=num_setup_views)
        process_changes(self.root)
        
    def tearDown(self):
        """
        Destroys the GUI window after testing
        """
        self.root.destroy()
        
    def get_configuration_view(self, view_num=0):
        return self.model.get_configuration_views()[view_num]
        
    def get_setup_view(self, view_num=0):
        return self.model.get_setup_views()[view_num]
        
    def configuration_class(self, *, x=None, y=None, view=None):
        """
        Creates a configuration class
        """
        if view == None:
            view = self.get_configuration_view()
            
        configuration_class_gui = view.create_configuration_class_gui()
        
        # Drag to a specified location
        if x != None and y != None:
            drag_to(configuration_class_gui, x, y, view.get_length_unit())
            
        return configuration_class_gui
        
    def attribute(self, configuration_class_gui):
        """
        Adds an attribute to a specified configuration class
        """
        configuration_class_gui.create_attribute()
        
        return configuration_class_gui.get_configuration_attributes_gui()[-1]
        
    def configuration_input(self, *, x=None, y=None, view=None):
        """
        Creates an input block
        """
        if view == None:
            view = self.get_configuration_view()
            
        configuration_input_gui = view.create_configuration_input_gui()
        
        # Drag to a specified location
        if x != None and y != None:
            drag_to(configuration_input_gui, x, y, view.get_length_unit())
            
        return configuration_input_gui
        
    def setup_class(self, configuration_class_gui, *, x=None, y=None, view=None):
        """
        Creates a setup class version of a configuration class
        """
        if view == None:
            view = self.get_setup_view()
            
        setup_class_gui = view.create_setup_class_gui(configuration_class_gui=configuration_class_gui)
        
        # Drag to a specified location
        if x != None and y != None:
            drag_to(setup_class_gui, x, y, view.get_length_unit())
            
        return setup_class_gui
        
    def linked_setup_class(self, setup_class_gui, *, x=None, y=None, view=None):
        if view == None:
            view = self.get_setup_view()
            
        setup_class_gui = view.create_setup_class_gui(setup_class_gui_to_copy=setup_class_gui)
        
        # Drag to a specified location
        if x != None and y != None:
            drag_to(setup_class_gui, x, y, view.get_length_unit())
            
        return setup_class_gui
        
    def check_coordinate(self, block, coordinate, grid_offset=None):
        """
        Check that a block has a specific grid coordinate
        """
        grid_offset_x, grid_offset_y = 0, 0
        
        if grid_offset != None:
            grid_offset_x, grid_offset_y = grid_offset
            grid_offset_x -= 0.5
            grid_offset_y -= 0.5
            
        x = coordinate[0] + grid_offset_x
        y = coordinate[1] + grid_offset_y
        
        self.assertEqual((block.get_x(), block.get_y()), (x, y))
        
    def check_text(self, block, view, *, text=None, is_bold=None):
        """
        Check that a block has a specific text on it
        """
        if text != None:
            self.assertEqual(block.get_text().replace("\n", " "), text)
            self.assertEqual(view.get_canvas().itemcget(block._GUIModelingBlock__label_text, "text").replace("\n", " "), text) 
            
        if is_bold != None:
            self.assertEqual(font.Font(font=view.get_canvas().itemcget(block._GUIModelingBlock__label_text, "font")).actual("weight") == "bold", is_bold)

class TestCreatingBlocks(Test):
    def test_configuration_class(self):
        view = self.get_configuration_view()
        configuration_class_gui = self.configuration_class(view=view)
        
        self.check_coordinate(configuration_class_gui, get_block_start_coordinates(view.get_length_unit())[0])
        self.assertEqual(len(configuration_class_gui.get_configuration_class().get_configuration_attributes()), 0)
        
    def test_configuration_attribute(self):
        configuration_class_gui = self.configuration_class()
        num_attributes = 5
        
        for i in range(num_attributes):
            self.attribute(configuration_class_gui)
            
        self.assertEqual(len(configuration_class_gui.get_configuration_class().get_configuration_attributes()), num_attributes)
        
        for i in range(num_attributes):
            configuration_attribute_gui = configuration_class_gui.get_configuration_attributes_gui()[i]
            self.check_coordinate(configuration_attribute_gui, \
                                  (configuration_class_gui.get_x(), configuration_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
    def test_configuration_input(self):
        view = self.get_configuration_view()
        configuration_input_gui = self.configuration_input(view=view)
        self.check_coordinate(configuration_input_gui, get_block_start_coordinates(view.get_length_unit())[0])
        
    def test_setup_class(self):
        configuration_class_gui = self.configuration_class()
        
        view = self.get_setup_view()
        setup_class_gui = self.setup_class(configuration_class_gui)
        
        self.check_coordinate(setup_class_gui, get_block_start_coordinates(view.get_length_unit())[0])
        
    def test_setup_attribute(self):
        configuration_class_gui = self.configuration_class()
        
        # Create attributes
        for i in range(5):
            self.attribute(configuration_class_gui)
            
            if i == 2:
                setup_class_gui = self.setup_class(configuration_class_gui)
                self.assertEqual(len(setup_class_gui.get_setup_class().get_setup_attributes()), 3)
                
        # Check attributes
        self.assertEqual(len(setup_class_gui.get_setup_class().get_setup_attributes()), 5)
        
        for i in range(5):
            setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[i]
            self.check_coordinate(setup_attribute_gui, (setup_class_gui.get_x(), setup_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
class TestDraggingBlocks(Test):
    def setUp(self):
        super().setUp()
        
        self.configuration_view = self.get_configuration_view()
        self.configuration_class_gui = self.configuration_class(x=10, y=10)
        
        self.setup_view = self.get_setup_view()
        
    def test_configuration_class(self):
        drag_to(self.configuration_class_gui, 20, 20)
        
        self.check_coordinate(self.configuration_class_gui, (20, 20))
        
    def test_configuration_attribute(self):
        # Create attributes
        for i in range(5):
            self.attribute(self.configuration_class_gui)
            
            if i == 2:
                drag_to(self.configuration_class_gui, 15, 15)
                
        drag_to(self.configuration_class_gui, 20, 20)
        
        # Check attributes
        for i in range(5):
            configuration_attribute_gui = self.configuration_class_gui.get_configuration_attributes_gui()[i]
            self.check_coordinate(configuration_attribute_gui, \
                                  (self.configuration_class_gui.get_x(), self.configuration_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
    def test_configuration_input(self):
        # Create attribute
        configuration_attribute_gui = self.attribute(self.configuration_class_gui)
        drag_to(self.configuration_class_gui, 12, 12)
        
        # Create input block and attach it to the created attribute
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, configuration_attribute_gui, "LEFT")
        
        # Move class and check that the input block followed along
        drag_to(self.configuration_class_gui, 20, 20)
        self.check_coordinate(configuration_input_gui, (configuration_attribute_gui.get_x()-INPUT_WIDTH, configuration_attribute_gui.get_y()))
        
        # Attach to block to other side and move class
        drag_and_attach_input(configuration_input_gui, configuration_attribute_gui, "RIGHT")
        drag_to(self.configuration_class_gui, 5, 5)
        
        # Check that input block followed along
        self.check_coordinate(configuration_input_gui, (configuration_attribute_gui.get_x()+CLASS_WIDTH, configuration_attribute_gui.get_y()))
        self.assertTrue(configuration_input_gui.is_attached())
        
        # Detach input block
        drag_to(configuration_input_gui, 15, 15)
        self.assertFalse(configuration_input_gui.is_attached())
        
    def test_setup_class(self):
        setup_class_gui = self.setup_class(self.configuration_class_gui, x=15, y=15)
        
        drag_to(self.configuration_class_gui, 20, 20)
        
        self.check_coordinate(setup_class_gui, (15, 15))
        
    def test_setup_attribute(self):
        # Create attributes
        for i in range(5):
            self.attribute(self.configuration_class_gui)
            
            if i == 2:
                setup_class_gui = self.setup_class(self.configuration_class_gui, x=15, y=15)
                
        drag_to(self.configuration_class_gui, 20, 20)
        
        # Check attributes
        for i in range(5):
            setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[i]
            self.check_coordinate(setup_attribute_gui, (setup_class_gui.get_x(), setup_class_gui.get_y()+CLASS_HEIGHT+i*ATTRIBUTE_HEIGHT))
            
class TestChangeName(Test):
    def test_class(self):
        configuration_name = "CONFIGURATION CLASS 123"
        setup_name = "SETUP CLASS 123"
        
        # Create configuration class and a setup version, changing both of their names
        configuration_class_gui = self.configuration_class(x=10, y=10)
        setup_class_gui = self.setup_class(configuration_class_gui, x=15, y=15)
        
        configuration_class_gui.set_name(configuration_name)
        setup_class_gui.set_name(setup_name)
        
        self.assertEqual(configuration_class_gui.get_name(), configuration_name)
        self.assertEqual(configuration_class_gui.get_configuration_class().get_name(), configuration_name)
        
        self.assertEqual(setup_class_gui.get_name(), setup_name)
        self.assertEqual(setup_class_gui.get_configuration_name(), configuration_name)
        self.assertEqual(setup_class_gui.get_setup_class().get_instance_name(), setup_name)
        self.assertEqual(setup_class_gui.get_setup_class().get_configuration_name(), configuration_name)
        
    def test_attribute(self):
        attribute_name = "ATTRIBUTE 123"
        
        configuration_class_gui = self.configuration_class(x=10, y=10)
        setup_class_gui = self.setup_class(configuration_class_gui, x=15, y=15)
        
        configuration_attribute_gui = self.attribute(configuration_class_gui)
        setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[-1]
        
        configuration_attribute_gui.set_name(attribute_name)
        
        self.assertEqual(configuration_attribute_gui.get_name(), attribute_name)
        self.assertEqual(configuration_attribute_gui.get_configuration_attribute().get_name(), attribute_name)
        self.assertEqual(setup_attribute_gui.get_setup_attribute().get_name(), attribute_name)
        
    def test_configuration_view(self):
        view_name = "CONFIGURATION VIEW 123"
        configuration_view = self.get_configuration_view(0)
        configuration_view.set_name(view_name)
        
        self.assertEqual(configuration_view.get_name(), view_name)
        
        for view in self.model.get_configuration_views() + self.model.get_setup_views():
            self.check_text(view._View__configuration_change_view_buttons[configuration_view], view, text=view_name, is_bold=False)
            
    def test_setup_view(self):
        view_name = "SETUP VIEW 123"
        setup_view = self.get_setup_view(0)
        setup_view.set_name(view_name)
        
        self.assertEqual(setup_view.get_name(), view_name)
        
        for view in self.model.get_configuration_views() + self.model.get_setup_views():
            self.check_text(view._View__setup_change_view_buttons[setup_view], view, text=view_name, is_bold=False)
            
    def test_set_calculation_type(self):
        configuration_view = self.get_configuration_view()
        setup_view = self.get_setup_view()
        
        configuration_class_gui = self.configuration_class(x=15, y=15)
        setup_class_gui = self.setup_class(configuration_class_gui, x=20, y=20)
        
        configuration_attribute_gui = self.attribute(configuration_class_gui)
        setup_attribute_gui = setup_class_gui.get_setup_attributes_gui()[-1]
        
        # Create and attach input block
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, configuration_attribute_gui, "LEFT")
        
        configuration_attribute = configuration_attribute_gui.get_configuration_attribute()
        
        # Default calculation type
        self.assertEqual(configuration_input_gui.get_calculation_type(), None)
        self.assertEqual(configuration_attribute.get_calculation_type(), None)
        self.check_text(configuration_attribute_gui, configuration_view, is_bold=False)
        self.check_text(setup_attribute_gui, setup_view, is_bold=False)
        
        # Set calculation type while connected
        configuration_input_gui.set_calculation_type(CalculationTypeAND)
        self.assertEqual(configuration_input_gui.get_calculation_type(), CalculationTypeAND)
        self.assertEqual(configuration_attribute.get_calculation_type(), CalculationTypeAND)
        self.check_text(configuration_attribute_gui, configuration_view, is_bold=True)
        self.check_text(setup_attribute_gui, setup_view, is_bold=True)
        
        # Detach input block
        drag_to(configuration_input_gui, 10, 10)
        self.assertEqual(configuration_input_gui.get_calculation_type(), CalculationTypeAND)
        self.assertEqual(configuration_attribute.get_calculation_type(), None)
        self.check_text(configuration_attribute_gui, configuration_view, is_bold=False)
        self.check_text(setup_attribute_gui, setup_view, is_bold=False)
        
        # Change calculation type while disconnected
        configuration_input_gui.set_calculation_type(CalculationTypeOR)
        self.assertEqual(configuration_input_gui.get_calculation_type(), CalculationTypeOR)
        self.assertEqual(configuration_attribute.get_calculation_type(), None)
        self.check_text(configuration_attribute_gui, configuration_view, is_bold=False)
        self.check_text(setup_attribute_gui, setup_view, is_bold=False)
        
        # Connect input block with the new calculation type
        drag_and_attach_input(configuration_input_gui, configuration_attribute_gui, "RIGHT")
        self.assertEqual(configuration_input_gui.get_calculation_type(), CalculationTypeOR)
        self.assertEqual(configuration_attribute.get_calculation_type(), CalculationTypeOR)
        self.check_text(configuration_attribute_gui, configuration_view, is_bold=True)
        self.check_text(setup_attribute_gui, setup_view, is_bold=True)
        
class TestSwitchPlaces(Test):
    def setUp(self):
        super().setUp(num_configuration_views=2, num_setup_views=2)
        
    def check_configuration_attribute_order(self, class_gui, top_attribute_gui, bottom_attribute_gui, connections_top, connections_bottom):
        """
        Checks that the order of attributes is correct in a configuration class
        """
        input_attributes_gui_top = top_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()
        input_attributes_gui_bottom = bottom_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()
        
        self.assertEqual(len(input_attributes_gui_top), connections_top)
        self.assertEqual(len(input_attributes_gui_bottom), connections_bottom)
        self.assertTrue(top_attribute_gui.get_y() < bottom_attribute_gui.get_y())
        
        input_configuration_attribute_gui_1, input_configuration_attribute_gui_2 = class_gui.get_configuration_attributes_gui()
        input_configuration_attribute_1, input_configuration_attribute_2 = class_gui.get_configuration_class().get_configuration_attributes()
        
        self.assertEqual((input_configuration_attribute_gui_1, input_configuration_attribute_gui_2), (top_attribute_gui, bottom_attribute_gui))
        self.assertEqual((input_configuration_attribute_1, input_configuration_attribute_2), (input_configuration_attribute_gui_1.get_configuration_attribute(), input_configuration_attribute_gui_2.get_configuration_attribute()))
        
    def check_setup_attribute_order(self, configuration_class_gui, top_configuration_attribute_gui, bottom_configuration_attribute_gui):
        """
        Checks that the order of attributes is correct in a setup class
        """
        for setup_class_gui in configuration_class_gui.get_setup_classes_gui():
            setup_attribute_gui_1, setup_attribute_gui_2 = setup_class_gui.get_setup_attributes_gui()
            configuration_attribute_gui_1 = setup_attribute_gui_1._GUISetupAttribute__configuration_attribute_gui
            configuration_attribute_gui_2 = setup_attribute_gui_2._GUISetupAttribute__configuration_attribute_gui
            
            self.assertEqual((configuration_attribute_gui_1, configuration_attribute_gui_2), (top_configuration_attribute_gui, bottom_configuration_attribute_gui))
            self.assertEqual(setup_attribute_gui_1.get_y() < setup_attribute_gui_2.get_y())
            
    def test_switch_attributes(self):
        input_configuration_class_gui = self.configuration_class(x=20, y=20)
        input_configuration_attribute_gui_1 = self.attribute(input_configuration_class_gui)
        input_configuration_attribute_gui_2 = self.attribute(input_configuration_class_gui)
        
        output_configuration_class_gui = self.configuration_class(x=10, y=10)
        output_configuration_attribute_gui = self.attribute(output_configuration_class_gui)
        
        # Create and attach input block to attribute
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, input_configuration_attribute_gui_1, "LEFT")
        
        # Add connection
        configuration_connection(output_configuration_attribute_gui, "LEFT", configuration_input_gui)
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2, 1, 0)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2)
        
        input_configuration_class_gui.swap_attribute_places(input_configuration_attribute_gui_1, True) # Should not move up when at the top
        input_configuration_class_gui.swap_attribute_places(input_configuration_attribute_gui_1, False) # Move down
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_2, input_configuration_attribute_gui_1, 0, 1)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_2, input_configuration_attribute_gui_1)
        
        input_configuration_class_gui.swap_attribute_places(input_configuration_attribute_gui_1, False) # Should not move down when at the bottom
        input_configuration_class_gui.swap_attribute_places(input_configuration_attribute_gui_1, True) # Move up
        
        self.check_configuration_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2, 1, 0)
        self.check_setup_attribute_order(input_configuration_class_gui, input_configuration_attribute_gui_1, input_configuration_attribute_gui_2)
        
    def check_view_order(self, views, top_view, bottom_view):
        """
        Checks that views are stored in a specific order
        """
        view_1, view_2 = views
        self.assertEqual((view_1, view_2), (top_view, bottom_view))
        
    def check_change_view_button_positions(self, is_configuration_view, top_view, bottom_view):
        """
        Checks that the buttons for changing views are in a specified order
        """
        for view in self.model.get_configuration_views() + self.model.get_setup_views():
            if is_configuration_view:
                change_view_buttons = view._View__configuration_change_view_buttons
            else:
                change_view_buttons = view._View__setup_change_view_buttons
                
            top_button = change_view_buttons[top_view]
            bottom_button = change_view_buttons[bottom_view]
            
            self.assertTrue(top_button.get_y() < bottom_button.get_y())
            
    def test_switch_change_configuration_views(self):
        configuration_view_1, configuration_view_2 = self.get_configuration_view(0), self.get_configuration_view(1)
        
        self.check_change_view_button_positions(True, configuration_view_1, configuration_view_2)
        
        self.model.swap_view_places(configuration_view_1, True) # Should not move up when at the top
        self.model.swap_view_places(configuration_view_1, False) # Move down
        
        self.check_view_order(self.model.get_configuration_views(), configuration_view_2, configuration_view_1)
        self.check_change_view_button_positions(True, configuration_view_2, configuration_view_1)
        
        self.model.swap_view_places(configuration_view_1, False) # Should not move down when at the bottom
        self.model.swap_view_places(configuration_view_1, True) # Move up
        
        self.check_view_order(self.model.get_configuration_views(), configuration_view_1, configuration_view_2)
        self.check_change_view_button_positions(True, configuration_view_1, configuration_view_2)
        
    def test_switch_change_setup_views(self):
        setup_view_1, setup_view_2 = self.get_setup_view(0), self.get_setup_view(1)
        
        self.check_change_view_button_positions(False, setup_view_1, setup_view_2)
        
        self.model.swap_view_places(setup_view_1, True) # Should not move up when at the top
        self.model.swap_view_places(setup_view_1, False) # Move down
        
        self.check_view_order(self.model.get_setup_views(), setup_view_2, setup_view_1)
        self.check_change_view_button_positions(False, setup_view_2, setup_view_1)
        
        self.model.swap_view_places(setup_view_1, False) # Should not move down when at the bottom
        self.model.swap_view_places(setup_view_1, True) # Move up
        
        self.check_view_order(self.model.get_setup_views(), setup_view_1, setup_view_2)
        self.check_change_view_button_positions(False, setup_view_1, setup_view_2)
        
class TestConnections(Test):
    def test_configuration_connection(self):
        input_configuration_class_gui = self.configuration_class(x=20, y=20)
        input_configuration_attribute_gui = self.attribute(input_configuration_class_gui)
        
        output_configuration_class_gui = self.configuration_class(x=10, y=10)
        first_output_configuration_attribute_gui = self.attribute(output_configuration_class_gui)
        second_output_configuration_attribute_gui = self.attribute(output_configuration_class_gui)
        
        # Create and attach input block to attribute
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, input_configuration_attribute_gui, "LEFT")
        
        configuration_connection(first_output_configuration_attribute_gui, "RIGHT", configuration_input_gui)
        
        self.assertEqual(len(first_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(second_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 0)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 1)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 1)
        
        # Disconnect input block from attribute
        drag_to(configuration_input_gui, 15, 15)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 1)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 0)
        
        # Add connection to disconnected input block
        configuration_connection(second_output_configuration_attribute_gui, "RIGHT", configuration_input_gui)
        
        self.assertEqual(len(first_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(second_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 2)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 0)
        
        # Reconnect input block to attribute
        drag_and_attach_input(configuration_input_gui, input_configuration_attribute_gui, "RIGHT")
        
        self.assertEqual(len(first_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
        self.assertEqual(len(second_output_configuration_attribute_gui._GUIConfigurationAttribute__connections), 1)
        
        self.assertEqual(len(configuration_input_gui._GUIConfigurationInput__connections), 2)
        self.assertEqual(len(input_configuration_attribute_gui.get_configuration_attribute().get_input_configuration_attributes()), 2)
        
    def test_setup_connection(self):
        # Create configuration classes and connect configuration attributes
        input_configuration_class_gui = self.configuration_class(x=20, y=20)
        input_configuration_attribute_gui = self.attribute(input_configuration_class_gui)
        
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, input_configuration_attribute_gui, "LEFT")
        
        output_configuration_class_gui = self.configuration_class(x=10, y=10)
        output_configuration_attribute_gui = self.attribute(output_configuration_class_gui)
        self.attribute(output_configuration_class_gui)
        
        configuration_connection(output_configuration_attribute_gui, "RIGHT", configuration_input_gui)
        
        # Create and connection setup classes
        input_setup_class_gui = self.setup_class(input_configuration_class_gui, x=20, y=20)
        output_setup_class_gui = self.setup_class(output_configuration_class_gui, x=10, y=10)
        
        setup_connection(output_setup_class_gui, "RIGHT", input_setup_class_gui, "LEFT")
        
        # Check GUI connection
        self.assertEqual(len(input_setup_class_gui._GUISetupClass__connections), 1)
        self.assertEqual(len(output_setup_class_gui._GUISetupClass__connections), 1)
        
        # Check calculation connections
        input_setup_class = input_setup_class_gui.get_setup_class()
        output_setup_class = output_setup_class_gui.get_setup_class()
        
        self.assertEqual(len(input_setup_class.get_input_setup_classes()), 1)
        self.assertEqual(len(output_setup_class.get_input_setup_classes()), 0)
        
        self.assertEqual(list(input_setup_class.get_input_setup_classes().keys())[0], output_setup_class)
        
    def test_external_configuration_connection(self):
        configuration_class_gui = self.configuration_class(x=10, y=10)
        output_configuration_attribute_gui = self.attribute(configuration_class_gui)
        input_configuration_attribute_gui = self.attribute(configuration_class_gui)
        
        configuration_input_gui = self.configuration_input()
        drag_and_attach_input(configuration_input_gui, input_configuration_attribute_gui, "RIGHT")
        
        connection = configuration_connection(output_configuration_attribute_gui, "RIGHT", configuration_input_gui)
        
        input_setup_class_gui = self.setup_class(configuration_class_gui, x=20, y=20)
        input_setup_attribute = input_setup_class_gui.get_setup_attributes_gui()[1].get_setup_attribute()
        
        self.assertEqual(len(input_setup_attribute.get_connected_setup_attributes()), 1) # When connection is not external
        connection.set_external(True)
        self.assertEqual(len(input_setup_attribute.get_connected_setup_attributes()), 0) # When connection is external
        
        # Check that the external connection takes input from another instance of the same class type
        output_setup_class_gui = self.setup_class(configuration_class_gui, x=10, y=10)
        setup_connection(output_setup_class_gui, "RIGHT", input_setup_class_gui, "LEFT")
        
        self.assertEqual(len(input_setup_attribute.get_connected_setup_attributes()), 1)
        
class TestCalculations(Test):
    def create_system(self, input_value_type, output_value_types, calculation_type):
        input_configuration_class = ConfigurationClass("Input")
        input_configuration_attribute = input_configuration_class.create_attribute("Attribute")
        input_configuration_attribute.set_value_type(input_value_type)
        input_configuration_attribute.set_calculation_type(calculation_type)
        
        output_configuration_class = ConfigurationClass("Output")
        
        for i, value_type in enumerate(output_value_types):
            output_configuration_attribute = output_configuration_class.create_attribute(f"Attribute {i}")
            output_configuration_attribute.set_value_type(value_type)
            
            input_configuration_attribute.add_input_configuration_attribute(output_configuration_attribute, False)
            
        input_setup_class = input_configuration_class.create_setup_version()
        output_setup_class = output_configuration_class.create_setup_version()
        
        input_setup_class.set_input_setup_class(output_setup_class)
        
        return input_setup_class, input_setup_class.get_setup_attributes()[0], output_setup_class, output_setup_class.get_setup_attributes()
        
    def check_calculation(self, calculation_type, input_value_type, output_value_types, output_values, result):
        input_setup_class, input_setup_attribute, output_setup_class, output_setup_attributes = self.create_system(input_value_type, output_value_types, calculation_type)
        
        for setup_attribute, value in zip(output_setup_attributes, output_values):
            setup_attribute.set_value(convert_string_to_value(value))
            
        input_setup_attribute.calculate_value()
        self.assertEqual(convert_value_to_string(input_setup_attribute.get_value()), result)
        
    def test_mean(self):
        self.check_calculation(CalculationTypeMean, ValueTypeNumber, [ValueTypeNumber]*3, ["3", "1", "2"], "2")
        self.check_calculation(CalculationTypeMean, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution]*3, ["7 / 3 / 4", "1 / 6 / 9", "5 / 8 / 2"], f"{round(13/3, DECIMALS_WHEN_ROUNDING)} / {round(17/3, DECIMALS_WHEN_ROUNDING)} / 5")
        
    def test_and(self):
        self.check_calculation(CalculationTypeAND, ValueTypeNumber, [ValueTypeNumber]*3, ["3", "1", "2"], "6")
        self.check_calculation(CalculationTypeAND, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution]*3, ["7 / 3 / 4", "1 / 6 / 9", "5 / 8 / 2"], "13 / 17 / 15")
        
    def test_or(self):
        self.check_calculation(CalculationTypeOR, ValueTypeNumber, [ValueTypeNumber]*3, ["3", "1", "2"], "1")
        self.check_calculation(CalculationTypeOR, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution]*3, ["7 / 3 / 4", "1 / 6 / 9", "5 / 8 / 2"], "1 / 3 / 2")
        
    def test_multiplication(self):
        self.check_calculation(CalculationTypeMultiplication, ValueTypeNumber, [ValueTypeNumber]*3, ["3", "1", "2"], "6")
        self.check_calculation(CalculationTypeMultiplication, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution]*3, ["7 / 3 / 4", "1 / 6 / 9", "5 / 8 / 2"], "35 / 144 / 72")
        self.check_calculation(CalculationTypeMultiplication, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution, ValueTypeNumber, ValueTypeTriangleDistribution], ["7 / 3 / 4", "2", "5 / 8 / 2"], "70 / 48 / 16")
        
    def test_division(self):
        self.check_calculation(CalculationTypeDivision, ValueTypeNumber, [ValueTypeNumber]*2, ["1", "2"], "0.5")
        self.check_calculation(CalculationTypeDivision, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution]*2, ["2 / 5 / 4", "3 / 1 / 6"], f"{round(2/3, DECIMALS_WHEN_ROUNDING)} / 5 / {round(2/3, DECIMALS_WHEN_ROUNDING)}")
        self.check_calculation(CalculationTypeDivision, ValueTypeTriangleDistribution, [ValueTypeTriangleDistribution, ValueTypeNumber], ["2 / 5 / 4", "2"], "1 / 2.5 / 2")
        
    def test_sample_triangle(self):
        self.check_calculation(CalculationTypeSampleTriangle, ValueTypeProbability, [ValueTypeTriangleDistribution]*2, ["1 / 2 / 3", "4 / 5 / 6"], "0")
        self.check_calculation(CalculationTypeSampleTriangle, ValueTypeProbability, [ValueTypeTriangleDistribution]*2, ["4 / 5 / 6", "1 / 2 / 3"], "1")
                
class TestScripts(Test):
    def setUp(self):
        super().setUp()
        
        self.script_if = ScriptInterface(self.model)
        
        self.configuration_views = self.model.get_configuration_views()
        self.setup_views = self.model.get_setup_views()
        
        self.setup_view_names = [setup_view.get_name() for setup_view in self.setup_views]
        
        self.class_names = ("CLASS 0", "CLASS 1", "CLASS 2")
        view_nums = (0, 0, 1)
        
        for i in range(3):
            class_name = self.class_names[i]
            view_num = view_nums[i]
            configuration_class_gui = self.configuration_class(x=10, y=10, view=self.configuration_views[view_num])
            configuration_class_gui.set_name(class_name)
             
            setup_class_gui = self.setup_class(configuration_class_gui, x=10*i, y=10*i, view=self.setup_views[view_num])
            setup_class_gui.set_name(f"{class_name} INSTANCE 0")
            
            if i == 0:
                self.setup_class_gui = setup_class_gui
                self.linked_setup_class(setup_class_gui, x=20, y=20, view=self.setup_views[view_num+2])
                
                for j in range(2):
                    configuration_attribute_gui = self.attribute(configuration_class_gui)
                    configuration_attribute_gui.set_name(f"{class_name} ATTRIBUTE {j}")
                    
                for j, setup_attribute_gui in enumerate(setup_class_gui.get_setup_attributes_gui()):
                    setup_attribute_gui.get_setup_attribute().set_value(convert_string_to_value(f"VALUE {j}"))
                    
                setup_class_gui_1 = self.setup_class(configuration_class_gui, x=20, y=20, view=self.setup_views[view_num])
                setup_class_gui_1.set_name(f"{class_name} INSTANCE 1")
                
                setup_connection(setup_class_gui, "RIGHT", setup_class_gui_1, "LEFT")
                
                setup_class_gui_2 = self.setup_class(configuration_class_gui, x=30, y=30, view=self.setup_views[view_num+1])
                setup_class_gui_2.set_name(f"{class_name} INSTANCE 2")
                
    def elements_are_equal(self, tuple1, tuple2):
        self.assertEqual(tuple(sorted(tuple1)), tuple(sorted(tuple2)))
        
    def test_get_current_view_name(self):
        for view in self.model.get_configuration_views() + self.model.get_setup_views():
            self.model.change_view(view)
            self.assertEqual(self.script_if.get_current_view_name(), view.get_name())
            
    def test_get_class_type_names(self):
        for view_name, names in zip([None] + self.setup_view_names, [self.class_names, ("CLASS 0", "CLASS 1"), ("CLASS 0", "CLASS 2"), ("CLASS 0",), ()]):
            self.elements_are_equal(self.script_if.get_class_type_names(view_name), names)
            
    def test_get_class_instance_names(self):
        for view_name, names in zip([None] + self.setup_view_names, [("CLASS 0 INSTANCE 0", "CLASS 0 INSTANCE 1", "CLASS 0 INSTANCE 2"), ("CLASS 0 INSTANCE 0", "CLASS 0 INSTANCE 1"), ("CLASS 0 INSTANCE 2",), ("CLASS 0 INSTANCE 0",), ()]):
            self.elements_are_equal(self.script_if.get_class_instance_names("CLASS 0", view_name), names)
            
    def test_get_attribute_names(self):
        for class_name, names in zip(["CLASS 0", "CLASS 1"], [("CLASS 0 ATTRIBUTE 0", "CLASS 0 ATTRIBUTE 1"), ()]):
            self.elements_are_equal(self.script_if.get_attribute_names(class_name), names)
            
    def test_get_input_class_names(self):
        for class_instance_name, names in zip(["CLASS 0 INSTANCE 0", "CLASS 0 INSTANCE 1", "CLASS 0 INSTANCE 2"], [(), (("CLASS 0", "CLASS 0 INSTANCE 0"),), ()]):
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name), names)
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_type="CLASS 0"), names)
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_type="CLASS 0", input_class_instance=("CLASS 0 INSTANCE 0")), names)
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_instance="CLASS 0 INSTANCE 0"), names)
            
        for class_instance_name in ["CLASS 0 INSTANCE 0", "CLASS 0 INSTANCE 1", "CLASS 0 INSTANCE 2"]:
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 1", class_instance_name), ())
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_type="CLASS 1"), ())
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_type="CLASS 0", input_class_instance=("CLASS 0 INSTANCE 1")), ())
            self.elements_are_equal(self.script_if.get_input_class_names("CLASS 0", class_instance_name, input_class_instance="CLASS 0 INSTANCE 1"), names)
            
    def test_get_attribute_values(self):
        self.elements_are_equal(self.script_if.get_attribute_values("CLASS 0", "CLASS 0 INSTANCE 0", "CLASS 0 ATTRIBUTE 0"), (("VALUE 0",),))
        self.elements_are_equal(self.script_if.get_attribute_values("CLASS 0", "CLASS 0 INSTANCE 0", "CLASS 0 ATTRIBUTE 1"), (("VALUE 1",),))
        self.elements_are_equal(self.script_if.get_attribute_values("CLASS 0", "CLASS 0 INSTANCE 0", None), (("VALUE 0",), ("VALUE 1",)))
        self.elements_are_equal(self.script_if.get_attribute_values("CLASS 1", None, None), (()))
        
    def test_convert_value_to_string(self):
        self.assertEqual(self.script_if.convert_value_to_string((1, 2, 3)), "1 / 2 / 3")
        
    def check_attribute_values(self, setup_class_gui, values):
        for setup_attribute_gui, value in zip(setup_class_gui.get_setup_attributes_gui(), values):
            self.assertEqual(setup_attribute_gui.get_setup_attribute().get_current_value(), value)
            
    def test_override_attribute_values(self):
        self.script_if.override_attribute_values("OVERRIDE", "CLASS 0")
        self.check_attribute_values(self.setup_class_gui, (("OVERRIDE",), ("OVERRIDE",)))
        
        self.script_if.reset_override_attribute_values(class_type="CLASS 0", class_instance="CLASS 0 INSTANCE 0", attribute="CLASS 0 ATTRIBUTE 0")
        self.check_attribute_values(self.setup_class_gui, (("VALUE 0",), ("OVERRIDE",)))
        
        self.script_if.reset_override_attribute_values(class_type="CLASS 0", class_instance="CLASS 0 INSTANCE 0")
        self.check_attribute_values(self.setup_class_gui, (("VALUE 0",), ("VALUE 1",)))
        
        self.script_if.override_attribute_values("OVERRIDE", "CLASS 0", class_instance="CLASS 0 INSTANCE 0", attribute="CLASS 0 ATTRIBUTE 0")
        self.check_attribute_values(self.setup_class_gui, (("OVERRIDE",), ("VALUE 1",)))
        
        self.script_if.override_attribute_values("OVERRIDE", "CLASS 0", class_instance="CLASS 0 INSTANCE 0")
        self.check_attribute_values(self.setup_class_gui, (("OVERRIDE",), ("OVERRIDE",)))
        
        self.script_if.reset_override_attribute_values()
        self.check_attribute_values(self.setup_class_gui, (("VALUE 0",), ("VALUE 1",)))
        
if __name__ == "__main__":
    input("Warning: Risk of flashing lights as GUI windows are rapidly created and destroyed. Press ENTER to proceed: ")
    unittest.main()
