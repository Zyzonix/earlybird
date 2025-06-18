#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2024 ZyzonixDevelopments
#
# date created  | 19-02-2024 12:35:29
# 
# file          | scripts/pagebuilder.py
# project       | earlybird
# file version  | 1.0.0
#
import subprocess
import time
import traceback

# import custom scripts
from scripts import hostinformationHandler
from scripts import configHandler
from scripts import commands
from config import *
from scripts.logHandler import logging

# default page
def startpage(request):
    hostname = hostinformationHandler.getFullHostname()
        
    answer = ""

    logging.write("Got request from: " + str(request.client.host) + " of " + hostname + "/")
    # <link rel="icon" type="image/x-icon" href="/favicon.ico">
    header = '''<html><head><title>earlybird - ''' + hostname + '''</title><link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
    p { font-family: Arial }
    table, th, ts { 
        font-family: Arial;
        border: none; 
        text-align: left; 
        min-width: 40%;
    }
    tr:nth-child(even) {
        background-color: #e0e0eb;
    }
    </style></head><body><h1>''' + hostname + ''' | IPMI/Wake-on-LAN-Server</h1><p>Please click on the hostname of the server you want to wakeup.</p>'''
    header += "<hr>"

    answer += header

    # providing False collects all clients
    clients = configHandler.getClientsFomConfig(False)

    foundClientsWithWol = False
    foundClientsWithIPMI = False

    # build custom panels
    body = ""
    wol = ""
    ipmi = ""
    footer = ""

    # if any clients configured
    if clients:
        wol += "<h3>Registered servers for Wake-on-LAN:</h3>"
        wol += "<table>"
        wol += "<tr>"
        wol += "<th>Hostname</th>"
        wol += "<th>Description</th>"
        wol += "<th>MAC</th>"
        wol += "<th>Server-IP</th>"
        wol += "<th>Autowakeup enabled</th>"
        wol += "</tr>"
        for client in clients:
            if clients[client]["type"] == "wol":
                foundClientsWithWol = True

                wol += "<tr>"
                wol += "<td><a href='http://" + hostname + "/wol/" + client + "'> " + client + "</a></td>"
                description = "-"
                if clients[client]["description"]: description = clients[client]["description"]
                wol += "<td>" + str(description) +"</td>"
                wol += "<td>" + clients[client]["mac"] +"</td>"
                ip = "unknown"
                if clients[client]["client_ip"]: ip = clients[client]["client_ip"]
                wol += "<td>" + str(ip) +"</td>"
                autowakeup = "unknown"
                if clients[client]["autowakeup"] != "": autowakeup = clients[client]["autowakeup"]
                wol += "<td>" + str(autowakeup) +"</td>"
                wol += "</tr>"
        wol += "</table><br>" 

        if not foundClientsWithWol:
            body += "<hr><p>No clients configured for Wake-on-LAN-Control. (Check logs if this is an issue)</p><hr>"
        else: answer += wol

        ipmi += "<h3>Registered servers for IPMI-Control:</h3>"
        ipmi += "<table>"
        ipmi += "<tr>"
        ipmi += "<th>Hostname</th>"
        ipmi += "<th>IPMI-IP</th>"
        ipmi += "<th>Autowakeup enabled</th>"
        ipmi += "<th>Client-IP</th>"
        ipmi += "</tr>"
        for client in clients:
            if clients[client]["type"] == "ipmi":
                foundClientsWithIPMI = True

                ipmi += "<tr>"
                ipmi += "<td><a href='http://" + hostname + "/ipmi/" + client + "'> " + client + "</a></td>"
                ipmi += "<td>" + clients[client]["ipmi_ip"] +"</td>"
                if clients[client]["autowakeup"] != "": autowakeup = clients[client]["autowakeup"]
                ipmi += "<td>" + str(autowakeup) +"</td>"
                ipmi += "<td>" + clients[client]["client_ip"] +"</td>"
                ipmi += "</tr>"
        ipmi += "</table><br>" 
        if not foundClientsWithIPMI:
            body += "<hr><p>No clients configured for IPMI-Control/Wakeup. (Check logs if this is an issue)</p><hr>"
        else: answer += ipmi

        logging.write("Retrieved table successfully")
    
    else:
        footer += "<p>Cannot read servers from config file, edit under:  " + SERVERSPATH + "</p>"
        logging.writeError("Cannot read servers from config file, edit under: " + SERVERSPATH)

    footer += "<p>For changing autowakeup or adding additional servers edit '" + SERVERSPATH + "' manually.</p>"
    footer += "<hr><p>earlybird v" + VERSION +" from: <a href='https://github.com/Zyzonix/earlybird'>github.com/Zyzonix/earlybird</a></p></body></html>"
    
    # add footer and body (body might be empty)
    answer += body + footer
    return answer

# wol subpage
def wol(clientName, request):
    hostname = hostinformationHandler.getFullHostname()

    logging.write("Got request from: " + str(request.client.host) + " of " + hostname + "/")
    resp = '''<html><head><title>earlybird - ''' + hostname + '''</title><link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
    p { font-family: Arial }
    table, th, ts { 
        font-family: Arial;
        border: none; 
        text-align: left; 
        min-width: 40%;
    }
    tr:nth-child(even) {
        background-color: #e0e0eb;
    }
    </style></head><body>'''

    # get specific client information
    clientData = configHandler.getClientsFomConfig(clientName) 
    
    if clientData:
        try:
            mac = clientData["mac"]
            resultEncoded = commands.wakeOnLAN(mac)
            result = resultEncoded.stdout.decode()[:-1]
            resultErr = resultEncoded.stderr.decode()[:-1]
            if "is not a hardware address" in resultErr:
                logging.writeError("Failed to wakeup " + clientName)
                logging.writeError(resultErr)
                raise
            else:
                logging.write(result)
                resp += "<p>Tried waking up " + clientName + " [" + mac + "]</p>"            
                resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p>"
        except:
            resp += "<p>Failed to wake up " + clientName + "</p>"
            resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p>"
    else:
        resp += "<p>Was not able to read config file under " + SERVERSPATH + " - Client not found: " + clientName + "</p>"
        resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p></body></html>"

    return resp

# ipmi subpage
def ipmi(clientName, request):
    hostname = hostinformationHandler.getFullHostname()

    logging.write("Got request from: " + str(request.client.host) + " of " + hostname + "/")
    resp = '''<html><head><title>earlybird - ''' + hostname + '''</title><link rel="icon" type="image/x-icon" href="/favicon.ico">
    <style>
    p { font-family: Arial }
    table, th, ts { 
        font-family: Arial;
        border: none; 
        text-align: left; 
        min-width: 40%;
    }
    tr:nth-child(even) {
        background-color: #e0e0eb;
    }
    </style></head><body>'''

    # get specific client information
    clientData = configHandler.getClientsFomConfig(clientName)

    if clientData:
        if clientData["type"] == "ipmi":
            try:
                # check if device is already powered on --> check status
                resultPowerStatusEncoded = commands.ipmiPowerStatus(clientData)
                
                resultPowerStatus = resultPowerStatusEncoded.stdout.decode()[:-1]
                resultPowerStatusErr = resultPowerStatusEncoded.stderr.decode()[:-1]

                # if not already on, power it on an check status
                if not "Chassis Power is on" in resultPowerStatus and not "Unable to establish IPMI v2" in resultPowerStatusErr:
                    resultPowerOnEncoded = commands.ipmiPowerOn(clientData)
                    time.sleep(2)
                    resultPowerStatusEncoded = commands.ipmiPowerStatus(clientData)
                
                    resultPowerOn = resultPowerOnEncoded.stdout.decode()[:-1]
                    resultPowerOnErr = resultPowerOnEncoded.stderr.decode()[:-1]
                    resultPowerStatus = resultPowerStatusEncoded.stdout.decode()[:-1]
                    
                    if "Chassis Power Control: Up/On" in resultPowerOn and "" == resultPowerOnErr and "Chassis Power is on" in resultPowerStatus:
                        resp += "<h3>Successful!</h3><p>IPMI-Status of " + clientName + " is: " + resultPowerStatus + "</p>"            
                        logging.write("Sent wake up command to IPMI console")
                        logging.write("Server wakeup successful!")
                
                    # if device is not powered on and ipmitool command fails
                    else:
                        resp += "<h3>Failed!</h3><p>Failed to initialize boot of " + clientName + " (IPMI-IP: " + clientData["ipmi_ip"] + ") " + " by IPMI - <b>check config!</b></p>" 
                        if resultPowerOn: 
                            resp += "<p>Command output: <i>" + resultPowerOn + "</i></p>"
                            logging.writeError("Result power on: " + resultPowerOn)    
                        if resultPowerOnErr: 
                            resp += "<p>Command output: <i>" + resultPowerOnErr + "</i></p>"
                            logging.writeError("Result power on: " + resultPowerOnErr)    
                        logging.writeError("IPMI boot command of " + clientName + " failed - check config.")

                    logging.writeError("ipmiPowerStatus Output:")
                    logging.writeError("- resultPowerOn: " + str(resultPowerOn))
                    logging.writeError("- resultPowerOnErr: " + str(resultPowerOnErr))
                    logging.writeError("- resultPowerStatus: " + str(resultPowerStatus))

                # if devide already powered on                 
                elif "Chassis Power is on" in resultPowerStatus:
                    resp += "<h3>Successful!</h3><p>Device already running: IPMI-Status of " + clientName + " is: " + resultPowerStatus + "</p>"
                    logging.write(clientName + " already powered on")
                
                # if ipmitool command fails
                else: 
                    resp += "<h3>Failed!</h3><p>Failed to initialize boot of " + clientName + " (IPMI-IP: " + clientData["ipmi_ip"] + ") " + " by IPMI - <b>check config!</b></p>" 
                    if resultPowerStatusErr: 
                        resp += "<p>Command output: <i>" + resultPowerStatusErr + "</i></p>"
                        logging.writeError("Result power on: " + resultPowerStatusErr)
            
                resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p>"
            
            # if fails to execute any ipmitool command
            except:
                resp += "<p>Failed to wake up " + clientName + "</p>"
                resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p>"
        
        # if client not configured for ipmi
        else:
            resp += "<p>Client is not configured for IPMI.</p>"
            resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p>"
    else:
        resp += "<p>Was not able to read config file under " + SERVERSPATH + "</p>"
        resp += "<p>Return to: <a href='http://" + hostname + "/'>" + hostname + "</a></p></body></html>"
    return resp  
