#!/usr/bin/python3
import sys, os, time, shutil, collections, re, subprocess, datetime
import pygame
import pygame.camera
import pygame.locals
import cv2
import psutil

today = datetime.date.today()

# first we check the OS and if we are on RPi
rpi = False
print("os : ", os.uname()[1], os.uname()[4])
# if (os.uname()[4].startswith("arm")) :
#     rpi = True
#     import picamera
#     from picamera.array import *
#     import RPi.GPIO as GPIO

CAM_RES = [0,0]
if rpi is False :
    capture = cv2.VideoCapture(1)
    #camtest = cv2.VideoCapture(0)
    if not capture.isOpened() :
        raise IOError("cannot open webcam")
    else :
        CAM_RES[0] = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        CAM_RES[1] = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        capture.release()
    print(CAM_RES)