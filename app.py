"""Ponto de entrada — define navegação e nomes do menu lateral."""
import streamlit as st

st.set_page_config(
    page_title="Tá Pago?",
    page_icon="💸",
    layout="centered",
    initial_sidebar_state="expanded",
)

pg = st.navigation([
    st.Page("Painel.py",                   title="Painel",      icon="💸"),
    st.Page("views/1_Novo_Boleto.py",      title="Novo Boleto", icon="➕"),
    st.Page("views/2_Historico.py",        title="Histórico",   icon="📊"),
])
pg.run()
