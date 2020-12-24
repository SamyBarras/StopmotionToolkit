import common.constants as constant


def actionButtn(inputbttn):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    if inputbttn == constant.SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constant.PLAY_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            myCamera.captureFrame()
    elif inputbttn == constant.PLAY_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constant.SHOT_BUTTON) == 0 :
            print("two buttons pressed together !")
        else :
            playBufferAnimation()
    else :
        return # not needed, just for clarity

