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
LOGDIR=/var/log/earlybird

echo "Started earlybird-Installer | https://github.com/Zyzonix/earlybird"
echo ""

# check if executed as root
USR=$(/usr/bin/id -u)
if [ $USR -ne 0 ]
  then echo "Please rerun this script as root (su -i or sudo)- exiting..."
  exit
fi

echo ""
echo "Installing required packages with APT..."
/usr/bin/apt install wakeonlan ipmitool python3-pip git python3-fastapi -y
echo "Done."

echo ""
echo "Creating directories..."
/usr/bin/mkdir -p $LOGDIR
/usr/bin/mkdir -p $BASEDIR/earlybird
cd $BASEDIR
echo "Done."

echo "Cloning from github..."
/usr/bin/git clone https://github.com/Zyzonix/earlybird.git
echo "Done."

echo ""
echo "Making main executeable executeable..."
/usr/bin/chmod +x $BASEDIR/earlybird/earlybird
echo "Done."

echo ""
echo "Linking main executeable..."
/usr/bin/ln -s $BASEDIR/earlybird/earlybird /usr/bin/earlybird
echo "Done."

echo ""
echo "Installing systemservices..."
/usr/bin/mv $BASEDIR/earlybird/services/earlybird-webclient.service $SYSTEMSERVICEPATH
/usr/bin/mv $BASEDIR/earlybird/services/earlybird-wakeup.service $SYSTEMSERVICEPATH

echo ""
echo "Enabling services..."
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable earlybird-webclient.service
/usr/bin/systemctl enable earlybird-wakeup.service
echo "Done."

echo ""
printf "%s " "Enter IP Address to bind webclient on (can be changed later in config.py):"
read IP
sed -i "s+SERVERIP.*+SERVERIP=$IP+g" /opt/earlybird/config.py
echo "Done."

echo ""
printf "%s " "Enter public domain if different from local e.g. for use behind proxy (can be left empty and/or changed later in config.py):"
read PUBLICSERVERNAME
sed -i "s+PUBLICSERVERNAME.*+PUBLICSERVERNAME=$PUBLICSERVERNAME+g" /opt/earlybird/config.py
echo "Done."

echo ""
echo "Installation complete."
echo "Configure your hosts in" $BASEDIR/earlybird/clients.ini


