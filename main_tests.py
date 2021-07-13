import requests
import datetime
import json
from testcontainers.compose import DockerCompose

def test_can_spawn_service_datastore_via_compose():
    with DockerCompose('.') as compose:
        host = compose.get_service_host("datastore", 8081)
        port = compose.get_service_port("datastore", 8081)
        assert host == "0.0.0.0"
        assert port == "8081"

def test_can_spawn_service_app_via_compose():
    with DockerCompose('.') as compose:
        host = compose.get_service_host("app", 8080)
        port = compose.get_service_port("app", 8080)
        assert host == "0.0.0.0"
        assert port == "8080"

def test_can_add_and_retrieve_correct_birthdate():
    with DockerCompose('.') as compose:
        compose.get_service_host("datastore", 8081)
        compose.get_service_port("datastore", 8081)

        app_host = compose.get_service_host("app", 8080)
        app_port = compose.get_service_port("app", 8080)

        # Test a correct formated date in the past can be added
        payload = '{\"dateOfBirth\": \"1988-1-14\"}'
        headers = {'Content-type': 'application/json'}
        r = requests.put("http://{}:{}/hello/daniel".format(app_host,app_port), headers=headers, data=payload)

        assert r.status_code == 204
        assert r.content == b''

        # Test the previous inserted birthdate can be retrieved
        r = requests.get("http://{}:{}/hello/daniel".format(app_host,app_port))
        assert r.status_code == 200
        assert 'Hello, daniel! Your birthday is in' in str(r.content)


        # Insert a birthdate which is today and retrieve the gratulations message
        today = datetime.datetime.today()
        birth_date = datetime.datetime(2000,today.month,today.day)

        payload = json.dumps({
            "dateOfBirth": birth_date.strftime('%Y-%m-%d')
            })
        headers = {'Content-type': 'application/json'}

        r = requests.put("http://{}:{}/hello/john".format(app_host,app_port), headers=headers, data=payload)
        r = requests.get("http://{}:{}/hello/john".format(app_host,app_port))

        assert r.status_code == 200
        assert 'Hello, john! Happy birthday!' in str(r.content)

def test_fail_when_adding_a_birthdate_in_the_future():
    with DockerCompose('.') as compose:
        compose.get_service_host("datastore", 8081)
        compose.get_service_port("datastore", 8081)

        app_host = compose.get_service_host("app", 8080)
        app_port = compose.get_service_port("app", 8080)

        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

        payload = json.dumps({
            "dateOfBirth": tomorrow.strftime('%Y-%m-%d')
            })
        headers = {'Content-type': 'application/json'}

        r = requests.put("http://{}:{}/hello/daniel".format(app_host,app_port), headers=headers, data=payload)
        
        assert 'cannot be in the future' in str(r.content)
        assert r.status_code == 400 

def test_fails_when_using_wrong_date_format():
    with DockerCompose('.') as compose:
        compose.get_service_host("datastore", 8081)
        compose.get_service_port("datastore", 8081)

        app_host = compose.get_service_host("app", 8080)
        app_port = compose.get_service_port("app", 8080)

        payload = json.dumps({
            "dateOfBirth": "14-01-1988"
            })
        headers = {'Content-type': 'application/json'}

        r = requests.put("http://{}:{}/hello/daniel".format(app_host,app_port), headers=headers, data=payload)

        assert 'dateOfBirth is missing or format is not' in str(r.content)
        assert r.status_code == 405

def test_fails_when_username_has_numbers():
    with DockerCompose('.') as compose:
        app_host = compose.get_service_host("app", 8080)
        app_port = compose.get_service_port("app", 8080)

        r = requests.get("http://{}:{}/hello/d4n13l".format(app_host,app_port))

        assert 'URL Format is not correct' in str(r.content)
        assert r.status_code == 405
