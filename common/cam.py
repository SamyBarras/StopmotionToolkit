#  run qv4l to check camera codec to use
#  https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
import sys, os, time, shutil, collections, re, datetime, logging
# dependencies
import pygame
import pygame.camera
from pygame.locals import *
import cv2
import psutil
import numpy as np
from threading import Thread, Timer

import common.constants as constants
import common.user_settings as user_settings
import common.image_processing as image_processing

class cam(object):
    #global ostype
    def __init__(self, arr, os, codec, buffer=4):
        self.id = arr[0]
        self.lastframe = None
        self.surface = None
        self.frameCount = 0
        self.buffer = buffer # how many frames we store for buffering / default is 4
        self.stream = streamConstructor (self.id, os, codec)
        if not self.stream.isOpened():
            logging.error("Unable to open video source %s", self.id)
            raise ValueError("Unable to open video source", self.id)
        self.size = (int(self.stream.get(3)),int(self.stream.get(4)))
        self.Q = collections.deque(maxlen=buffer)
        self.stopped = False
    
    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon=True
        t.start()
        return self
        
    def update(self):
        while True :
            if self.stream.isOpened():
                ret, self.frame = self.stream.read()
                if ret:
                    self.Q.append(self.frame)
                else:
                    self.release()
                    return
            else:
                self.release()
                return
            if self.stopped :
                return
    
    def capturedisp(self, display, target, name): # with output display
        tmp_frame = self.read()
        fname = "{}_{}.png".format(name, str(self.frameCount).zfill(5))
        filename = os.path.join(target,"HQ",fname)
        cv2.imwrite(filename, tmp_frame)
        filename = os.path.join(target,fname)
        cv2.imwrite(filename, image_processing.rescaleImg(tmp_frame,50))
        logging.info("Frame \"%s\" saved", fname)
        logging.debug("\"%s\" written!",filename)
        self.lastframe = image_processing.rescaleToDisplay(tmp_frame, display)
        self.frameCount += 1
    
    def capture(self, target, name) : # no output display
        tmp_frame = self.read()
        fname = "{}_{}.png".format(name, str(self.frameCount).zfill(5))
        filename = os.path.join(target,"HQ",fname)
        cv2.imwrite(filename, tmp_frame)
        filename = os.path.join(target,fname)
        cv2.imwrite(filename, image_processing.rescaleImg(tmp_frame,50))
        logging.info("Frame \"%s\" saved", fname)
        logging.debug("\"%s\" written!",filename)
        self.lastframe = tmp_frame
        self.frameCount += 1
        
    
    def release(self):
        self.stream.release()
        self.stopped = True
        
    def read(self):
        if len(self.Q) > 1 :
            return self.Q[-1]
            
def streamConstructor (id, os=0, codec='MJPG', w=1920, h=1080, fps=30):
    cap = None
    cap = cv2.VideoCapture()
    if os == 0 : 
        cap.open(id, apiPreference=cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1.0) # ELP camera -> OFF:1.0  / ON:3.0
        cap.set(cv2.CAP_PROP_AUTO_WB, 0) # 0 to turn off auto_white_balance
        cap.set(cv2.CAP_PROP_EXPOSURE, 0.01)
    elif os == 1 :
        cap.open(id)
        cap.read()
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75) # ELP camera -> OFF:1.0  / ON:3.0
        cap.set(cv2.CAP_PROP_AUTO_WB, 0) # 0 to turn off auto_white_balance
    else :
        cap.open(id)
        if os == 2 :
            cap.set(cv2.CAP_PROP_SETTINGS,0) # will show camera settings on WINDOWS OS
        
    # setup
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*codec))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    cap.set(cv2.CAP_PROP_FPS, fps)
    # auto exposure and white balance disabling

    return cap


