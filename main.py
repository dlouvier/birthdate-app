from flask import Request
import json
from datetime import datetime
from google.cloud import datastore
import re
import sys

PATH_REGEX = '^/hello/[a-z]*$'
DATE_FORMAT = '%Y-%m-%d'
DATASTORE_KIND = 'Birthdates'

def app(request: Request):
    """
        app is the main function which takes care of the routing
        and the initial path validation.
        Depending of the request it forward it to get_user_birthdate
        or put_user_birthdate.

        It returns a response code that is forwarded to the client by
        GCP.
    """
    
    if re.match(PATH_REGEX, request.path):
        username = request.path.split("/")[2]

        if request.method == 'GET' and username != "":
            return get_user_birthdate(username)

        elif request.method == 'PUT':
            try:
                args = request.get_json()
                date_of_birth = datetime.strptime(args['dateOfBirth'], DATE_FORMAT)
            except Exception as err:
                print(err)
                sys.stdout.flush()
                return response_helper(405,'dateOfBirth is missing or format is not %Y-%m-%d')

            return put_user_birthdate(username,date_of_birth)
        else:
            return response_helper(405, 'Only GET and PUT HTTP method are allowed.')

    else:
        return response_helper(405, 'URL Format is not correct.')

def get_user_birthdate(username):
    try:  
        client = datastore.Client()
        key = client.key(DATASTORE_KIND, username)
        entity = client.get(key)
    except Exception as err:
        print(err)
        sys.stdout.flush()
        return response_helper(500, 'Internal error.')

    if entity == None:
        return response_helper(404, 'Username ({}) does not exist in the database.'.format(username))

    birthdate = datetime.strptime(entity['dateOfBirth'], "%Y-%m-%d")
    today = datetime.today()

    # Calculate if today is the same day of the birthdate or already passed this year
    if datetime(2000,today.month,today.day) == datetime(2000,birthdate.month,birthdate.day):
        return response_helper(200,'Hello, {}! Happy birthday!'.format(username))
    elif datetime(2000,today.month,today.day) > datetime(2000,birthdate.month,birthdate.day):
        delta = datetime(2000,today.month,today.day) - datetime(2000,birthdate.month,birthdate.day)
    elif datetime(2000,today.month,today.day) < datetime(2000,birthdate.month,birthdate.day):
        delta = datetime(2000,birthdate.month,birthdate.day) - datetime(2000,today.month,today.day)

    return response_helper(200,'Hello, {}! Your birthday is in {} day(s)'.format(username,delta.days)) 

def put_user_birthdate(username: str, date_of_birth: datetime):
    delta = date_of_birth - datetime.today()

    if delta.days >= 0:
        return response_helper(400, 'Username dateOfBirth ({}) cannot be in the future'.format(date_of_birth))
    
    try:
        client = datastore.Client()
        birthdate = datastore.Entity(key=client.key(DATASTORE_KIND,username))
        birthdate['dateOfBirth'] = date_of_birth.strftime(DATE_FORMAT)
        client.put(birthdate)
    except Exception as err:
        print(err)
        sys.stdout.flush()
        return response_helper(500, 'Internal error.')

    return ('', 204)

def response_helper(code, msg):
    if (code >= 200) and (code < 300):
        response_type = "message"
    else:
        response_type = "error"

    return (json.dumps(
                    { response_type: msg }
                ), code
            )