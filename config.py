#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 19-02-2024 12:08:26
# 
# file          | config.py
# project       | earlybird
# file version  | 1.0.0
#

#-----------------------------
# Only config parameters here!
#-----------------------------

# software version
VERSION="1.0"

# base directory
# PATHS must end with '/'!
BASEDIR = "/opt/earlybird/"
SERVERSPATH = BASEDIR + "clients.ini"

# ip to bind server on
SERVERIP="<IPv4>"

# required APT packages for this tool
REQUIREDAPTPACKAGES=["ipmitool", "wakeonlan"]

# wakeupinterval in seconds
WAKEUPINTERVAL = 60

# retry count
RETRYCOUNT = 5

# MAILCONFIG
MAILENABLED = True
AUTH = True
MAILSERVER = "<mailserver>"
MAILSERVERPORT = 587
MAILUSER = "<mail-user>"
MAILPASSWORD = "<mail-passwd>"
EMAILRECEIVER = "<email-receiver-address>"
EMAILSENDER = "earlybird Server <" + MAILUSER + ">"