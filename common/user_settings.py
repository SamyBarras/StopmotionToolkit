# ===========================================================
#                   STANDARD USERS PARAMETERS
# ===========================================================
FPS = 12 # framerate for your animations
PREVIEW_DURATION = 2 # duration in seconds for the preview
ONIONSKIN = 3 # nth of frames to show in onion skin

# file and directories naming conventions
PROJECT_NAME = "" # string added to project directory (YYYYMMDD_PROJECT_NAME)
TAKE_NAME = "take" # template name for takes, will be saved : "projectDir / take_00 / take00_[######].png"

# output
EXPORT_ANIM = True # "True" will export latest take to a .mp4 movie file in take's directory when closing app


# ===========================================================
#                   CONFIG PARAMETERS (MORE)
# (do not change these if you're not confident with the app)
# ===========================================================
# WEBCAM DEBUG
# change this if needed of a specific webcamera (set to True)
# 0 will be built-in camera OR first plugged camera
forceCamera = False
camIndex = 0
# CAMERA CODEC
# change this if your camera do not give proper resolution
camera_codec = 'MJPG' # H264
#  DEBUG / INFOS
show_console = False
# shutdown the computer @ end (only for raspberry pi)
shutdown_rpi = True
