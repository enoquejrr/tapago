"""Testes para services/boleto_service.py."""
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def storage_mock():
    mock = MagicMock()
    mock.usuario = "usr-001"
    return mock


@pytest.fixture
def svc(storage_mock):
    with patch("storage_service._get_supabase_client", return_value=MagicMock()):
        from services.boleto_service import BoletoService
        return BoletoService(storage_mock)


def _boleto(descricao="Luz", valor=100.0, vencimento="2025-07-10", competencia="2025-07"):
    return {
        "id": "fake-id",
        "descricao": descricao,
        "valor": valor,
        "vencimento": vencimento,
        "competencia": competencia,
        "categoria": None,
        "pago": False,
        "criado_em": "",
    }


# ── criar_recorrente ──────────────────────────────────────────────────────────

def test_criar_recorrente_chama_create_n_vezes(svc, storage_mock):
    storage_mock.create.return_value = _boleto()
    svc.criar_recorrente("Luz", 100.0, "2025-07-10", "2025-07", meses=3)
    assert storage_mock.create.call_count == 3


def test_criar_recorrente_retorna_lista(svc, storage_mock):
    storage_mock.create.return_value = _boleto()
    result = svc.criar_recorrente("Luz", 100.0, "2025-07-10", "2025-07", meses=2)
    assert isinstance(result, list)
    assert len(result) == 2


def test_criar_recorrente_vencimentos_corretos(svc, storage_mock):
    """Verifica que os vencimentos gerados são passados corretamente ao storage."""
    chamadas = []

    def _fake_create(descricao, valor, vencimento, competencia, categoria=None):
        chamadas.append(vencimento)
        return _boleto(vencimento=vencimento, competencia=competencia)

    storage_mock.create.side_effect = _fake_create
    svc.criar_recorrente("Test", 50.0, "2025-11-30", "2025-11", meses=3)
    assert chamadas[0] == "2025-11-30"
    assert chamadas[1] == "2025-12-30"
    assert chamadas[2] == "2026-01-30"


def test_criar_recorrente_fevereiro_ajusta_dia(svc, storage_mock):
    chamadas = []

    def _fake_create(descricao, valor, vencimento, competencia, categoria=None):
        chamadas.append(vencimento)
        return _boleto(vencimento=vencimento, competencia=competencia)

    storage_mock.create.side_effect = _fake_create
    svc.criar_recorrente("Seguro", 200.0, "2025-01-31", "2025-01", meses=2)
    assert chamadas[1] == "2025-02-28"


def test_criar_recorrente_passa_categoria(svc, storage_mock):
    storage_mock.create.return_value = _boleto()
    svc.criar_recorrente("Luz", 100.0, "2025-07-10", "2025-07", categoria="Energia", meses=1)
    _, kwargs = storage_mock.create.call_args
    # categoria pode vir como arg posicional ou keyword
    call_args = storage_mock.create.call_args
    assert "Energia" in call_args.args or call_args.kwargs.get("categoria") == "Energia"


# ── verificar_duplicata ───────────────────────────────────────────────────────

def test_verificar_duplicata_encontrada(svc, storage_mock):
    storage_mock.check_duplicate.return_value = True
    assert svc.verificar_duplicata("Netflix", "2025-07-01") is True
    storage_mock.check_duplicate.assert_called_once_with("Netflix", "2025-07-01")


def test_verificar_duplicata_nao_encontrada(svc, storage_mock):
    storage_mock.check_duplicate.return_value = False
    assert svc.verificar_duplicata("Netflix", "2025-07-01") is False


def test_verificar_duplicata_delega_ao_storage(svc, storage_mock):
    storage_mock.check_duplicate.return_value = False
    svc.verificar_duplicata("Água", "2025-08-15")
    storage_mock.check_duplicate.assert_called_once_with("Água", "2025-08-15")
