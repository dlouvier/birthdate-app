from flask import Request
import json
from datetime import datetime
from google.cloud import datastore
import re

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
                args = request.get_json(silent=True)
                date_of_birth = datetime.strptime(args['dateOfBirth'], DATE_FORMAT)
            except Exception as e:
                print(e)
                return (json.dumps(
                            { 'error': 'dateOfBirth is missing or format is not %Y-%m-%d' }
                        ),405
                    )

            return put_user_birthdate(username,date_of_birth)
        else:
            return (json.dumps(
                            { 'error': 'Only GET and PUT HTTP method are allowed.' }
                        ),405
                    )
    else:
        return (json.dumps(
                        { 'error': 'URL Format is not correct.' }
                    ),405
                )

def get_user_birthdate(username):
    client = datastore.Client()
    key = client.key(DATASTORE_KIND, username)
    entity = client.get(key)

    birthdate = datetime.strptime(entity['dateOfBirth'], "%Y-%m-%d")
    today = datetime.today()

    # Calculate if today is the same day of the birthdate or already passed this year
    if datetime(2000,today.month,today.day) == datetime(2000,birthdate.month,birthdate.day):
        return json.dumps(
            { 'message': 'Hello, {}! Happy birthday!'.format(username) }
        )
    elif datetime(2000,today.month,today.day) > datetime(2000,birthdate.month,birthdate.day):
        delta = datetime(2000,today.month,today.day) - datetime(2000,birthdate.month,birthdate.day)
    elif datetime(2000,today.month,today.day) < datetime(2000,birthdate.month,birthdate.day):
        delta = datetime(2000,birthdate.month,birthdate.day) - datetime(2000,today.month,today.day)

    return json.dumps(
        { 'message': 'Hello, {}! Your birthday is in {} day(s)'.format(username,delta.days) }
    )

def put_user_birthdate(username: str, date_of_birth: datetime):
    delta = date_of_birth - datetime.today()

    if delta.days >= 0:
        return "Date is NOT correct"
    
    client = datastore.Client()

    birthdate = datastore.Entity(key=client.key(DATASTORE_KIND,username))
    birthdate['dateOfBirth'] = date_of_birth.strftime(DATE_FORMAT)

    client.put(birthdate)

    return ('', 204)
