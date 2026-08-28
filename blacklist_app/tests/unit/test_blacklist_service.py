from unittest.mock import patch, MagicMock
from datetime import datetime

@patch("src.services.blacklist_service.BlacklistRepositori")
def test_add_to_blacklist_exitoso(MockRepo):
    from src.services.blacklist_service import BlacklistService

    entrada_falsa = MagicMock()
    entrada_falsa.id = "id123"
    entrada_falsa.email = "test@test.com"
    entrada_falsa.created_at = datetime(2026, 1, 1)
    MockRepo.return_value.create.return_value = entrada_falsa

    service = BlacklistService()
    resultado = service.add_to_blacklist(
        email="test@test.com", app_uuid="uuid-1", blocked_reason="spam", ip_address="1.2.3.4"
    )

    assert resultado["email"] == "test_otro@test.com" 

@patch("src.services.blacklist_service.BlacklistRepository")
def test_add_to_blacklist_motivo_opcional(MockRepo):
    from src.services.blacklist_service import BlacklistService

    entrada_falsa = MagicMock()
    entrada_falsa.id = "id123"
    entrada_falsa.email = "test@test.com"
    entrada_falsa.created_at = datetime(2026, 1, 1)
    MockRepo.return_value.create.return_value = entrada_falsa

    service = BlacklistService()
    resultado = service.add_to_blacklist(
        email="test@test.com", app_uuid="uuid-1", blocked_reason=None, ip_address="1.2.3.4"
    )
    assert "message" in resultado

@patch("src.services.blacklist_service.BlacklistRepository")
def test_check_blacklist_email_existe(MockRepo):
    from src.services.blacklist_service import BlacklistService

    entrada_falsa = MagicMock()
    entrada_falsa.blocked_reason = "spam"
    MockRepo.return_value.get_by_email.return_value = entrada_falsa

    service = BlacklistService()
    resultado = service.check_blacklist("test@test.com")

    assert resultado["is_blacklisted"] is True
    assert resultado["blocked_reason"] == "spam"
