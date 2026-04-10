"""Modelos de dados do app Tá Pago? (TypedDict)."""
from typing import Optional
from typing_extensions import TypedDict, Required


class Boleto(TypedDict, total=False):
    id:          Required[str]
    descricao:   Required[str]
    valor:       Required[float]
    vencimento:  Required[str]   # YYYY-MM-DD
    competencia: Required[str]   # YYYY-MM
    pago:        Required[bool]
    categoria:   Optional[str]
    criado_em:   str


class Categoria(TypedDict):
    nome:    str
    usuario: str
