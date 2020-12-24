#!/usr/bin/python3
# customs imports
import sys, os, time, shutil, collections, re, datetime
# dependencies
import pygame
import pygame.camera
from pygame.locals import *
import cv2
import psutil
import numpy as np
from threading import Thread, Timer
# custom imports
from common.constants import *
from common.user_settings import *
from common.cam import *
from common.image_processing import *


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
    regEx = '\A' + drives[ostype]
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
    
    workingdir = os.path.join(drivepath, "stopmotion", datetime.datetime.now().strftime('%Y_%m_%d/%H%M%S')+"_"+project_name)
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
    if forceCamera is True :
        # camera to use is defined by user settings
        cap = cv2.VideoCapture(camIndex)
        arr = [camIndex,cap.get(3),cap.get(4)]
        cap.release()
        return arr
    else :
        id = -1
        r = (0, 4)
        for i in range(r[0], r[1]):
            tmp = None
            cap = streamConstructor (i, ostype)
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
    import gi
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk
    
    allmonitors = []
    gdkdsp = Gdk.Display.get_default()
    if gdkdsp is not None :
        monitors = gdkdsp.get_n_monitors()
        for i in range(monitors):
            monitor = gdkdsp.get_monitor(i)
            print(monitor)
            scale = monitor.get_scale_factor()
            geo = monitor.get_geometry()
            allmonitors.append([
                monitor.is_primary()] + [n * scale for n in [
                    geo.x, geo.y, geo.width, geo.height
                ]
            ])
        print("screens : ", allmonitors)
    if len(allmonitors) > 0 :
        #SCREEN_SIZE = (allmonitors[0][3],allmonitors[0][4])
        return True, geo.width, geo.height
    else :
        return False, 0 ,0


def displayAnimation():
    global is_playing
    while is_playing :
        for i in frames : # frames is pygame.surface array            
            screen.blit(i, (0, 0))
            pygame.display.flip()
            time.sleep(1/FPS) # to keep framerate
        is_playing=False

def displayCameraStream(buffer):
    # display video stream
    if buffer is not None:
        screen.blit(rescaleToDisplay(buffer, screen), (0, 0))

    # display onion skin
    if ONIONSKIN >= 1 :
        # if onion skin set, we show previous frames with less opacity
        f = ONIONSKIN
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
    
    if show_console is True :
        screen.blit(textsurface,(25,25))
        screen.blit(fpsconsole, (25,60))
    
    pygame.display.flip()

if __name__== "__main__":
    global ostype
    # setup
    ostype = detectOS()                 # int (0:RPi, 1:OSX, 2:WIN)
    workingdir = setupDir()             # path of working dir
    outputDisplay, w, h = getMonitor () # boolean, width, height
    # pygame
    pygame.init()
    pygame.font.init()
    myfont = pygame.font.SysFont('Helvetica', 15)
    pygame.display.set_caption('stopmotion project')
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()
    # frames buffer for animation preview--> ring buffer # duration in seconds for animation preview (last X seconds)
    maxFramesBuffer = int(PREVIEW_DURATION*FPS)
    frames = collections.deque(maxlen=maxFramesBuffer)
    # camera initialisation
    video_device = getCameraDevice()    # array [camera_id, width, height]
    myCamera = cam(video_device, ostype, camera_codec) # video_device, os, codec, buffer
    myCamera.start() # threaded

    textsurface = myfont.render("Camera résolution : " + ' '.join(str(x) for x in myCamera.size), False, (250, 0, 0))
    
    # window if outputdisplay is available
    if outputDisplay is True:
        screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE) #pygame.RESIZABLE pygame.FULLSCREEN
    else :
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        # pygame.display.init()
        print("no display found")
        screen = pygame.display.set_mode((1,1))
        
    # loop
    finish = False
    is_playing = False
    while not finish:
        clock.tick(50)
        frameBuffer = myCamera.read()
        fpsconsole = myfont.render(str(clock.get_fps()), False, (250, 0, 0))
        # then function needed only if output display is set
        if outputDisplay is True :
            if is_playing is True :
                displayAnimation()
            else :
                displayCameraStream(frameBuffer)
            
        # pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finish = True
            if event.type == KEYDOWN :
                if event.key == K_t :
                    myCamera.capture(screen, workingdir, take_name)
                    frames.append(myCamera.lastframe)
                if event.key == K_p :
                    is_playing = True
                if event.key == K_q or event.key == K_ESCAPE:
                    finish = True
        

    myCamera.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()