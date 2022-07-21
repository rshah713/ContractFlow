"""
Rohan Shah
7/14/22

Custom-made Firebase REST API wrapper in Python
Somewhat low-level as all input is sanitized through util.py wrapper funcs
so no input validation
"""

import json
import urllib.request as request
import urllib.parse as parse
import urllib.error as error
from http import client
from datetime import datetime
from authentication.auth import API_KEY, BASE_URL

class Firebase():
    def __init__(self, username, credentials):
        """
        `credentials`: dict returned by a successful login function
            - { 'kind': ...,
                'idToken': ...,
                'email' : ...,
                'expiresIn' : ...,
                'localId' : ...
                }
        `username`: the username (auto-appended to BASEURL) to write/read data
        """
        
        self.credentials = credentials
        self.username = username
        self.BASE_URL = BASE_URL
        self.API_KEY = API_KEY
        
        
        """
        BASE_URL: The base url of the entire firebase project. Appending /folderName/.json will access individual data
    
        API_KEY: Web API Key needed for creating new users, and can be used to access database in `?auth=`
        
        """
        
    def read_path(self, path=''):
        """
        `path`: path following BASE_URL, can be as nested as stored JSON allows
            - ex: meetings/appt1 (/users/{username} auto-appended)
        :returns dict with requested informaton
            - {} means path was unauthorized/not found
        """
        
        req_url = self.BASE_URL + 'users/' + self.username + '/' + path + '/.json' # .json can also be used (no difference)
        
        req_url = req_url.replace(' ', "%20")
        
        auth = {'auth' : self.credentials['idToken']}
        auth = parse.urlencode(auth)
        
        req_url += '?' + auth
        
        try:
            resp = request.urlopen(req_url)
            resp =  resp.read().decode('utf-8') # from bytes --> string
            resp = json.loads(resp) # from string --> dict
        except error.HTTPError as err:
            resp = {}
            self.log_error(str(err), path)
        except client.InvalidURL as err:
            """ printing err returns a long msg w/ path alr in there
            so we save shorthand name (https://stackoverflow.com/a/58045927/12514570)
            and the msg IS the str(err)
            """
            
            module = err.__class__.__module__
            if module is None or module == str.__class__.__module__:
                errorName = err.__class__.__name__
            errorName =  module + '.' + err.__class__.__name__
            
            resp = {}
            self.log_error(errorName, str(err))
            
        except Exception as e:
            self.log_error(str(e), path)

        if resp is None:
            resp = {}
        return resp
        
    def patch_path(self, path, data):
        """
        `path`: path to push data, for example locations or locations/Cranbury Center
        data: dict of data to dump
        """
        
        payload = json.dumps(data).encode() #dict --> json --> bytes/json
        req_url = self.BASE_URL + 'users/' + self.username + '/' + path + '/.json'
        
        req_url = req_url.replace(' ', "%20")
        
        
        auth = {'auth' : self.credentials['idToken']}
        auth = parse.urlencode(auth)
        req_url += '?' + auth
        
        
        req = request.Request(req_url, data=payload, method="PATCH")
        try:
            resp = request.urlopen(req)
            return resp.code
        except error.HTTPError as err:
            self.log_error(str(err), path)
            print(err)
        except client.InvalidURL as err:
            """ printing err returns a long msg w/ path alr in there
            so we save shorthand name (https://stackoverflow.com/a/58045927/12514570)
            and the msg IS the str(err)
            """
            
            module = err.__class__.__module__
            if module is None or module == str.__class__.__module__:
                errorName = err.__class__.__name__
            errorName =  module + '.' + err.__class__.__name__
            
            self.log_error(errorName, str(err))
            
        except Exception as e:
            self.log_error(str(e), path)
            
            
    def delete_path(self, path):
        req_url = self.BASE_URL + 'users/' + self.username + '/' + path + '/.json' # .json can also be used (no difference)
        
        req_url = req_url.replace(' ', "%20")
        
        auth = {'auth' : self.credentials['idToken']}
        auth = parse.urlencode(auth)
        req_url += '?' + auth
        
        req = request.Request(req_url, method="DELETE")
        
        try:
            resp = request.urlopen(req)
            return resp.code
        except error.HTTPError as err:
            self.log_error(str(err), path)
            print(err)
        except client.InvalidURL as err:
            """ printing err returns a long msg w/ path alr in there
            so we save shorthand name (https://stackoverflow.com/a/58045927/12514570)
            and the msg IS the str(err)
            """
            
            module = err.__class__.__module__
            if module is None or module == str.__class__.__module__:
                errorName = err.__class__.__name__
            errorName =  module + '.' + err.__class__.__name__
            
            self.log_error(errorName, str(err))
            
        except Exception as e:
            self.log_error(str(e), path)
        
        
    def log_error(self, err, desc):
        """
        Nested under /logs/self.username/
        
        we don't catch errors here lol
        """
        
        ######## WE CAN'T USE '.' IN KEYS
        # https://groups.google.com/g/firebase-talk/c/vtX8lfxxShk
        # that means for usernames we dropping underscores
        err = err.replace('.', '_')
        err = err.replace('[', '<')
        err = err.replace(']', '>')
        
        payload = {err: desc, 'date': str(datetime.now())}
        
        payload = json.dumps(payload).encode() #dict --> json --> bytes/json
        
        req_url = self.BASE_URL + 'logs/' + self.username + '/.json'
        req_url = req_url.strip()
        
        auth = {'auth' : self.credentials['idToken']}
        auth = parse.urlencode(auth)
        req_url += '?' + auth
        
        req = request.Request(req_url, data=payload, method="PATCH")
        
        loader = request.urlopen(req)
        
        return loader.code
        

def sign_up_with_email(email, password):
    """ create user w/ email + password via REST
    https://firebase.google.com/docs/reference/rest/auth#section-create-email-password
    """
    
    ENDPOINT_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=" + API_KEY
    
    
    
    headers = {"content-type": "application/json; charset=UTF-8" } # WE NEED HEADERS
    # I SPENT LIKE 3.5 / 4 HOURS AND IT FAILED
    # AND FINALLY, IDK WHY, BUT I DUG INTO SOURCE CODE OF PYREBASE WHICH USES REQUESTS BUT FIGURED OUT HEADERS PUSH THIS THRU

    user_payload = {
        'email' : email,
        'password' : password,
        'returnSecureToken' : True
    }

    user_payload = json.dumps(user_payload).encode() #dict --> json --> bytes/json
    req = request.Request(ENDPOINT_URL, data=user_payload, headers=headers, method="POST")
    try:
        new_user_json = request.urlopen(req)
        new_user_json = new_user_json.read().decode('utf-8')
        new_user_json = json.loads(new_user_json) # json string --> python dict
    except error.HTTPError as err:
        # email alr exists (prolly)
        # EMAIL_EXISTS, OPERATION_NOT_ALLOWED, or TOO_MANY_ATTEMPTS_TRY_LATER
        print("EMAIL_EXISTS / TOO_MANY_ATTEMPTS_TRY_LATER:", str(err))
        new_user_json = {}
    
    return new_user_json

def login_with_email_password(email, password):
    ENDPOINT_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + API_KEY
    
    headers = {"content-type": "application/json; charset=UTF-8" } # WE NEED HEADERS
    # I SPENT LIKE 3.5 / 4 HOURS AND IT FAILED AND FINALLY IDK WHY I DUG INTO SOURCE CODE OF PYREBASE WHICH USES REQUESTS BUT FIGURED OUT HEADERS PUSH THIS THRU
    
    user_payload = {
        'email' : email,
        'password' : password,
        'returnSecureToken' : True
    }
    user_payload = json.dumps(user_payload).encode() #dict --> json --> bytes/json
    req = request.Request(ENDPOINT_URL, data=user_payload, headers=headers, method="POST")
    
    
    try:
        new_user_json = request.urlopen(req)
        new_user_json = new_user_json.read().decode('utf-8')
        new_user_json = json.loads(new_user_json) # json string --> python dict
    except error.HTTPError as err:
        # EMAIL_NOT_FOUND, INVALID_PASSWORD, or USER_DISABLED
        print("EMAIL_NOT_FOUND / INVALID_PASSWORD / USER_DISABLED:", str(err))
        new_user_json = {}
        
    return new_user_json
