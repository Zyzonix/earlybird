#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 27-07-2023 21:52:48
# 
# file          | wakeup.py
# project       | wolserver
# file version  | 1.0
#
import traceback
from datetime import datetime
import sys, time
import subprocess

# import custom scripts
from scripts import hostinformationHandler
from scripts import configHandler
from scripts import commands
from scripts import mail
from scripts.logHandler import logging
from config import *


# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime

# only functions which collect data
class utils():

    # prints all clients
    def printClientInformation(clients):
        logging.write("")
        wolClients = []
        ipmiClients = []

        for client in clients.keys():
            if clients[client]["type"] == "wol":
                wolClients.append("[WoL] " + client.upper() + " [" + clients[client]["mac"] + "] (Autowakeup: " + str(clients[client]["autowakeup"]) + ")")
            elif clients[client]["type"] == "ipmi":
                ipmiClients.append("[IPMI] " + client.upper() + " [IPMI-IP: " + clients[client]["ipmi_ip"] + "] (Autowakeup: " + str(clients[client]["autowakeup"]) + ")")

        if wolClients or ipmiClients: logging.write("Properly configured clients:")
        if wolClients: logging.write("Wake-on-LAN clients:")
        for client in wolClients: logging.write(client)

        if ipmiClients: logging.write("IPMI clients:")
        for client in ipmiClients: logging.write(client)

        logging.write("")
        logging.write("If clients are missing check config!")

# handle wakeup of servers
class handleWakeup():
    
    # client = dict with client specific config
    def wakeupClient(clientName, clientData):
        
        # boolean, if true = retry wakeup (only for WoL required) if false = no retry required
        returnValue = ""
        reason = ""

        if clientData["type"] == "wol":
            resultEncoded = commands.wakeOnLAN(clientData["mac"])
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]

            if "is not a hardware address" in resultErr:
                logging.writeError("[WoL] Failed to wakeup " + clientName)
                logging.writeError(resultErr)
                returnValue = False
                reason = "failed"
            else:
                logging.write("[WoL] " + result)
                returnValue = True
                reason = "success"

        elif clientData["type"] == "ipmi":
            # check if device is already powered on --> check status
            resultPowerOnEncoded = commands.ipmiPowerOn(clientData)
            resultPowerOn = resultPowerOnEncoded.stdout.decode()[:-1]
            resultPowerOnErr = resultPowerOnEncoded.stderr.decode()[:-1]

            # if not already on, power it on an check status
            if not "Chassis Power is on" in resultPowerOn and not "Unable to establish IPMI v2" in resultPowerOnErr:

                resultPowerOnEncoded = commands.ipmiPowerOn(clientData)
                time.sleep(2)
                resultPowerStatusEncoded = commands.ipmiPowerStatus(clientData)
            
                resultPowerOn = resultPowerOnEncoded.stdout.decode()[:-1]
                resultPowerOnErr = resultPowerOnEncoded.stderr.decode()[:-1]
                resultPowerStatus = resultPowerStatusEncoded.stdout.decode()[:-1]
                
                if "Chassis Power Control: Up/On" in resultPowerOn and "" == resultPowerOnErr and "Chassis Power is on" in resultPowerStatus:
                    logging.write("[IPMI] Sent wake up command to IPMI console - Server wakeup successful!")
                    reason = "success"

            
                # if device is not powered on and ipmitool command fails
                else:
                    if resultPowerOn: 
                        logging.writeError("[IPMI] Result power on: " + resultPowerOn)    
                    if resultPowerOnErr: 
                        logging.writeError("[IPMI] Result power on: " + resultPowerOnErr)    
                    logging.writeError("[IPMI] IPMI boot command of " + clientName + " failed - check config.")
                    reason = "failed"

            # if devide already powered on                 
            elif "Chassis Power is on" in resultPowerOn:
                logging.write(clientName + " already powered on")
                reason = "failed"
            
            # if ipmitool command fails
            else: 
                if resultPowerOnErr: 
                    logging.writeError("[IPMI] Result power on: " + resultPowerOnErr)
                    reason = "failed"

            # set returnValue to False because if already on or config wrong not retry required!
            # retry for IPMI not required!
            returnValue = False

        else: 
            returnValue = False
            reason = "failed"

        return returnValue, reason

    # returns true if is pingable
    def pingHost(client, ip):
        try:
            resultEncoded = subprocess.run("/usr/bin/ping -c2 " + ip, capture_output=True, shell=True)
            returnCode = resultEncoded.returncode
            if returnCode == 0: 
                return True
            else: return False

        except:
            logging.writeError("Failed to ping " + client + " (" + str(ip) + ")")
            logging.writeExecError(traceback.format_exc())
            return False

    # main instance
    def runner(clients, forceWakeupAll):
        
        # general lists
        statusWoLUnknownList = []
        statusIPMIUnknownList = []

        # dict of servers that are aleady pingable
        awakeWoLList = {}
        awakeIPMIList = {}

        # list of successful IPMI wakeups but not pingable
        successfulIPMIwakeupList = []

        # list of servers that failed to wakeup 
        failedWoLList = {}
        failedIPMIList = {}

        if forceWakeupAll:
            for client in clients:
                if clients[client]["type"] == "wol": statusWoLUnknownList.append(client)
                elif clients[client]["type"] == "ipmi": statusIPMIUnknownList.append(client)

        else: 
            for client in clients:
                if clients[client]["autowakeup"]: 
                    if clients[client]["type"] == "wol": statusWoLUnknownList.append(client)
                    elif clients[client]["type"] == "ipmi": statusIPMIUnknownList.append(client)

        # save servers list from beginning for mail
        if MAILENABLED: 
            wolClientsToWakeup = []
            ipmiClientsToWakeup = []
            for client in statusWoLUnknownList: wolClientsToWakeup.append(client)
            for client in statusIPMIUnknownList: ipmiClientsToWakeup.append(client)


        # get config setting into var
        RETRIESLEFT = RETRYCOUNT

        while RETRIESLEFT > 0:
            logging.write("Wakeup intervals left: " + str(RETRIESLEFT - 1))

            # first add all clients to a separate list which will be the base for the loop
            localStatusWoLUnknownList = []
            if statusWoLUnknownList:
                for client in statusWoLUnknownList:
                    localStatusWoLUnknownList.append(statusWoLUnknownList)

                for client in localStatusWoLUnknownList:
                    logging.write("[WoL] Trying to wake up " + client)
                    # check if pingable, if yes, remove from unknownList and add to successful dict
                    pingable = handleWakeup.pingHost(client, clients[client]["server_ip"])
                    
                    if pingable:
                        logging.write("[WoL] Can ping " + client + " (" + str(clients[client]["server_ip"]) + ")")
                        awakeWoLList[client] = "Client running (" + clients[client]["server_ip"] + ")" 
                        statusWoLUnknownList.remove(client)
                    
                    else:
                        logging.write("[WoL] Cannot ping " + client + " (" + str(clients[client]["server_ip"]) + ")")
                        returnValue, reason = handleWakeup.wakeupClient(client, clients[client])
                        if not returnValue:
                            if reason == "failed":
                                failedWoLList[client] = "Wakeup failed"
                                statusWoLUnknownList.remove(client)

            # first add all clients to a separate list which will be the base for the loop
            localStatusIPMIUnknownList = []
            if statusIPMIUnknownList:
                for client in statusIPMIUnknownList:
                    localStatusIPMIUnknownList.append(statusIPMIUnknownList)

                for client in localStatusIPMIUnknownList:
                    logging.write("[IPMI] Trying to wake up " + client)
                    # check if pingable, if yes, remove from unknownList and add to successful dict
                    if clients[client]["server_ip"]: pingable = handleWakeup.pingHost(client, clients[client]["server_ip"])
                    else: pingable = False

                    if pingable:
                        logging.write("[IPMI] Can ping " + client + " (" + str(clients[client]["server_ip"]) + ")")
                        awakeIPMIList[client] = "Client running"
                        statusIPMIUnknownList.remove(client)

                    else:
                        returnValue, reason = handleWakeup.wakeupClient(client, clients[client])
                        if not returnValue:
                            
                            if reason == "failed":
                                failedIPMIList[client] = "Failed to connect via IPMI - check config!"
                                statusIPMIUnknownList.remove(client)     
                            
                            elif reason == "success":

                                # add to list, to check if host ist pingable later
                                successfulIPMIwakeupList.append(client)
                                statusIPMIUnknownList.remove(client)
                
            for client in successfulIPMIwakeupList:

                # try pinging clients waked up with IPMI
                if clients[client]["server_ip"]: 
                    pingable = handleWakeup.pingHost(client, clients[client]["server_ip"])
                
                    if pingable:
                        logging.write("[IPMI] Can ping " + client + " (" + str(clients[client]["server_ip"]) + ")")
                        awakeIPMIList[client] = "Client running"
                        successfulIPMIwakeupList.remove(client)

            # break if last run
            if RETRIESLEFT == 1: 
                for client in statusWoLUnknownList:
                    failedWoLList[client] = "Failed to wakeup after " + str(RETRYCOUNT) + " retries"
                    statusWoLUnknownList.remove(client)
                    logging.writeError("[WoL] Failed to wakeup " + client + " after " + str(RETRYCOUNT) + " intervals.")
                if not (statusWoLUnknownList and statusIPMIUnknownList or awakeWoLList or awakeIPMIList or failedWoLList or failedIPMIList):
                    logging.writeError("Not all lists are empty:")
                    logging.writeError("statusWoLUnknownList: " + str(statusWoLUnknownList))
                    logging.writeError("statusIPMIUnknownList: " + str(statusIPMIUnknownList))  
                    logging.writeError("awakeWoLList: " + str(awakeWoLList))  
                    logging.writeError("awakeIPMIList: " + str(awakeIPMIList))  
                    logging.writeError("failedWoLList: " + str(failedWoLList))  
                    logging.writeError("failedIPMIList: " + str(failedIPMIList))      
                break

            # check if lists are still containing clients, if not, break
            if not statusWoLUnknownList and not statusIPMIUnknownList and not successfulIPMIwakeupList:
                logging.write("Finished waking up all clients")
                RETRIESLEFT = 1
                break

            logging.write("Going to sleep for " + str(WAKEUPINTERVAL) + "s")
            time.sleep(WAKEUPINTERVAL)
            RETRIESLEFT -= 1

        # start to build final mail, if enabled
        if MAILENABLED: mail.mailHandler.sendMail(
            wolClientsToWakeup, 
            ipmiClientsToWakeup,
            awakeWoLList, 
            awakeIPMIList,
            successfulIPMIwakeupList, 
            failedWoLList,
            failedIPMIList,
            clients)

class wakeup():

    # initialization function
    def __init__(self):

        logging.write("Starting earlybird wakeup")
        logging.write("Running on " + hostinformationHandler.getFullHostname())

        # retrieve registered servers
        clients = configHandler.getClientsFomConfig(False)
        if not clients: 
            logging.writeError("No clients found - check config.")
            return

        if len(sys.argv) == 3:

            # all equals no third argument
            if sys.argv[2] == "all":
                logging.write("Trying to wakeup all servers")
                
                # wakeup all clients (ignore autowakeup!)
                handleWakeup.runner(clients, True)

            # only list all hosts configured in config
            elif sys.argv[2] == "list":
                utils.printClientInformation(clients)
            
            # wakeup one specific server
            else:
                if not sys.argv[2].upper() in clients.keys(): 
                    logging.writeError("Server is not registered in config file (servers.ini)")
                else:
                    clientData = clients[sys.argv[2].upper()]
                    handleWakeup.wakeupClient(sys.argv[2].upper(), clientData)
        
        # wakeup all hosts as usual (autowakeup sensitive)
        else:
            logging.write("Starting controlled wakeup")
            handleWakeup.runner(clients, False)

if __name__ == "__main__":
    wakeup() 