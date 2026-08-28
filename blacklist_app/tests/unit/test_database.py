import pytest
from flask import Flask
from src.db.database import init_db, create_tables, db


def test_init_db_sin_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    app = Flask(_name_)
    with pytest.raises(ValueError):
        init_db(app)


def test_init_db_con_database_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = Flask(_name_)
    result = init_db(app)
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
    assert result is db


def test_create_tables(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = Flask(_name_)
    init_db(app)
    create_tables(app)
