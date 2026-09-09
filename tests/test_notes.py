"""
Tests for the notes CRUD API — the golden path, the 404 case, and the
422 validation case.
"""
from fastapi.testclient import TestClient


def test_create_note(client: TestClient) -> None:
    response = client.post("/notes", json={"title": "First note", "content": "hello"})

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "First note"
    assert body["content"] == "hello"
    assert body["is_pinned"] is False


def test_create_note_validation_error(client: TestClient) -> None:
    response = client.post("/notes", json={"content": "missing title"})

    assert response.status_code == 422


def test_get_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "Note", "content": "body"}).json()

    response = client.get(f"/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_note_not_found(client: TestClient) -> None:
    response = client.get("/notes/999999")

    assert response.status_code == 404


def test_list_notes(client: TestClient) -> None:
    client.post("/notes", json={"title": "A"})
    client.post("/notes", json={"title": "B"})

    response = client.get("/notes")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "Original", "content": "v1"}).json()

    response = client.patch(f"/notes/{created['id']}", json={"title": "Updated"})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Updated"
    assert body["content"] == "v1"  # untouched field stays as-is


def test_update_note_not_found(client: TestClient) -> None:
    response = client.patch("/notes/999999", json={"title": "Updated"})

    assert response.status_code == 404


def test_delete_note(client: TestClient) -> None:
    created = client.post("/notes", json={"title": "To delete"}).json()

    delete_response = client.delete(f"/notes/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/notes/{created['id']}")
    assert get_response.status_code == 404


def test_delete_note_not_found(client: TestClient) -> None:
    response = client.delete("/notes/999999")

    assert response.status_code == 404
