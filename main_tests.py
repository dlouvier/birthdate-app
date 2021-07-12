import requests
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

def test_example():
    with DockerCompose('.') as compose:
        host = compose.get_service_host("app", 8080)
        port = compose.get_service_port("app", 8080)

        x = requests.get('http://{}:{}/'.format(host,port))
        assert x.status_code == 405
