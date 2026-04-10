"""Testes para operações CRUD do StorageService."""
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def client():
    return MagicMock()


@pytest.fixture
def svc(client):
    with patch("storage_service._get_supabase_client", return_value=client):
        from storage_service import StorageService
        s = StorageService(usuario="usr-001")
        s.client = client
        return s


# ── update_status ─────────────────────────────────────────────────────────────

def test_update_status_pago(svc, client):
    """Marca como pago usando ID UUID (string)."""
    bid = "550e8400-e29b-41d4-a716-446655440000"
    svc.update_status(bid, True)
    chain = client.table.return_value.update.return_value.eq.return_value.eq.return_value
    chain.execute.assert_called_once()


def test_update_status_nao_pago(svc, client):
    """Marca como não pago."""
    bid = "550e8400-e29b-41d4-a716-446655440001"
    svc.update_status(bid, False)
    client.table.assert_called_with("boletos")


def test_update_status_erro_levanta_runtime(svc, client):
    """Erros do Supabase são convertidos em RuntimeError."""
    client.table.side_effect = Exception("network error")
    with pytest.raises(RuntimeError, match="status"):
        svc.update_status("some-id", True)


# ── delete ────────────────────────────────────────────────────────────────────

def test_delete_chama_supabase(svc, client):
    """delete() deve acionar a chain correta."""
    bid = "abc-123"
    svc.delete(bid)
    client.table.assert_called_with("boletos")


def test_delete_erro_levanta_runtime(svc, client):
    """Erros de delete são convertidos em RuntimeError."""
    client.table.side_effect = Exception("timeout")
    with pytest.raises(RuntimeError, match="excluir"):
        svc.delete("abc-123")


# ── get_categorias ────────────────────────────────────────────────────────────

def test_get_categorias_retorna_lista(svc, client):
    mock_res = MagicMock()
    mock_res.data = [{"nome": "Alimentação"}, {"nome": "Saúde"}]
    client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_res

    cats = svc.get_categorias()
    assert cats == ["Alimentação", "Saúde"]


def test_get_categorias_vazio(svc, client):
    mock_res = MagicMock()
    mock_res.data = []
    client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = mock_res

    cats = svc.get_categorias()
    assert cats == []


def test_get_categorias_erro_retorna_lista_vazia(svc, client):
    """Em caso de erro, retorna [] sem propagar exceção."""
    client.table.side_effect = Exception("db error")
    cats = svc.get_categorias()
    assert cats == []


# ── create ────────────────────────────────────────────────────────────────────

def test_create_retorna_dict_normalizado(svc, client):
    mock_res = MagicMock()
    mock_res.data = [{
        "id": "row-uuid",
        "descricao": "Luz",
        "valor": 150.0,
        "vencimento": "2025-07-10",
        "competencia": "2025-07",
        "categoria": None,
        "pago": False,
        "criado_em": "2025-07-01T00:00:00",
    }]
    client.table.return_value.insert.return_value.execute.return_value = mock_res

    row = svc.create("Luz", 150.0, "2025-07-10", "2025-07")
    assert row["id"] == "row-uuid"
    assert row["valor"] == 150.0
    assert row["pago"] is False


def test_create_resposta_vazia_levanta_runtime(svc, client):
    mock_res = MagicMock()
    mock_res.data = []
    client.table.return_value.insert.return_value.execute.return_value = mock_res

    with pytest.raises(RuntimeError):
        svc.create("Luz", 150.0, "2025-07-10", "2025-07")


# ── check_duplicate ───────────────────────────────────────────────────────────

def test_check_duplicate_encontrado(svc, client):
    mock_res = MagicMock()
    mock_res.data = [{"id": "x"}]
    (client.table.return_value.select.return_value
     .eq.return_value.eq.return_value.eq.return_value.execute.return_value) = mock_res

    assert svc.check_duplicate("Netflix", "2025-07-01") is True


def test_check_duplicate_nao_encontrado(svc, client):
    mock_res = MagicMock()
    mock_res.data = []
    (client.table.return_value.select.return_value
     .eq.return_value.eq.return_value.eq.return_value.execute.return_value) = mock_res

    assert svc.check_duplicate("Netflix", "2025-07-01") is False
