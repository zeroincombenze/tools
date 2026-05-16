def test_get_messages_empty(client):
    response = client.get("/api/messages")

    assert response.status_code == 200
    assert response.get_json() == []


def test_add_message(client):
    response = client.post(
        "/api/messages",
        json={"text": "Hello test"}
    )

    assert response.status_code == 201
    assert response.get_json()["status"] == "ok"


def test_get_messages_after_insert(client):
    response = client.get("/api/messages")
    data = response.get_json()

    assert len(data) >= 1
    assert data[0]["text"] == "Hello test"


def test_add_empty_message(client):
    response = client.post(
        "/api/messages",
        json={"text": ""}
    )

    assert response.status_code == 400
