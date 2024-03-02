#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 27-02-2024 09:51:13
# 
# file          | scripts/commands.py
# project       | earlybird
# file version  | 1.0
#
import subprocess

# import custom scripts
from scripts.logHandler import logging

# wol function
def wakeOnLAN(mac):
    resultEncoded = subprocess.run("/usr/bin/wakeonlan " + mac, capture_output=True, shell=True)
    logging.write("[WoL] Sent WoL-signal to " + str(mac))
    return resultEncoded

# ipmi status check
# clientData is dictionary with specific client data
def ipmiPowerStatus(clientData):
    resultPowerStatusEncoded = subprocess.run("/usr/bin/ipmitool -I lanplus -H " 
                                                + clientData["ipmi_ip"] 
                                                + " -U " + clientData["ipmi_username"] 
                                                + " -P " + clientData["ipmi_password"] 
                                                + " power status", capture_output=True, shell=True)
    return resultPowerStatusEncoded

# ipmi power on command
# clientData is dictionary with specific client data
def ipmiPowerOn(clientData):
    resultPowerOnEncoded = subprocess.run("/usr/bin/ipmitool -I lanplus -H " 
                                                + clientData["ipmi_ip"] 
                                                + " -U " + clientData["ipmi_username"] 
                                                + " -P " + clientData["ipmi_password"] 
                                                + " power on", capture_output=True, shell=True)
    return resultPowerOnEncoded