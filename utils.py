"""Funções utilitárias para lógica de datas e formatação."""
from datetime import datetime, timedelta


def get_current_month() -> str:
    """Retorna competência atual no formato YYYY-MM."""
    return datetime.now().strftime("%Y-%m")


def days_until_due(vencimento: str) -> int:
    """Calcula dias até vencimento. Retorna negativo se vencido."""
    due_date = datetime.strptime(vencimento, "%Y-%m-%d").date()
    today = datetime.now().date()
    return (due_date - today).days


def is_overdue(vencimento: str) -> bool:
    """Verifica se a data de vencimento já passou."""
    return days_until_due(vencimento) < 0


def is_due_soon(vencimento: str, days: int = 3) -> bool:
    """Verifica se vence em até N dias (não vencido)."""
    delta = days_until_due(vencimento)
    return 0 <= delta <= days


def format_currency(value: float) -> str:
    """Formata valor em moeda brasileira."""
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_date_br(date_str: str) -> str:
    """Converte YYYY-MM-DD para DD/MM/YYYY."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%d/%m/%Y")


def extract_month(date_str: str) -> str:
    """Extrai competência (YYYY-MM) de uma data YYYY-MM-DD."""
    return date_str[:7]
