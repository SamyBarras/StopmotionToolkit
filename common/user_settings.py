# ===========================================================
#                   STANDARD USERS PARAMETERS
# ===========================================================
# Project and takes setup
USEPROJECTFOLDER = False    # True will create a directory where to put takes, False will save takes into "stopmotion" folder
MAKEUNIKPROJECT = False     # Create numbered projects folders if existing
PROJECT_NAME = "PROJECT"    # default string used for project directory if none (empty string) set by user
TAKE_NAME = "anim"          # template name for takes, will be saved : "PROJECT / take_00 / take00_[######].png"

# animation setup
FPS = 12                    # framerate for your animations
PREVIEW_DURATION = 2        # duration in seconds for the previewSurface
ONIONSKIN = 3               # nth of frames to show in onion skin

# output
EXPORT_ANIM = True          # Set to True if you want to generate .mp4 file at end of each take


# ===========================================================
#                   CONFIG PARAMETERS (MORE)
# (do not change these if you're not confident with the app)
# ===========================================================
# WEBCAM DEBUG
# 
forceCamera = False         # Set to True if you want to force the use of a specific camera index
camIndex = 0                # Camera index used if "forceCamera" set to True

# ===========================================================
#                     EXTRA PARAMETERS
# (do not change these if you're not confident with the app)
# ===========================================================
# DEBUG / INFOS
show_console = False        # debug console
show_infos = True           # infos (take + project idrectory)
shutdown_rpi = False        # shutdown the RPi when closing the app
