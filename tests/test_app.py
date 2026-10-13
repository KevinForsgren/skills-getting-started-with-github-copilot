import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client():
    original_activities = copy.deepcopy(app_module.activities)
    with TestClient(app_module.app) as test_client:
        yield test_client
    app_module.activities = original_activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client):
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert activities["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_new_participant(client):
    email = "newstudent@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_unknown_activity(client):
    response = client.post("/activities/Unknown Club/signup", params={"email": "student@example.com"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_duplicate_signup_is_rejected_without_changing_participants(client):
    email = "duplicate@mergington.edu"
    signup_url = "/activities/Chess Club/signup"

    first_response = client.post(signup_url, params={"email": email})
    participants_after_first_signup = client.get("/activities").json()["Chess Club"]["participants"]

    second_response = client.post(signup_url, params={"email": email})

    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json() == {"detail": "Student already signed up for this activity"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == participants_after_first_signup


def test_unregister_removes_existing_participant(client):
    email = "remove-me@mergington.edu"
    signup_url = "/activities/Chess Club/signup"

    client.post(signup_url, params={"email": email})
    response = client.delete(signup_url, params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in client.get("/activities").json()["Chess Club"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    response = client.delete("/activities/Unknown Club/signup", params={"email": "student@example.com"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_missing_participant(client):
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "not-registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Student is not signed up for this activity"}
