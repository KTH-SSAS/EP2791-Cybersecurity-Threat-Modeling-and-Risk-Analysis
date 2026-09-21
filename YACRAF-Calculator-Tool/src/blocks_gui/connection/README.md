# Code structure

Found in `connection_gui.py` is the main class for managing `Connections` (between `Attributes` and `Inputs` in `Configuration View` and between the triangle blocks in `Setup Views`). The connection between the triangle blocks used in `Setup Views` is found in `connection_with_blocks_gui.py`, inheriting from the class in `connection_gui.py`. Connection corner and triangle blocks are found in `connection_blocks_gui.py`. System-view connections pass values unchanged and do not have editable scalar multipliers.
