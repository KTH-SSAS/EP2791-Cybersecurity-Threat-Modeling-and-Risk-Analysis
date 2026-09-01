import os

from program_paths import CONFIG_PATH

SETTINGS_FILE = os.path.join(CONFIG_PATH, "settings.txt")

class Settings:
    """
    Manages general settings that are saved to file
    """
    def __init__(self, save_name=None):
        self.__canvas_width = 800
        self.__canvas_height = 600
        self.__num_samples = 10000
        self.__percentile_range = 5
        self.__pos_calculation_mode = "ratio"
        self.__warn_duplicate_names = True
        self.__save_name = save_name
        
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file_settings:
                for line in file_settings:
                    variable, value = [config.strip() for config in line.split("=")]
                    
                    if variable == "CANVAS_WIDTH":
                        self.__canvas_width = int(value)
                        
                    elif variable == "CANVAS_HEIGHT":
                        self.__canvas_height = int(value)
                        
                    elif variable == "NUM_SAMPLES":
                        self.set_num_samples(value) # Number of Monte Carlo samples for distribution calculations

                    elif variable == "PERCENTILE_RANGE":
                        self.set_percentile_range(value)

                    elif variable == "POS_CALCULATION_MODE":
                        self.set_pos_calculation_mode(value)
                        
                    elif variable == "WARN_DUPLICATE_NAMES":
                        self.__warn_duplicate_names = value == "True"
                        
                    elif variable == "SAVE_NAME":
                        if save_name == None:
                            self.__save_name = value
                            
    def get_canvas_width(self):
        return self.__canvas_width
        
    def get_canvas_height(self):
        return self.__canvas_height
        
    def set_canvas_size(self, width, height):
        self.__canvas_width = width
        self.__canvas_height = height
        
    def get_num_samples(self):
        return self.__num_samples
        
    def set_num_samples(self, num_samples):
        self.__num_samples = max(1, int(num_samples))

    def get_percentile_range(self):
        return self.__percentile_range

    def get_distribution_percentiles(self):
        lower_percentile = self.__percentile_range / 100
        return lower_percentile, 0.5, 1 - lower_percentile

    def set_percentile_range(self, percentile_range):
        percentile_range = int(percentile_range)
        self.__percentile_range = percentile_range if percentile_range in (0, 5) else 5

    def get_pos_calculation_mode(self):
        return self.__pos_calculation_mode

    def set_pos_calculation_mode(self, calculation_mode):
        calculation_mode = str(calculation_mode).strip().lower()
        self.__pos_calculation_mode = calculation_mode if calculation_mode in ("ratio", "distribution") else "ratio"
        
    def warns_duplicate_names(self):
        return self.__warn_duplicate_names
        
    def set_warn_duplicate_names(self, warn_duplicate_names):
        self.__warn_duplicate_names = warn_duplicate_names
        
    def get_save_name(self):
        return self.__save_name
        
    def save(self):
        with open(SETTINGS_FILE, "w") as file_settings:
            for variable, value in [("CANVAS_WIDTH", self.__canvas_width), \
                                    ("CANVAS_HEIGHT", self.__canvas_height), \
                                    ("NUM_SAMPLES", self.__num_samples), \
                                    ("PERCENTILE_RANGE", self.__percentile_range), \
                                    ("POS_CALCULATION_MODE", self.__pos_calculation_mode), \
                                    ("WARN_DUPLICATE_NAMES", self.__warn_duplicate_names), \
                                    ("SAVE_NAME", self.__save_name)]:
                file_settings.write(f"{variable} = {value}\n")
