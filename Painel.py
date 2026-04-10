"""Dashboard — visão do mês atual."""
import html as _html
import streamlit as st
from app_logging import setup_logging
setup_logging()
from datetime import datetime, timedelta
from auth import check_auth, sidebar_logout
from storage_service import StorageService
from utils import (
    get_current_month,
    format_currency,
    format_date_br,
    days_until_due,
    is_overdue,
    is_due_soon,
    MESES_PT,
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 860px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.07);
    }
</style>
""", unsafe_allow_html=True)

username = check_auth()
sidebar_logout()
storage = StorageService(usuario=username)

if "current_month" not in st.session_state:
    st.session_state.current_month = get_current_month()

# ── Cabeçalho ──────────────────────────────────────────────────────────────
ano, mes = st.session_state.current_month.split("-")

col_title, col_nav = st.columns([3, 2])
with col_title:
    st.markdown(
        "<h2 style='margin-bottom:0; color:#1E293B'>💸 Tá Pago?</h2>",
        unsafe_allow_html=True,
    )

with col_nav:
    c_prev, c_label, c_next = st.columns([1, 1.8, 1])
    with c_prev:
        st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
        if st.button("←", use_container_width=True, help="Mês anterior"):
            d = datetime.strptime(st.session_state.current_month, "%Y-%m") - timedelta(days=1)
            st.session_state.current_month = d.strftime("%Y-%m")
            st.rerun()
    with c_label:
        st.markdown(
            f"<div style='margin-top:10px; text-align:center; font-weight:600; font-size:15px; color:#4F46E5'>"
            f"{MESES_PT[mes]}<br><span style='font-size:12px; color:#94A3B8; font-weight:400'>{ano}</span></div>",
            unsafe_allow_html=True,
        )
    with c_next:
        st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
        if st.button("→", use_container_width=True, help="Mês seguinte"):
            d = datetime.strptime(st.session_state.current_month, "%Y-%m") + timedelta(days=32)
            st.session_state.current_month = d.strftime("%Y-%m")
            st.rerun()

st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)

# ── Dados ───────────────────────────────────────────────────────────────────
try:
    boletos = storage.get_by_month(st.session_state.current_month)
except RuntimeError as e:
    st.error(str(e))
    st.stop()

total_mes = sum(b["valor"] for b in boletos)
total_pago = sum(b["valor"] for b in boletos if b["pago"])
total_pendente = total_mes - total_pago
pct_pago = int(total_pago / total_mes * 100) if total_mes > 0 else 0

# ── Cards de resumo ─────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("💰 Total do mês", format_currency(total_mes))
with c2:
    st.metric("✅ Pago", format_currency(total_pago))
with c3:
    st.metric("⏳ Pendente", format_currency(total_pendente))

st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
st.progress(pct_pago / 100, text=f"{pct_pago}% pago neste mês")
st.divider()

# ── Lista de boletos ─────────────────────────────────────────────────────────
if not boletos:
    st.info("Nenhum pagamento cadastrado para este mês. Use **Novo Pagamento** na barra lateral para adicionar.")
else:
    # ── Filtro por categoria ─────────────────────────────────────────────────
    categorias_mes = sorted({b["categoria"] for b in boletos if b.get("categoria")})
    if categorias_mes:
        cat_opcoes = ["Todas"] + categorias_mes
        cat_filtro = st.selectbox("Filtrar por categoria:", cat_opcoes, key="painel_cat_filtro")
        if cat_filtro != "Todas":
            boletos = [b for b in boletos if b.get("categoria") == cat_filtro]

    vencidos = [b for b in boletos if not b["pago"] and is_overdue(b["vencimento"])]
    proximos = [b for b in boletos if not b["pago"] and is_due_soon(b["vencimento"])]
    normais  = [b for b in boletos if not b["pago"] and not is_overdue(b["vencimento"]) and not is_due_soon(b["vencimento"])]
    pagos    = [b for b in boletos if b["pago"]]

    def card(b: dict, border_color: str, status_text: str, btn_key: str, undo: bool = False) -> None:
        cat = b.get("categoria") or ""
        descricao_safe = _html.escape(b["descricao"])
        cat_safe = _html.escape(cat)
        cat_html = (
            f'<span style="background:#EEF2FF; color:#4F46E5; padding:1px 8px; '
            f'border-radius:999px; font-size:11px; margin-left:8px">{cat_safe}</span>'
            if cat_safe else ""
        )
        valor_color = "#94A3B8" if undo else border_color
        col_info, col_btn = st.columns([7, 1])
        with col_info:
            st.markdown(
                f"""<div style="border-left:4px solid {border_color}; padding:10px 16px;
                    background:white; border-radius:0 10px 10px 0; margin-bottom:4px;
                    box-shadow:0 1px 2px rgba(0,0,0,0.05)">
                    <div style="display:flex; justify-content:space-between; align-items:center">
                        <div>
                            <strong style="font-size:15px; color:#1E293B">{descricao_safe}</strong>
                            {cat_html}
                        </div>
                        <strong style="color:{valor_color}; font-size:15px">{format_currency(b['valor'])}</strong>
                    </div>
                    <div style="color:#94A3B8; font-size:12px; margin-top:5px">{status_text}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with col_btn:
            st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
            label = "↩️" if undo else "✓"
            help_text = "Desfazer pagamento" if undo else "Marcar como pago"
            if st.button(label, key=btn_key, use_container_width=True, help=help_text):
                try:
                    with st.spinner("Atualizando..."):
                        storage.update_status(b["id"], not undo)
                except RuntimeError as e:
                    st.error(str(e))
                st.rerun()

    if vencidos:
        st.markdown(
            "<div style='color:#EF4444; font-weight:700; font-size:13px; "
            "text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px'>🔴 Vencidos</div>",
            unsafe_allow_html=True,
        )
        for b in vencidos:
            dias = abs(days_until_due(b["vencimento"]))
            card(b, "#EF4444", f"Vencido há {dias} dia(s) — {format_date_br(b['vencimento'])}", f"v_{b['id']}")

    if proximos:
        st.markdown(
            "<div style='color:#F59E0B; font-weight:700; font-size:13px; "
            "text-transform:uppercase; letter-spacing:0.06em; margin:16px 0 8px'>🟡 Próximos do vencimento</div>",
            unsafe_allow_html=True,
        )
        for b in proximos:
            dias = days_until_due(b["vencimento"])
            card(b, "#F59E0B", f"Vence em {dias} dia(s) — {format_date_br(b['vencimento'])}", f"p_{b['id']}")

    if normais:
        st.markdown(
            "<div style='color:#10B981; font-weight:700; font-size:13px; "
            "text-transform:uppercase; letter-spacing:0.06em; margin:16px 0 8px'>🟢 No prazo</div>",
            unsafe_allow_html=True,
        )
        for b in normais:
            dias = days_until_due(b["vencimento"])
            card(b, "#10B981", f"Vence em {dias} dia(s) — {format_date_br(b['vencimento'])}", f"n_{b['id']}")

    if pagos:
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        with st.expander(f"✅ Pagos ({len(pagos)})", expanded=False):
            for b in pagos:
                card(b, "#94A3B8", f"Vencimento: {format_date_br(b['vencimento'])}", f"pg_{b['id']}", undo=True)

# ── Rodapé ───────────────────────────────────────────────────────────────────
st.divider()
st.caption("🔒 Seus dados são privados · [Política de Privacidade](views/4_Privacidade.py) · Tá Pago?")
