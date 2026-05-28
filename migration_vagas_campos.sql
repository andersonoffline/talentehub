-- ═══════════════════════════════════════════════════════════
-- SmartHub — Atualizar tabela vagas com novos campos
-- Execute no Supabase SQL Editor ANTES de usar os filtros
-- ═══════════════════════════════════════════════════════════

-- Adicionar colunas de filtro (seguro — ignora se já existirem)
ALTER TABLE vagas
  ADD COLUMN IF NOT EXISTS modalidade      text DEFAULT 'presencial',  -- 'remoto' | 'hibrido' | 'presencial'
  ADD COLUMN IF NOT EXISTS tipo_contrato   text DEFAULT 'clt',         -- 'clt' | 'pj' | 'estagio' | 'freelance'
  ADD COLUMN IF NOT EXISTS nivel           text,                        -- 'junior' | 'pleno' | 'senior' | 'especialista' | 'lideranca'
  ADD COLUMN IF NOT EXISTS area            text,                        -- 'tecnologia' | 'marketing' | etc
  ADD COLUMN IF NOT EXISTS cidade          text,
  ADD COLUMN IF NOT EXISTS salario_min     numeric,
  ADD COLUMN IF NOT EXISTS salario_max     numeric,
  ADD COLUMN IF NOT EXISTS requisitos      text,
  ADD COLUMN IF NOT EXISTS beneficios      text;

-- Índices para performance nos filtros
CREATE INDEX IF NOT EXISTS idx_vagas_modalidade     ON vagas(modalidade);
CREATE INDEX IF NOT EXISTS idx_vagas_tipo_contrato  ON vagas(tipo_contrato);
CREATE INDEX IF NOT EXISTS idx_vagas_nivel          ON vagas(nivel);
CREATE INDEX IF NOT EXISTS idx_vagas_area           ON vagas(area);
CREATE INDEX IF NOT EXISTS idx_vagas_cidade         ON vagas(cidade);
CREATE INDEX IF NOT EXISTS idx_vagas_salario        ON vagas(salario_min, salario_max);
CREATE INDEX IF NOT EXISTS idx_vagas_status         ON vagas(status);
CREATE INDEX IF NOT EXISTS idx_vagas_created        ON vagas(created_at DESC);

-- Adicionar coluna logo_url na tabela empresas (para o card de vaga)
ALTER TABLE empresas
  ADD COLUMN IF NOT EXISTS logo_url text;

-- Verificar resultado
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'vagas' AND table_schema = 'public'
ORDER BY ordinal_position;
