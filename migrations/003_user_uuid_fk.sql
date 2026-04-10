-- Migration 003: Adicionar coluna user_uuid (UUID) como FK para auth.users
-- Objetivo: Substituir gradualmente o campo usuario (TEXT) por uma FK tipada,
--           melhorando integridade referencial e performance das queries com RLS.
--
-- ATENÇÃO: execute com cuidado em produção com dados existentes.
-- Passos:
--   1. Adiciona coluna user_uuid nullable
--   2. Popula a partir de auth.users (match por email, se disponível)
--      OU deixa para ser preenchida em novos inserts
--   3. Cria index para performance
--   4. (Opcional, sprint futura) tornar NOT NULL e dropar coluna usuario TEXT

-- Passo 1: Adicionar coluna
ALTER TABLE boletos
    ADD COLUMN IF NOT EXISTS user_uuid UUID REFERENCES auth.users(id) ON DELETE CASCADE;

-- Passo 2: Tentar popular a partir do campo usuario (email)
-- Se usuario armazena email, o update abaixo conecta os dados existentes:
UPDATE boletos b
SET user_uuid = u.id
FROM auth.users u
WHERE b.user_uuid IS NULL
  AND b.usuario = u.email;

-- Passo 3: Index para queries por user_uuid
CREATE INDEX IF NOT EXISTS idx_boletos_user_uuid ON boletos (user_uuid);

-- Verificação: quantos rows foram conectados
SELECT
    COUNT(*) FILTER (WHERE user_uuid IS NOT NULL) AS conectados,
    COUNT(*) FILTER (WHERE user_uuid IS NULL)     AS pendentes,
    COUNT(*)                                       AS total
FROM boletos;

-- NOTA: Para tornar NOT NULL no futuro (após confirmar 0 pendentes):
-- ALTER TABLE boletos ALTER COLUMN user_uuid SET NOT NULL;
-- ALTER TABLE boletos DROP COLUMN usuario;
-- (atualizar políticas RLS para usar user_uuid = auth.uid() diretamente)
