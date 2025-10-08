# Code structure

Found in `connection_gui.py` is the main class for managing `Connections` (between `Attributes` and `Inputs` in `Configuration View` and between the triangle blocks in `Setup Views`). The connection between the triangle blocks used in `Setup Views` is found in `connection_with_blocks_gui.py`, inheriting from the class in `connection_gui.py`. Any blocks related to `Connections`, such as the corner blocks, triangle blocks, or block for input scalars in `Setup Views` are found in `connection_blocks_gui.py`.
