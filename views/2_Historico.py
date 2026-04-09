"""Página de histórico e resumo anual por categoria."""
import streamlit as st
import pandas as pd
from auth import check_auth
from storage_service import StorageService
from utils import format_currency, format_date_br

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 860px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

username = check_auth()
storage = StorageService(usuario=username)

if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>📊 Histórico</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Consulte, filtre e exclua boletos registrados.</p>", unsafe_allow_html=True)
st.divider()

todos_boletos = storage.load_all()

if not todos_boletos:
    st.info("Nenhum boleto registrado ainda.")
    st.stop()

meses = sorted({b["competencia"] for b in todos_boletos}, reverse=True)
anos  = sorted({b["competencia"][:4] for b in todos_boletos}, reverse=True)

# ── Filtros ─────────────────────────────────────────────────────────────────
col_fil1, col_fil2 = st.columns(2)
with col_fil1:
    mes_selecionado = st.selectbox("Filtrar por mês:", meses)
with col_fil2:
    ano_resumo = st.selectbox("Resumo anual — ano:", anos)

# ── Tabela do mês ────────────────────────────────────────────────────────────
boletos_filtrados = storage.get_by_month(mes_selecionado)

st.markdown(
    f"<div style='font-weight:600; color:#1E293B; margin:16px 0 8px'>"
    f"{len(boletos_filtrados)} boleto(s) em {mes_selecionado}</div>",
    unsafe_allow_html=True,
)

if boletos_filtrados:
    df = pd.DataFrame(boletos_filtrados)
    df["Status"] = df["pago"].map({True: "✅ Pago", False: "⏳ Pendente"})
    df["Valor"] = df["valor"].apply(format_currency)
    df["Vencimento"] = df["vencimento"].apply(format_date_br)
    df["Categoria"] = df["categoria"].fillna("—")

    st.dataframe(
        df[["descricao", "Valor", "Vencimento", "Categoria", "Status"]],
        column_config={
            "descricao": st.column_config.TextColumn("Descrição"),
            "Valor": st.column_config.TextColumn("Valor"),
            "Vencimento": st.column_config.TextColumn("Vencimento"),
            "Categoria": st.column_config.TextColumn("Categoria"),
            "Status": st.column_config.TextColumn("Status"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # ── Exclusão com confirmação ─────────────────────────────────────────────
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    del_id = st.selectbox(
        "Excluir boleto:",
        options=[b["id"] for b in boletos_filtrados],
        format_func=lambda bid: next(b["descricao"] for b in boletos_filtrados if b["id"] == bid),
        index=None,
        placeholder="Selecione para excluir...",
    )

    if del_id:
        if st.session_state.delete_confirm == del_id:
            st.warning("Tem certeza? Esta ação não pode ser desfeita.")
            c1, c2 = st.columns(2)
            if c1.button("✓ Confirmar exclusão", type="primary", use_container_width=True):
                storage.delete(del_id)
                st.session_state.delete_confirm = None
                st.rerun()
            if c2.button("✗ Cancelar", use_container_width=True):
                st.session_state.delete_confirm = None
                st.rerun()
        else:
            if st.button("🗑️ Excluir selecionado"):
                st.session_state.delete_confirm = del_id
                st.rerun()

# ── Resumo anual por categoria ───────────────────────────────────────────────
st.divider()
st.markdown(
    f"<h4 style='color:#1E293B'>Total por categoria em {ano_resumo}</h4>",
    unsafe_allow_html=True,
)

totais = storage.get_totals_by_category(ano_resumo)
if not totais:
    st.info("Nenhum dado para este ano.")
else:
    df_cat = pd.DataFrame(
        sorted(totais.items(), key=lambda x: -x[1]),
        columns=["Categoria", "Total"],
    )
    df_cat["Total (R$)"] = df_cat["Total"].apply(format_currency)

    col_tbl, col_chart = st.columns([1, 2])
    with col_tbl:
        st.dataframe(
            df_cat[["Categoria", "Total (R$)"]],
            use_container_width=True,
            hide_index=True,
        )
    with col_chart:
        st.bar_chart(df_cat.set_index("Categoria")["Total"])
