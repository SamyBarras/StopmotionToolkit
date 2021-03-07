#!/bin/bash
# launched from ".../stopmotiontool/_install/" directory
echo "===== RPI CONFIGURATION ====="
echo "===== temp copy"
cp ./_images_/splash.png /home/pi/Desktop/splash.png
echo "===== change Desktop image and color"
sudo cp ./desktop-items-0.conf /home/pi/.config/pcmanfm/LXDE-pi/desktop-items-0.conf
echo "===== change RPI splash screenSurface"
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
sudo reboot


