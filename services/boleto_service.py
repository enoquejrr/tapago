"""Serviço de negócio para boletos/pagamentos.

Responsabilidades:
- Regras de negócio: recorrência mensal, detecção de duplicatas
- Orquestra chamadas ao StorageService (camada de dados)

O StorageService cuida apenas do acesso ao banco (Supabase).
"""
import calendar
from datetime import datetime
from typing import List, Optional

from models import Boleto
from storage_service import StorageService


class BoletoService:
    def __init__(self, storage: StorageService):
        self.storage = storage

    def criar_recorrente(
        self,
        descricao: str,
        valor: float,
        vencimento: str,
        competencia: str,
        categoria: Optional[str] = None,
        meses: int = 1,
    ) -> List[Boleto]:
        """Cria N boletos mensais corrigindo dias inválidos (ex: 31 de fevereiro).

        Regra: o dia do vencimento é mantido quando possível; caso o mês de
        destino tenha menos dias, usa o último dia válido do mês.
        """
        criados: List[Boleto] = []
        base_date = datetime.strptime(vencimento, "%Y-%m-%d")

        for i in range(meses):
            month = ((base_date.month - 1 + i) % 12) + 1
            year = base_date.year + (base_date.month - 1 + i) // 12
            max_day = calendar.monthrange(year, month)[1]
            day = min(base_date.day, max_day)
            nova_data = base_date.replace(year=year, month=month, day=day)
            nova_vencimento = nova_data.strftime("%Y-%m-%d")
            nova_competencia = nova_data.strftime("%Y-%m")
            criados.append(
                self.storage.create(descricao, valor, nova_vencimento, nova_competencia, categoria)
            )

        return criados

    def verificar_duplicata(self, descricao: str, vencimento: str) -> bool:
        """Retorna True se já existe pagamento com mesmo nome e data de vencimento."""
        return self.storage.check_duplicate(descricao, vencimento)
