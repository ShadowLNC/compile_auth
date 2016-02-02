import os
wd = os.path.dirname(os.path.abspath(__file__)) #working directory
os.chdir(wd)

from configparser import ConfigParser
config = ConfigParser(
    {"authfile": "../authorised_keys", "keyfolder": "individual_keys"})
config.read(["config", "../config"]) #try either spot

if "GDRIVE" in config:
    #we have a drive configuration and should use it
    pass #todo: implement

mainCFG = config["DEFAULT"]
with open(mainCFG.get("authfile"), "w") as authfile:
    #using authfile to store all
    for dirpath,dirnames,filenames in os.walk(mainCFG.get("keyfolder")):
        for f in filenames:
            with open(os.path.join(dirpath,f)) as file:
                authfile.write(file.read()+"\n")
