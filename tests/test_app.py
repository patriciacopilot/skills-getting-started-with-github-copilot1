import os
import sys
import urllib.parse

from fastapi.testclient import TestClient

# Ensure `src` is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity from the in-memory DB
    assert "Chess Club" in data


def test_signup_new_participant():
    activity = "Chess Club"
    email = "testuser@example.com"
    url = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 200
    payload = resp.json()
    assert "Signed up" in payload.get("message", "")

    # Verify participant appears in the activity list
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    data = resp2.json()
    assert email in data[activity]["participants"]


def test_signup_duplicate_fails():
    activity = "Chess Club"
    email = "testuser@example.com"
    url = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 400


def test_signup_activity_not_found():
    activity = "Nonexistent Activity"
    email = "nobody@example.com"
    url = f"/activities/{urllib.parse.quote(activity)}/signup?email={urllib.parse.quote(email)}"
    resp = client.post(url)
    assert resp.status_code == 404
