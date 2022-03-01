import json
import pytest
import pydantic
from src.main import app, Item
from fastapi.testclient import TestClient


client = TestClient(app)

user_inputs = [
    Item(sender="mish", recipient="moosh", message="toosh"),
    Item(sender="kish", recipient="moosh", message="soosh"),
    Item(sender="fish", recipient="moosh", message="foosh")
]


# sanity testing for project
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


# validation testing for empty recipient param
def test_no_messages():
    response = client.get('/messages/get_messages')
    assert response.status_code == 400
    assert response.json() == {"detail": "Recipient not exist"}


# testing send messages and find messages in recipient's list
def test_get_recipient_name():
    response = client.post('/messages/send', data=user_inputs[0].json())
    assert response.status_code == 200 and response.json() == {"status": "ok"}
    response = client.get('/messages/get_messages', params={"recipient": "moosh"})
    assert response.json() == [{"sender": "mish", "message": "toosh"}] and response.status_code == 200
    response = client.post('/messages/send', data=user_inputs[1].json())
    assert response.status_code == 200 and response.json() == {"status": "ok"}
    response = client.get('/messages/get_messages', params={"recipient": "moosh"})
    assert response.json() == [{"sender": "mish", "message": "toosh"}, {"sender": "kish", "message": "soosh"}] and \
        len(response.json()) == 2 and response.status_code == 200


# testing raising validation exception for recipient not found
def test_get_wrong_recipient_name():
    response = client.get('/messages/get_messages', params={"recipient": "moosh"})
    print(json.dumps(response.json(), indent=4))
    response = client.post('/messages/send', data=user_inputs[2].json())
    assert response.status_code == 200 and response.json() == {"status": "ok"}
    response = client.get('/messages/get_messages', params={"recipient": "moosh"})
    assert response.json() == [{"sender": "fish", "message": "foosh"}] and response.status_code == 200
    response = client.get('/messages/get_messages', params={"recipient": "koosh"})
    assert response.status_code == 400 and response.json() == {"detail": "Recipient not exist"}


# testing raising validation exception for too long parameters
def test_message_too_long():
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Item(sender="fish", recipient="moosh", message="foosh" * 1000)

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Item(sender="fish", recipient="moosh" * 10, message="foosh")

    with pytest.raises(pydantic.error_wrappers.ValidationError):
        Item(sender="fish" * 10, recipient="moosh", message="foosh")


