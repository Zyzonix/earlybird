#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 16-02-2024 11:33:15
# 
# file          | scripts/configHandler.py
# project       | earlybird
# file version  | 1.0
#
from configparser import ConfigParser
import traceback

# import custom scripts
from scripts.logHandler import logging
from config import SERVERSPATH


def clientImportData(serversImpHandler, client):
    clientData = {}
    # try to find type of wakeup: ipmi/wol
    try:
        clientType = serversImpHandler[client]["type"]

        # if client should be waked up by wake on lan
        if clientType == "wol":
            
            try:
                clientMAC = serversImpHandler[client]["mac"]
                clientAutowakeup = serversImpHandler.getboolean(client, "autowakeup")
                clientIP = serversImpHandler[client]["server_ip"]

                # add all settings to dictionary
                # check if clientAutowakeup is not empty
                if clientMAC and (clientAutowakeup != ""):
                    clientData["type"] = clientType.lower()
                    clientData["mac"] = clientMAC.lower()
                    clientData["autowakeup"] = clientAutowakeup
                    clientData["server_ip"] = clientIP
            
            except:
                logging.writeError("Configuration of host " + client + " incomplete!")

        # if client will be crontrolled with ipmi
        elif clientType == "ipmi":
            
            try: 
                clientIPMIIP = serversImpHandler[client]["ipmi_ip"]
                clientIPMIUsername = serversImpHandler[client]["ipmi_username"]
                clientIPMIPassword = serversImpHandler[client]["ipmi_password"]
                clientAutowakeup = serversImpHandler.getboolean(client, "autowakeup")
                try: 
                    clientServerIP = serversImpHandler[client]["server_ip"]
                except:
                    logging.write("No server ip configured for " + client)
                    clientServerIP = ""

                # add all settings to dictionary
                # check if clientAutowakeup is not empty
                if clientIPMIIP and clientIPMIPassword and clientIPMIUsername and (clientAutowakeup != ""):
                    clientData["type"] = clientType.lower()
                    clientData["ipmi_username"] = clientIPMIUsername
                    clientData["ipmi_password"] = clientIPMIPassword
                    clientData["ipmi_ip"] = clientIPMIIP
                    clientData["autowakeup"] = clientAutowakeup
                    clientData["server_ip"] = clientServerIP
            
            except:
                logging.writeError("Configuration of host " + client + " incomplete!")
                
        else:
            logging.writeError("Could not determine type of entry: " + client + " type=" + clientType)

        return clientData 
    
    except:
        logging.writeError("Failed to get type of entry: " + client)
        logging.writeError("Skipping...")
        return False


# lookup clients from config, if clientName provided only this client's data will be returned
def getClientsFomConfig(lookupClient):

    clients = {}
    # create config importer
    serversImpHandler = ConfigParser(comment_prefixes='/', allow_no_value=True)

    if not lookupClient == False:
        try:
            serversImpHandler.read(SERVERSPATH)
            logging.write("Found clients.ini file. (" + SERVERSPATH + ") Clients in file: " + str(serversImpHandler.sections()))
            logging.write("Looking up: " + lookupClient)

            if lookupClient in serversImpHandler.sections():
                clientData = clientImportData(serversImpHandler, lookupClient)
                
                if clientData:
                    # set dic to returned dic, because only one client should be looked up
                    clients = clientData
            else:
                logging.writeError("Client not found")
                return False

        except:
            logging.writeError("Cannot load servers config file!")
            logging.writeExecError(traceback.format_exc())
            return False
        
        return clients

    else:
        try:
            serversImpHandler.read(SERVERSPATH)
            logging.write("Found clients.ini file. (" + SERVERSPATH + ") Clients in file: " + str(serversImpHandler.sections()))
            for client in serversImpHandler.sections():
                clientData = clientImportData(serversImpHandler, client)
                if clientData:
                    clients[client] = clientData 

        except:
            logging.writeError("Cannot load servers config file!")
            logging.writeExecError(traceback.format_exc())
            return False
        
        logging.write("Got hosts: " + str(clients))
        if not clients: logging.writeError("No hosts configured - config file empty")
        return clients