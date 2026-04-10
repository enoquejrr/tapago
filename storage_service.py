"""Serviço de persistência de dados via Supabase."""
import logging
import os
from typing import List, Dict, Any
from models import Boleto

import streamlit as st
from supabase import create_client, Client

logger = logging.getLogger(__name__)


def _get_supabase_client(access_token: str = None) -> Client:
    """Retorna client Supabase isolado por sessão de usuário.

    Usa st.session_state em vez de @st.cache_resource para evitar que o
    token de um usuário sobrescreva o de outro no objeto compartilhado.
    """
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except Exception:
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")

    if "supabase_client" not in st.session_state:
        st.session_state["supabase_client"] = create_client(url, key)

    client: Client = st.session_state["supabase_client"]
    if access_token:
        client.postgrest.auth(access_token)
    return client


class StorageService:
    """Gerencia leitura, escrita e atualização de boletos no Supabase."""

    def __init__(self, usuario: str = None, access_token: str = None):
        self.client: Client = _get_supabase_client(access_token)
        self.usuario = usuario

    def _row(self, r: dict) -> Boleto:
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

    def _query(self):
        """Query base já filtrada pelo usuário logado."""
        return self.client.table("boletos").select("*").eq("usuario", self.usuario)

    # ── Leitura ────────────────────────────────────────────────────────────────

    def load_all(self) -> List[Boleto]:
        """Carrega todos os boletos do usuário."""
        try:
            res = self._query().order("vencimento").execute()
            return [self._row(r) for r in res.data]
        except Exception as e:
            logger.error("Erro ao carregar boletos: %s", e, exc_info=True)
            raise RuntimeError("Não foi possível carregar os pagamentos. Tente novamente.") from e

    def get_by_month(self, competencia: str) -> List[Boleto]:
        """Retorna boletos de um mês específico do usuário."""
        try:
            res = (
                self._query()
                .eq("competencia", competencia)
                .order("vencimento")
                .execute()
            )
            return [self._row(r) for r in res.data]
        except Exception as e:
            logger.error("Erro ao buscar boletos do mês %s: %s", competencia, e, exc_info=True)
            raise RuntimeError("Não foi possível carregar os pagamentos do mês. Tente novamente.") from e

    def check_duplicate(self, descricao: str, vencimento: str) -> bool:
        """Verifica se já existe pagamento com mesmo nome e data de vencimento."""
        try:
            res = (
                self._query()
                .eq("descricao", descricao)
                .eq("vencimento", vencimento)
                .execute()
            )
            return len(res.data) > 0
        except Exception as e:
            logger.error("Erro ao verificar duplicata: %s", e, exc_info=True)
            return False  # em caso de erro, não bloqueia o usuário

    def get_categorias(self) -> List[str]:
        """Retorna lista de categorias do usuário logado."""
        try:
            res = (
                self.client.table("categorias")
                .select("nome")
                .eq("usuario", self.usuario)
                .order("nome")
                .execute()
            )
            return [r["nome"] for r in res.data]
        except Exception as e:
            logger.error("Erro ao buscar categorias: %s", e, exc_info=True)
            return []

    # ── Escrita ────────────────────────────────────────────────────────────────

    def create(self, descricao: str, valor: float, vencimento: str, competencia: str, categoria: str = None) -> Boleto:
        """Cria novo boleto para o usuário logado."""
        try:
            row = {
                "descricao": descricao,
                "valor": valor,
                "vencimento": vencimento,
                "competencia": competencia,
                "categoria": categoria,
                "pago": False,
                "usuario": self.usuario,
            }
            res = self.client.table("boletos").insert(row).execute()
            if not res.data:
                raise RuntimeError("Resposta vazia do servidor ao criar pagamento.")
            return self._row(res.data[0])
        except RuntimeError:
            raise
        except Exception as e:
            logger.error("Erro ao criar boleto: %s", e, exc_info=True)
            raise RuntimeError("Não foi possível salvar o pagamento. Tente novamente.") from e

    def update_status(self, boleto_id: str, pago: bool) -> None:
        """Marca boleto como pago/não pago."""
        try:
            self.client.table("boletos").update({"pago": pago}).eq("id", boleto_id).eq("usuario", self.usuario).execute()
        except Exception as e:
            logger.error("Erro ao atualizar status do boleto %s: %s", boleto_id, e, exc_info=True)
            raise RuntimeError("Não foi possível atualizar o status. Tente novamente.") from e

    def delete(self, boleto_id: str) -> None:
        """Remove um boleto."""
        try:
            self.client.table("boletos").delete().eq("id", boleto_id).eq("usuario", self.usuario).execute()
        except Exception as e:
            logger.error("Erro ao excluir boleto %s: %s", boleto_id, e, exc_info=True)
            raise RuntimeError("Não foi possível excluir o pagamento. Tente novamente.") from e

    def create_categoria(self, nome: str) -> None:
        """Salva nova categoria para o usuário logado (ignora duplicatas)."""
        try:
            self.client.table("categorias").insert(
                {"nome": nome, "usuario": self.usuario}
            ).execute()
        except Exception as e:
            msg = str(e).lower()
            if "duplicate" in msg or "unique" in msg or "23505" in msg:
                return  # categoria já existe para este usuário — sem erro
            logger.error("Erro ao criar categoria: %s", e, exc_info=True)
            raise RuntimeError("Não foi possível salvar a categoria. Tente novamente.") from e
