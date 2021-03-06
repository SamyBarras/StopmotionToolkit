
# Fresh RPi install

* Get last Debian version and mirror it to the SDCard using [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
* Insert SD card in Raspberry Pi, and follow instructions for Debian installation
* Password for Pi user should be changed to "map"
* Once RPi is ready, we can start the installation of the stopmotion toolkit app !

## Get files and setup
Clone project's repo from GitHub :

``` bash
cd /
sudo git clone https://github.com/samybarras/stopmotiontool
```

When project is downloaded, we can continue the installation :
``` bash
cd /stopmotiontool/_install/
bash install.sh
```

## Modify RPi config

### Silent boot
This should modify the RPI splash screen to Mamatus logo :
``` bash
cd /stopmotiontool/install/
bash rpi_config.sh
```
Documentation :
* [Boot on Raspbian Strech in console mode](https://scribles.net/silent-boot-on-raspbian-stretch-in-console-mode/)
* [Silent boot on Raspbian Strech](https://scribles.net/silent-boot-on-raspbian-stretch-in-console-mode/)


### Setup config file
We also need to modify RPi config file. To do so follow [this tuto](https://www.enricozini.org/blog/2020/himblick/raspberry-pi-4-force-video-mode-at-boot/) to modify config file, and force display output to HDMI1 even if no display connected :
``` bash
sudo nano /boot/config.txt
``` 
``` bash
# Pretend that a monitor is attached on HDMI0
hdmi_force_hotplug=1:0
# Pretend that the monitor is a monitor and not a TV
hdmi_group=2:0
# Pretend that the monitor has resolution 1920x1080
hdmi_mode=82:0
```

### Launch app at startup (optional)
Now we can setup autostart file](https://www.digikey.com/en/maker/projects/how-to-run-a-raspberry-pi-program-on-startup/cc16cb41a3d447b8aaacf1da14368b13), so our app will launch at startup.

``` bash
# autostart
mkdir /home/pi/.config/autostart
nano /home/pi/.config/autostart/stopmotool.desktop
```
And in this new file, write :
``` 
[Desktop Entry]
Type=Application
Name=StopmotionTool
Exec=xterm -hold -e '/usr/bin/python3 /stopmotiontool/stopmotiontool.py'
```
Save and quit file (ctrl+o ctrl+x)

### We should be good :)
Now we can restart RPi and check if everything works fine :
```bash
sudo reboot
```