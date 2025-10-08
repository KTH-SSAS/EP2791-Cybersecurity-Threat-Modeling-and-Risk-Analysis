# Code structure

Found in the `configuration` directory are all GUI blocks used strictly in `Configuration Views` and in the `setup` directory those strictly in `Setup Views`. Meanwhile, the `connection` directory contains all classes relevant to `Connections` between blocks in both `View` types.

The files within this directory contain the following:

1. `buttons_gui.py`: All classes relevant for the different buttons that one can press throughout the GUI
2. `circle_indicator_gui.py`: Class for circular indicators that appear in the GUI, such as those indicating linked copies, scalar/offsets in `Configuration Views`, or script markers
3. `general_gui.py`: General GUI block classes that are used by both `View` types
4. `pressable_entry.py`: Custom class for the manual entry fields that are used throughout the GUI, where an Entry that can be typed in appears by pressing its label/rectangle
