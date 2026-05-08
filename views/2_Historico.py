"""Página de histórico e resumo anual por categoria."""
import streamlit as st
import pandas as pd
from auth import check_auth, sidebar_logout
from storage_service import StorageService
from utils import format_currency, format_date_br

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 860px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

username = check_auth()
sidebar_logout()
storage = StorageService(usuario=username, access_token=st.session_state.get("access_token"))

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>📊 Histórico</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Consulte e filtre pagamentos e receitas registrados.</p>", unsafe_allow_html=True)
st.divider()

try:
    todos_boletos = storage.load_all()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

if not todos_boletos:
    st.info("Nenhum registro ainda. Use **Novo Pagamento / Receita** no menu lateral para começar.")
    st.stop()

meses = sorted({b["competencia"] for b in todos_boletos}, reverse=True)
anos  = sorted({b["competencia"][:4] for b in todos_boletos}, reverse=True)

# ── Filtros ─────────────────────────────────────────────────────────────────
col_fil1, col_fil2, col_fil3 = st.columns(3)
with col_fil1:
    mes_selecionado = st.selectbox("Filtrar por mês:", meses)
with col_fil2:
    ano_resumo = st.selectbox("Resumo anual — ano:", anos)
with col_fil3:
    ordenar_por = st.selectbox("Ordenar por:", ["Vencimento", "Valor ↑", "Valor ↓", "Descrição"])

# ── Tabela do mês — filtrado em memória (sem query extra) ────────────────────
boletos_filtrados = [b for b in todos_boletos if b["competencia"] == mes_selecionado]

_ordem = {
    "Vencimento": lambda x: x["vencimento"],
    "Valor ↑":    lambda x: x["valor"],
    "Valor ↓":    lambda x: -x["valor"],
    "Descrição":  lambda x: x["descricao"].lower(),
}
boletos_filtrados = sorted(boletos_filtrados, key=_ordem[ordenar_por])

_PAGE_SIZE = 50
total_filtrados = len(boletos_filtrados)

st.markdown(
    f"<div style='font-weight:600; color:#1E293B; margin:16px 0 8px'>"
    f"{total_filtrados} registro(s) em {mes_selecionado}</div>",
    unsafe_allow_html=True,
)

if boletos_filtrados:
    # ── Paginação (só exibe controles se houver mais de PAGE_SIZE itens) ──────
    if total_filtrados > _PAGE_SIZE:
        total_paginas = (total_filtrados - 1) // _PAGE_SIZE + 1
        pagina = st.number_input(
            f"Página (1–{total_paginas})",
            min_value=1, max_value=total_paginas, value=1, step=1,
        )
        inicio = (pagina - 1) * _PAGE_SIZE
        boletos_pagina = boletos_filtrados[inicio: inicio + _PAGE_SIZE]
        st.caption(f"Exibindo {inicio + 1}–{min(inicio + _PAGE_SIZE, total_filtrados)} de {total_filtrados}")
    else:
        boletos_pagina = boletos_filtrados

    df = pd.DataFrame(boletos_pagina)
    df["Status"] = df["pago"].map({True: "✅ Pago", False: "⏳ Pendente"})
    df["Valor"] = df["valor"].apply(format_currency)
    df["Vencimento"] = df["vencimento"].apply(format_date_br)
    df["Categoria"] = df["categoria"].fillna("—")
    df["Tipo"] = df["tipo"].map({"pagamento": "💸 Pagamento", "receita": "💰 Receita"}).fillna("💸 Pagamento")

    st.dataframe(
        df[["descricao", "Tipo", "Valor", "Vencimento", "Categoria", "Status"]],
        column_config={
            "descricao": st.column_config.TextColumn("Descrição"),
            "Tipo": st.column_config.TextColumn("Tipo"),
            "Valor": st.column_config.TextColumn("Valor"),
            "Vencimento": st.column_config.TextColumn("Vencimento"),
            "Categoria": st.column_config.TextColumn("Categoria"),
            "Status": st.column_config.TextColumn("Status"),
        },
        use_container_width=True,
        hide_index=True,
    )

# ── Resumo anual por categoria ───────────────────────────────────────────────
st.divider()
st.markdown(
    f"<h4 style='color:#1E293B'>Total por categoria em {ano_resumo}</h4>",
    unsafe_allow_html=True,
)

# Resumo por categoria — filtrado em memória (sem query extra)
totais: dict = {}
totais_rec: dict = {}
for b in todos_boletos:
    if not b["competencia"].startswith(ano_resumo):
        continue
    cat = b.get("categoria") or "Sem categoria"
    if b.get("tipo", "pagamento") == "receita":
        totais_rec[cat] = totais_rec.get(cat, 0) + b["valor"]
    else:
        totais[cat] = totais.get(cat, 0) + b["valor"]

if not totais and not totais_rec:
    st.info("Nenhum registro para este ano.")
else:
    tab_pag, tab_rec = st.tabs(["💸 Pagamentos", "💰 Receitas"])

    with tab_pag:
        if not totais:
            st.info("Nenhum pagamento registrado para este ano.")
        else:
            df_cat = pd.DataFrame(
                sorted(totais.items(), key=lambda x: -x[1]),
                columns=["Categoria", "Total"],
            )
            df_cat["Total (R$)"] = df_cat["Total"].apply(format_currency)
            col_tbl, col_chart = st.columns([1, 2])
            with col_tbl:
                st.dataframe(df_cat[["Categoria", "Total (R$)"]], use_container_width=True, hide_index=True)
            with col_chart:
                st.markdown("<div style='font-size:12px; color:#94A3B8; margin-bottom:4px'>Valores em R$</div>", unsafe_allow_html=True)
                st.bar_chart(df_cat.set_index("Categoria")["Total"], use_container_width=True, y_label="R$")

    with tab_rec:
        if not totais_rec:
            st.info("Nenhuma receita registrada para este ano.")
        else:
            df_rec = pd.DataFrame(
                sorted(totais_rec.items(), key=lambda x: -x[1]),
                columns=["Categoria", "Total"],
            )
            df_rec["Total (R$)"] = df_rec["Total"].apply(format_currency)
            col_tbl2, col_chart2 = st.columns([1, 2])
            with col_tbl2:
                st.dataframe(df_rec[["Categoria", "Total (R$)"]], use_container_width=True, hide_index=True)
            with col_chart2:
                st.markdown("<div style='font-size:12px; color:#94A3B8; margin-bottom:4px'>Valores em R$</div>", unsafe_allow_html=True)
                st.bar_chart(df_rec.set_index("Categoria")["Total"], use_container_width=True, y_label="R$", color="#059669")
