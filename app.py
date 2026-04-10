"""Ponto de entrada — define navegação e nomes do menu lateral."""
import streamlit as st

st.set_page_config(
    page_title="Tá Pago?",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="expanded",
)

if not st.session_state.get("user"):
    pg = st.navigation(
        [st.Page("views/0_Login.py", title="Login", icon="🔐")],
        position="hidden",
    )
else:
    pg = st.navigation([
        st.Page("Painel.py",               title="Painel",          icon="💸"),
        st.Page("views/1_Novo_Boleto.py",  title="Novo Pagamento",  icon="➕"),
        st.Page("views/2_Historico.py",    title="Histórico",       icon="📊"),
        st.Page("views/3_Excluir.py",      title="Excluir",         icon="🗑️"),
    ])

pg.run()
