# T2 CPRO12 — Diagnóstico Profundo WhatsApp
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Tipo:** READ-ONLY — diagnóstico pré-implementação
**Branch:** feature/people-management-reorganization
**Número alvo:** (92) 98221-4414

---

## Self-Check (10 itens)

| Item | Status |
|------|--------|
| STEP 0 — contrato lido, §77 confirmado, §13.1 + INV-2 citados | ✅ |
| STEP 1 — TOKEN obtido | ✅ |
| STEP 2 — Evolution: containers + portas + DNS verificados | ✅ |
| STEP 3 — código WhatsApp existente lido inteiro (3 serviços) | ✅ |
| STEP 4 — número (92) 98221-4414 verificado no .env e banco | ✅ |
| STEP 5 — recursos VPS verificados (disco, RAM, porta) | ✅ |
| STEP 6 — endpoint de envio de kit por WhatsApp verificado | ✅ |
| STEP 7 — relatório com plano de ação gerado | ✅ |
| STEP 8 — §77 + commit + push | ✅ |
| INV-2 — ZERO alterações de código | ✅ |
| INV-8 — NENHUMA mensagem WhatsApp enviada | ✅ |

---

## STEP 0 — Contrato

`CONTRACTS_GEDEON.md` lido. Último parágrafo antes desta tarefa: **§75** (Diagnóstico canais envio kit GED).
Novo contrato: **§77** (conforme especificado no prompt).
**§13.1 respeitado** — todos os arquivos WhatsApp lidos antes de qualquer conclusão.
**INV-2 respeitado** — diagnóstico READ-ONLY absoluto. INV-8: zero mensagens enviadas.

---

## STEP 1 — TOKEN

```
TOKEN_OK: eyJhbGciOiJIUzI1NiIs...  ✅
```

---

## STEP 2 — Evolution API: instalada ou externa?

### 2.1 — Containers com Evolution/WhatsApp
```
docker ps | grep -i "evolution|whatsapp|wpp"
RESULTADO: (sem output) — nenhum container
docker ps -a | grep -i "evolution|whatsapp"
RESULTADO: nenhum container (running ou stopped)
Imagens: nenhuma imagem Evolution/WhatsApp
```

### 2.2 — Portas comuns da Evolution (curl com timeout)
| Porta | curl localhost | Resultado |
|-------|---------------|-----------|
| 8081 | `curl -s --connect-timeout 2 http://localhost:8081/manager` | ❌ sem resposta |
| 8082 | `curl -s --connect-timeout 2 http://localhost:8082/` | ❌ sem resposta |
| 4000 | `curl -s --connect-timeout 2 http://localhost:4000/` | ❌ sem resposta |
| 8080 | em uso | ✅ Backend FastAPI |
| 3000 | em uso | ✅ Next.js frontend |

### 2.3 — Portas via netstat
```
netstat -tlnp | grep -E "8080|8081|8082|3000|4000"
tcp   0.0.0.0:8080   LISTEN   docker-proxy (Backend)
tcp   0.0.0.0:3000   LISTEN   next-server (Frontend)
Portas 8081, 8082, 4000: LIVRES
```

### 2.4 — DNS da URL configurada
```
Host configurado: api.evolution.app.br
nslookup api.evolution.app.br:
  Server: 127.0.0.53
  ** server can't find api.evolution.app.br: NXDOMAIN

ping api.evolution.app.br:
  ping: api.evolution.app.br: Name or service not known
```

### 2.5 — docker-compose tem Evolution?
```
grep -in "evolution|whatsapp" docker-compose*.yml
docker-compose.yml: EVOLUTION_API_URL e EVOLUTION_API_KEY como variáveis de ambiente do backend
→ Declaradas como env vars para o container, mas SEM serviço Evolution definido
```

**Conclusão STEP 2:** Evolution API **NÃO está instalada** no VPS. URL `api.evolution.app.br` é NXDOMAIN. Nenhum container, nenhuma imagem, nenhuma porta respondendo. Apenas variáveis de ambiente apontando para URL inexistente.

---

## STEP 3 — Código WhatsApp existente

### Todos os arquivos WhatsApp/Evolution no projeto (excluindo venv/pycache):

```
backend/modules/integrations/connectors/whatsapp/
  ├── __init__.py
  ├── controller.py       ← REST endpoints Evolution API
  └── service.py          ← WhatsAppService (aiohttp direto)

backend/modules/integrations/whatsapp/
  ├── models/
  │   ├── message_log.py
  │   ├── message_queue.py
  │   ├── message_template.py
  │   ├── whatsapp_config.py
  │   └── __init__.py
  └── services/
      ├── chatbot_service.py
      ├── whatsapp_service.py  ← WhatsAppService v2 (fila+banco)
      └── __init__.py

backend/modules/client_portal/controllers/
  └── whatsapp_controller.py  ← Webhook + tickets WhatsApp
```

---

### Serviço A — `connectors/whatsapp/service.py` (aiohttp direto)

**Env vars:** `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `WHATSAPP_INSTANCE_ID`, `WHATSAPP_API_ENABLED`
**Evolution endpoint:** `POST /message/sendText/{instance}`
**Métodos:**
- `send_kit_notification(phone, client_name, month, year, docs_count, portal_url)` → mensagem texto formatada
- `send_certificate_alert(phone, client_name, cert_type, expiry_date, days_remaining)`
- `send_nfse_notification(phone, client_name, nfse_number, value, month, year)`
- `send_custom(phone, message)`
- `check_status()` → `GET /instance/fetchInstances`

**Estado:** Código pronto. Falha silenciosamente quando `WHATSAPP_API_ENABLED=false` (retorna `{"status":"disabled"}`). Quando `enabled=true` e URL inválida → lança exception aiohttp.

---

### Serviço B — `integrations/whatsapp/services/whatsapp_service.py` (fila+banco)

**Tipo:** Sistema completo com fila de mensagens, templates aprovados, rate limiting, webhooks, relatórios diários.
**Tabelas necessárias:** `whatsapp_configs`, `message_queue`, `message_log`, `message_template`
**Estado crítico:** Método `_send_message_now` tem comentário explícito:
```python
# Simula envio para API (em produção, fazer chamada HTTP real)
external_id = f"wamid.{message.id}"  # ← gerado localmente, não é externo real
```
**Tabelas no banco:** NENHUMA — `SELECT table_name FROM information_schema.tables WHERE table_name ILIKE '%whatsapp%'` → 0 rows.

---

### Serviço C — `client_portal/controllers/whatsapp_controller.py` (webhook portal)

**Função:** Recebe webhooks do Evolution API, cria/atualiza tickets de suporte.
**Env vars adicionais:** `WHATSAPP_WEBHOOK_SECRET`, `WHATSAPP_NUMBER`, `EVOLUTION_INSTANCE`
**Estado:** Nenhuma dessas 3 vars está no `.env` → portal WhatsApp completamente desabilitado.
**Campo `clients.whatsapp`** referenciado no código (busca cliente pelo número WhatsApp).

---

### 3.3 — Endpoints REST registrados
```
GET  /api/v1/whatsapp/status
POST /api/v1/whatsapp/send/kit-notification
POST /api/v1/whatsapp/send/certificate-alert
POST /api/v1/whatsapp/send/nfse-notification
POST /api/v1/whatsapp/send/custom

POST /whatsapp/webhook   (client_portal)
GET  /whatsapp/config    (client_portal)

POST /api/v1/notifications/webhooks/whatsapp  (notification_controller)
```

### 3.4 — Status endpoint (resposta real)
```json
{
    "online": false,
    "instance": "conecta-pro",
    "enabled": true,
    "details": {
        "online": false,
        "error": "Cannot connect to host api.evolution.app.br:443 ssl:default [Name or service not known]"
    }
}
```

---

## STEP 4 — Número (92) 98221-4414 e Configuração

### 4.1 — No .env
```
grep -rn "98221|92984|PHONE|NUMERO|NUMBER" .env
Chaves presentes: WHATSAPP_API_ENABLED, EVOLUTION_API_URL, EVOLUTION_API_KEY, WHATSAPP_INSTANCE_ID
Número 98221-4414: NÃO encontrado
WHATSAPP_NUMBER: NÃO configurado
```

### 4.2 — Tabelas WhatsApp no banco
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name ILIKE '%whatsapp%' OR table_name ILIKE '%wapp%' OR table_name ILIKE '%evolution%'
→ 0 rows (nenhuma tabela WhatsApp existe no banco)
```

### 4.3 — Campo `whatsapp` na tabela clients
O código em `client_portal/whatsapp_controller.py` faz:
```sql
SELECT id, name FROM clients WHERE whatsapp = :phone AND ativo = true LIMIT 1
```
→ Campo `clients.whatsapp` **existe** na tabela, mas **nenhum cliente tem número cadastrado**.

---

## STEP 5 — Recursos do VPS para instalar Evolution

| Recurso | Estado | Para Evolution API |
|---------|--------|-------------------|
| Disco disponível | **331 GB livres** / 387 GB total (15% usado) | ✅ Evolution usa ~500 MB imagem |
| RAM disponível | **13 GB disponíveis** / 31 GB total | ✅ Evolution usa ~200–400 MB |
| CPU | 8 cores AMD EPYC 9354P | ✅ |
| Docker | v29.1.3 | ✅ pronto para `docker run` |
| Porta 8081 | **LIVRE** | ✅ porta padrão Evolution |
| Porta 8082 | LIVRE | ✅ alternativa |
| Porta 4000 | LIVRE | ✅ alternativa |

---

## STEP 6 — O que falta para enviar kit por WhatsApp

### 6.1 — `people_management/ged/` tem WhatsApp?
```
grep -rn "whatsapp|wapp" backend/modules/people_management/ged/ --include="*.py"
→ 0 resultados: GED people_management NÃO tem referência a WhatsApp
```

### 6.2 — Funções de envio WhatsApp no projeto
```
grep -rn "def send.*whatsapp|def enviar.*whatsapp|def send_message|sendMessage" backend/ --include="*.py"
→ Apenas em venv (tqdm, kombu, locust) e módulos não-WhatsApp (Telegram, fase5/agents)
→ Nenhuma função `send_message` WhatsApp nos módulos de negócio (excluindo serviços A/B/C já listados)
```

### 6.3 — Fluxo atual (dois passos manuais, sem automação)
```
1. POST /ged/kits/{id}/send       → muda status para "enviado" (sem WhatsApp)
2. POST /whatsapp/send/kit-notification  → envia mensagem (falha — Evolution não instalada)
```
**Não há integração automática GED→WhatsApp.**

---

## STEP 7 — Relatório: Evolution instalada ou externa?

**Resposta:** NÃO instalada. URL `api.evolution.app.br` é um domínio inválido/inexistente (NXDOMAIN).

---

## Hipóteses

| # | Hipótese | Resultado |
|---|----------|-----------|
| H1 | Evolution API NÃO instalada no VPS | ✅ CONFIRMADO — zero containers, DNS NXDOMAIN |
| H2 | Existe código de controller WhatsApp | ✅ CONFIRMADO — 3 serviços distintos encontrados |
| H3 | Código consegue enviar mensagem de texto + link | ✅ CONFIRMADO (serviço A pronto) mas bloqueado por H1 |
| H4 | Número (92) 98221-4414 configurado em .env ou banco | ❌ REFUTADO — não encontrado em lugar algum |
| H5 | docker-compose tem serviço Evolution | ❌ REFUTADO — apenas env vars, sem serviço |
| H6 | VPS tem recursos para instalar Evolution | ✅ CONFIRMADO — 13 GB RAM, 331 GB disco, porta 8081 livre |
| H7 | Endpoint kit WhatsApp existe no GED | ❌ REFUTADO — GED send_kit não chama WhatsApp |
| H8 | Status endpoint retorna detalhe da instância | ✅ CONFIRMADO — retorna error "ssl:default [Name or service not known]" |

---

## Plano de ação para WhatsApp funcionar

### Pré-requisito: Jordan autoriza Opção A ou B

---

### Opção A — Evolution API Self-Hosted (RECOMENDADA)

```bash
# Passo 1 — Instalar Evolution API via Docker (porta 8081)
# (requer edição docker-compose.yml — autorização Jordan)
# Adicionar serviço:
#   evolution-api:
#     image: atendai/evolution-api:latest
#     container_name: evolution-api
#     restart: unless-stopped
#     ports: ["8081:8080"]
#     environment:
#       AUTHENTICATION_API_KEY: <gerar-chave>
#       DATABASE_CONNECTION_URI: postgresql://postgres:...@postgres:5432/evolution
#     networks: [conecta-pro-network]

# Passo 2 — Atualizar .env
EVOLUTION_API_URL=http://evolution-api:8081
EVOLUTION_API_KEY=<chave-gerada>
WHATSAPP_INSTANCE_ID=conecta-pro
WHATSAPP_NUMBER=5592982214414    # (92) 98221-4414

# Passo 3 — Criar instância + QR Code (ação manual Jordan)
POST /instance/create  {"instanceName": "conecta-pro", "qrcode": true}
GET /instance/qrcode/conecta-pro  → escanear com celular da Conecta

# Passo 4 — Testar
GET /api/v1/whatsapp/status → {"online": true}
POST /api/v1/whatsapp/send/custom {"phone": "5592982214414", "message": "Teste"}

# Passo 5 — Integrar GED (prompt separado)
POST /ged/kits/{id}/send + POST /whatsapp/send/kit-notification → automatizar no mesmo endpoint
```

**Estimativa:** 1 prompt implementação (docker-compose + .env + teste) + 1 ação manual Jordan (QR Code no celular).

---

### Opção B — Evolution API Cloud

```
1. Criar conta em evolution.app.br (plano pago ~$20/mês)
2. Obter URL da instância (ex: https://minha-instancia.evolution.app.br)
3. Atualizar EVOLUTION_API_URL e EVOLUTION_API_KEY no .env
4. Conectar número via painel web
5. Testar endpoint status
```

---

### Opção C — WhatsApp Business API Meta (Oficial)

```
1. Conta Meta Business + número (92) 98221-4414 verificado (~7 dias)
2. Criar migration para tabelas: whatsapp_configs, message_queue, message_log, message_template
3. Implementar envio real em _send_message_now (serviço B)
4. Cadastrar templates no Meta (aprovação 1-3 dias)
5. Custo: ~R$ 0,30/mensagem
```

---

## Status Final

| Componente | Estado |
|------------|--------|
| Evolution API container | ❌ Não instalado |
| DNS api.evolution.app.br | ❌ NXDOMAIN |
| Código serviço A (aiohttp) | ✅ Pronto |
| Código serviço B (fila+banco) | ⚠️ Simulado (sem chamada HTTP real + tabelas ausentes) |
| Código serviço C (webhook/portal) | ✅ Pronto |
| Tabelas DB WhatsApp | ❌ Não existem |
| WHATSAPP_API_ENABLED | ⚠️ true (mas URL inválida) |
| WHATSAPP_NUMBER | ❌ Não configurado |
| Número 98221-4414 | ❌ Não cadastrado em clientes |
| Recursos VPS | ✅ Suficientes (13 GB RAM, 331 GB disco, 8081 livre) |
| Integração GED→WhatsApp | ❌ Ausente |

**Próximo passo:** Jordan decide entre Opção A (self-hosted, recomendada) ou B (cloud).

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `ffd4c45a` → corrigido | `docs(contracts): §77 — Diagnóstico profundo WhatsApp Evolution API` |
| relatorio | `ca1c8f25` → corrigido | `docs(relatorio): T2-DIAG-WHATSAPP CPRO12 — relatório completo 3 serviços` |
