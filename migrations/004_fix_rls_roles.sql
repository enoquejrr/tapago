-- Migration 004 — Corrige políticas RLS: anon → authenticated
-- Problema: policies criadas com "to anon" não se aplicam a usuários
-- autenticados via JWT, que usam o role "authenticated" no Supabase.

-- ── Dropar políticas antigas (role anon) ────────────────────────────────────
drop policy if exists "boletos_usuario_select" on boletos;
drop policy if exists "boletos_usuario_insert" on boletos;
drop policy if exists "boletos_usuario_update" on boletos;
drop policy if exists "boletos_usuario_delete" on boletos;

drop policy if exists "categorias_usuario_select" on categorias;
drop policy if exists "categorias_usuario_insert" on categorias;
drop policy if exists "categorias_usuario_update" on categorias;
drop policy if exists "categorias_usuario_delete" on categorias;

-- ── Recriar com role authenticated ──────────────────────────────────────────

-- boletos
create policy "boletos_usuario_select" on boletos
  for select to authenticated
  using (usuario = auth.uid()::text);

create policy "boletos_usuario_insert" on boletos
  for insert to authenticated
  with check (usuario = auth.uid()::text);

create policy "boletos_usuario_update" on boletos
  for update to authenticated
  using  (usuario = auth.uid()::text)
  with check (usuario = auth.uid()::text);

create policy "boletos_usuario_delete" on boletos
  for delete to authenticated
  using (usuario = auth.uid()::text);

-- categorias
create policy "categorias_usuario_select" on categorias
  for select to authenticated
  using (usuario = auth.uid()::text);

create policy "categorias_usuario_insert" on categorias
  for insert to authenticated
  with check (usuario = auth.uid()::text);

create policy "categorias_usuario_update" on categorias
  for update to authenticated
  using  (usuario = auth.uid()::text)
  with check (usuario = auth.uid()::text);

create policy "categorias_usuario_delete" on categorias
  for delete to authenticated
  using (usuario = auth.uid()::text);

-- ── Verificação ──────────────────────────────────────────────────────────────
select tablename, policyname, roles, cmd
from pg_policies
where tablename in ('boletos', 'categorias')
order by tablename, cmd;
