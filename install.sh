#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 16-02-2024 11:05:18
# 
# file          | install.sh
# project       | earlybird
# file version  | 1.0
#
BASEDIR=/opt
SYSTEMSERVICEPATH=/etc/systemd/system/

echo "Started earlybird-Installer | https://github.com/Zyzonix/earlybird"
echo ""

# check if executed as root
USR=$(/usr/bin/id -u)
if [ $USR -ne 0 ]
  then echo "Please rerun this script as root (su -i or sudo)- exiting..."
  exit
fi

echo "Installing required packages with APT..."
/usr/bin/apt install wakeonlan ipmitool python3-pip git -y
echo "Done."

echo "Installing python module fastapi..."
/usr/bin/pip3 install uvicorn fastapi
echo "Done."

echo "Creating directories..."
/usr/bin/mkdir -p $BASEDIR/earlybird
cd $BASEDIR
echo "Done."

echo "Cloning from github..."
/usr/bin/git clone https://github.com/Zyzonix/earlybird.git
echo "Done."

echo "Making main executeable executeable..."
/usr/bin/chmod +x $BASEDIR/earlybird/earlybird
echo "Done."

echo "Linking main executeable..."
/usr/bin/ln -s $BASEDIR/earlybird/earlybird /usr/bin/earlybird
echo "Done."

echo "Installing systemservices..."
/usr/bin/mv $BASEDIR/earlybird/services/earlybird-server.service $SYSTEMSERVICEPATH
/usr/bin/mv $BASEDIR/earlybird/services/earlybird-wakeup.service $SYSTEMSERVICEPATH
echo "Enabling services..."
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable earlybird-server.service
/usr/bin/systemctl enable earlybird-wakeup.service
echo "Done."

echo "Installation complete."
echo "Configure your hosts in" $BASEDIR/earlybird/clients.ini


