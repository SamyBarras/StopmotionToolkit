#!/usr/bin/python3
# customs imports
import sys, os, time, collections, re, datetime, subprocess
import log, logging
from colorlog import ColoredFormatter
# dependencies
import pygame
import pygame.camera
from pygame.locals import *
import cv2
import psutil
import numpy as np
from threading import Thread, Timer
# custom imports
from common import *

# logging setup
mylog = logging.getLogger('pythonConfig')
#logFile = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop', 'stopmo.log')
logFile = os.path.join(os.path.dirname(__file__),'stopmo.log')
# append to log file if same day, or start from clean file
if not os.path.exists(logFile) or log.is_file_older_than_x_days(logFile) :
    fh = logging.FileHandler(logFile, mode='w')
else :
    fh = logging.FileHandler(logFile, mode='w')
fh.setLevel(log.LOG_LEVEL)
fh.setFormatter(log.CustomFormatter())
mylog.addHandler(fh)

def detectOS ():
    ostype = None
    #print(sys.platform) alternative, will output : linux / darwin (osx) / win
    mylog.debug("os : %s - %s " %(os.uname()[1], os.uname()[4]))
    if (os.uname()[4].startswith("arm")) : # rpi
        ostype = 0
    elif (os.uname()[4].startswith("x86_64")) : # osx
        ostype = 1
    else :
        ostype = 2
        # throw error --> can't run on this machine (OS issue)
        mylog.critical("OS not recognized -- please play with Rpi or OSX !")
        sys.exit(2)
    return ostype

def setupProjectDir():
    '''
        This way of checking external drives needs startX to work
    '''
    mylog.info("==== setup project dir =====")
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
            mylog.debug("External drive found -> %s -> %s" %(drivepath, drivesize))
            found = True
    if found is False :
        mylog.warning("External drive not found ! Project will be stored in Desktop...")
        if ostype == 2 :
            # windows
            drivepath = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        else :
            # 0 and 1 are OSX and Linux systems
            drivepath = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
    else :
        mylog.debug(drivepath)

    if not user_settings.PROJECT_NAME : # project_name custom paramater is not set... we use time to make unik name
        dirname = datetime.datetime.now().strftime('%Y%m%d') #_%H%M%S')
    else :
        # desktop / PROJECT_NAME / take
        dirname = datetime.datetime.now().strftime('%Y%m%d') + "_" + user_settings.YYYYMMDD_PROJECT_NAME

    projectdir = os.path.join(drivepath, "stopmotion", dirname)
    # do not create dir here, if it's not existing it will ask for new take from 0
    return projectdir

def setupTakeDir(projectdir, _t):
    mylog.info("==== setup working dir =====")

    if not os.path.exists(projectdir):
        takeDir = user_settings.TAKE_NAME + "_" + str(_t).zfill(2)
    else :
        takeDir = user_settings.TAKE_NAME + "_" + str(_t).zfill(2)
        tmpdir = os.path.join(projectdir, takeDir)
        if os.path.exists(tmpdir) :
            # project already exists 
            # let's get last take number
            # and create a new take (incremented)
            lasttakedir = os.path.basename(max([os.path.join(projectdir, d) for d in os.listdir(projectdir)], key=os.path.getmtime)).split("_")
            if lasttakedir[0] == user_settings.TAKE_NAME :
                # same take name (should always be)
                # here we assume dir has name "XXXXXXXX_00"
                lasttakenum = int(lasttakedir[-1])
                _t = lasttakenum+1
            #
            takeDir = user_settings.TAKE_NAME + "_" + str(_t).zfill(2)
    
    workingdir = os.path.join(projectdir, takeDir)
    if not os.path.exists(workingdir) :
        os.makedirs(workingdir)

    HQFilesDir = os.path.join(workingdir,"HQ")
    if not os.path.exists(HQFilesDir) : 
        os.makedirs(HQFilesDir)
    
    # last checks before continuing
    if os.path.exists(workingdir) and os.path.exists(HQFilesDir):
        mylog.info("Working directory : %s" %workingdir)
        return workingdir, _t
    else :
        # throw error --> can't setup working dir
        mylog.error("error while creating working dir")
        quit()

def newTake () :
    # called each time we start a new shot (takes)
    global frames, myCamera, takenum, take, workingdir, SETUP, infos_take
    SETUP = True
    #animSetup.show(extraSurface, surf_center)
    # export last take as movie file
    if frames is not None and user_settings.EXPORT_ANIM is True :
        mylog.info("Export of take \"%s\" as movie file using ffmpeg..." %take)
        image_processing.compileAnimation(workingdir, frames, take)
    # setup take and new dir
    workingdir, takenum = setupTakeDir(projectdir, takenum) # path of working dir
    # reset everything
    take = user_settings.TAKE_NAME + str(takenum).zfill(2)
    frames = collections.deque(maxlen=maxFramesBuffer)
    myCamera.lastframe = None
    myCamera.frameCount = 0
    # update takenum for next time
    takenum += 1
    SETUP = False

    infos_take = defaultFont.render(workingdir, True, (255, 255, 255))
    #animSetup.hide(extraSurface, surf_center)

    return workingdir

def getCameraDevice():
    res_w = 0
    arr = []
    mylog.info("==== setup camera =====")
    if user_settings.forceCamera is True :
        # camera to use is defined by user settings
        cap = cam.streamConstructor (camIndex, ostype, user_settings.camera_codec)
        if cap.read()[0]:
            arr = [camIndex, cap.get(3), cap.get(4)]
            cap.release()
            return arr
        else :
            mylog.critical("Camera not found !")
            quit()
    else :
        id = -1
        r = (0, 3)
        for i in range(r[0], r[1]):
            tmp = None
            try :
                cap = cam.streamConstructor (i, ostype, constants.codecs[ostype])
            except :
                mylog.error("Unexpected error:")
                break
            else :    
                if cap.read()[0]:
                    tmp_w = cap.get(3)
                    tmp_h = cap.get(4)
                    cap.release()
                    tmp_cam = [i,tmp_w, tmp_h]
                    mylog.debug("cam %s -> (%s,%s)" %(i, tmp_w, tmp_h))
                    if tmp_w > res_w :
                        res_w = tmp_w
                        arr = tmp_cam
                    id = i

        if id == -1 :
            # throw error here --> no camera found
            mylog.critical("Camera not found at all !")
            quit()
        else :
            mylog.info("Camera id : %s (%s , %s)" %(arr[0], arr[1], arr[2]))

        return arr


def getMonitor ():
    mylog.info("==== setup output display =====")
    if ostype == 0 :
        #raspberry pi
        drivers = ('directfb', 'fbcon', 'svgalib')
        found = False
        for driver in drivers:
            mylog.debug("Trying \'%s\'" %driver)
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                mylog.debug('%s -> failed' %driver)
                continue
            else :
                found = True
                break
        if not found:
            #raise Exception('No suitable video driver found.')
            return False, 0, 0
        else :
            mylog.info("Screen resolution : %s - %s" %(pygame.display.Info().current_w, pygame.display.Info().current_h))
            return True, pygame.display.Info().current_w, pygame.display.Info().current_h
    else :
        mylog.info("Screen resolution : %s - %s" %(pygame.display.Info().current_w, pygame.display.Info().current_h))
        return True, pygame.display.Info().current_w, pygame.display.Info().current_h

def defineWindowedSize(displaysize) :
    scale_factor = 0.65 #in windowed mode, the window will be twice smaller than the screenSurface
    _w = int(displaysize[0]*scale_factor)
    _h = int(displaysize[1]*scale_factor)
    mylog.debug("windowed size = %s , %s" %(_w, _h))
    return (_w, _h)

def definePreviewSize(camsize, displaysize):
    global WINDOWED_SIZE
    ix, iy = (camsize[0], camsize[1])
    bx, by = (displaysize[0], displaysize[1])
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    
    if sx >= ix :
        sx, sy = definePreviewSize(camsize,WINDOWED_SIZE)

    return (int(sx),int(sy))

def displayAnimation():
    global IS_PLAYING
    while IS_PLAYING :
        for i in frames : # frames is pygame.surface array           
            screenSurface.blit(i, surf_center)
            pygame.display.flip()
            time.sleep(1/user_settings.FPS) # to keep framerate 
        IS_PLAYING=False

def displayCameraStream(buffer):
    global IS_PLAYING
    # display video stream
    if buffer is not None :
        img = None
        if wb is True :
            img = image_processing.white_balance(buffer)
        else :
            img = buffer

        #img = image_processing.rescaleToDisplay(img, PREVIEW_SIZE)
        img = image_processing.rescaleToDisplay(img, rescale_factor)
        previewSurface.blit(img, (0,0))

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
                previewSurface.blit(img, (0,0))
            else :
                pass
            f -= 1
            

def ledBlink ():
    global IS_SHOOTING, IS_PLAYING, SETUP
    while True :
        if IS_SHOOTING is True:
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
            time.sleep(0.1)
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)
            time.sleep(0.1)
        elif IS_PLAYING is True :
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
        elif SETUP is True :
            GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
            time.sleep(0.3)
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)
            time.sleep(0.3)
        else :
            GPIO.output(constants.OUTPUT_LED,GPIO.HIGH)
    
    # end of thread, we turn off LED
    GPIO.output(constants.OUTPUT_LED,GPIO.LOW)
            

def capture() :
    global IS_SHOOTING, infos_frame
    # start shooting
    IS_SHOOTING = True
    #animTake.show(extraSurface, surf_center)
    if outputdisplay is True :
        myCamera.capturedisp(PREVIEW_SIZE, workingdir, take)
    else :
        myCamera.capture(workingdir, take)
    #
    if myCamera.lastframe is not None :
        frames.append(myCamera.lastframe)
    else :
        mylog.error("Error while shooting : last frame is empty !")
    # end of shooting
    pygame.time.delay(30)
    IS_SHOOTING = False

    infos_frame = defaultFont.render("Frame %s" %str(myCamera.frameCount).zfill(5), True, (255, 255, 255))
    #animTake.hide(extraSurface, surf_center)

# GPIO FUNCTIONS
def setupGpio():
    mylog.info("==== setup GPIO =====")
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
    mylog.info("GPIO pins are ready ! ")

def actionButtn(inputbttn):
    global IS_PLAYING, IS_SHOOTING, finish, SETUP, CARTON
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screenSurface
    --> need to recode this to allow combined buttons
    '''
    action = -1
    #start counting pressed time
    pressed_time=time.monotonic()
    while GPIO.input(inputbttn) == 0 :
        if time.monotonic()-pressed_time >= constants.PRESSINGTIME :
            CARTON = True
            if inputbttn == constants.SHOT_BUTTON :
                animSetup.show(extraSurface, (0,0))
            elif inputbttn == constants.PLAY_BUTTON :
                animQuit.show(extraSurface, (0,0))
            else :
                pass
        pass
    pressed_time=time.monotonic()-pressed_time

    if pressed_time >= constants.PRESSINGTIME :
        if inputbttn == constants.SHOT_BUTTON :
            newTake()
            animSetup.hide(extraSurface, (0,0))
        elif inputbttn == constants.PLAY_BUTTON :
            finish = True
            animQuit.hide(extraSurface, (0,0))
        CARTON = False
    else :
        if inputbttn == constants.SHOT_BUTTON :
            CARTON = True
            animTake.show(extraSurface, (0,0))
            capture()
            animTake.hide(extraSurface, (0,0))
            CARTON = False
        elif inputbttn == constants.PLAY_BUTTON :
            IS_PLAYING = True
    return action


def quit():
    pygame.quit()
    if ostype == 0 :
        GPIO.cleanup()
    # export animation before quitting totally
    if user_settings.EXPORT_ANIM is True and frames is not None :
        mylog.info("Export of take \"%s\" as movie file using ffmpeg..." %take)
        image_processing.compileAnimation(workingdir, frames, take)
    mylog.info("Goodbye Animator !")
    sys.exit()
    # finally, we quit !


if __name__== "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    mylog.debug("script dir : %s" %dir_path)
    # global var setup
    frames = None # framebuffer for animation
    IS_PLAYING = False
    IS_SHOOTING = False
    SETUP = True
    CARTON = False
    PREVIEW_SIZE = (0,0)
    screenSurface = None
    workingdir = None
    takenum = 0
    take = None
    infos_take = None
    wb = False # white balance activation
    # initialise pygame
    pygame.init()
    # setup
    ostype = detectOS()                 # int (0:RPi, 1:OSX, 2:WIN)
    # frames buffer for animation previewSurface
    # --> ring buffer # duration in seconds for animation previewSurface (last X seconds)
    maxFramesBuffer = int(user_settings.PREVIEW_DURATION*user_settings.FPS)

    # GPIO initialisation
    if ostype == 0 :
        import RPi.GPIO as GPIO
        setupGpio()
        leds = Thread(target=ledBlink, daemon=True)
        leds.start()

    # camera initialisation
    video_device = getCameraDevice()    # array [camera_id, width, height]
    myCamera = cam.cam(video_device, ostype, constants.codecs[ostype]) # video_device, os, codec, buffer
    myCamera.start() # threaded    

    # ============ output display
    outputdisplay, w, h = getMonitor () # boolean, width, height
    # not in headless mode
    if outputdisplay is True:
        FULLSCREEN = False
        DISPLAY_SIZE = (w, h)
        WINDOWED_SIZE = defineWindowedSize(DISPLAY_SIZE)
        screenSurface = pygame.display.set_mode(WINDOWED_SIZE) # , pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.RESIZABLE #  pygame.FULLSCREEN
        mylog.info("Window size : %s, %s" %(WINDOWED_SIZE[0], WINDOWED_SIZE[1]))

        PREVIEW_SIZE = definePreviewSize(myCamera.size, WINDOWED_SIZE)
        previewSurface = pygame.Surface(PREVIEW_SIZE)
        extraSurface = pygame.Surface(PREVIEW_SIZE)
        mylog.info("Preview size : %s, %s" %(PREVIEW_SIZE[0], PREVIEW_SIZE[1]))
        # calc center of surface
        surf_center = (
            (screenSurface.get_width()-previewSurface.get_width())/2,
            (screenSurface.get_height()-previewSurface.get_height())/2
        )
        rescale_factor = image_processing.rescaleFactor (myCamera.size, PREVIEW_SIZE)
        # font and info elements
        pygame.font.init()
        defaultFont = pygame.font.SysFont(pygame.font.get_default_font(), 30)
        consoleFont = pygame.font.SysFont(pygame.font.get_default_font(), 20)
        pygame.display.set_caption('stopmotion project')

        # hide mouse
        pygame.mouse.set_visible(False)
        pygame.mouse.get_rel()

        # ==== sprites ======
        animTake = animation.Animation(PREVIEW_SIZE, (255,0,0), 128, "") # size, color, alpha
        animSetup = animation.Animation(PREVIEW_SIZE, (0,0,0), 170, "building new take !") # size, color, alpha
        animQuit = animation.Animation(PREVIEW_SIZE, (0,0,0), 170, "quitting app !") # size, color, alpha
        animLongPress = animation.Animation(PREVIEW_SIZE, (0,0,0), 170, "")

        # do not allow screenSurface saver
        pygame.display.set_allow_screensaver(False)

        #
        if os == 0 :
            subprocess.call("v4l2ucp") #we launch additional app to control webcam

    else :
        mylog.warning("Stopmotion tool run in headless mode !")
    
    # ==== new project ====
    projectdir = setupProjectDir()
    # ==== new take =====
    workingdir = newTake ()
    # update texts for console and infos
    infos_take = defaultFont.render(workingdir, True, (255, 255, 255))
    infos_frame = defaultFont.render("Frame %s" %str(myCamera.frameCount).zfill(5), True, (255, 255, 255))
    infos_cam = consoleFont.render("Camera résolution : " + ' '.join(str(x) for x in myCamera.size), True, (250, 0, 0))
    infos_fps = consoleFont.render("Animation framerate : " + str(user_settings.FPS), True, (250, 0, 0))
    # ============ ready to animate
    mylog.info("==== ready to animate :) =====")
    # main loop
    finish = False
    prev_frame_time = time.time()
    while not finish:
        # function which do not need output display
        frameBuffer = myCamera.read()
        new_frame_time = time.time()
        # then function needed only if output display is available (we have a screenSurface)
        if outputdisplay is True :
            # pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finish = True
                if event.type == KEYDOWN :
                    if event.key == K_c :
                        user_settings.show_console = not user_settings.show_console
                    if event.key == K_t :
                        capture()
                    if event.key == K_p and outputdisplay is True :
                        IS_PLAYING = True
                    if event.key == K_n :
                        SETUP = True
                        newTake()
                    if event.key == K_f and outputdisplay is True :
                        if not FULLSCREEN:
                            screenSurface = pygame.display.set_mode(DISPLAY_SIZE, pygame.FULLSCREEN)#modes[0]
                        else:
                            screenSurface = pygame.display.set_mode(WINDOWED_SIZE)
                        # recalc surf center 
                        #PREVIEW_SIZE = definePreviewSize(myCamera.size, (pygame.display.Info().current_w, pygame.display.Info().current_h))
                        FULLSCREEN = not FULLSCREEN
                    if event.key == K_b and outputdisplay is True :
                        wb = not wb
                    if event.key == K_q :
                        myCamera.release()
                        quit()
                        sys.exit()
                    if event.key == K_ESCAPE:
                        myCamera.release()
                        quit()
                        finish = True
            # should not be there...
            surf_center = (
                (screenSurface.get_width()-PREVIEW_SIZE[0])/2,
                (screenSurface.get_height()-PREVIEW_SIZE[1])/2
            )
            # switch between animation previewSurface and onion skin view
            if IS_PLAYING is True :
                displayAnimation()
            else:
                displayCameraStream(frameBuffer)

            # update screen 
            screenSurface.fill((0,0,0))
            screenSurface.blit(previewSurface, surf_center)

            if user_settings.show_console is True :
                # calculate framerate
                fps = 1/(new_frame_time-prev_frame_time)
                fpsConsole = consoleFont.render(str("App fps : %s" %fps), True, (250, 0, 0))
                screenSurface.blit(fpsConsole, (25, screenSurface.get_height()-40))
                console = consoleFont.render(str("Cam Résolution : %s  |  Anim FPS : %s  | Preview res : %sx%s |  White Balance : %s " %('x'.join(str(x) for x in myCamera.size), str(user_settings.FPS), PREVIEW_SIZE[0], PREVIEW_SIZE[1], wb)), True, (250, 0, 0))
                screenSurface.blit(console, (25, screenSurface.get_height()-20))

            if user_settings.show_infos is True :
                tempSurface = pygame.Surface(infos_frame.get_size(), SRCALPHA)
                tempSurface.fill((0,0,0,50))
                tempSurface.blit(infos_frame,(0,0))
                screenSurface.blit(tempSurface, (20,20))

                tempSurface = pygame.Surface(infos_take.get_size(), SRCALPHA)
                tempSurface.fill((0,0,0,50))
                tempSurface.blit(infos_take,(0,0))
                screenSurface.blit(tempSurface, (screenSurface.get_width()-infos_take.get_size()[0]-20,20))

            if CARTON is True :
                # extra informations given in "animation" class object
                screenSurface.blit(extraSurface, surf_center)
                
            pygame.display.flip()
            # update frame time for fps count
            prev_frame_time = new_frame_time
            # handle mouse move
            mouse_move = pygame.mouse.get_rel()
            if not all(mouse_move) :
                pygame.mouse.set_visible(False)
            else :
                pygame.mouse.set_visible(True)
            


if ostype == 0 and user_settings.shutdown_rpi :
    # turn off RPi at end
    subprocess.call("sudo shutdown -h now", shell=True) # turn off computer !


    