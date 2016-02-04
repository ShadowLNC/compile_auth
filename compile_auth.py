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
    #we have a drive configuration and should use it
    pass #todo: implement

with open(mainCFG.get("authfile"), "w") as authfile:
    for dirpath,dirnames,filenames in os.walk(mainCFG.get("keyfolder")):
        
        #foreach file
        for f in filenames:
            with open(os.path.join(dirpath,f)) as file:
                authfile.write(file.read()+"\n") #using authfile to store all

