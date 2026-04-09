"""Serviço de persistência de dados via Supabase."""
import os
from typing import List, Dict, Any
from datetime import datetime

try:
    import streamlit as st
    _url = st.secrets["supabase"]["url"]
    _key = st.secrets["supabase"]["key"]
except Exception:
    _url = os.environ.get("SUPABASE_URL", "")
    _key = os.environ.get("SUPABASE_KEY", "")

from supabase import create_client, Client


class StorageService:
    """Gerencia leitura, escrita e atualização de boletos no Supabase."""

    def __init__(self):
        self.client: Client = create_client(_url, _key)

    def _row(self, r: dict) -> Dict[str, Any]:
        """Normaliza resposta do Supabase para o formato esperado pelo app."""
        return {
            "id": str(r["id"]),
            "descricao": r["descricao"],
            "valor": float(r["valor"]),
            "vencimento": str(r["vencimento"]),
            "competencia": r["competencia"],
            "categoria": r.get("categoria"),
            "pago": r["pago"],
            "criado_em": r.get("criado_em", ""),
        }

    def load_all(self) -> List[Dict[str, Any]]:
        """Carrega todos os boletos."""
        res = self.client.table("boletos").select("*").order("vencimento").execute()
        return [self._row(r) for r in res.data]

    def save_all(self, boletos: List[Dict[str, Any]]) -> None:
        """No-op: Supabase é a fonte da verdade."""
        pass

    def create(self, descricao: str, valor: float, vencimento: str, competencia: str, categoria: str = None) -> Dict[str, Any]:
        """Cria novo boleto."""
        row = {
            "descricao": descricao,
            "valor": valor,
            "vencimento": vencimento,
            "competencia": competencia,
            "categoria": categoria,
            "pago": False,
        }
        res = self.client.table("boletos").insert(row).execute()
        return self._row(res.data[0])

    def create_recurring(self, descricao: str, valor: float, vencimento: str, competencia: str, categoria: str = None, meses: int = 1) -> List[Dict[str, Any]]:
        """Cria N boletos mensais a partir da data base."""
        criados = []
        base_date = datetime.strptime(vencimento, "%Y-%m-%d")
        for i in range(meses):
            nova_data = base_date.replace(
                month=((base_date.month - 1 + i) % 12) + 1,
                year=base_date.year + (base_date.month - 1 + i) // 12
            )
            nova_vencimento = nova_data.strftime("%Y-%m-%d")
            nova_competencia = nova_data.strftime("%Y-%m")
            criados.append(self.create(descricao, valor, nova_vencimento, nova_competencia, categoria))
        return criados

    def get_by_month(self, competencia: str) -> List[Dict[str, Any]]:
        """Retorna boletos de um mês específico."""
        res = (
            self.client.table("boletos")
            .select("*")
            .eq("competencia", competencia)
            .order("vencimento")
            .execute()
        )
        return [self._row(r) for r in res.data]

    def update_status(self, boleto_id: str, pago: bool) -> None:
        """Marca boleto como pago/não pago."""
        self.client.table("boletos").update({"pago": pago}).eq("id", int(boleto_id)).execute()

    def delete(self, boleto_id: str) -> None:
        """Remove um boleto."""
        self.client.table("boletos").delete().eq("id", int(boleto_id)).execute()

    def get_total_month(self, competencia: str) -> float:
        """Calcula total de boletos de um mês."""
        boletos = self.get_by_month(competencia)
        return sum(b["valor"] for b in boletos)

    def get_total_paid_month(self, competencia: str) -> float:
        """Calcula total de boletos pagos de um mês."""
        boletos = self.get_by_month(competencia)
        return sum(b["valor"] for b in boletos if b["pago"])

    def get_totals_by_category(self, year: str) -> Dict[str, float]:
        """Retorna soma de valores por categoria para um ano."""
        res = (
            self.client.table("boletos")
            .select("categoria, valor")
            .like("competencia", f"{year}-%")
            .execute()
        )
        totais: Dict[str, float] = {}
        for r in res.data:
            cat = r.get("categoria") or "Sem categoria"
            totais[cat] = totais.get(cat, 0) + float(r["valor"])
        return totais

    def get_categorias(self) -> List[str]:
        """Retorna lista de categorias salvas."""
        res = self.client.table("categorias").select("nome").order("nome").execute()
        return [r["nome"] for r in res.data]

    def create_categoria(self, nome: str) -> None:
        """Salva nova categoria (ignora duplicatas)."""
        self.client.table("categorias").upsert({"nome": nome}).execute()
