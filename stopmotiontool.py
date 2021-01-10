#!/usr/bin/python3
# customs imports
import sys, os, time, collections, re, datetime
# dependencies
import pygame
import pygame.camera
from pygame.locals import *
import cv2
import psutil
import numpy as np
from threading import Thread, Timer
import pickle
# custom imports
from common import *


def detectOS ():
    ostype = None
    print("os : ", os.uname()[1], os.uname()[4])
    if (os.uname()[4].startswith("arm")) : # rpi
        ostype = 0
    elif (os.uname()[4].startswith("x86_64")) : # osx
        ostype = 1
    else :
        ostype = 2
        # throw error --> can't run on this machine (OS issue)
        print("os not recognized -- please play with Rpi or OSX !")
        sys.exit(2)
    return ostype


def setupDir():
    print("==== setup working dir =====")
    partitions = psutil.disk_partitions()
    drivesize = 0
    regEx = '\A' + constants.drives[ostype]
    found = False
    #print(drives[ostype])
    for p in partitions :
        drivepath = p.mountpoint
        psize = psutil.disk_usage(p.mountpoint).free
        tmp = re.search(regEx, p.mountpoint)
        # search for external drive according to OS "drivepath"
        # filter size of external drives to keep the one which has more free space
        if tmp is not None and  psize > drivesize:
            drivepath = p.mountpoint
            drivesize = psize
            found = True
    if found is False :
        print("Working directory will be saved in /Desktop")
        if ostype == 2 :
            # windows
            drivepath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        else :
            # 0 and 1 are OSX and Linux systems
            drivepath = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    
    workingdir = os.path.join(drivepath, "stopmotion", datetime.datetime.now().strftime('%Y_%m_%d/%H%M%S')+"_" + user_settings.project_name)
    if not os.path.exists(workingdir):
        os.makedirs(workingdir)
    
    HQFilesDir = os.path.join(workingdir,"HQ")
    if not os.path.exists(HQFilesDir) : 
        os.makedirs(HQFilesDir)

    if os.path.exists(workingdir) and os.path.exists(HQFilesDir):
        print(workingdir)
        return workingdir
    else :
        # throw error --> can't setup working dir
        print("error while creating working dir")
        quit()

def getCameraDevice():
    res_w = 0
    arr = []
    print("==== setup camera =====")
    if user_settings.forceCamera is True :
        # camera to use is defined by user settings
        cap = cam.streamConstructor (camIndex, ostype, user_settings.camera_codec)
        if cap.read()[0]:
            arr = [camIndex, cap.get(3), cap.get(4)]
            cap.release()
            return arr
        else :
            print("no camera found !")
            quit()
    else :
        id = -1
        r = (0, 4)
        for i in range(r[0], r[1]):
            tmp = None
            cap = cam.streamConstructor (i, ostype)
            if cap.read()[0]:
                tmp_w = cap.get(3)
                tmp_h = cap.get(4)
                cap.release()
                tmp_cam = [i,tmp_w, tmp_h]
                print(i , tmp_w, tmp_h)
                if tmp_w > res_w :
                    res_w = tmp_w
                    arr = tmp_cam
                id = i
                
        if id == -1 :
            # throw error here --> no camera found
            print("no camera found !")
            quit()
        return arr


def getMonitor ():
    print("==== setup output display =====")
    if ostype == 0 :
        #raspberry pi
        drivers = ('directfb', 'fbcon', 'svgalib')
        found = False
        for driver in drivers:
            print("Trying \'" + driver + "\'")
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER',driver)
            try:
                pygame.display.init()
            except pygame.error:
                print('failed')
                continue
            found = True
            break
        if not found:
            #raise Exception('No suitable video driver found.')
            return False, 0, 0
        else :
            return True, pygame.display.Info().current_w, pygame.display.Info().current_h
    else :
        return True, pygame.display.Info().current_w, pygame.display.Info().current_h
            
def displayAnimation():
    global IS_PLAYING
    while IS_PLAYING :
        for i in frames : # frames is pygame.surface array            
            screen.blit(i, (0, 0))
            pygame.display.flip()
            time.sleep(1/user_settings.FPS) # to keep framerate
        IS_PLAYING=False

def displayCameraStream(buffer):
    # display video stream
    if buffer is not None:
        screen.blit(image_processing.rescaleToDisplay(buffer, screen), (0, 0))

    # display onion skin
    if user_settings.ONIONSKIN >= 1 :
        # if onion skin set, we show previous frames with less opacity
        f = user_settings.ONIONSKIN
        while f > 0 :
            if len(frames) >= f :
                alpha = 255/int(f+1)
                frame = frames[-f] # frames is pygame.surface array
                img = frame.copy()
                img.set_alpha(alpha)
                screen.blit(img, (0, 0))
            else :
                pass
            f -= 1
    
    if user_settings.show_console is True :
        screen.blit(textsurface,(25,25))
        screen.blit(fpsconsole, (25,60))
    
    pygame.display.flip()

def ledBlink ():
    global IS_SHOOTING, IS_PLAYING
    while True :
        if IS_SHOOTING is True:
            print("is shooting")
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
            time.sleep(0.2)
        elif IS_PLAYING is True :
            print("is playing")
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
        else :
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)

def capture() :
    global IS_SHOOTING, frames, myCamera
    IS_SHOOTING = True
    myCamera.capture(screen, workingdir, user_settings.take_name)
    frames.append(myCamera.lastframe)
    IS_SHOOTING = False

# GPIO FUNCTIONS
def setupGpio():
    GPIO.setmode(GPIO.BCM)
    # play button
    GPIO.setup(constants.PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.PLAY_BUTTON, GPIO.FALLING)
    GPIO.add_event_callback(constants.PLAY_BUTTON, actionButtn,"play")
    # shot button
    GPIO.setup(constants.SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.SHOT_BUTTON, GPIO.FALLING)
    GPIO.add_event_callback(constants.SHOT_BUTTON,actionButtn,"take")
    # led
    GPIO.setup(constants.OUTPUT_LED, GPIO.OUT) # SHOT_LED
    print("==== setup GPIO =====")

def actionButtn(inputbttn,i):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    if inputbttn == constants.SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constants.PLAY_BUTTON) == 0 :
            print("two buttons pressed together !")
            return 0
        else :
            print(i)
            capture()
            return 1 #capture()
    elif inputbttn == constants.PLAY_BUTTON and GPIO.input(inputbttn) == 0:
        if GPIO.input(constants.SHOT_BUTTON) == 0 :
            print("two buttons pressed together !")
            return 0
        else :
            print(i)
            #displayAnimation()
            return 2
    else :
        return None # not needed, just for clarity

if __name__== "__main__":
    global IS_SHOOTING, IS_PLAYING, frames, myCamera
    # pygame
    pygame.init()
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    # setup
    ostype = detectOS()                 # int (0:RPi, 1:OSX, 2:WIN)
    workingdir = setupDir()             # path of working dir
    outputdisplay, w, h = getMonitor () # boolean, width, height
    # frames buffer for animation preview
    # --> ring buffer # duration in seconds for animation preview (last X seconds)
    maxFramesBuffer = int(user_settings.PREVIEW_DURATION*user_settings.FPS)
    frames = collections.deque(maxlen=maxFramesBuffer)
    # GPIO initialisation
    if ostype == 0 :
        import common.inputs as inputs
        inputs.setupGpio()
        leds = Thread(target=ledBlink, daemon=True)
        leds.start()
    # camera initialisation
    video_device = getCameraDevice()    # array [camera_id, width, height]
    myCamera = cam.cam(video_device, ostype, user_settings.camera_codec) # video_device, os, codec, buffer
    myCamera.start() # threaded
    print(myCamera)

    # not in headless mode
    if outputdisplay is True:
        screen = pygame.display.set_mode((w,h), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE ) #pygame.RESIZABLE pygame.FULLSCREEN
        # font and info elements
        pygame.font.init()
        myfont = pygame.font.SysFont('Helvetica', 15)
        textsurface = myfont.render("Camera résolution : " + ' '.join(str(x) for x in myCamera.size), False, (250, 0, 0))
        pygame.display.set_caption('stopmotion project')
    else :
        print("==> stopmotion tool run in headless mode !")

        
    # main loop
    finish = False
    IS_PLAYING = False
    while not finish:
        # function which do not need output display
        clock.tick(50)
        frameBuffer = myCamera.read()
        # then function needed only if output display is available (we have a screen)
        if outputdisplay is True :
            fpsconsole = myfont.render(str(clock.get_fps()), False, (250, 0, 0))
            # switch between animation preview and onion skin view
            if IS_PLAYING is True :
                displayAnimation()
            else :
                displayCameraStream(frameBuffer)
            
            # pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
                if event.type == KEYDOWN :
                    if event.key == K_t :
                        capture()
                    if event.key == K_p :
                        IS_PLAYING = True
                    if event.key == K_q or event.key == K_ESCAPE:
                        finish = True


def quit ():
    myCamera.release()
    pygame.quit()
    if ostype == 0 :
        GPIO.cleanup()
    # export animation before quitting totally
    image_processing.compileAnimation(workingdir, frames, user_settings.take_name)
    # finally, we quit !
    sys.exit()     

quit()