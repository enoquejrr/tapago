"""Página de exclusão de pagamentos com seleção múltipla."""
import streamlit as st
from collections import defaultdict
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
storage = StorageService(usuario=username)

# Inicializa estados de controle
if "ids_para_excluir" not in st.session_state:
    st.session_state.ids_para_excluir = []
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "msg_sucesso" not in st.session_state:
    st.session_state.msg_sucesso = ""

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>🗑️ Excluir Pagamentos</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Selecione os pagamentos que deseja remover.</p>", unsafe_allow_html=True)
st.divider()

# ── Mensagem de sucesso persistida no session_state ──────────────────────────
if st.session_state.msg_sucesso:
    st.success(st.session_state.msg_sucesso)
    st.session_state.msg_sucesso = ""

todos_boletos = storage.load_all()

if not todos_boletos:
    st.info("Nenhum pagamento registrado ainda.")
    st.stop()

# Inicializa checkboxes para novos boletos
for b in todos_boletos:
    key = f"chk_{b['id']}"
    if key not in st.session_state:
        st.session_state[key] = False

# ── IDs selecionados (calculado dos checkboxes atuais) ───────────────────────
selecionados = [b["id"] for b in todos_boletos if st.session_state.get(f"chk_{b['id']}")]

# ── Bloco de confirmação ─────────────────────────────────────────────────────
if st.session_state.confirm_delete and st.session_state.ids_para_excluir:
    n = len(st.session_state.ids_para_excluir)
    st.warning(f"⚠️ Você está prestes a excluir **{n} pagamento(s)**. Esta ação **não pode ser desfeita**.")
    c1, c2 = st.columns(2)
    if c1.button("✓ Confirmar exclusão", type="primary", use_container_width=True):
        for bid in st.session_state.ids_para_excluir:
            storage.delete(bid)
            st.session_state.pop(f"chk_{bid}", None)
        n_excluidos = len(st.session_state.ids_para_excluir)
        st.session_state.ids_para_excluir = []
        st.session_state.confirm_delete = False
        st.session_state.msg_sucesso = f"✅ {n_excluidos} pagamento(s) excluído(s) com sucesso."
        st.rerun()
    if c2.button("✗ Cancelar", use_container_width=True):
        st.session_state.ids_para_excluir = []
        st.session_state.confirm_delete = False
        st.rerun()

# ── Barra de ação ────────────────────────────────────────────────────────────
elif selecionados:
    col_info, col_btn = st.columns([3, 2])
    with col_info:
        st.markdown(
            f"<div style='padding:10px 0; color:#1E293B; font-weight:600'>"
            f"{len(selecionados)} pagamento(s) selecionado(s)</div>",
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button(f"🗑️ Excluir {len(selecionados)} pagamento(s)", type="primary", use_container_width=True):
            st.session_state.ids_para_excluir = list(selecionados)
            st.session_state.confirm_delete = True
            st.rerun()

st.divider()

# ── Lista por mês ────────────────────────────────────────────────────────────
MESES_PT = {
    "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
    "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
    "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro",
}

por_mes = defaultdict(list)
for b in todos_boletos:
    por_mes[b["competencia"]].append(b)
meses_ordenados = sorted(por_mes.keys(), reverse=True)

for mes in meses_ordenados:
    boletos_mes = por_mes[mes]
    ano, num_mes = mes.split("-")
    ids_mes = [b["id"] for b in boletos_mes]
    n_sel_mes = sum(1 for bid in ids_mes if st.session_state.get(f"chk_{bid}"))
    titulo = f"{MESES_PT[num_mes]} {ano} — {len(boletos_mes)} pagamento(s)"
    if n_sel_mes:
        titulo += f" · {n_sel_mes} selecionado(s)"

    with st.expander(titulo, expanded=True):
        col_sel, col_desel = st.columns(2)
        with col_sel:
            if st.button("☑ Selecionar todos", key=f"sel_{mes}", use_container_width=True):
                for bid in ids_mes:
                    st.session_state[f"chk_{bid}"] = True
                st.rerun()
        with col_desel:
            if st.button("☐ Desmarcar todos", key=f"desel_{mes}", use_container_width=True):
                for bid in ids_mes:
                    st.session_state[f"chk_{bid}"] = False
                st.rerun()

        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

        for b in boletos_mes:
            col_chk, col_info = st.columns([0.5, 9])
            with col_chk:
                st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
                st.checkbox("", key=f"chk_{b['id']}", label_visibility="collapsed")
            with col_info:
                cat = f" · {b['categoria']}" if b.get("categoria") else ""
                status = "✅" if b["pago"] else "⏳"
                st.markdown(
                    f"<div style='padding:6px 0; border-bottom:1px solid #F1F5F9'>"
                    f"<strong>{b['descricao']}</strong>"
                    f"<span style='color:#64748B; font-size:13px'>{cat}</span>"
                    f"&nbsp;&nbsp;"
                    f"<span style='color:#4F46E5; font-weight:600'>{format_currency(b['valor'])}</span>"
                    f"&nbsp;&nbsp;"
                    f"<span style='color:#94A3B8; font-size:12px'>Venc. {format_date_br(b['vencimento'])} {status}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
