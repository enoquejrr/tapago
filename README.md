# Tá Pago?

App para organizar pagamentos mensais com cadastro e login por usuário.

## Stack

- [Streamlit](https://streamlit.io) — interface web
- [Supabase](https://supabase.com) — banco de dados PostgreSQL + autenticação
- [supabase-py](https://github.com/supabase-community/supabase-py) — cliente Python do Supabase
- [pytest](https://pytest.org) — testes automatizados

## Funcionalidades

- Cadastro e login com email/senha (confirmação por email, recuperação de senha)
- Rate limiting no login (bloqueio após 5 tentativas incorretas)
- Dados isolados por usuário via Row Level Security (RLS) no Supabase
- Visualização de pagamentos por mês com status (vencido, próximo, no prazo, pago)
- Filtro por categoria no Painel
- Lançamento de pagamentos recorrentes (repete por N meses)
- Detecção de pagamentos duplicados
- Categorias customizáveis por usuário com resumo anual e gráfico
- Histórico com filtro por mês, ordenação (vencimento, valor, descrição) e paginação
- Exclusão múltipla com seleção por checkbox
- Política de privacidade (LGPD)

## Páginas

| Página | Descrição |
|---|---|
| Painel | Visão do mês atual com resumo, filtro por categoria e lista por status |
| Novo Pagamento | Formulário para registrar pagamentos (com suporte a recorrência) |
| Histórico | Tabela com ordenação, paginação + resumo anual por categoria |
| Excluir | Exclusão múltipla com checkboxes por mês |
| Privacidade | Política de privacidade e direitos LGPD |

## Estrutura do projeto

```
.
├── app.py                  # Entry point — navegação Streamlit
├── Painel.py               # Dashboard principal
├── auth.py                 # Autenticação Supabase
├── storage_service.py      # Acesso ao banco (Supabase)
├── services/
│   └── boleto_service.py   # Regras de negócio (recorrência, duplicatas)
├── models.py               # TypedDict: Boleto, Categoria
├── utils.py                # Funções utilitárias e MESES_PT
├── pages.py                # Constantes de navegação
├── app_logging.py          # Configuração de logging estruturado
├── views/
│   ├── 0_Login.py
│   ├── 1_Novo_Boleto.py
│   ├── 2_Historico.py
│   ├── 3_Excluir.py
│   └── 4_Privacidade.py
├── migrations/             # SQL versionado do schema Supabase
│   ├── 001_initial_schema.sql
│   ├── 002_user_isolation.sql   # RLS + isolamento por usuário
│   └── 003_user_uuid_fk.sql     # FK tipada para auth.users
├── tests/                  # Suite pytest
│   ├── conftest.py
│   ├── test_utils.py
│   ├── test_storage_create_recurring.py
│   ├── test_storage_operations.py
│   └── test_boleto_service.py
└── .github/workflows/ci.yml  # GitHub Actions — roda pytest no push
```

## Como rodar localmente

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie o arquivo `.streamlit/secrets.toml`:
   ```toml
   [supabase]
   url = "https://xxxx.supabase.co"
   key = "eyJ..."
   ```
4. Rode o app:
   ```bash
   streamlit run app.py
   ```

## Testes

```bash
pip install pytest
pytest
```

## Configuração do Supabase

### Banco de dados

Execute os arquivos da pasta `migrations/` em ordem no SQL Editor do Supabase:

1. `001_initial_schema.sql` — schema inicial
2. `002_user_isolation.sql` — habilita RLS com isolamento real por usuário
3. `003_user_uuid_fk.sql` — adiciona coluna `user_uuid` UUID com FK para `auth.users`

> ⚠️ As políticas RLS garantem que cada usuário acessa **apenas seus próprios dados**, mesmo via REST API direta.

### Autenticação

- **Authentication → URL Configuration → Site URL:** URL do app no Streamlit Cloud
- **Authentication → Email → SMTP Settings:** configure SMTP próprio (ex: Resend) para envio de emails de confirmação e recuperação de senha

## Deploy

Hospedado no [Streamlit Community Cloud](https://share.streamlit.io).  
Secrets configurados em **Settings → Secrets** do app:

```toml
[supabase]
url = "https://xxxx.supabase.co"
key = "eyJ..."
```
