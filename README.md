# Tá Pago?

App para organizar pagamentos mensais com cadastro e login por usuário.

## Stack

- [Streamlit](https://streamlit.io) — interface web
- [Supabase](https://supabase.com) — banco de dados PostgreSQL + autenticação
- [supabase-py](https://github.com/supabase-community/supabase-py) — cliente Python do Supabase

## Funcionalidades

- Cadastro e login com email/senha (confirmação por email, recuperação de senha)
- Dados isolados por usuário — cada um vê apenas seus próprios pagamentos
- Visualização de pagamentos por mês com status (vencido, próximo, no prazo, pago)
- Lançamento de pagamentos recorrentes (repete por N meses)
- Detecção de pagamentos duplicados
- Categorias customizáveis com resumo anual por categoria e gráfico
- Exclusão múltipla com seleção por checkbox

## Páginas

| Página | Descrição |
|---|---|
| Painel | Visão do mês atual com resumo e lista por status |
| Novo Pagamento | Formulário para registrar pagamentos |
| Histórico | Tabela filtrável + resumo anual por categoria |
| Excluir | Exclusão múltipla com checkboxes por mês |

## Como rodar localmente

1. Clone o repositório
2. Instale as dependências:
   ```bash
   pip3 install -r requirements.txt
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

## Configuração do Supabase

### Banco de dados
```sql
create table boletos (
  id bigserial primary key,
  descricao text not null,
  valor numeric(10,2) not null,
  vencimento date not null,
  competencia text not null,
  categoria text,
  pago boolean not null default false,
  usuario text,
  criado_em timestamptz not null default now()
);

create table categorias (
  id bigserial primary key,
  nome text not null unique
);

-- Políticas RLS
alter table boletos enable row level security;
alter table categorias enable row level security;
create policy "allow_all_boletos" on boletos for all to anon using (true) with check (true);
create policy "allow_all_categorias" on categorias for all to anon using (true) with check (true);
```

### Autenticação
- **Authentication → URL Configuration → Site URL:** URL do app no Streamlit Cloud
- **Authentication → Email → SMTP Settings:** configurar SMTP próprio (ex: Resend) para envio de emails de confirmação e recuperação de senha

## Deploy

Hospedado no [Streamlit Community Cloud](https://share.streamlit.io).  
Secrets configurados em **Settings → Secrets** do app com apenas:

```toml
[supabase]
url = "https://xxxx.supabase.co"
key = "eyJ..."
```
