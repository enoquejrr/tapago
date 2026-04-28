"""Autenticação via Supabase Auth."""
import streamlit as st
from supabase import create_client, Client
import pages


@st.cache_resource
def _get_auth_client() -> Client:
    """Cria e cacheia o client de autenticação Supabase."""
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )


def get_client() -> Client:
    return _get_auth_client()


def check_auth() -> str:
    """Verifica sessão ativa e retorna o user_id (UUID). Redireciona para login se não autenticado."""
    # Sessão já carregada neste run
    if st.session_state.get("user"):
        return st.session_state["user"].id

    # Tenta restaurar a partir do access_token salvo
    if st.session_state.get("access_token"):
        try:
            client = get_client()
            res = client.auth.get_user(st.session_state["access_token"])
            st.session_state["user"] = res.user
            return res.user.id
        except Exception:
            st.session_state.pop("access_token", None)

    # Sem sessão válida — redireciona para login
    st.switch_page(pages.LOGIN)
    st.stop()


def logout():
    """Encerra sessão e redireciona para login."""
    try:
        client = get_client()
        client.auth.sign_out()
    except Exception:
        pass
    st.session_state.pop("user", None)
    st.session_state.pop("access_token", None)
    st.session_state.pop("supabase_client", None)  # força novo client no próximo login
    st.switch_page(pages.LOGIN)


def sidebar_logout():
    """Exibe email do usuário e botão Sair na sidebar."""
    user = st.session_state.get("user")
    if user:
        with st.sidebar:
            st.markdown("---")
            st.caption("👤 supporttapago@gmail.com")
            if st.button("Sair", use_container_width=True):
                logout()
