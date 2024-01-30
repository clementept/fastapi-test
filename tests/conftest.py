from fastapi.testclient import TestClient
import pytest
from app.database import Base, get_db
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
import pytest
from app.oauth2 import create_access_token
from app import models

SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{
    settings.database_hostname}:{settings.database_port}/{settings.test_database_name}'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_user(client):
    res = client.post(
        "/users", json={"email": "hello@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    return new_user


@pytest.fixture
def test_user2(client):
    res = client.post(
        "/users", json={"email": "hello2@mail.com", "password": "123"})

    new_user = res.json()
    new_user["password"] = "123"

    return new_user


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [
        {
            "title": "Post 1",
            "content": "Post 1 content",
            "owner_id": test_user['id']
        },
        {
            "title": "Post 2",
            "content": "Post 2 content",
            "owner_id": test_user['id']
        },
        {
            "title": "Post 3",
            "content": "Post 3 content",
            "owner_id": test_user['id']
        },
        {
            "title": "Post 4",
            "content": "Post 4 content",
            "owner_id": test_user2['id']
        }
    ]

    def create_post_model(post):
        return models.Post(**post)

    posts_map = map(create_post_model, posts_data)

    posts_list = list(posts_map)

    session.add_all(posts_list)
    session.commit()

    posts = session.query(models.Post).all()

    return posts
