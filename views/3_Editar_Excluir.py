"""Página de edição e exclusão de pagamentos."""
import html as _html
from datetime import datetime, date
import streamlit as st
from collections import defaultdict
from auth import check_auth, sidebar_logout
from storage_service import StorageService
from utils import format_currency, format_date_br, MESES_PT

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 860px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

username = check_auth()
sidebar_logout()
storage = StorageService(usuario=username, access_token=st.session_state.get("access_token"))

# Inicializa estados de controle
if "ids_para_excluir" not in st.session_state:
    st.session_state.ids_para_excluir = []
if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False
if "editando_id" not in st.session_state:
    st.session_state.editando_id = None

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>✏️ Editar / Excluir Pagamentos</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Selecione para excluir ou clique em ✏️ para editar.</p>", unsafe_allow_html=True)
st.divider()

try:
    todos_boletos = storage.load_all()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

if not todos_boletos:
    st.info("Nenhum pagamento registrado ainda. Use **Novo Pagamento** no menu lateral para começar.")
    st.stop()

# Inicializa checkboxes para novos boletos
for b in todos_boletos:
    key = f"chk_{b['id']}"
    if key not in st.session_state:
        st.session_state[key] = False

# ── Modo edição ──────────────────────────────────────────────────────────────
if st.session_state.editando_id:
    boleto_edit = next((b for b in todos_boletos if b["id"] == st.session_state.editando_id), None)

    if boleto_edit is None:
        st.session_state.editando_id = None
        st.rerun()

    st.markdown(
        f"<div style='background:#F0F9FF; border:1px solid #BAE6FD; border-radius:10px; padding:16px 20px; margin-bottom:16px'>"
        f"<strong style='color:#0369A1'>✏️ Editando: {_html.escape(boleto_edit['descricao'])}</strong>"
        f"</div>",
        unsafe_allow_html=True,
    )

    categorias = storage.get_categorias()
    cat_atual = boleto_edit.get("categoria")
    cat_opcoes = ["(sem categoria)"] + categorias
    cat_index = cat_opcoes.index(cat_atual) if cat_atual in cat_opcoes else 0

    with st.form("form_edicao"):
        col1, col2 = st.columns(2)
        with col1:
            nova_categoria = st.selectbox("Categoria", cat_opcoes, index=cat_index)
            nova_descricao = st.text_input("Descrição", value=boleto_edit["descricao"], max_chars=200)
        with col2:
            novo_valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, value=boleto_edit["valor"], format="%.2f")
            venc_atual = date.fromisoformat(boleto_edit["vencimento"])
            novo_vencimento = st.date_input("Data de vencimento", value=venc_atual)

        c_salvar, c_cancelar = st.columns(2)
        salvar = c_salvar.form_submit_button("✓ Salvar alterações", type="primary", use_container_width=True)
        cancelar = c_cancelar.form_submit_button("✗ Cancelar", use_container_width=True)

    if salvar:
        if not nova_descricao.strip():
            st.error("A descrição não pode estar vazia.")
        else:
            cat_final = None if nova_categoria == "(sem categoria)" else nova_categoria
            try:
                with st.spinner("Salvando alterações..."):
                    storage.update(
                        boleto_id=st.session_state.editando_id,
                        descricao=nova_descricao.strip(),
                        valor=novo_valor,
                        vencimento=str(novo_vencimento),
                        categoria=cat_final,
                    )
                st.session_state.editando_id = None
                st.toast("Pagamento atualizado com sucesso.", icon="✅")
            except RuntimeError as e:
                st.error(str(e))
            st.rerun()

    if cancelar:
        st.session_state.editando_id = None
        st.rerun()

    st.divider()

# ── IDs selecionados (calculado dos checkboxes atuais) ───────────────────────
em_edicao = st.session_state.editando_id is not None
selecionados = [b["id"] for b in todos_boletos if st.session_state.get(f"chk_{b['id']}")]

# ── Bloco de confirmação ─────────────────────────────────────────────────────
if not em_edicao and st.session_state.confirm_delete and st.session_state.ids_para_excluir:
    n = len(st.session_state.ids_para_excluir)
    st.warning(f"⚠️ Você está prestes a excluir **{n} pagamento(s)**. Esta ação **não pode ser desfeita**.")
    c1, c2 = st.columns(2)
    if c1.button("✓ Confirmar exclusão", type="primary", use_container_width=True):
        try:
            n_excluidos = len(st.session_state.ids_para_excluir)
            with st.spinner(f"Excluindo {n_excluidos} pagamento(s)..."):
                for bid in st.session_state.ids_para_excluir:
                    storage.delete(bid)
                    st.session_state.pop(f"chk_{bid}", None)
            st.session_state.ids_para_excluir = []
            st.session_state.confirm_delete = False
            st.toast(f"{n_excluidos} pagamento(s) excluído(s) com sucesso.", icon="✅")
        except RuntimeError as e:
            st.error(str(e))
            st.session_state.ids_para_excluir = []
            st.session_state.confirm_delete = False
        st.rerun()
    if c2.button("✗ Cancelar", use_container_width=True):
        st.session_state.ids_para_excluir = []
        st.session_state.confirm_delete = False
        st.rerun()

# ── Barra de ação ────────────────────────────────────────────────────────────
elif not em_edicao and selecionados:
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

# ── Seleção rápida por nome ──────────────────────────────────────────────────
if not em_edicao:
    # Agrupa por descrição para montar o painel
    por_nome: dict[str, list] = defaultdict(list)
    for b in todos_boletos:
        por_nome[b["descricao"]].append(b)

    # Só mostra o painel se houver nomes com mais de 1 ocorrência
    nomes_repetidos = {nome: boletos for nome, boletos in por_nome.items() if len(boletos) > 1}

    if nomes_repetidos:
        with st.expander("⚡ Seleção rápida por nome", expanded=True):
            st.markdown(
                "<p style='color:#64748B; font-size:13px; margin-top:0; margin-bottom:12px'>"
                "Selecione todas as ocorrências de um pagamento de uma vez.</p>",
                unsafe_allow_html=True,
            )
            for nome, boletos_nome in sorted(nomes_repetidos.items()):
                ids_nome = [b["id"] for b in boletos_nome]
                total_valor = sum(b["valor"] for b in boletos_nome)
                n_sel = sum(1 for bid in ids_nome if st.session_state.get(f"chk_{bid}"))
                todos_sel = n_sel == len(ids_nome)

                col_desc, col_info_rapido, col_btn_rapido = st.columns([4, 3, 2])
                with col_desc:
                    badge = f" <span style='color:#4F46E5; font-weight:700'>[{n_sel}/{len(ids_nome)}]</span>" if n_sel else ""
                    st.markdown(
                        f"<div style='padding:8px 0'>"
                        f"<strong>{_html.escape(nome)}</strong>{badge}<br>"
                        f"<span style='color:#64748B; font-size:12px'>"
                        f"{len(ids_nome)}x · {format_currency(total_valor)} no total</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with col_info_rapido:
                    st.markdown("<div style='padding:8px 0'></div>", unsafe_allow_html=True)
                with col_btn_rapido:
                    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
                    label = "☐ Desmarcar" if todos_sel else "☑ Selecionar todas"
                    if st.button(label, key=f"rapido_{nome}", use_container_width=True):
                        for bid in ids_nome:
                            st.session_state[f"chk_{bid}"] = not todos_sel
                        st.rerun()

        st.divider()

# ── Lista por mês ────────────────────────────────────────────────────────────
mes_atual = datetime.now().strftime("%Y-%m")

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

    with st.expander(titulo, expanded=(mes == mes_atual)):
        if not em_edicao:
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
            col_chk, col_info, col_edit = st.columns([0.5, 8, 1])
            with col_chk:
                st.markdown("<div style='margin-top:4px'></div>", unsafe_allow_html=True)
                st.checkbox("", key=f"chk_{b['id']}", label_visibility="collapsed", disabled=em_edicao)
            with col_info:
                cat_raw = f" · {b['categoria']}" if b.get("categoria") else ""
                cat = _html.escape(cat_raw)
                descricao_safe = _html.escape(b["descricao"])
                status = "✅" if b["pago"] else "⏳"
                is_editing_this = b["id"] == st.session_state.editando_id
                bg = "background:#EFF6FF;" if is_editing_this else ""
                st.markdown(
                    f"<div style='padding:6px 0; border-bottom:1px solid #F1F5F9; {bg}'>"
                    f"<strong>{descricao_safe}</strong>"
                    f"<span style='color:#64748B; font-size:13px'>{cat}</span>"
                    f"&nbsp;&nbsp;"
                    f"<span style='color:#4F46E5; font-weight:600'>{format_currency(b['valor'])}</span>"
                    f"&nbsp;&nbsp;"
                    f"<span style='color:#94A3B8; font-size:12px'>Venc. {format_date_br(b['vencimento'])} {status}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with col_edit:
                st.markdown("<div style='margin-top:2px'></div>", unsafe_allow_html=True)
                if st.button("✏️", key=f"edit_{b['id']}", help="Editar este pagamento"):
                    st.session_state.editando_id = b["id"]
                    for bid in [bl["id"] for bl in todos_boletos]:
                        st.session_state[f"chk_{bid}"] = False
                    st.session_state.confirm_delete = False
                    st.session_state.ids_para_excluir = []
                    st.rerun()
