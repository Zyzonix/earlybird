#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 27-02-2024 09:42:43
# 
# file          | scripts/mail.py
# project       | earlybird
# file version  | 1.0
#
import traceback
from datetime import datetime

# import custom scripts
from scripts import hostinformationHandler
from config import *
from scripts.logHandler import logging

class mailHandler():

    # main mail builder
    def buildMail(wolClientsToWakeup, 
                  ipmiClientsToWakeup, 
                  awakeWoLList, 
                  awakeIPMIList, 
                  successfulIPMIwakeupList, 
                  failedWoLList, 
                  failedIPMIList,
                  allClientData):
        
        mailText = ""
        mailText += "earlybird - Wakeupserver | " + hostinformationHandler.getFullHostname() + "\n\n"
        mailText += "Wakeup protocol:\n"
        mailText += "Current time: " + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + "\n\n"
        mailText += "Configuration: \n" 
        mailText += "Base directory: " + BASEDIR + "\n" 
        mailText += "Client configuration file: " + SERVERSPATH + "\n"
        mailText += "earlybird-Server: " + SERVERIP + "\n" 
        mailText += "Systemservices Webserver: earlybird-server\n" 
        mailText += "Systemservices Wakeup: earlybird-wakeup\n" 
        mailText += "\n-----------------------\n"

        if awakeWoLList:
            mailText += "\nSuccessfully woke up the follwing hosts via WoL:\n"
            for client in awakeWoLList.keys():
                mailText += "[WoL] " + client + " (" + str(allClientData[client]["server_ip"]) + ") [" + allClientData[client]["mac"] + "] - " + awakeWoLList[client] + "\n"
            mailText += "\n"

        if failedWoLList:
            mailText += "\nFailed to wake up the follwing hosts via WoL:\n"
            for client in failedWoLList.keys():
                mailText += "[WoL] " + client + " (" + str(allClientData[client]["server_ip"]) + ") [" + allClientData[client]["mac"] + "] - " + failedWoLList[client] + "\n"
            mailText += "\n"
        
        if awakeIPMIList:
            mailText += "\nSuccessfully woke up the follwing hosts via IPMI:\n"
            for client in awakeIPMIList.keys():
                if allClientData[client]["server_ip"]: 
                    mailText += "[IPMI] " + client + " (" + str(allClientData[client]["server_ip"]) + "), IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - " + awakeIPMIList[client] + "\n"
                else: 
                    mailText += "[IPMI] " + client + ", IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - " + awakeIPMIList[client] + "\n"
            mailText += "\n"
        
        if successfulIPMIwakeupList:
            mailText += "\nSuccessfully woke up the following hosts via IPMI but cannot ping them (IP might not be provided):\n"
            for client in successfulIPMIwakeupList:
                if allClientData[client]["server_ip"]: 
                    mailText += "[IPMI] " + client + " (" + str(allClientData[client]["server_ip"]) + "), IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - Cannot ping host OS\n"
                else: 
                    mailText += "[IPMI] " + client + " (no IP provided), IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - IPMI boot command sent successfully\n"
            mailText += "\n"
        
        if failedIPMIList:
            mailText += "\nFailed to wake up the follwing hosts via IPMI:\n"
            for client in failedIPMIList.keys():
                if allClientData[client]["server_ip"]: 
                    mailText += "[IPMI] " + client + " (" + str(allClientData[client]["server_ip"]) + "), IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - " + awakeIPMIList[client] + "\n"
                else: 
                    mailText += "[IPMI] " + client + ", IPMI-IP: " + allClientData[client]["ipmi_ip"] + " - " + failedIPMIList[client] + "\n"
            mailText += "\n"

        if wolClientsToWakeup or ipmiClientsToWakeup: mailText += "\n-----------------------"
        if wolClientsToWakeup:
            mailText += "\nAll WoL-Clients to wakeup were:\n"
            for client in wolClientsToWakeup:
                mailText += "- " + client + "\n"

        if ipmiClientsToWakeup:
            mailText += "\nAll IPMI-Clients to wakeup were:\n"
            for client in ipmiClientsToWakeup:
                mailText += "- " + client + "\n"
        
        if not (wolClientsToWakeup and ipmiClientsToWakeup):
            mailText += "\nNo clients to wakeup found...\n\n"

        mailText += "-----------------------\n"
        mailText += "All configured hosts can also be waked up manually in the webinterface of: http://" + hostinformationHandler.getFullHostname() + "/"
        mailText += "\n"
        mailText += "earlybird Version: " + VERSION + "\n"
        mailText += "Source code: https://github.com/Zyzonix/earlybird/"
        return mailText


    def sendMail(wolClientsToWakeup, 
                ipmiClientsToWakeup, 
                awakeWoLList, 
                awakeIPMIList, 
                successfulIPMIwakeupList, 
                failedWoLList, 
                failedIPMIList,
                allClientData):
        
        if AUTH and EMAILRECEIVER and EMAILSENDER and MAILUSER and MAILSERVER and MAILPASSWORD and MAILSERVERPORT:
            # only import if enabled
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.header import Header

            logging.write("Building mail...")

            if AUTH:
                smtp = smtplib.SMTP(MAILSERVER)
                smtp.connect(MAILSERVER, MAILSERVERPORT)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login(MAILUSER, MAILPASSWORD)
                
            else:
                smtp = smtplib.SMTP()
                smtp.connect(MAILSERVER, MAILSERVERPORT)
            
            subject = "earlybird - Wakeup Results"
            msgRoot = MIMEMultipart("alternative")
            msgRoot['Subject'] = Header(subject, "utf-8")
            msgRoot['From'] = EMAILSENDER
            msgRoot['To'] = EMAILRECEIVER
            mailContent = mailHandler.buildMail(wolClientsToWakeup, 
                                                ipmiClientsToWakeup,
                                                awakeWoLList, 
                                                awakeIPMIList,
                                                successfulIPMIwakeupList, 
                                                failedWoLList,
                                                failedIPMIList,
                                                allClientData)
            
            mailText = MIMEText(mailContent, "plain", "utf-8")
            msgRoot.attach(mailText)

            try:
                smtp.sendmail(MAILUSER, EMAILRECEIVER, msgRoot.as_string())
                logging.write("Sent mail successfully to " + EMAILRECEIVER)
            except:
                logging.writeError("Failed to send mail to " + EMAILRECEIVER + " | Check your settings!")
                logging.writeExecError(traceback.format_exc())
            
        else:
            logging.write("Mailing disabled or not configured properly.")

