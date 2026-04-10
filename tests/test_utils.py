"""Testes para utils.py — lógica de datas e formatação."""
import pytest
from datetime import date, datetime
from unittest.mock import patch
from utils import (
    format_currency,
    format_date_br,
    days_until_due,
    is_overdue,
    is_due_soon,
    get_current_month,
    MESES_PT,
)


# ── format_currency ──────────────────────────────────────────────────────────

def test_format_currency_inteiro():
    assert format_currency(1000.0) == "R$ 1.000,00"


def test_format_currency_centavos():
    assert format_currency(0.99) == "R$ 0,99"


def test_format_currency_grande():
    assert format_currency(1234567.89) == "R$ 1.234.567,89"


def test_format_currency_zero():
    assert format_currency(0.0) == "R$ 0,00"


# ── format_date_br ───────────────────────────────────────────────────────────

def test_format_date_br():
    assert format_date_br("2025-03-15") == "15/03/2025"


def test_format_date_br_primeiro_dia():
    assert format_date_br("2025-01-01") == "01/01/2025"


# ── days_until_due ───────────────────────────────────────────────────────────

_HOJE = datetime(2025, 6, 15)


def test_days_until_due_hoje():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert days_until_due("2025-06-15") == 0


def test_days_until_due_futuro():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert days_until_due("2025-06-20") == 5


def test_days_until_due_passado():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert days_until_due("2025-06-10") == -5


# ── is_overdue / is_due_soon ─────────────────────────────────────────────────

def test_is_overdue_vencido():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert is_overdue("2025-06-14") is True


def test_is_overdue_hoje_nao_vencido():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert is_overdue("2025-06-15") is False


def test_is_due_soon_dentro():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert is_due_soon("2025-06-17") is True  # 2 dias


def test_is_due_soon_fora():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert is_due_soon("2025-06-19") is False  # 4 dias


def test_is_due_soon_vencido_nao_conta():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        assert is_due_soon("2025-06-14") is False  # já vencido


# ── MESES_PT ─────────────────────────────────────────────────────────────────

def test_meses_pt_completo():
    assert len(MESES_PT) == 12
    assert MESES_PT["01"] == "Janeiro"
    assert MESES_PT["12"] == "Dezembro"


def test_meses_pt_todos_os_meses():
    for i in range(1, 13):
        assert f"{i:02d}" in MESES_PT


# ── get_current_month ────────────────────────────────────────────────────────

def test_get_current_month_formato():
    mes = get_current_month()
    assert len(mes) == 7
    assert mes[4] == "-"
    # Verifica que é um ano e mês válidos
    ano, num = mes.split("-")
    assert ano.isdigit() and 2020 <= int(ano) <= 2100
    assert num.isdigit() and 1 <= int(num) <= 12


# ── extract_month ─────────────────────────────────────────────────────────────

def test_extract_month_basico():
    from utils import extract_month
    assert extract_month("2025-07-15") == "2025-07"


def test_extract_month_janeiro():
    from utils import extract_month
    assert extract_month("2025-01-01") == "2025-01"


def test_extract_month_dezembro():
    from utils import extract_month
    assert extract_month("2025-12-31") == "2025-12"


# ── is_due_soon com parâmetro days customizado ────────────────────────────────

def test_is_due_soon_custom_days():
    with patch("utils.datetime") as mock_dt:
        mock_dt.strptime = datetime.strptime
        mock_dt.now.return_value = _HOJE
        # vence em 7 dias, janela de 10 → True
        assert is_due_soon("2025-06-22", days=10) is True
        # vence em 7 dias, janela de 5 → False
        assert is_due_soon("2025-06-22", days=5) is False


# ── format_currency edge cases ────────────────────────────────────────────────

def test_format_currency_valor_muito_pequeno():
    assert format_currency(0.01) == "R$ 0,01"


def test_format_currency_milhao():
    assert format_currency(1_000_000.0) == "R$ 1.000.000,00"


# ── format_date_br edge cases ─────────────────────────────────────────────────

def test_format_date_br_fim_de_ano():
    assert format_date_br("2025-12-31") == "31/12/2025"


def test_format_date_br_fevereiro_bissexto():
    assert format_date_br("2024-02-29") == "29/02/2024"
