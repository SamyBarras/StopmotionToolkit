#!/bin/bash

echo "===== RPI CONFIGURATION ====="
echo "===== change RPI splash screen"
cd /usr/share/plymouth/themes
sudo cp -a pix mamatus
cd mamatus
sudo mv pix.plymouth mamatus.plymouth
sudo mv pix.script mamatus.script
sudo rm splash.png
sudo wget https://maudetsamy.com/_images/splash.png
sudo sed -i 's/pix/mamatus/g; s/Raspberry Pi/My/g' mamatus.plymouth
sudo sed -i 's/pix/mamatus/g' /etc/plymouth/plymouthd.conf
echo "===== change Desktop image and color"
cd /home/pi/Pictures
sudo wget -N http://maudetsamy.com/mamatus/_images/mamatus_logo.jpg
sudo pcmanfm --set-wallpaper /home/pi/Pictures/mamatus_logo.jpg --wallpaper-mode=center

