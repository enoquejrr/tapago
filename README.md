# Rastreador da Grana

App pessoal para organizar pagamentos mensais com login por usuário.

## Stack

- [Streamlit](https://streamlit.io) — interface web
- [Supabase](https://supabase.com) — banco de dados PostgreSQL
- [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) — autenticação

## Funcionalidades

- Visualização de boletos por mês com status (vencido, próximo, no prazo, pago)
- Lançamento de boletos recorrentes (repete por N meses)
- Categorias customizáveis
- Resumo anual por categoria com gráfico
- Login individual — cada usuário vê apenas seus próprios dados

## Como rodar localmente

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Crie o arquivo `.streamlit/secrets.toml` com suas credenciais (veja abaixo)
4. Rode o app:
   ```bash
   streamlit run app.py
   ```

## Configuração de secrets

Crie `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://xxxx.supabase.co"
key = "eyJ..."

[cookie]
name = "rastreadordagrana"
key = "uma_chave_aleatoria_longa"
expiry_days = 30

[credentials.usernames.seu_usuario]
name = "Seu Nome"
password = "$2b$12$..."  # hash bcrypt gerado via script
```

## Deploy

Hospedado no [Streamlit Community Cloud](https://share.streamlit.io). Os secrets são configurados no painel do app em **Advanced settings → Secrets**.
