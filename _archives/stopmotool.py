#!/usr/bin/python3
import sys, os, time, shutil, collections, re, subprocess, datetime
import pygame
import pygame.camera
from pygame.locals import *
import cv2
import psutil
from threading import Thread, Timer
import picamera
from picamera.array import *
import RPi.GPIO as GPIO
from common.constants import *
from common.user_settings import *
today = datetime.date.today()

class Capture(object):
    global IS_PLAYING, frames, workingdir, HQFilesDir, IS_SHOOTING, SCREEN_SIZE
    def __init__(self,camRes):
        self.size = camRes
        # if use of picamera, we need to update this part !
        self.clist = pygame.camera.list_cameras()
        if not self.clist:
            raise ValueError("Sorry, no camera detected.")
        self.cam = pygame.camera.Camera(self.clist[0], self.size)
        self.cam.start()
        self.video = pygame.Surface(self.size, 0, screen)
        self.frameCount = 0

    def videoStreamCapture(self):
        # if you don't want to tie the framerate to the camera, you can check
        # if the camera has an image ready.  note that while this works
        # on most cameras, some will never return true.
        if self.cam.query_image():
            self.video = self.cam.get_image(self.video)
            self.video.set_alpha(127) # not full alpha for videostream
        screen.blit(pygame.transform.scale(self.video, SCREEN_SIZE),(0,0))        
    
    def captureFrame (self):
        global IS_SHOOTING
        IS_SHOOTING = True
        self.snapshot = pygame.image.tostring(self.video.copy(),"RGB")
        self.lastframe = pygame.image.fromstring(self.snapshot, self.size, "RGB", False)
        # save full size image
        fname = str(self.frameCount).zfill(5) + ".png"
        fpath = os.path.join(HQFilesDir,fname)
        pygame.image.save(self.lastframe, fpath)
        # save half res
        if self.size[0] >= 640 :
            # save half res picture
            lowRes = (int(self.size[0]/2),int(self.size[1]/2))
            f = pygame.transform.scale(self.lastframe, lowRes)
            fpath = os.path.join(workingdir,fname)
            pygame.image.save(f, fpath)
        #cv2.imwrite(filepath, cv2.cvtColor(wrap,cv2.COLOR_BGR2RGB))
        # append low res to frame
        frames.append(self.snapshot)
        print("Frame ",fname," saved")
        self.frameCount += 1
        IS_SHOOTING = False

def displayOnionSkin():
    # show onion skin
    frame = None
    if ONIONSKIN >= 1 :
        # if onion skin set, we show previous frames with less opacity
        f = ONIONSKIN
        while f > 0 :
            if len(frames) >= f :
                alpha = 255/int(f+1)
                frame = frames[-f]
                frame = pygame.image.fromstring(frame, myCamera.size, "RGB", False)
                image = pygame.transform.scale(frame, SCREEN_SIZE)
                image.set_alpha(alpha)
                screen.blit(image,(0,0)) #,special_flags=pygame.BLEND_ADD
            else :
                pass
            f -= 1
    return
    
def playBufferAnimation():
    global IS_PLAYING, start_time
    if not(IS_PLAYING): #block animation event while animation is running
        IS_PLAYING=True
        print("[INFO] Play animation")        
        while IS_PLAYING :
            current_time = pygame.time.get_ticks()
            for img in frames:
                    start = time.time()
                    img = pygame.image.fromstring(img, myCamera.size, "RGB", False)
                    screen.blit(pygame.transform.scale(img,SCREEN_SIZE), (0, 0))
                    end = time.time()
                    time.sleep(1/FPS) # to keep framerate
                    #print("display take:", end-start,"seconds")
            IS_PLAYING=False

def testDrive():
    global HQFilesDir
    #test = os.system("lsblk")
    #documentspath = subprocess.run(['xdg-user-dir','DOCUMENTS'],capture_output=True, text=True).stdout #DESKTOP
    #drivepath = os.path.join(str.strip(documentspath)+"/")
    drivepath = os.getcwd() # default directory is user's Desktop
    # checking for usb drives
    partitions = psutil.disk_partitions()
    drivesize = 0    
    for p in partitions :
        regEx = re.search("\A/media/pi", p.mountpoint)
        psize = psutil.disk_usage(p.mountpoint).free
        # we only keep the one with biggest free space
        if regEx is not None and  psize > drivesize:
            drivepath = p.mountpoint
            drivesize = psize
    drivepath = os.path.join(drivepath,"stopmotion", datetime.datetime.now().strftime('%Y_%m_%d/%H%M%S'))
    if not os.path.exists(drivepath):
        os.makedirs(drivepath)
        HQFilesDir = os.path.join(drivepath,"HQ")
        os.makedirs(HQFilesDir)
    if os.path.exists(drivepath) and os.path.exists(HQFilesDir):
        return drivepath
    else :
        return None
    
def testCam():
    CAM_RES = [0,0]
    camCheck = subprocess.run(['vcgencmd','get_camera'],capture_output=True, text=True).stdout
    camCheck = str.strip(camCheck).split()
    supported = re.split('(\w*)=(\d*)', camCheck[0])[2] # 0 -> not supported  1 -> supported
    detected = re.split('(\w*)=(\d*)', camCheck[1])[2] # 0 -> not detected   1 -> detected
    c = int(supported)+int(detected) # calculate for easy detection
    if c == 2 :
        print('-->',supported, detected)
        with picamera.PiCamera() as cam :
            CAM_RES = cam.MAX_RESOLUTION
    else :
        camtest = cv2.VideoCapture(3)
        if not camtest.isOpened() :
            raise IOError("cannot open webcam")
        else :
            camtest.set(3, 1920)
            camtest.set(4,1080)
            CAM_RES[0] = int(camtest.get(cv2.CAP_PROP_FRAME_WIDTH))
            CAM_RES[1] = int(camtest.get(cv2.CAP_PROP_FRAME_HEIGHT))
            print(CAM_RES)
            camtest.release()
    return CAM_RES
           
def actionButtn(inputbttn):
    '''
    function called each time a button is pressed
    will define to shot a frame / play anim / or get out of waiting screen
    '''
    if inputbttn == SHOT_BUTTON and GPIO.input(inputbttn) == 0:
        myCamera.captureFrame()
    elif inputbttn == PLAY_BUTTON and GPIO.input(inputbttn) == 0:
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

def compileAnimation(): #channel
    global HQFilesDir, workingdir
    if (len(frames) > 1) :
        print("Compiling...")
        os.system("ffmpeg -framerate 12 -start_number 0 -i "+ HQFilesDir +"/%05d.png"+" -vcodec mpeg4 "+workingdir+"/animation.mov")
        '''
        out = (
            ffmpeg
            .input(HQFilesDir +'/*.png', pattern_type='glob', framerate=12)
            .output(workingdir+'/animation.h264')
            .run()
            )
        '''
        print("Animation compiled.")
    else :
        print("no files to compile")
    
def setupGpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHOT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(SHOT_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(PLAY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PLAY_BUTTON, GPIO.FALLING, callback=actionButtn)
    GPIO.setup(OUTPUT_LED, GPIO.OUT) # SHOT_LED
    
if __name__== "__main__":
    global start_time, IS_PLAYING, workingdir, IS_SHOOTING, SCREEN_SIZE
    # startup action
    #myCamera.main()
    try :
        # setup functions
        setupGpio()
        pygame.init()
        camres = testCam()
        if camres[0] <= 0 :
            raise UnboundLocalError("no camera found")
        else :
            print("Webcam resolution is %s x %s pixels" %(camres[0],camres[1]))
            pygame.camera.init()
            
        workingdir = testDrive()
        if workingdir is None :
            raise UnboundLocalError("error during setup process of working dir")
        else :
            print("Working dir is ", workingdir.replace("/media/pi",""))
            
        #screen = pygame.display.set_mode(SCREEN_SIZE, 0)
        screenInfo = pygame.display.Info()
        SCREEN_SIZE = (screenInfo.current_w,screenInfo.current_h)
        screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN) #pygame.FULLSCREEN
        # frames buffer --> ring buffer # duration in seconds for animation preview (last X seconds)
        maxFramesBuffer = int(PREVIEW_DURATION*FPS)
        frames = collections.deque(maxlen=maxFramesBuffer)
        print("Anim preview : {} sec @ {}fps".format(PREVIEW_DURATION,FPS))
        start_time = pygame.time.get_ticks()
        #
        myCamera = Capture(camres)
        IS_SHOOTING = False
        IS_PLAYING = False
        leds = Thread(target=blinkLed, daemon=True)
        leds.start()
        run = True
        while run :
            if not(IS_PLAYING):
                displayOnionSkin()
                myCamera.videoStreamCapture()
            # update screen     
            pygame.display.flip()
            # pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    myCamera.cam.stop()
                    run = False
                    
    except UnboundLocalError as e:
        print ("[UNBOUNDLOCALERROR] " % e.message)
        pass
    except OSError as e:
        print ("[SYS ERROR] Loading setup functions :" % e.message)
    except KeyboardInterrupt :
        # called when ctrl+c is pressed
        print("ended by user")
    finally:
        print("Goodbye animator !")
        GPIO.cleanup()
        pygame.quit()
        compileAnimation()
        sys.exit()
    