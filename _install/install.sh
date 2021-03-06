#!/bin/bash

echo "=========== update apt-get"
sudo apt-get update
sudo apt-get upgrade

echo "=========== install python3"
sudo apt-get install -y python3

echo "=========== install dependencies"
sudo apt-get install -y libatlas-base-dev libatlas3-base libhdf5-dev libhdf5-serial-dev libjasper-dev  libqtgui4  libqt4-test 
sudo apt-get install -y libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev
sudo apt-get install -y libsdl2-mixer-dev libsdl2-image-dev libsdl2-ttf-dev
sudo apt-get install -y v4l2ucp

echo "=========== install usb-drive auto-mount"
sudo apt-get install -y usbmount exfat-fuse exfat-utils     # adding support to exFat partitions
sudo apt-get install -y ntfs-3g                             # adding support to ntfs partitions

echo "=========== install xterm for auto-load in console startX"
sudo apt-get install -y xterm -y
sudo apt-get autoclean

echo "=========== Create Desktop shortcut"
cp icon.png /home/pi/Pictures/icon.png
cp stopmotiontool.desktop /home/pi/Desktop/stopmotiontool.desktop

echo "=========== install python requirements"
cd ../
pip3 install -r requirements.txt