import .constants as constants
import RPi.GPIO as GPIO


def setupGpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(constants.SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.SHOT_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(constants.PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.PLAY_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(constants.OUTPUT_LED, GPIO.OUT) # SHOT_LED
    print("==== setup GPIO =====")

def actionButtn(inputbttn):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    print("gpio action")
    if inputbttn == constant.SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constant.PLAY_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            print("capture frame")
            capture()
    elif inputbttn == constant.PLAY_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constant.SHOT_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            print("show animation")
            displayAnimation()
    else :
        return # not needed, just for clarity



