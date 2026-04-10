"""Página para registrar um novo pagamento."""
import streamlit as st
from datetime import date
from auth import check_auth, sidebar_logout
from storage_service import StorageService
from services.boleto_service import BoletoService

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 680px; }
    .stButton > button { border-radius: 8px; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

username = check_auth()
sidebar_logout()
storage = StorageService(usuario=username)
boleto_svc = BoletoService(storage)

# ── Cabeçalho ──────────────────────────────────────────────────────────────
st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>➕ Novo Pagamento</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Registre uma conta ou pagamento para o mês.</p>", unsafe_allow_html=True)
st.divider()

# ── Categoria (fora do form para reagir ao selectbox sem precisar submeter) ─
categorias_salvas = storage.get_categorias()
opcoes_cat = [""] + categorias_salvas + ["+ Nova categoria..."]

# Após salvar uma nova categoria, o session_state mantém ela selecionada
if "cat_selecionada" not in st.session_state:
    st.session_state.cat_selecionada = ""

# Se a categoria salva anteriormente já está na lista, pré-seleciona ela
idx_default = 0
if st.session_state.cat_selecionada in opcoes_cat:
    idx_default = opcoes_cat.index(st.session_state.cat_selecionada)

col_cat_outer, _ = st.columns(2)
with col_cat_outer:
    cat_escolhida = st.selectbox(
        "Categoria",
        opcoes_cat,
        index=idx_default,
        help="Opcional. Use para o resumo anual.",
    )
    st.session_state.cat_selecionada = cat_escolhida

    nova_cat = None
    if cat_escolhida == "+ Nova categoria...":
        nova_cat = st.text_input(
            "Nome da nova categoria",
            placeholder="Ex: Pets, Academia...",
            max_chars=50,
        )

# ── Formulário ─────────────────────────────────────────────────────────────
with st.form("form_novo_boleto", clear_on_submit=True):
    descricao = st.text_input(
        "Descrição *",
        placeholder="Ex: Conta de água, Netflix, Aluguel...",
        help="Nome do pagamento ou conta.",
        max_chars=200,
    )

    col_val, col_rep = st.columns(2)
    with col_val:
        valor = st.number_input(
            "Valor (R$) *",
            min_value=0.01,
            step=0.01,
            format="%.2f",
            help="Valor exato do pagamento.",
        )
    with col_rep:
        repetir = st.number_input(
            "Repetir (meses)",
            min_value=1,
            max_value=24,
            value=1,
            step=1,
            help="1 = sem repetição. Ex: 3 cria pagamentos para este e os 2 meses seguintes.",
        )

    vencimento = st.date_input(
        "Data de vencimento *",
        value=date.today(),
        help="Dia em que o pagamento vence.",
    )

    submitted = st.form_submit_button("💾 Salvar pagamento", use_container_width=True, type="primary")

    if submitted:
        if vencimento is None:
            st.error("Selecione uma data de vencimento.")
        elif not descricao.strip():
            st.error("A descrição é obrigatória.")
        elif valor <= 0:
            st.error("O valor deve ser maior que zero.")
        else:
            try:
                if boleto_svc.verificar_duplicata(descricao.strip(), vencimento.strftime("%Y-%m-%d")):
                    st.warning(f"⚠️ Já existe um pagamento **{descricao.strip()}** com vencimento em {vencimento.strftime('%d/%m/%Y')}. O pagamento foi salvo mesmo assim.")

                categoria_final = None
                if cat_escolhida == "+ Nova categoria..." and nova_cat and nova_cat.strip():
                    with st.spinner("Salvando categoria..."):
                        storage.create_categoria(nova_cat.strip())
                    categoria_final = nova_cat.strip()
                    st.session_state.cat_selecionada = nova_cat.strip()
                elif cat_escolhida and cat_escolhida != "+ Nova categoria...":
                    categoria_final = cat_escolhida

                competencia = vencimento.strftime("%Y-%m")
                label_spinner = "Salvando pagamento..." if repetir == 1 else f"Criando {int(repetir)} pagamentos..."
                with st.spinner(label_spinner):
                    boleto_svc.criar_recorrente(
                        descricao=descricao.strip(),
                        valor=valor,
                        vencimento=vencimento.strftime("%Y-%m-%d"),
                        competencia=competencia,
                        categoria=categoria_final,
                        meses=int(repetir),
                    )

                if repetir == 1:
                    st.toast(f"Pagamento '{descricao.strip()}' registrado para {competencia}.", icon="✅")
                else:
                    st.toast(f"{int(repetir)} pagamentos de '{descricao.strip()}' criados a partir de {competencia}.", icon="✅")
            except RuntimeError as e:
                st.error(str(e))
