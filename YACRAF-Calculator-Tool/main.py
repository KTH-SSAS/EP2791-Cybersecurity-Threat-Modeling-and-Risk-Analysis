import tkinter as tk
import sys
import os

sys.path.append("config")
from program_paths import *

# Set up the paths for modules that are imported elsewhere in the program
for path in IMPORT_PATHS:
    sys.path.append(path)
    
from settings import Settings

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <save_name>")
        
        saves_path = os.path.join(BASE_PATH, SAVES_DIRECTORY)
        print(f"Existing saves: {[name for name in os.listdir(saves_path) if os.path.isdir(os.path.join(saves_path, name))]}")
        return
        
    save_name = sys.argv[1]
    
    settings = Settings(save_name)
    settings.save()
    
    from model import Model
    
    root = tk.Tk()
    model = Model(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()

