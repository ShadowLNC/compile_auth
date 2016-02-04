from oauth2client import client as oauth2
from oauth2client.file import Storage
import json

def make_flow(secrets, scope, store=None):
    #make flow
    flow = oauth2.flow_from_clientsecrets(secrets, scope=scope,
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')
    
    #get auth, exchange for tokens
    auth_uri = flow.step1_get_authorize_url()
    print("Copy the URL, then paste the authorisation code below:\n" + auth_uri)
    auth_code = input("Authorisation Code: ")
    credentials = flow.step2_exchange(auth_code)

    #store and return
    if store and type(store)==str: store = Storage(store) #allow from filename
    if store:
        credentials.set_store(store)
        store.put(credentials)
    return credentials

def from_store(filepath):
    store = Storage(filepath)
    return store.get()

def service_account(filepath, scope, sub=None):
    with open(filepath, "r") as f: sa_details = json.load(f)
    sa_details["service_account_name"] = sa_details["client_email"] #snafu fix
    sa_details["scope"] = scope
    if sub: sa_details["sub"] = sub
    return oauth2.SignedJwtAssertionCredentials(**sa_details)
