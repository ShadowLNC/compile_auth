import os
wd = os.path.dirname(os.path.abspath(__file__)) #working directory
os.chdir(wd)

from configparser import ConfigParser
config = ConfigParser(
    {"authfile": "../authorised_keys", "keyfolder": "../individual_keys"})
#try multiple config locations, preferred ../compile_auth.cfg
#note all paths are relative to this file!
config.read(["config", "compile_auth.cfg", "../compile_auth.cfg"])
mainCFG = config["DEFAULT"]

if "GDRIVE" in config:
    #download from Google Drive
    from drive_fetch import *
    driveCFG = config["GDRIVE"]
    credentials = getCredentials(driveCFG.get("credentials"),
                     driveCFG.getboolean("use-service-account", fallback=False),
                     driveCFG.get("scope",
                     fallback="https://www.googleapis.com/auth/drive.readonly"))
    tmpfolder = getFolder(getDrive(credentials), driveCFG.get("drivefolder"),
                          validTypes=["application/octet-stream", "text/plain"])
    #download then move, this prevents half-downloads and removal of old keys
    replaceKeys(mainCFG.get("keyfolder"), driveCFG.get("subfolder"),
                tmpfolder, driveCFG.get("keyarchive", fallback=None))

with open(mainCFG.get("authfile"), "w") as authfile:
    for dirpath,dirnames,filenames in os.walk(mainCFG.get("keyfolder")):
        
        #foreach file
        for f in filenames:
            with open(os.path.join(dirpath,f)) as file:
                authfile.write(file.read()+"\n") #using authfile to store all

