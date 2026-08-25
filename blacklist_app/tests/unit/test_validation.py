from unittest.mock import Mock
import pytest
from src.utils.validation import validate_uuid, get_client_ip
from src.models.errors import BadRequestError


def test_validate_uuid_con_uuid_valido():
    resultado = validate_uuid("123e4567-e89b-12d3-a456-426614174000")
    assert resultado is True  


def test_validate_uuid_con_uuid_invalido():
    with pytest.raises(BadRequestError):
        validate_uuid("aaabbbb")


def test_get_client_ip_con_header_forwarded():
    request = Mock()
    request.headers.get.return_value = "1.1.1.1, 2.2.2.2"
    assert get_client_ip(request) == "1.1.1.1" 


def test_get_client_ip_sin_header():
    request = Mock()
    request.headers.get.return_value = None
    request.remote_addr = "10.0.0.5"
    assert get_client_ip(request) == "10.0.0.5"


def test_get_client_ip_sin_ip_disponible():
    request = Mock()
    request.headers.get.return_value = None
    request.remote_addr = None
    assert get_client_ip(request) == "unknown"  
