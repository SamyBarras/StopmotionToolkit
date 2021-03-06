#!/bin/bash
# launched from ".../stopmotiontool/_install/" directory
echo "===== RPI CONFIGURATION ====="
echo "===== temp copy"
cp ./_images_/splash.png /home/pi/Desktop/splash.png
echo "===== change Desktop image and color"
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority
export XDG_RUNTIME_DIR=/run/user/1000
sudo pcmanfm --set-wallpaper _images_/mamatus_logo.jpg --wallpaper-mode=center
echo "===== change RPI splash screen"
cd /usr/share/plymouth/themes
sudo cp -a pix mamatus
cd mamatus
sudo mv pix.plymouth mamatus.plymouth
sudo mv pix.script mamatus.script
sudo rm splash.png
sudo mv /home/pi/Desktop/splash.png /usr/share/plymouth/themes/mamatus
#sudo wget https://maudetsamy.com/_images/splash.png
sudo sed -i 's/pix/mamatus/g; s/Raspberry Pi/My/g' mamatus.plymouth
sudo sed -i 's/pix/mamatus/g' /etc/plymouth/plymouthd.conf


