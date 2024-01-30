from typing import List

import pytest
from app import schemas

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts")

    assert res.status_code == 200
    assert len(res.json()) == len(test_posts)

def test_get_one_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts")

    assert res.status_code == 200
    assert len(res.json()) == len(test_posts)

def test_unaithorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts")

    assert res.status_code == 401

def test_unaithorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/88888")

    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")

    post = schemas.PostOut(**res.json())

    assert res.status_code == 200
    assert post.Post.id == test_posts[0].id
    assert post.Post.title == test_posts[0].title
    assert post.Post.content == test_posts[0].content
    assert post.Post.owner_id == test_posts[0].owner_id


@pytest.mark.parametrize("title, content, published",[
                             ("new title 1", "new content 1", True),
                             ("new title 2", "new content 2", False),
                             ("new title 3", "new content 3", False),
                         ])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("/posts", json={"title": title, "content": content, "published": published})

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
                         

def test_create_post_default_published_true(authorized_client, test_user):
    res = authorized_client.post("/posts", json={"title": "title", "content": "content"})

    created_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert created_post.title == "title"
    assert created_post.content == "content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


def test_unaithorized_user_create_post(client):
    res = client.post("/posts", json={"title": "title", "content": "content"})

    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")

    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user):
    res = authorized_client.delete("/posts/8888")

    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")

    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }

    res = authorized_client.put(f"/posts/{test_posts[0].id}", json = data)
    updated_post = schemas.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.title == data["title"]
    assert updated_post.content == data["content"]


def test_update_other_user_post(authorized_client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }

    res = authorized_client.put(f"/posts/{test_posts[3].id}", json = data)

    assert res.status_code == 403



def test_unauthorized_user_update_post(client, test_user, test_posts):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_posts[0].id
    }

    res = client.put(f"/posts/{test_posts[3].id}", json = data)

    assert res.status_code == 401

def test_UPDATE_post_non_exist(authorized_client, test_user):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": "8888"
    }

    res = authorized_client.put("/posts/8888", json = data)

    assert res.status_code == 404