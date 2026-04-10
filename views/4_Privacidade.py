"""Página de política de privacidade — conformidade LGPD."""
import streamlit as st

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; max-width: 720px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='color:#1E293B; margin-bottom:4px'>🔒 Privacidade e Dados</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; margin-top:0'>Como o Tá Pago? coleta, usa e protege suas informações.</p>", unsafe_allow_html=True)
st.divider()

st.markdown("""
### Quais dados coletamos?

- **Email e senha** — usados exclusivamente para autenticação. A senha é armazenada com hash seguro pelo Supabase Auth e nunca é acessível por nós.
- **Dados de pagamentos** — descrição, valor, data de vencimento, categoria e status (pago/pendente) que você cadastra manualmente.

### Para que usamos seus dados?

Seus dados são usados **somente** para exibir e gerenciar seus pagamentos dentro do app. Não compartilhamos, vendemos ou utilizamos suas informações para fins de marketing ou análise de terceiros.

### Como seus dados são protegidos?

- Toda comunicação é criptografada via **HTTPS/TLS**.
- O acesso ao banco de dados é controlado por **Row Level Security (RLS)** — cada usuário só pode ver e modificar seus próprios dados.
- Credenciais de acesso ao banco não são expostas no código-fonte.

### Por quanto tempo armazenamos seus dados?

Seus dados ficam armazenados enquanto sua conta estiver ativa. Ao solicitar a exclusão da conta, todos os seus dados serão removidos permanentemente.

### Seus direitos (LGPD — Lei nº 13.709/2018)

De acordo com a Lei Geral de Proteção de Dados, você tem direito a:

- **Acesso** — saber quais dados temos sobre você
- **Correção** — corrigir dados incompletos ou incorretos
- **Exclusão** — solicitar a remoção dos seus dados
- **Portabilidade** — receber seus dados em formato legível

### Como exercer seus direitos?

Entre em contato pelo email do responsável pelo app. Você também pode excluir seus pagamentos diretamente na página **Excluir Pagamentos** do app.

### Alterações nesta política

Esta política pode ser atualizada periodicamente. A data da última atualização está indicada abaixo.

---
""")

st.caption("Última atualização: Abril de 2026 · Tá Pago?")
