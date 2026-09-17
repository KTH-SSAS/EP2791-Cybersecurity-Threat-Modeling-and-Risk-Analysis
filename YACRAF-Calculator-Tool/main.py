import tkinter as tk
import sys
import os

sys.path.append("config")
from program_paths import *

# Set up the paths for modules that are imported elsewhere in the program
for path in IMPORT_PATHS:
    sys.path.append(path)
    
from settings import Settings

DEFAULT_SAVE_NAME = "example_distribution"


def get_save_name(arguments):
    """Return the requested save, using the distribution example by default."""
    if len(arguments) == 1:
        return DEFAULT_SAVE_NAME

    if len(arguments) == 2 and arguments[1] != "--list":
        return arguments[1]

    print(f"Usage: {arguments[0]} [<save_name> | --list]")

    saves_path = os.path.join(BASE_PATH, SAVES_DIRECTORY)
    save_names = sorted(name for name in os.listdir(saves_path)
                        if os.path.isdir(os.path.join(saves_path, name)))
    print(f"Existing saves: {save_names}")
    return None


def main():
    save_name = get_save_name(sys.argv)

    if save_name is None:
        return
    
    settings = Settings(save_name)
    settings.save()
    
    from model import Model
    
    root = tk.Tk()
    model = Model(root)

    # The default launch is an example rather than an editing workspace, so
    # show its system view immediately instead of the metamodel definition.
    if save_name == DEFAULT_SAVE_NAME and model.get_setup_views():
        model.change_view(model.get_setup_views()[0])

    root.mainloop()
    
if __name__ == "__main__":
    main()
