-- Adiciona coluna tipo para distinguir pagamentos de receitas.
-- Registros existentes recebem 'pagamento' como padrão.
alter table boletos add column if not exists tipo text not null default 'pagamento';
