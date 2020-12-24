import common.constants

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SHOT_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PLAY_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(OUTPUT_LED, GPIO.OUT) # SHOT_LED

def actionButtn(inputbttn):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    if inputbttn == SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(PLAY_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            myCamera.captureFrame()
    elif inputbttn == PLAY_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(SHOT_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            playBufferAnimation()
    else :
        return # not needed, just for clarity

def ledBlink ():
    global IS_SHOOTING, IS_PLAYING
    while True :
        if IS_SHOOTING is True:
            GPIO.output(OUTPUT_LED,GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(OUTPUT_LED,GPIO.LOW)
            time.sleep(0.2)
        elif IS_PLAYING is True :
            GPIO.output(OUTPUT_LED,GPIO.LOW)
        else :
            GPIO.output(OUTPUT_LED,GPIO.HIGH)