# Code structure

Throughout the code, `Configuration Views` refer to `Metamodel Views` and `Setup Views` to `System Views`.

Found in the `blocks_calculation` directory are the `Class` and `Attribute` classes used to track relations between blocks and calculate any values. Meanwhile, the `blocks_gui` directory contain the corresponding GUI versions, wrapping the aforementioned ones. The `Model` class tracks and manages the main objects of the program, where the classes in the `views` directory tracks any `View` specific objects and draws the corrsponding GUI. When editing a block, the window that pops up is managed by the `Options` class. Furthermore, the `ScriptInterface` class defines the API used by scripts to interact with the program.

Found inside `helper_functions_general.py` are general helper functions used throughout the code of the program.

The figure below shows an overview of the most central classes throughout the code and their relations to each other.

![Image of a configuration view for the Yacraf metamodel](../img/classes.svg)
