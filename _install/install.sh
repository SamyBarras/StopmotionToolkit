#!/bin/bash

echo "=========== update apt-get"
sudo apt-get update

echo "=========== install python3"
sudo apt-get install -y python3

echo "=========== install dependencies"
sudo apt-get install -y libatlas-base-dev libatlas3-base libhdf5-dev libhdf5-serial-dev libjasper-dev  libqtgui4  libqt4-test 
sudo apt-get install -y libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
sudo apt-get install -y libsdl2-mixer-dev libsdl2-image-dev libsdl2-ttf-dev

echo "=========== install usb-drive auto-mount"
sudo apt-get install -y usbmount exfat-fuse exfat-utils

echo "=========== install xterm for auto-load in console startX"
sudo apt-get install -y xterm -y
sudo apt-get autoclean


echo "=========== install python requirements"
cd ../
pip3 install -r requirements.txt