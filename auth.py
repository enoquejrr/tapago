"""Helper de autenticação compartilhado entre todas as páginas."""
import streamlit as st
import streamlit_authenticator as stauth


def check_auth() -> str:
    """Exibe login se necessário e retorna o username autenticado."""
    authenticator = stauth.Authenticate(
        st.secrets["credentials"].to_dict(),
        st.secrets["cookie"]["name"],
        st.secrets["cookie"]["key"],
        st.secrets["cookie"]["expiry_days"],
    )
    authenticator.login()
    if not st.session_state.get("authentication_status"):
        st.stop()
    authenticator.logout("Sair", "sidebar")
    return st.session_state["username"]
