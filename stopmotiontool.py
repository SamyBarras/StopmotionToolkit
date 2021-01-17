#!/usr/bin/python3
# customs imports
import sys, os, time, collections, re, datetime, subprocess, logging
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

# logging     https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3
class MyFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.INFO:
            self._style._fmt = "%(message)s"
        else:
            color = {
                logging.WARNING: 33,
                logging.ERROR: 31,
                logging.FATAL: 31,
                logging.DEBUG: 36
            }.get(record.levelno, 0)
            self._style._fmt = f"\033[{color}m%(levelname)s\033[0m: %(message)s"
        return super().format(record)

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
#handler = logging.StreamHandler()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(MyFormatter())
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def detectOS ():
    ostype = None
    logging.debug("os : %s - %s ", os.uname()[1], os.uname()[4])
    if (os.uname()[4].startswith("arm")) : # rpi
        ostype = 0
    elif (os.uname()[4].startswith("x86_64")) : # osx
        ostype = 1
    else :
        ostype = 2
        # throw error --> can't run on this machine (OS issue)
        logging.critical("OS not recognized -- please play with Rpi or OSX !")
        sys.exit(2)
    return ostype

def setupDir(_t):
    logging.info("==== setup working dir =====")
    partitions = psutil.disk_partitions()
    drivesize = 0
    regEx = '\A' + constants.drives[ostype]
    found = False
    
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
        logging.warning("External drive not found ! Project will be stored in Desktop...")
        if ostype == 2 :
            # windows
            drivepath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        else :
            # 0 and 1 are OSX and Linux systems
            drivepath = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

    if not user_settings.PROJECT_NAME : # project_name custom paramater is not set... we use time to make unik name
        dirname = datetime.datetime.now().strftime('%Y%m%d') #_%H%M%S')
    else :
        # desktop / PROJECT_NAME / take
        dirname = datetime.datetime.now().strftime('%Y%m%d') + "_" + user_settings.PROJECT_NAME
    
    #workingdir = os.path.join(drivepath, "stopmotion", dirname, _t)
    #datetime.datetime.now().strftime('%Y_%m_%d/%H%M%S')) # use time to name dir
    # # + "_" + user_settings.project_name)
    projectdir = os.path.join(drivepath, "stopmotion", dirname)
    if not os.path.exists(projectdir):
        takeDir = user_settings.TAKE_NAME + "_" + str(_t).zfill(2)
    else :
        # project already exists -> we create a new take
        lasttakedir = os.path.basename(max([os.path.join(projectdir, d) for d in os.listdir(projectdir)], key=os.path.getmtime)).split("_")
        if lasttakedir[0] == user_settings.TAKE_NAME :
            # same take name (should always be)
            lasttakenum = int(lasttakedir[-1])
            _t = lasttakenum+1
            takeDir = user_settings.TAKE_NAME + "_" + str(_t).zfill(2)
    
    workingdir = os.path.join(projectdir, takeDir)
    if not os.path.exists(workingdir) :
        os.makedirs(workingdir)

    HQFilesDir = os.path.join(workingdir,"HQ")
    if not os.path.exists(HQFilesDir) : 
        os.makedirs(HQFilesDir)

    if os.path.exists(workingdir) and os.path.exists(HQFilesDir):
        logging.info("Working directory : %s", workingdir)
        return workingdir, _t
    else :
        # throw error --> can't setup working dir
        logging.error("error while creating working dir")
        quit()

def getCameraDevice():
    res_w = 0
    arr = []
    logging.info("==== setup camera =====")
    if user_settings.forceCamera is True :
        # camera to use is defined by user settings
        cap = cam.streamConstructor (camIndex, ostype, user_settings.camera_codec)
        if cap.read()[0]:
            arr = [camIndex, cap.get(3), cap.get(4)]
            cap.release()
            return arr
        else :
            logging.error("Camera not found !")
            quit()
    else :
        id = -1
        r = (0, 2)
        for i in range(r[0], r[1]):
            tmp = None
            try :
                cap = cam.streamConstructor (i, ostype)
            except (RuntimeError, TypeError, NameError, ValueError):
                break
            else :    
                if cap.read()[0]:
                    tmp_w = cap.get(3)
                    tmp_h = cap.get(4)
                    cap.release()
                    tmp_cam = [i,tmp_w, tmp_h]
                    logging.debug("cam %s -> (%s,%s)",i, tmp_w, tmp_h)
                    if tmp_w > res_w :
                        res_w = tmp_w
                        arr = tmp_cam
                    id = i

        if id == -1 :
            # throw error here --> no camera found
            logging.error("Camera not found !")
            quit()
        else :
            logging.info("Camera id : %s (%s , %s)", arr[0], arr[1], arr[2])

        return arr


def getMonitor ():
    logging.info("==== setup output display =====")
    if ostype == 0 :
        #raspberry pi
        drivers = ('directfb', 'fbcon', 'svgalib')
        found = False
        for driver in drivers:
            logging.debug("Trying \'%s\'", driver)
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                logging.debug('%s -> failed', driver)
                continue
            else :
                found = True
                break
        if not found:
            #raise Exception('No suitable video driver found.')
            return False, 0, 0
        else :
            logging.info("Screen resolution : %s - %s", pygame.display.Info().current_w, pygame.display.Info().current_h)
            return True, pygame.display.Info().current_w, pygame.display.Info().current_h
    else :
        logging.info("Screen resolution : %s - %s", pygame.display.Info().current_w, pygame.display.Info().current_h)
        return True, pygame.display.Info().current_w, pygame.display.Info().current_h


def defineDisplaySize(camsize, screen_w, screen_h) :
    cam_w = camsize[0]
    cam_h = camsize[1]
    if ostype == 0 : # rpi
        if cam_w > screen_w :
            if screen_w > 1024 :
                return (int(screen_w/2), int(screen_h/2))
            else :
                return (screen_w, screen_h)
        else :
            if cam_w > 1024 :
                return (int(cam_w/2), int(cam_h/2))
            else :
                return (cam_w, cam_h)
    else :
        # not rpi, no speed issue
        if cam_w > screen_w :
            return (int(screen_w), int(screen_h))
        else :
            return (cam_w, cam_h)

def displayAnimation():
    global IS_PLAYING
    if outputdisplay is True :
        while IS_PLAYING :
            for i in frames : # frames is pygame.surface array            
                screen.blit(i, (0, 0))
                pygame.display.flip()
                time.sleep(1/user_settings.FPS) # to keep framerate
            IS_PLAYING=False

def displayCameraStream(buffer):
    # display video stream
    #print(buffer)
    if buffer is not None :
        screen.blit(image_processing.rescaleToDisplay(buffer, SCREEN_SIZE), (0, 0))

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
        screen.blit(infos_take,(25,25))
        screen.blit(infos_cam, (25,50))
        screen.blit(infos_fps, (25,75))
    
    pygame.display.flip()

def ledBlink ():
    global IS_SHOOTING, IS_PLAYING
    while True :
        if IS_SHOOTING is True:
            logging.debug("is shooting")
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
            time.sleep(0.2)
        elif IS_PLAYING is True :
            logging.debug("is playing")
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
        else :
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)

def capture() :
    global IS_SHOOTING, take
    IS_SHOOTING = True

    if outputdisplay is True :
        myCamera.capturedisp(SCREEN_SIZE, workingdir, take)
    else :
        myCamera.capture(workingdir, take)
    #
    if myCamera.lastframe is not None :
        frames.append(myCamera.lastframe)
    else :
        logging.error("Error while shooting : last frame is empty !")

    IS_SHOOTING = False

# GPIO FUNCTIONS
def setupGpio():
    logging.info("==== etup GPIO =====")
    GPIO.setmode(GPIO.BCM)
    # play button
    GPIO.setup(constants.PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.PLAY_BUTTON, GPIO.FALLING)
    GPIO.add_event_callback(constants.PLAY_BUTTON, actionButtn)
    # shot button
    GPIO.setup(constants.SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(constants.SHOT_BUTTON, GPIO.FALLING)
    GPIO.add_event_callback(constants.SHOT_BUTTON,actionButtn)
    # led
    GPIO.setup(constants.OUTPUT_LED, GPIO.OUT) # SHOT_LED
    logging.info("GPIO pins are ready ! ")

def actionButtn(inputbttn):
    global IS_PLAYING, IS_SHOOTING, finish
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    --> need to recode this to allow combined buttons
    '''
    if inputbttn == constants.SHOT_BUTTON and GPIO.input(inputbttn) == 0 :
        #start counting pressed time
        pressed_time=time.monotonic()
        while GPIO.input(inputbttn) == 0 :
            pass
        pressed_time=time.monotonic()-pressed_time
        if pressed_time < constants.PRESSINGTIME :
            logging.debug("short press -> capture")
            capture()
            return 1
        elif pressed_time >= constants.PRESSINGTIME :
            logging.debug("long press --> new take")
            newTake()
            return 0

    elif inputbttn == constants.PLAY_BUTTON and GPIO.input(inputbttn) == 0 :
        #start counting pressed time
        pressed_time=time.monotonic()
        while GPIO.input(inputbttn) == 0 :
            pass
        pressed_time=time.monotonic()-pressed_time
        if pressed_time < constants.PRESSINGTIME :
            if outputdisplay is True :
                IS_PLAYING = True
                logging.debug("play anim")
            else :
                logging.debug("no display to show animation")
            return 2
        elif pressed_time >= constants.PRESSINGTIME :
            logging.debug("long press --> shut down")
            finish = True
            return 0
    
    else :
        return None # not needed, just for clarity
    
    # alternative ---> detect if both buttons are pressed together
    # if inputbttn == constants.SHOT_BUTTON and GPIO.input(inputbttn) == 0:
    #     if GPIO.input(constants.PLAY_BUTTON) == 0 :
    #         print("two buttons pressed together !")
    #         return 0
    #     else :
    #         print("capture")
    #         capture()
    #         return 1
    # elif inputbttn == constants.PLAY_BUTTON and GPIO.input(inputbttn) == 0:
    #     if GPIO.input(constants.SHOT_BUTTON) == 0 :
    #         print("two buttons pressed together !")
    #         return 0
    #     else :
    #         if outputdisplay is True :
    #             IS_PLAYING = True
    #             print("play anim")
    #         else :
    #             print("no display to sho animation")
    #         return 2
    # else :
    #     return None # not needed, just for clarity

def newTake () :
    # called each time we start a new shot (takes)
    global frames, workingdir, myCamera, takenum, take
    # setup take and new dir
    workingdir, takenum = setupDir(takenum) # path of working dir
    # reset everything
    take = user_settings.TAKE_NAME + str(takenum).zfill(2)
    frames = collections.deque(maxlen=maxFramesBuffer)
    myCamera.lastframe = None
    myCamera.frameCount = 0
    # update takenum for next time
    takenum += 1


if __name__== "__main__":
    # global var setup
    frames = None # framebuffer for animation
    IS_PLAYING = False
    IS_SHOOTING = False
    SCREEN_SIZE = (0,0)
    screen = None
    workingdir = None
    takenum = 0
    take = None
    # pygame
    pygame.init()
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    # setup
    ostype = detectOS()                 # int (0:RPi, 1:OSX, 2:WIN)

    # frames buffer for animation preview
    # --> ring buffer # duration in seconds for animation preview (last X seconds)
    maxFramesBuffer = int(user_settings.PREVIEW_DURATION*user_settings.FPS)

    # GPIO initialisation
    if ostype == 0 :
        #import common.inputs as inputs
        import RPi.GPIO as GPIO
        #inputs.setupGpio()
        setupGpio()
        leds = Thread(target=ledBlink, daemon=True)
        leds.start()
    # camera initialisation
    video_device = getCameraDevice()    # array [camera_id, width, height]
    myCamera = cam.cam(video_device, ostype, user_settings.camera_codec) # video_device, os, codec, buffer
    myCamera.start() # threaded    
    # ==== new project ====
    # ==== new take =====
    newTake ()
    # ============ output last setup
    # detect output display
    outputdisplay, w, h = getMonitor () # boolean, width, height
    # not in headless mode
    if outputdisplay is True:
        SCREEN_SIZE = defineDisplaySize(myCamera.size, w, h)
        logging.info("Window size : %s", SCREEN_SIZE)
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % image_processing.centerScreen((w, h), SCREEN_SIZE)
        screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN) # , pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE #  pygame.FULLSCREEN
        
        # font and info elements
        pygame.font.init()
        myfont = pygame.font.SysFont('Helvetica', 15)
        infos_take = myfont.render("Take : " + os.path.basename(os.path.dirname(workingdir)) + "/" + os.path.basename(workingdir), False, (250, 0, 0))
        infos_cam = myfont.render("Camera résolution : " + ' '.join(str(x) for x in myCamera.size), False, (250, 0, 0))
        infos_fps = myfont.render("Animation framerate : " + str(user_settings.FPS), False, (250, 0, 0))
        pygame.display.set_caption('stopmotion project')
    else :
        logging.warning("Stopmotion tool run in headless mode !")
    
    # ============ ready
    logging.info("==== ready to animate :) =====")
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
                    if event.key == K_n :
                        newTake()
                    if event.key == K_q :
                        quit()
                    if event.key == K_ESCAPE:
                        finish = True

def quit ():
    myCamera.release()
    pygame.quit()
    if ostype == 0 :
        GPIO.cleanup()
    # export animation before quitting totally
    if user_settings.EXPORT_ANIM is True :
        image_processing.compileAnimation(workingdir, frames, take)
    # finally, we quit !

quit()

if ostype == 0 and user_settings.shutdown_rpi is True:
    # turn off RPi at end
    subprocess.call("sudo shutdown -h now", shell=True) # turn off computer !