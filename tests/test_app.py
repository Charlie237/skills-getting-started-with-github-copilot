"""Tests for the Mergington High School API."""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"],
        },
    }
    activities.clear()
    activities.update(original)
    yield


client = TestClient(app)


class TestGetActivities:
    def test_returns_all_activities(self):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activity_has_required_fields(self):
        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess


class TestSignupForActivity:
    def test_successful_signup(self):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/Chess Club/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert email in activities["Chess Club"]["participants"]

    def test_duplicate_signup_rejected(self):
        # Arrange - michael is already signed up
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/Chess Club/signup", params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student is already signed up"

    def test_signup_nonexistent_activity(self):
        # Act
        response = client.post(
            "/activities/Nonexistent/signup",
            params={"email": "student@mergington.edu"},
        )

        # Assert
        assert response.status_code == 404


class TestUnregisterFromActivity:
    def test_successful_unregister(self):
        # Arrange - michael is in Chess Club
        email = "michael@mergington.edu"

        # Act
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_not_signed_up(self):
        # Arrange
        email = "notmember@mergington.edu"

        # Act
        response = client.request(
            "DELETE",
            "/activities/Chess Club/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400

    def test_unregister_nonexistent_activity(self):
        # Act
        response = client.request(
            "DELETE",
            "/activities/Nonexistent/unregister",
            params={"email": "student@mergington.edu"},
        )

        # Assert
        assert response.status_code == 404
