#API calls
from httplib2 import Http
from apiclient.discovery import build as buildService
import io
from apiclient.http import MediaIoBaseDownload

#misc
from simpleAuth import from_store,service_account
from datetime import datetime
import shutil
import tempfile
import re
import os

def getFolder(drive, folderId, validTypes=[], exportTypes={}, target=None):
    """A note on recursion
        We could get a list of all subfolders at level n
        and then use a batch request to list them all,
        however this would complicate the recursion, and
        besides, for a heavily nested folder, every file
        must still be downloaded individually, meaning
        that any savings by using the batch request would
        be insignificant compared to the number of files
        downloaded.

        By not using batch requests, we eliminate
        complexity, albeit at a slightly increased cost
        in requests. (Callback function is also avoided.)
        
        Neither this function, nor the Drive API, are
        designed to download large amounts of data. You
        will be limited by recursion limits in addition
        to API quotas; if you really need to download
        complex file structures, it's recommended that
        you use an iterative strategy instead.
    """

    #make temporary target, or if specified, check empty/not exists
    if target is None: target = tempfile.mkdtemp()
    elif os.path.isdir(target):
        if os.listdir(target): raise ValueError("Download Target not Empty")
    else: os.mkdir(target)

    #get folder's filelist
    files = drive.files()
    filelist = []
    #the value for q could filter mimeTypes but makes query long and
    #doesn't do much for efficiency as we check each mimeType regardless
    req = files.list(q="'"+folderId+"' in parents", pageSize=1000,
                     fields="files(id,mimeType,name),nextPageToken")
    #get each page and compile list
    while req:
        res = req.execute()
        filelist += res["files"]
        req = files.list_next(req, res)
    
    #get each file
    for f in filelist:
        
        #fix invalid chars
        newname = re.sub("(^-)|[^a-zA-Z0-9\._\-]|(\.$)", "_", f["name"])
        newpath=os.path.join(target,newname)

        #prevent duplicates
        if os.path.isfile(newpath):
            #already exists, add a numeric identifier before file extension
            dot = newname.rfind(".")
            if dot<0: dot = len(newname) #causes correct behaviour if no dot
            fname = newname[:dot]
            ext = newname[dot:] #if no dot this will be ''; "a"[5:]==''
            copy = 0 #incremented before test
            
            #test each number in case multiple duplicates
            while os.path.isfile(newpath):
                #will run at least once since we didn't update newname yet
                copy += 1
                newname = "{}_{}{}".format(fname,copy,ext)
                newpath=os.path.join(target,newname)
        
        #check mimeType and handle
        if f["mimeType"]=="aplication/vnd.google-apps.folder":
            #create a subfolder and recurse
            mkdir
            getFolder(drive, f["id"], validTypes, exportTypes, newpath)
            continue
        if f["mimeType"] in validTypes:
            req = files.get_media(fileId=f["id"])#, acknowledgeAbuse=True)
        elif f["mimeType"] in exportTypes:
            req = files.export(fileId=f["id"],
                               mimeType=exportTypes[f["mimeType"]])
        else: continue #not wanted

        #download - io.BytesIO()/inherits BufferedIOBase
        with open(newpath, "wb") as fh:
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while done is False: status, done = downloader.next_chunk()
            #with open(newpath, "wb") as f2: f2.write(fh.read()) #write
    return target

def getCredentials(credentialsPath, serviceAcc=False, scope=""):
    #generate credentials; scope only required for service accounts
    if serviceAcc: credentials = service_account(credentialsPath, scope)
    else: credentials = from_store(credentialsPath)
    return credentials

def getDrive(credentials):
    #generate drive object
    http_auth = credentials.authorize(Http())
    drive = buildService('drive', 'v3', http=http_auth)
    return drive

def replaceKeys(key_root, subfolder, new_folder, archive_root=None):
    #archive old, move new
    curfolder = os.path.join(key_root, subfolder)
    
    if not os.path.isdir(curfolder): pass #will be created, can't archive/delete
    elif archive_root is None: shutil.rmtree(curfolder) #delete old, no archive
    else:
        #first check that archive folder+subfolder exist
        if not os.path.isdir(archive_root): os.mkdir(archive_root)
        if not os.path.isdir(os.path.join(archive_root, subfolder)):
            os.mkdir(os.path.join(archive_root, subfolder))

        #now move to datestamped sub-subfolder
        #windows disallows : and [:19] chops microseconds; using local tz
        timestamp = datetime.now().isoformat()[:19].replace(":","_")
        arcfolder = os.path.join(archive_root, subfolder, timestamp)
        shutil.move(curfolder, arcfolder)
    shutil.move(new_folder, curfolder) #move new keys in

#if file is run directly, generate credentials with default scope
if __name__ == "__main__":
    from simpleAuth import make_flow
    import os
    secrets = input("Path to client secrets file (include file):\n>")
    os.chdir( os.path.dirname(os.path.abspath(secrets)) ) #cd to secrets folder
    scope = input("Custom scope (optional):\n>")
    if not scope: scope="https://www.googleapis.com/auth/drive.readonly" #default
    make_flow(secrets, scope, store="credentials")
    print("Use the \"credentials\" file for compile_auth")
