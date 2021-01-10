# GPIO Inputs (BCM) & OUTPUTS
PLAY_BUTTON = 16
SHOT_BUTTON = 20
OUTPUT_LED = 21
# OS specific variables
# [rpi,osx,windows]
drives = ["/media/pi","/Volumes",""]
# other global vars
global frames = None # framebuffer for animation
global IS_PLAYING = False
global IS_SHOOTING = False
global SCREEN_SIZE = (0,0)
