"""Fixtures compartilhadas para testes do Tá Pago?."""
import sys
import os
from unittest.mock import MagicMock, patch

# ── Mock do Streamlit ANTES de qualquer import do projeto ────────────────────
# Necessário porque storage_service.py e auth.py importam streamlit no topo.
_st_mock = MagicMock()
_st_mock.cache_resource = lambda func: func   # decorator transparente
_st_mock.secrets = {"supabase": {"url": "http://fake", "key": "fake-key"}}
sys.modules.setdefault("streamlit", _st_mock)

# Garante que o root do projeto está no sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest


@pytest.fixture
def mock_supabase_client():
    """Client Supabase completamente mockado."""
    return MagicMock()


@pytest.fixture
def storage(mock_supabase_client):
    """StorageService com client Supabase mockado."""
    with patch("storage_service._get_supabase_client", return_value=mock_supabase_client):
        from storage_service import StorageService
        svc = StorageService(usuario="user-test-123")
        svc.client = mock_supabase_client
        return svc
