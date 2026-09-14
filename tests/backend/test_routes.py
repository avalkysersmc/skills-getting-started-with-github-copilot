import pytest


EXPECTED_ACTIVITY_FIELDS = {
    "description",
    "schedule",
    "max_participants",
    "participants",
}


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    activities = response.json()
    assert response.status_code == 200
    assert expected_activity in activities
    assert set(activities[expected_activity]) == EXPECTED_ACTIVITY_FIELDS
    assert isinstance(activities[expected_activity]["participants"], list)


def test_signup_registers_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in client.get("/activities").json()[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "expected_status", "expected_detail"),
    [
        (
            "Unknown Club",
            "student@mergington.edu",
            404,
            "Activity not found",
        ),
        (
            "Chess Club",
            "michael@mergington.edu",
            400,
            "Student already signed up for this activity",
        ),
    ],
)
def test_signup_rejects_invalid_requests(
    client,
    activity_name,
    email,
    expected_status,
    expected_detail,
):
    # Arrange
    initial_activities = client.get("/activities").json()

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail
    assert client.get("/activities").json() == initial_activities


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in client.get("/activities").json()[activity_name]["participants"]


@pytest.mark.parametrize(
    ("activity_name", "email", "expected_detail"),
    [
        ("Unknown Club", "student@mergington.edu", "Activity not found"),
        (
            "Chess Club",
            "notregistered@mergington.edu",
            "Student is not signed up for this activity",
        ),
    ],
)
def test_unregister_rejects_invalid_requests(
    client,
    activity_name,
    email,
    expected_detail,
):
    # Arrange
    initial_activities = client.get("/activities").json()

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail
    assert client.get("/activities").json() == initial_activities


def test_unregister_requires_email(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
