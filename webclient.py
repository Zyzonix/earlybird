#!/usr/bin/env python3
#
# written by ZyzonixDev
# published by ZyzonixDevelopments
#
# Copyright (c) 2023 ZyzonixDevelopments
#
# date created  | 27-07-2023 21:53:19
# 
# file          | webclient.py
# project       | wolserver
# file version  | 1.0
#
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
from starlette.responses import FileResponse
import subprocess

# import custom scripts
from scripts import hostinformationHandler
from scripts import pagebuilder
from scripts.logHandler import logging
from config import *

hostinformationHandler.publicHostname = PUBLICSERVERNAME

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# time for logging / console out
class ctime():
    def getTime():
        curTime = "" + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        return curTime
    
# check if required packages are installed
class checkPackages():

    def packagesInstalled():
        allPackagesInstalled = True
        for package in REQUIREDAPTPACKAGES:
            resultPackageCheckEncoded = subprocess.run("/usr/bin/dpkg -s " + package, capture_output=True, shell=True) 
            resultPackageCheck = resultPackageCheckEncoded.stdout.decode()[:-1]
            resultPackageCheckErr = resultPackageCheckEncoded.stderr.decode()[:-1]
            if "is not installed" in (resultPackageCheck or resultPackageCheckErr):
                allPackagesInstalled = False

        return allPackagesInstalled

# web register points
class server():

    # general WOL info
    @app.get("/", response_class=HTMLResponse)
    async def startpage(request: Request):
        answer = pagebuilder.startpage(request)
        return answer  

    # url to wakeup with wake on lan
    @app.get("/wol/{clientName}", response_class=HTMLResponse)
    async def wol_init(clientName, request: Request):
        answer = pagebuilder.wol(clientName, request)
        return answer

    # url to wakeup with IPMI
    @app.get("/ipmi/{clientName}", response_class=HTMLResponse)
    async def ipmi_init(clientName, request: Request):
        answer = pagebuilder.ipmi(clientName, request)
        return answer
    
    # favicon page
    @app.get('/favicon.ico')
    async def favicon():
        return FileResponse(BASEDIR + "favicon.ico") #full path here to make icon work 
    

    # initialize server
    def __init__(self):
        logging.write("Running earlybird version: " + VERSION)
        logging.write("Initializing webserver on " + hostinformationHandler.getFullHostname())

        # check if required packages are installed:
        if not checkPackages.packagesInstalled():
            logging.writeError("Not all required packages " + str(REQUIREDAPTPACKAGES) + " are installed, exiting.")
            return

        uvicorn.run(app, port=80, host=SERVERIP)


# init server class
if __name__ == "__main__":
    server()