-- ============================================================
-- Migração 001 — Schema inicial
-- Executar no SQL Editor do Supabase
-- ============================================================

-- Tabela de boletos/pagamentos
create table if not exists boletos (
  id           bigserial primary key,
  descricao    text        not null,
  valor        numeric     not null,
  vencimento   date        not null,
  competencia  text        not null,       -- formato YYYY-MM
  categoria    text,
  pago         boolean     not null default false,
  usuario      text        not null,       -- user_id do Supabase Auth
  criado_em    timestamptz not null default now()
);

-- Tabela de categorias (schema ANTES da migração 002)
create table if not exists categorias (
  id    bigserial primary key,
  nome  text not null unique
);

-- Políticas permissivas originais (NÃO usar em produção — ver migração 002)
-- create policy "allow_all_boletos"   on boletos   for all to anon using (true) with check (true);
-- create policy "allow_all_categorias" on categorias for all to anon using (true) with check (true);
