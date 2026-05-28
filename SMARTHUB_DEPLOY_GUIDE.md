# SmartHub — Guia de Conclusão

## ✅ O que foi entregue agora

### 1. `planos.html` — Stripe integrado
- Toggle mensal/anual com preços dinâmicos (R$97↔R$77, R$197↔R$157)
- 3 cards (Free, Pro, Business) com features completas
- Tabela comparativa + FAQ accordion
- Botão de checkout redireciona para link Stripe com email pré-preenchido
- **ÚNICO passo seu:** substituir os 4 links no arquivo:

```js
const STRIPE_LINKS = {
  pro_mensal:      'https://buy.stripe.com/test/SEU_LINK_PRO_MENSAL',
  pro_anual:       'https://buy.stripe.com/test/SEU_LINK_PRO_ANUAL',
  business_mensal: 'https://buy.stripe.com/test/SEU_LINK_BUSINESS_MENSAL',
  business_anual:  'https://buy.stripe.com/test/SEU_LINK_BUSINESS_ANUAL',
};
```

Para obter os links: Stripe Dashboard → Products → [Plano] → Payment Links → Create link

---

### 2. `mensagens.html` — Chat empresa ↔ candidato
- Lista de conversas com busca
- Bolhas de chat estilo WhatsApp
- Atualização em tempo real via Supabase Realtime
- Marca mensagens como lidas automaticamente
- Contador de não lidas no header
- **Depende do SQL de notificações (passo abaixo)**

---

### 3. `vagas-listagem.html` — Busca avançada
- Barra de busca por texto (título, descrição, área)
- Filtros: cidade, modalidade (remoto/híbrido/presencial), contrato, nível, área, faixa salarial
- Chips de filtros ativos com botão de remover
- Paginação (10 por página)
- Ordenação: recentes / maior salário / menor salário
- **Depende do SQL de campos (passo abaixo)**

---

### 4. `migration_notificacoes_mensagens.sql`
- Cria tabela `notificacoes` com RLS
- Cria tabela `mensagens` com RLS
- Triggers automáticos:
  - Candidato recebe notificação quando status muda no kanban
  - Empresa recebe notificação quando alguém se candidata

### 5. `migration_vagas_campos.sql`
- Adiciona colunas de filtro na tabela `vagas`
- Adiciona `logo_url` na tabela `empresas`

---

## 📋 Checklist de deploy

### Passo 1 — Executar SQLs no Supabase
1. Acesse https://app.supabase.com → seu projeto → SQL Editor
2. Execute `migration_vagas_campos.sql` (primeiro)
3. Execute `migration_notificacoes_mensagens.sql`

### Passo 2 — Configurar Stripe
1. Acesse https://dashboard.stripe.com/test/payment-links
2. Crie 4 Payment Links (Pro Mensal, Pro Anual, Business Mensal, Business Anual)
3. Cole os links no `planos.html` onde está `SEU_LINK_*`

### Passo 3 — Adicionar link de Mensagens na navbar
Em cada página protegida (candidato-dashboard, gestor-dashboard), adicionar:
```html
<a href="mensagens.html">💬 Mensagens</a>
```

### Passo 4 — Push para GitHub → Vercel deploya
```bash
cd C:\Users\admin\Desktop\telenthub
copy *.html telenthub\ /Y
git add -A
git commit -m "feat: planos Stripe + mensagens + busca avançada + notificações"
git push origin main
```

---

## 🔜 Próximas melhorias (opcional)

| Feature | Esforço | Impacto |
|---|---|---|
| Upload de foto (candidato + empresa) | Médio | Alto |
| Email transacional (confirmação de candidatura) | Médio | Alto |
| Dashboard stats reais (visualizações, contatos) | Médio | Médio |
| IA de triagem automática | Alto | Alto |
| Exportar relatórios PDF/CSV | Médio | Médio |

---

*Gerado em: 28/05/2026*
