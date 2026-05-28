-- ═══════════════════════════════════════════════════════════
-- SmartHub — Migrations pendentes
-- Execute no Supabase SQL Editor: https://app.supabase.com
-- ═══════════════════════════════════════════════════════════

-- ─────────────────────────────────────
-- 1. TABELA: notificacoes
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS notificacoes (
  id          uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id     uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  tipo        text NOT NULL,         -- 'candidatura', 'status', 'mensagem', 'vaga', 'sistema'
  titulo      text NOT NULL,
  corpo       text,
  lida        boolean DEFAULT false,
  url         text,                  -- link de destino ao clicar
  referencia_id uuid,                -- id da candidatura, vaga, ou mensagem relacionada
  created_at  timestamptz DEFAULT now()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_notif_user_id   ON notificacoes(user_id);
CREATE INDEX IF NOT EXISTS idx_notif_lida      ON notificacoes(user_id, lida);
CREATE INDEX IF NOT EXISTS idx_notif_created   ON notificacoes(created_at DESC);

-- RLS
ALTER TABLE notificacoes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Usuário vê suas notificações"
  ON notificacoes FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Sistema insere notificações"
  ON notificacoes FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Usuário marca como lida"
  ON notificacoes FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Usuário deleta suas notificações"
  ON notificacoes FOR DELETE
  USING (auth.uid() = user_id);


-- ─────────────────────────────────────
-- 2. TABELA: mensagens
-- ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS mensagens (
  id              uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  conversa_id     uuid NOT NULL,           -- agrupa mensagens de uma conversa
  remetente_id    uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  destinatario_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  candidatura_id  uuid REFERENCES candidaturas(id) ON DELETE SET NULL,
  texto           text NOT NULL,
  lida            boolean DEFAULT false,
  created_at      timestamptz DEFAULT now()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_msg_conversa   ON mensagens(conversa_id);
CREATE INDEX IF NOT EXISTS idx_msg_remetente  ON mensagens(remetente_id);
CREATE INDEX IF NOT EXISTS idx_msg_dest       ON mensagens(destinatario_id);
CREATE INDEX IF NOT EXISTS idx_msg_created    ON mensagens(created_at DESC);

-- RLS
ALTER TABLE mensagens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Participante vê mensagens da conversa"
  ON mensagens FOR SELECT
  USING (auth.uid() = remetente_id OR auth.uid() = destinatario_id);

CREATE POLICY "Participante envia mensagem"
  ON mensagens FOR INSERT
  WITH CHECK (auth.uid() = remetente_id);

CREATE POLICY "Destinatário marca como lida"
  ON mensagens FOR UPDATE
  USING (auth.uid() = destinatario_id);


-- ─────────────────────────────────────
-- 3. FUNCTION: notificar_candidatura
-- Dispara notificação ao candidato quando
-- uma empresa avança o status da candidatura
-- ─────────────────────────────────────
CREATE OR REPLACE FUNCTION notificar_mudanca_status()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  v_candidato_user_id uuid;
  v_titulo_vaga text;
  v_empresa_nome text;
  v_msg text;
BEGIN
  -- Só age quando o status muda
  IF OLD.status = NEW.status THEN RETURN NEW; END IF;

  -- Pegar user_id do candidato
  SELECT c.user_id INTO v_candidato_user_id
  FROM candidatos c WHERE c.id = NEW.candidato_id;

  -- Pegar título da vaga e empresa
  SELECT v.titulo, e.nome_fantasia
  INTO v_titulo_vaga, v_empresa_nome
  FROM vagas v
  JOIN empresas e ON v.empresa_id = e.id
  WHERE v.id = NEW.vaga_id;

  -- Montar mensagem conforme novo status
  CASE NEW.status
    WHEN 'entrevista' THEN
      v_msg := 'Parabéns! Você foi chamado para entrevista.';
    WHEN 'aprovado' THEN
      v_msg := '🎉 Você foi aprovado! Entre em contato com a empresa.';
    WHEN 'reprovado' THEN
      v_msg := 'Sua candidatura não avançou desta vez. Continue tentando!';
    ELSE
      v_msg := 'Seu status foi atualizado.';
  END CASE;

  -- Inserir notificação
  INSERT INTO notificacoes (user_id, tipo, titulo, corpo, url, referencia_id)
  VALUES (
    v_candidato_user_id,
    'status',
    v_empresa_nome || ' — ' || v_titulo_vaga,
    v_msg,
    'candidato-dashboard.html',
    NEW.id
  );

  RETURN NEW;
END;
$$;

-- Trigger na tabela candidaturas
DROP TRIGGER IF EXISTS trg_notificar_status ON candidaturas;
CREATE TRIGGER trg_notificar_status
  AFTER UPDATE ON candidaturas
  FOR EACH ROW EXECUTE FUNCTION notificar_mudanca_status();


-- ─────────────────────────────────────
-- 4. FUNCTION: notificar_nova_candidatura
-- Notifica a empresa quando alguém se candidata
-- ─────────────────────────────────────
CREATE OR REPLACE FUNCTION notificar_nova_candidatura()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS $$
DECLARE
  v_empresa_user_id uuid;
  v_titulo_vaga text;
  v_candidato_nome text;
BEGIN
  SELECT e.user_id INTO v_empresa_user_id
  FROM vagas v JOIN empresas e ON v.empresa_id = e.id
  WHERE v.id = NEW.vaga_id;

  SELECT v.titulo INTO v_titulo_vaga FROM vagas v WHERE v.id = NEW.vaga_id;
  SELECT c.nome INTO v_candidato_nome FROM candidatos c WHERE c.id = NEW.candidato_id;

  INSERT INTO notificacoes (user_id, tipo, titulo, corpo, url, referencia_id)
  VALUES (
    v_empresa_user_id,
    'candidatura',
    'Nova candidatura em ' || v_titulo_vaga,
    (COALESCE(v_candidato_nome, 'Um candidato')) || ' se candidatou à sua vaga.',
    'gestor-dashboard.html',
    NEW.id
  );

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_notif_candidatura ON candidaturas;
CREATE TRIGGER trg_notif_candidatura
  AFTER INSERT ON candidaturas
  FOR EACH ROW EXECUTE FUNCTION notificar_nova_candidatura();


-- ─────────────────────────────────────
-- 5. VERIFICAR resultado
-- ─────────────────────────────────────
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('notificacoes', 'mensagens')
ORDER BY table_name;
