from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Arrange: start in a clean state for this test
    activity = client.get("/activities").json()[activity_name]
    if email in activity["participants"]:
        client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Act: register then unregister
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200

    delete_response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert delete_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_duplicate_signup_is_rejected():
    activity_name = "Chess Club"
    email = "duplicate@mergington.edu"

    # Arrange
    client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200

    second_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert second_response.status_code == 400
