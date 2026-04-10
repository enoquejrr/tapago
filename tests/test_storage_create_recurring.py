"""Testes para BoletoService.criar_recorrente — foco em meses com <31 dias."""
from unittest.mock import MagicMock, patch
import pytest


@pytest.fixture
def boleto_svc(mock_supabase_client):
    with patch("storage_service._get_supabase_client", return_value=mock_supabase_client):
        from storage_service import StorageService
        from services.boleto_service import BoletoService

        storage = StorageService(usuario="user-abc")
        storage.client = mock_supabase_client

        def _fake_create(descricao, valor, vencimento, competencia, categoria=None):
            return {
                "id": "fake-id",
                "descricao": descricao,
                "valor": valor,
                "vencimento": vencimento,
                "competencia": competencia,
                "categoria": categoria,
                "pago": False,
                "criado_em": "",
            }
        storage.create = _fake_create
        return BoletoService(storage)


def test_recorrencia_simples(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Aluguel", valor=1500.0,
        vencimento="2025-03-10", competencia="2025-03", meses=1,
    )
    assert len(criados) == 1
    assert criados[0]["vencimento"] == "2025-03-10"
    assert criados[0]["competencia"] == "2025-03"


def test_recorrencia_tres_meses(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Academia", valor=99.0,
        vencimento="2025-03-15", competencia="2025-03", meses=3,
    )
    assert len(criados) == 3
    assert [c["vencimento"] for c in criados] == ["2025-03-15", "2025-04-15", "2025-05-15"]


def test_recorrencia_fevereiro_dia_31(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Seguro", valor=200.0,
        vencimento="2025-01-31", competencia="2025-01", meses=2,
    )
    assert criados[0]["vencimento"] == "2025-01-31"
    assert criados[1]["vencimento"] == "2025-02-28"


def test_recorrencia_fevereiro_bissexto(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Seguro", valor=200.0,
        vencimento="2024-01-31", competencia="2024-01", meses=2,
    )
    assert criados[1]["vencimento"] == "2024-02-29"


def test_recorrencia_dia_30_em_fevereiro(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Plano", valor=50.0,
        vencimento="2025-01-30", competencia="2025-01", meses=2,
    )
    assert criados[1]["vencimento"] == "2025-02-28"


def test_recorrencia_virada_de_ano(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Netflix", valor=39.90,
        vencimento="2025-11-05", competencia="2025-11", meses=3,
    )
    assert [c["competencia"] for c in criados] == ["2025-11", "2025-12", "2026-01"]
    assert [c["vencimento"] for c in criados] == ["2025-11-05", "2025-12-05", "2026-01-05"]


def test_recorrencia_competencia_correta(boleto_svc):
    criados = boleto_svc.criar_recorrente(
        descricao="Água", valor=80.0,
        vencimento="2025-06-20", competencia="2025-06", meses=4,
    )
    for c in criados:
        assert c["competencia"] == c["vencimento"][:7]
