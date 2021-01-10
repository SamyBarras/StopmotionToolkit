import common.constants as constants
import RPi.GPIO as GPIO


def setupGpio():
    GPIO.setmode(GPIO.BCM)
    # shot button
    GPIO.setup(constants.SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.SHOT_BUTTON, GPIO.FALLING, callback=actionButtn)
    # play button
    GPIO.setup(constants.PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.PLAY_BUTTON, GPIO.FALLING, callback=actionButtn)
    # led
    GPIO.setup(constants.OUTPUT_LED, GPIO.OUT) # SHOT_LED
    print("==== setup GPIO =====")

def actionButtn(inputbttn):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    print("gpio action")
    if inputbttn == constants.SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constants.PLAY_BUTTON) == 0 :
            print("two buttons pressed together !")
            return 0
        else :
            print("capture frame")
            return 1 #capture()
    elif inputbttn == constants.PLAY_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constants.SHOT_BUTTON) == 0 :
            print("two buttons pressed together !")
            return 0
        else :
            print("show animation")
            #displayAnimation()
            return 2
    else :
        return # not needed, just for clarity

def capture() :
    global IS_SHOOTING, frames, myCamera
    IS_SHOOTING = True
    myCamera.capture(screen, workingdir, user_settings.take_name)
    frames.append(myCamera.lastframe)
    IS_SHOOTING = False

