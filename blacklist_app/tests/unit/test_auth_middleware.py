import pytest
from flask import Flask
from src.middleware.auth_middleware import require_bearer_token

app = Flask(__name__)

@app.route('/protegido')
@require_bearer_token
def vista_protegida():
    return {"message": "ok"}, 200

@pytest.fixture
def client():
    return app.test_client()

def test_sin_header_authorization(client):
    resp = client.get('/protegido')
    assert resp.status_code == 401

def test_header_mal_formado(client):
    resp = client.get('/protegido', headers={"Authorization": "Token test"})
    assert resp.status_code == 401

def test_token_no_configurado_en_servidor(client, monkeypatch):
    monkeypatch.delenv("BEARER_TOKEN", raising=False)
    resp = client.get('/protegido', headers={"Authorization": "Bearer test"})
    assert resp.status_code == 500

def test_token_incorrecto(client):
    resp = client.get('/protegido', headers={"Authorization": "Bearer test_incorrect"})
    assert resp.status_code == 401

def test_token_correcto_deja_pasar(client):
    resp = client.get('/protegido', headers={"Authorization":  "bearer_token_test"})
    assert resp.status_code == 200
