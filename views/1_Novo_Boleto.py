"""Página para registrar um novo boleto."""
import streamlit as st
from datetime import date
from auth import check_auth
from storage_service import StorageService

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 680px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

username = check_auth()
storage = StorageService(usuario=username)

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>➕ Novo Boleto</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Registre uma conta ou boleto para o mês.</p>", unsafe_allow_html=True)
st.divider()

# ── Formulário ─────────────────────────────────────────────────────────────
categorias_salvas = storage.get_categorias()
opcoes_cat = [""] + categorias_salvas + ["+ Nova categoria..."]

with st.form("form_novo_boleto", clear_on_submit=True):
    descricao = st.text_input(
        "Descrição *",
        placeholder="Ex: Conta de água, Netflix, Aluguel...",
        help="Nome do boleto ou conta.",
    )

    col_val, col_venc = st.columns(2)
    with col_val:
        valor = st.number_input(
            "Valor (R$) *",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            help="Valor exato do boleto.",
        )
    with col_venc:
        vencimento = st.date_input(
            "Data de vencimento *",
            value=date.today(),
            help="Dia em que o boleto vence.",
        )

    col_cat, col_rep = st.columns(2)
    with col_cat:
        cat_escolhida = st.selectbox(
            "Categoria",
            opcoes_cat,
            help="Opcional. Use para o resumo anual.",
        )
        nova_cat = None
        if cat_escolhida == "+ Nova categoria...":
            nova_cat = st.text_input(
                "Nome da nova categoria",
                placeholder="Ex: Pets, Academia...",
            )

    with col_rep:
        repetir = st.number_input(
            "Repetir por quantos meses?",
            min_value=1,
            max_value=24,
            value=1,
            step=1,
            help="1 = sem repetição. Ex: 3 cria boletos para este e os 2 meses seguintes.",
        )

    submitted = st.form_submit_button("💾 Salvar boleto", use_container_width=True, type="primary")

    if submitted:
        if not descricao.strip():
            st.error("A descrição é obrigatória.")
        elif valor <= 0:
            st.error("O valor deve ser maior que zero.")
        else:
            categoria_final = None
            if cat_escolhida == "+ Nova categoria..." and nova_cat and nova_cat.strip():
                storage.create_categoria(nova_cat.strip())
                categoria_final = nova_cat.strip()
            elif cat_escolhida and cat_escolhida != "+ Nova categoria...":
                categoria_final = cat_escolhida

            competencia = vencimento.strftime("%Y-%m")
            storage.create_recurring(
                descricao=descricao.strip(),
                valor=valor,
                vencimento=vencimento.strftime("%Y-%m-%d"),
                competencia=competencia,
                categoria=categoria_final,
                meses=int(repetir),
            )

            if repetir == 1:
                st.success(f"Boleto **{descricao.strip()}** registrado para {competencia}.")
            else:
                st.success(f"**{int(repetir)} boletos** de *{descricao.strip()}* criados a partir de {competencia}.")
