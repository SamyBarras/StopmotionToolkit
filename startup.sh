#!/bin/bash
#Extract speed info from ethtool. If speed is 10 Mb/s, no cable is connected. If it is 100 Mb/s, there is a cable present.
SPEED=`ethtool eth0 | grep -i "Speed" | awk '{print $2}' | grep -o '[0-9]*'`
if ifconfig | grep -i "eth0"  > /dev/null 2>&1; then
        echo "Ethernet interface is already up. Checking Cable connection..."
        if [ $SPEED >= 100 ]; then
                echo "Ethernet connection OK."
                cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd
                git pull https://github.com/SamyBarras/stopmotiontoolkit
        else
                echo "Error: No cable connected. Bringing down eth0"
                ifdown --force eth0
                exit
        fi


        exit
else
        if [ $SPEED >= 100 ]; then
                echo "Cable connection detected. Bringing up eth0..."
                ifup eth0
                cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd
                git pull https://github.com/SamyBarras/stopmotiontoolkit
        else
                echo "Error: No cable connected."
                exit
        fi
fi
exit