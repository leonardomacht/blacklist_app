import pytest
from unittest.mock import patch
from flask import Flask
from src.routes.blacklist_router import blacklist_bp

app = Flask(__name__)
app.register_blueprint(blacklist_bp)

HEADERS = {"Authorization": "Bearer bearer_token_test"}

@pytest.fixture
def client():
    return app.test_client()

def test_post_sin_body(client):
    resp = client.post('/blacklists', headers=HEADERS, json={})
    assert resp.status_code == 400

def test_post_datos_validos(client):
    with patch("src.routes.blacklist_router.blacklist_service") as mock_service:
        mock_service.add_to_blacklist.return_value = {
            "message": "ok", "id": "1", "email": "test@test.com", "created_at": "2026-01-01 00:00:00"
        }
        resp = client.post('/blacklists', headers=HEADERS, json={
            "email": "test@test.com",
            "app_uuid": "123e4567-e89b-12d3-a456-426614174000"
        })
    assert resp.status_code == 201

def test_post_sin_autenticacion(client):
    resp = client.post('/blacklists', json={
        "email": "test@test.com",
        "app_uuid": "123e4567-e89b-12d3-a456-426614174000"
    })
    assert resp.status_code == 401

def test_get_email_en_lista(client):
    with patch("src.routes.blacklist_router.blacklist_service") as mock_service:
        mock_service.check_blacklist.return_value = {
            "is_blacklisted": True, "email": "test@test.com", "blocked_reason": "spam"
        }
        resp = client.get('/blacklists/test@test.com', headers=HEADERS)
    assert resp.status_code == 200
    assert resp.get_json()["is_blacklisted"] is True

def test_ping(client):
    resp = client.get('/blacklists/ping')
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "pong"
