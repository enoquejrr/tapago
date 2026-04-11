"""Tela de login, cadastro e recuperação de senha."""
import time
import streamlit as st
from auth import get_client
import pages

_MAX_TENTATIVAS = 5
_BLOQUEIO_SEGUNDOS = 60


def _check_rate_limit() -> bool:
    """Retorna True se o login está bloqueado. Exibe aviso com tempo restante."""
    agora = time.time()
    bloqueado_ate = st.session_state.get("login_bloqueado_ate", 0)
    if agora < bloqueado_ate:
        restante = int(bloqueado_ate - agora)
        st.error(f"Muitas tentativas. Aguarde {restante}s para tentar novamente.")
        return True
    return False


def _registrar_falha() -> None:
    """Incrementa contador de falhas; bloqueia após MAX_TENTATIVAS."""
    agora = time.time()
    # Zera contador se o bloqueio anterior já expirou
    if agora >= st.session_state.get("login_bloqueado_ate", 0):
        tentativas = st.session_state.get("login_tentativas", 0) + 1
        st.session_state["login_tentativas"] = tentativas
        if tentativas >= _MAX_TENTATIVAS:
            st.session_state["login_bloqueado_ate"] = agora + _BLOQUEIO_SEGUNDOS
            st.session_state["login_tentativas"] = 0


def _registrar_sucesso() -> None:
    """Zera contadores após login bem-sucedido."""
    st.session_state.pop("login_tentativas", None)
    st.session_state.pop("login_bloqueado_ate", None)

st.markdown("""
<style>
    .block-container { padding-top: 3rem !important; max-width: 480px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# Se já está logado, vai direto para o painel
if st.session_state.get("user"):
    st.switch_page(pages.PAINEL)

st.markdown(
    "<h2 style='text-align:center; color:#1E293B; margin-bottom:4px'>💸 Tá Pago?</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#64748B; margin-bottom:24px'>Organize seus pagamentos mensais</p>",
    unsafe_allow_html=True,
)

tab_entrar, tab_cadastro, tab_senha = st.tabs(["Entrar", "Criar conta", "Esqueci a senha"])

client = get_client()

# ── Entrar ───────────────────────────────────────────────────────────────────
with tab_entrar:
    with st.form("form_login"):
        email = st.text_input("Email", placeholder="seu@email.com")
        senha = st.text_input("Senha", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")

    if submitted:
        if _check_rate_limit():
            pass  # mensagem já exibida dentro de _check_rate_limit
        elif not email or not senha:
            st.error("Preencha email e senha.")
        else:
            try:
                with st.spinner("Entrando..."):
                    res = client.auth.sign_in_with_password({"email": email, "password": senha})
                _registrar_sucesso()
                st.session_state["user"] = res.user
                st.session_state["access_token"] = res.session.access_token
                st.rerun()
            except Exception as e:
                _registrar_falha()
                msg = str(e).lower()
                if "invalid" in msg or "credentials" in msg:
                    tentativas = st.session_state.get("login_tentativas", 0)
                    restantes = max(0, _MAX_TENTATIVAS - tentativas)
                    aviso = f" ({restantes} tentativa(s) restante(s))" if restantes > 0 else ""
                    st.error(f"Email ou senha incorretos.{aviso}")
                elif "confirmed" in msg or "not confirmed" in msg:
                    st.warning("Confirme seu email antes de entrar. Verifique sua caixa de entrada.")
                else:
                    st.error("Erro ao entrar. Tente novamente.")

# ── Criar conta ──────────────────────────────────────────────────────────────
with tab_cadastro:
    with st.form("form_cadastro"):
        email_c = st.text_input("Email", placeholder="seu@email.com", key="cad_email")
        senha_c = st.text_input("Senha", type="password", placeholder="Mínimo 6 caracteres", key="cad_senha")
        senha_c2 = st.text_input("Confirmar senha", type="password", placeholder="Repita a senha", key="cad_senha2")
        submitted_c = st.form_submit_button("Criar conta", use_container_width=True, type="primary")

    if submitted_c:
        if not email_c or not senha_c:
            st.error("Preencha todos os campos.")
        elif senha_c != senha_c2:
            st.error("As senhas não coincidem.")
        elif len(senha_c) < 6:
            st.error("A senha deve ter pelo menos 6 caracteres.")
        else:
            try:
                client.auth.sign_up({"email": email_c, "password": senha_c})
                st.success("Conta criada! Verifique seu email e clique no link de confirmação antes de entrar.")
            except Exception as e:
                msg = str(e).lower()
                if "already" in msg or "registered" in msg:
                    st.error("Este email já está cadastrado. Tente entrar ou recuperar a senha.")
                else:
                    st.error(f"Erro ao criar conta: {e}")

# ── Esqueci a senha ──────────────────────────────────────────────────────────
with tab_senha:
    with st.form("form_senha"):
        email_r = st.text_input("Email cadastrado", placeholder="seu@email.com", key="rec_email")
        submitted_r = st.form_submit_button("Enviar link de recuperação", use_container_width=True, type="primary")

    if submitted_r:
        if not email_r:
            st.error("Informe seu email.")
        else:
            try:
                client.auth.reset_password_email(email_r)
                st.success("Link enviado! Verifique sua caixa de entrada.")
            except Exception as e:
                st.error(f"Erro ao enviar link: {e}")
