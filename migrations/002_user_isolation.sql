-- ============================================================
-- Migração 002 — Isolamento real por usuário + RLS
-- Executar no SQL Editor do Supabase
-- ATENÇÃO: execute cada bloco em ordem e verifique erros
-- ============================================================

-- ── 1. Adicionar coluna usuario à tabela categorias ─────────
alter table categorias
  add column if not exists usuario text;

-- Marcar categorias existentes como pertencentes a um usuário padrão
-- (substituir pelo user_id real se necessário, ou limpar a tabela)
-- UPDATE categorias SET usuario = '<seu_user_id>' WHERE usuario IS NULL;

-- Tornar a coluna obrigatória após popular dados existentes
-- (só executar depois de popular todos os registros acima)
-- alter table categorias alter column usuario set not null;

-- Remover unique constraint antiga (nome único global) e criar por usuário
alter table categorias drop constraint if exists categorias_nome_key;
create unique index if not exists categorias_nome_usuario_idx on categorias (nome, usuario);

-- ── 2. Habilitar RLS nas duas tabelas ───────────────────────
alter table boletos    enable row level security;
alter table categorias enable row level security;

-- ── 3. Remover políticas permissivas antigas ─────────────────
drop policy if exists "allow_all_boletos"    on boletos;
drop policy if exists "allow_all_categorias" on categorias;

-- ── 4. Políticas reais de isolamento por usuário ─────────────

-- boletos: cada usuário vê e altera apenas os seus
create policy "boletos_usuario_select" on boletos
  for select to anon
  using (usuario = auth.uid()::text);

create policy "boletos_usuario_insert" on boletos
  for insert to anon
  with check (usuario = auth.uid()::text);

create policy "boletos_usuario_update" on boletos
  for update to anon
  using  (usuario = auth.uid()::text)
  with check (usuario = auth.uid()::text);

create policy "boletos_usuario_delete" on boletos
  for delete to anon
  using (usuario = auth.uid()::text);

-- categorias: cada usuário vê e altera apenas as suas
create policy "categorias_usuario_select" on categorias
  for select to anon
  using (usuario = auth.uid()::text);

create policy "categorias_usuario_insert" on categorias
  for insert to anon
  with check (usuario = auth.uid()::text);

create policy "categorias_usuario_update" on categorias
  for update to anon
  using  (usuario = auth.uid()::text)
  with check (usuario = auth.uid()::text);

create policy "categorias_usuario_delete" on categorias
  for delete to anon
  using (usuario = auth.uid()::text);

-- ── 5. Índices de performance ────────────────────────────────
create index if not exists idx_boletos_usuario    on boletos (usuario);
create index if not exists idx_boletos_competencia on boletos (competencia);
create index if not exists idx_boletos_vencimento  on boletos (vencimento);
create index if not exists idx_boletos_status      on boletos (pago);
create index if not exists idx_categorias_usuario  on categorias (usuario);

-- ── Verificação ──────────────────────────────────────────────
-- Após executar, teste com curl (deve retornar [] sem JWT):
--
--   curl 'https://<project>.supabase.co/rest/v1/boletos?select=*' \
--     -H 'apikey: <anon_key>' \
--     -H 'Authorization: Bearer <anon_key>'
--
-- Resultado esperado: [] (array vazio) ou erro 401
