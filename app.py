"""Aplicação Streamlit para rastreamento de boletos/contas mensais."""
import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
from datetime import datetime, timedelta
from storage_service import StorageService
from utils import (
    get_current_month,
    format_currency,
    format_date_br,
    days_until_due,
    is_overdue,
    is_due_soon,
    extract_month
)

MESES_PT = {
    "01": "Janeiro", "02": "Fevereiro", "03": "Março", "04": "Abril",
    "05": "Maio", "06": "Junho", "07": "Julho", "08": "Agosto",
    "09": "Setembro", "10": "Outubro", "11": "Novembro", "12": "Dezembro"
}

# Configuração Streamlit
st.set_page_config(
    page_title="Rastreador da Grana",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============= LOGIN =============
authenticator = stauth.Authenticate(
    st.secrets["credentials"].to_dict(),
    st.secrets["cookie"]["name"],
    st.secrets["cookie"]["key"],
    st.secrets["cookie"]["expiry_days"],
)

authenticator.login()

if not st.session_state.get("authentication_status"):
    st.stop()

username = st.session_state["username"]
authenticator.logout("Sair", "sidebar")

# Inicialização
storage = StorageService(usuario=username)
if "current_month" not in st.session_state:
    st.session_state.current_month = get_current_month()
if "refresh" not in st.session_state:
    st.session_state.refresh = False
if "delete_confirm" not in st.session_state:
    st.session_state.delete_confirm = None


# ============= HEADER =============
st.title("📋 Rastreador da Grana")
st.markdown("Organize seus pagamentos sem complicações!")

# Menu de navegação
tab1, tab2, tab3 = st.tabs(["📅 Mês Atual", "➕ Novo Boleto", "📊 Histórico"])


# ============= TAB 1: VISUALIZAÇÃO DO MÊS =============
with tab1:
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        ano, mes = st.session_state.current_month.split("-")
        st.subheader(f"{MESES_PT[mes]} {ano}")

    with col2:
        if st.button("← Mês Anterior", use_container_width=True):
            data_anterior = datetime.strptime(st.session_state.current_month, "%Y-%m") - timedelta(days=1)
            st.session_state.current_month = data_anterior.strftime("%Y-%m")
            st.rerun()

    with col3:
        if st.button("Mês Seguinte →", use_container_width=True):
            data_proxima = datetime.strptime(st.session_state.current_month, "%Y-%m") + timedelta(days=32)
            st.session_state.current_month = data_proxima.strftime("%Y-%m")
            st.rerun()

    st.divider()

    # Carregar boletos do mês
    boletos = storage.get_by_month(st.session_state.current_month)
    total_mes = storage.get_total_month(st.session_state.current_month)
    total_pago = storage.get_total_paid_month(st.session_state.current_month)
    total_pendente = total_mes - total_pago

    # Cards de resumo
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        st.metric("💰 Total", format_currency(total_mes))
    with col_r2:
        st.metric("✅ Pago", format_currency(total_pago))
    with col_r3:
        st.metric("⏳ Pendente", format_currency(total_pendente))

    st.divider()

    if not boletos:
        st.info("ℹ️ Nenhum boleto cadastrado para este mês.")
    else:
        # Separar boletos por status
        boletos_vencidos = []
        boletos_proximos = []
        boletos_normais = []
        boletos_pagos = []

        for b in boletos:
            if b["pago"]:
                boletos_pagos.append(b)
            elif is_overdue(b["vencimento"]):
                boletos_vencidos.append(b)
            elif is_due_soon(b["vencimento"]):
                boletos_proximos.append(b)
            else:
                boletos_normais.append(b)

        # Exibir boletos vencidos
        if boletos_vencidos:
            st.warning("🔴 **VENCIDOS**")
            for b in boletos_vencidos:
                with st.container(border=True):
                    col_v1, col_v2, col_v3, col_v4 = st.columns([3, 1.5, 2, 0.5])
                    with col_v1:
                        st.write(f"**{b['descricao']}**")
                        if b.get("categoria"):
                            st.caption(b["categoria"])
                    with col_v2:
                        st.write(format_currency(b["valor"]))
                    with col_v3:
                        dias = days_until_due(b["vencimento"])
                        st.write(f"Vencido há {abs(dias)} dia(s)")
                    with col_v4:
                        if st.button("✓", key=f"mark_{b['id']}", help="Marcar como pago"):
                            storage.update_status(b["id"], True)
                            st.rerun()

        # Exibir boletos próximos do vencimento
        if boletos_proximos:
            st.warning("🟡 **PRÓXIMOS DO VENCIMENTO** (≤ 3 dias)")
            for b in boletos_proximos:
                with st.container(border=True):
                    col_p1, col_p2, col_p3, col_p4 = st.columns([3, 1.5, 2, 0.5])
                    with col_p1:
                        st.write(f"**{b['descricao']}**")
                        if b.get("categoria"):
                            st.caption(b["categoria"])
                    with col_p2:
                        st.write(format_currency(b["valor"]))
                    with col_p3:
                        dias = days_until_due(b["vencimento"])
                        st.write(f"Vence em {dias} dia(s) — {format_date_br(b['vencimento'])}")
                    with col_p4:
                        if st.button("✓", key=f"mark_soon_{b['id']}", help="Marcar como pago"):
                            storage.update_status(b["id"], True)
                            st.rerun()

        # Exibir boletos normais
        if boletos_normais:
            st.success("🟢 **NO PRAZO**")
            for b in boletos_normais:
                with st.container(border=True):
                    col_n1, col_n2, col_n3, col_n4 = st.columns([3, 1.5, 2, 0.5])
                    with col_n1:
                        st.write(f"{b['descricao']}")
                        if b.get("categoria"):
                            st.caption(b["categoria"])
                    with col_n2:
                        st.write(format_currency(b["valor"]))
                    with col_n3:
                        dias = days_until_due(b["vencimento"])
                        st.write(f"Vence em {dias} dia(s) — {format_date_br(b['vencimento'])}")
                    with col_n4:
                        if st.button("✓", key=f"mark_normal_{b['id']}", help="Marcar como pago"):
                            storage.update_status(b["id"], True)
                            st.rerun()

        # Exibir boletos pagos
        if boletos_pagos:
            with st.expander("✅ **PAGOS**", expanded=False):
                for b in boletos_pagos:
                    with st.container(border=True):
                        col_pg1, col_pg2, col_pg3, col_pg4 = st.columns([3, 1.5, 2, 0.5])
                        with col_pg1:
                            st.write(f"~~{b['descricao']}~~")
                            if b.get("categoria"):
                                st.caption(b["categoria"])
                        with col_pg2:
                            st.write(format_currency(b["valor"]))
                        with col_pg3:
                            st.write(f"Vencimento: {format_date_br(b['vencimento'])}")
                        with col_pg4:
                            if st.button("↩️", key=f"undo_{b['id']}", help="Marcar como não pago"):
                                storage.update_status(b["id"], False)
                                st.rerun()


# ============= TAB 2: NOVO BOLETO =============
with tab2:
    st.subheader("Registrar novo boleto")

    categorias_salvas = storage.get_categorias()
    opcoes_cat = [""] + categorias_salvas + ["+ Nova categoria..."]

    with st.form("form_novo_boleto"):
        descricao = st.text_input("Descrição", placeholder="Ex: Conta de água, Netflix, etc.")
        col_f1, col_f2 = st.columns(2)

        with col_f1:
            valor = st.number_input("Valor (R$)", min_value=0.01, step=0.01, format="%.2f")

        with col_f2:
            vencimento = st.date_input("Data de vencimento")

        col_f3, col_f4 = st.columns(2)

        with col_f3:
            cat_escolhida = st.selectbox("Categoria (opcional)", opcoes_cat)
            nova_cat = None
            if cat_escolhida == "+ Nova categoria...":
                nova_cat = st.text_input("Nome da nova categoria", placeholder="Ex: Pets, Academia...")

        with col_f4:
            repetir = st.number_input(
                "Repetir por quantos meses?", min_value=1, max_value=24, value=1, step=1,
                help="1 = sem repetição. Ex: 3 criará boletos para este e os 2 meses seguintes."
            )

        # Auto-preenchendo competência
        competencia = vencimento.strftime("%Y-%m")

        submitted = st.form_submit_button("Salvar Boleto", use_container_width=True)

        if submitted:
            if not descricao:
                st.error("❌ A descrição é obrigatória.")
            elif valor <= 0:
                st.error("❌ O valor deve ser maior que 0.")
            else:
                categoria_final = None
                if cat_escolhida == "+ Nova categoria..." and nova_cat and nova_cat.strip():
                    storage.create_categoria(nova_cat.strip())
                    categoria_final = nova_cat.strip()
                elif cat_escolhida and cat_escolhida != "+ Nova categoria...":
                    categoria_final = cat_escolhida

                storage.create_recurring(
                    descricao=descricao,
                    valor=valor,
                    vencimento=vencimento.strftime("%Y-%m-%d"),
                    competencia=competencia,
                    categoria=categoria_final,
                    meses=repetir
                )
                if repetir == 1:
                    st.success(f"✅ Boleto '{descricao}' registrado para {competencia}.")
                else:
                    st.success(f"✅ {repetir} boletos de '{descricao}' criados a partir de {competencia}.")
                st.rerun()


# ============= TAB 3: HISTÓRICO =============
with tab3:
    st.subheader("Histórico de todos os boletos")

    todos_boletos = storage.load_all()
    if not todos_boletos:
        st.info("ℹ️ Nenhum boleto registrado ainda.")
    else:
        meses = sorted(set(b["competencia"] for b in todos_boletos), reverse=True)
        anos = sorted(set(b["competencia"][:4] for b in todos_boletos), reverse=True)

        col_fil1, col_fil2 = st.columns(2)
        with col_fil1:
            mes_selecionado = st.selectbox("Filtrar por mês:", meses)
        with col_fil2:
            ano_resumo = st.selectbox("Resumo anual por categoria — ano:", anos)

        boletos_filtrados = storage.get_by_month(mes_selecionado)

        st.write(f"**{len(boletos_filtrados)} boleto(s) em {mes_selecionado}**")

        if boletos_filtrados:
            df = pd.DataFrame(boletos_filtrados)
            df["Status"] = df["pago"].map({True: "✅ Pago", False: "⏳ Pendente"})
            df["Valor"] = df["valor"].apply(format_currency)
            df["Vencimento"] = df["vencimento"].apply(format_date_br)
            df["Categoria"] = df["categoria"].fillna("—")

            st.dataframe(
                df[["descricao", "Valor", "Vencimento", "Categoria", "Status"]],
                column_config={
                    "descricao": st.column_config.TextColumn("Descrição"),
                    "Valor": st.column_config.TextColumn("Valor"),
                    "Vencimento": st.column_config.TextColumn("Vencimento"),
                    "Categoria": st.column_config.TextColumn("Categoria"),
                    "Status": st.column_config.TextColumn("Status"),
                },
                use_container_width=True,
                hide_index=True,
            )

            # Exclusão com confirmação
            del_id = st.selectbox(
                "Excluir boleto:",
                options=[b["id"] for b in boletos_filtrados],
                format_func=lambda bid: next(b["descricao"] for b in boletos_filtrados if b["id"] == bid),
                index=None,
                placeholder="Selecione para excluir..."
            )
            if del_id:
                if st.session_state.delete_confirm == del_id:
                    c1, c2 = st.columns(2)
                    if c1.button("✓ Confirmar exclusão", type="primary"):
                        storage.delete(del_id)
                        st.session_state.delete_confirm = None
                        st.rerun()
                    if c2.button("✗ Cancelar"):
                        st.session_state.delete_confirm = None
                        st.rerun()
                else:
                    if st.button("🗑️ Excluir selecionado"):
                        st.session_state.delete_confirm = del_id
                        st.rerun()

        st.divider()
        with st.expander(f"📊 Total por categoria em {ano_resumo}", expanded=False):
            totais = storage.get_totals_by_category(ano_resumo)
            if not totais:
                st.info("Nenhum dado para este ano.")
            else:
                df_cat = pd.DataFrame(
                    sorted(totais.items(), key=lambda x: -x[1]),
                    columns=["Categoria", "Total (R$)"]
                )
                st.dataframe(df_cat, use_container_width=True, hide_index=True)
                st.bar_chart(df_cat.set_index("Categoria"))


# ============= FOOTER =============
st.divider()
st.caption("🔒 Dados salvos no Supabase | Rastreador da Grana")
