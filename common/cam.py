#  run qv4l to check camera codec to use
#  https://www.pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
import sys, os, time, shutil, collections, re, datetime
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
    
    def capture(self, display, target, name):
        tmp_frame = self.read()
        fname = "{}_{}.png".format(name, str(self.frameCount).zfill(5))
        filename = os.path.join(target,"HQ",fname)
        cv2.imwrite(filename, tmp_frame)
        filename = os.path.join(target,fname)
        cv2.imwrite(filename, image_processing.rescaleImg(tmp_frame,50))
        print("{} written!".format(filename))
        self.lastframe = image_processing.rescaleToDisplay(tmp_frame, display)
        self.frameCount += 1
        
    
    def release(self):
        self.stream.release()
        self.stopped = True
        
    def read(self):
        if len(self.Q) > 1 :
            return self.Q[-1]
            
def streamConstructor (id, os=0, codec='MJPG', w=1920, h=1080, fps=30):
    cap = None
    if os == 0 :
        cap = cv2.VideoCapture()
        cap.open(id, apiPreference=cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*codec))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        cap.set(cv2.CAP_PROP_FPS, fps)
    else :
        cap = cv2.VideoCapture(id)
    return cap


