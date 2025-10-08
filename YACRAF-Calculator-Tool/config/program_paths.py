import os

# Used program paths
CONFIG_PATH = os.path.dirname(__file__)
BASE_PATH = os.path.join(CONFIG_PATH, "..")

SOURCE_PATH = os.path.join(BASE_PATH, "src")

BLOCKS_CALCULATION_PATH = os.path.join(SOURCE_PATH, "blocks_calculation")
BLOCKS_CALCULATION_CONFIGURATION_PATH = os.path.join(BLOCKS_CALCULATION_PATH, "configuration")
BLOCKS_CALCULATION_SETUP_PATH = os.path.join(BLOCKS_CALCULATION_PATH, "setup")

BLOCKS_GUI_PATH = os.path.join(SOURCE_PATH, "blocks_gui")
BLOCKS_GUI_CONFIGURATION_PATH = os.path.join(BLOCKS_GUI_PATH, "configuration")
BLOCKS_GUI_SETUP_PATH = os.path.join(BLOCKS_GUI_PATH, "setup")
BLOCKS_GUI_CONNECTION_PATH = os.path.join(BLOCKS_GUI_PATH, "connection")

VIEW_PATH = os.path.join(SOURCE_PATH, "views")

IMPORT_PATHS = (SOURCE_PATH, \
                BLOCKS_CALCULATION_PATH, \
                BLOCKS_CALCULATION_CONFIGURATION_PATH, \
                BLOCKS_CALCULATION_SETUP_PATH, \
                BLOCKS_GUI_PATH, \
                BLOCKS_GUI_CONFIGURATION_PATH, \
                BLOCKS_GUI_SETUP_PATH, \
                BLOCKS_GUI_CONNECTION_PATH, \
                VIEW_PATH)

SAVES_DIRECTORY = "saves"
SCRIPTS_PATH = os.path.join(BASE_PATH, "scripts")
