from app import schemas
from .database import client, session

def test_root(client):
    res = client.get("/")
    print(res.json().get('message'))
    assert res.status_code == 200
    assert res.json().get('message') == 'Hello World on docker'


def test_create_user(client):
    res = client.post("/users", json={"email": "hello@mail.com", "password": "123"})
    
    new_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert new_user.email == "hello@mail.com"


def test_login_user(client):
    res = client.post("/login", data={"username": "hello@mail.com", "password": "12345"})
    print(res.json())

    assert res.status_code == 200
