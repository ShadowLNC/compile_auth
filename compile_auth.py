from os import path, walk
wd = path.dirname(path.abspath(__file__)) #working directory
with open(path.join(wd,"../authorized_keys"), "w") as authfile:
    #using authfile to store all
    for dirpath,dirnames,filenames in walk(path.join(wd,"individual_keys")):
        for f in filenames:
            with open(path.join(dirpath,f)) as file:
                authfile.write(file.read()+"\n")
