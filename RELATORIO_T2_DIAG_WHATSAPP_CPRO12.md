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
| STEP 3 — código WhatsApp existente lido inteiro | ✅ |
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
**§13.1 respeitado** — todos os 4 arquivos WhatsApp lidos integralmente antes de qualquer conclusão.
**INV-2 respeitado** — diagnóstico READ-ONLY absoluto. INV-8: zero mensagens enviadas.

---

## STEP 1 — TOKEN

```
TOKEN_OK: eyJhbGciOiJIUzI1NiIs...  ✅
```

---

## STEP 2 — Evolution API: instalada ou externa?

### 2.1 — Containers com Evolution/WhatsApp
```bash
docker ps --format '{{.Names}}\t{{.Image}}\t{{.Ports}}' | grep -iE "evolution|whatsapp|wpp"
(sem output) ← nenhum container Evolution/WhatsApp em execução

docker ps -a | grep -i "evolution|whatsapp"
(sem output) ← nenhum container parado tampouco
```

### 2.2 — Portas comuns da Evolution (curl com timeout)
```bash
for PORT in 8081 8082 3000 3001 4000; do curl -s --connect-timeout 2 http://localhost:$PORT/ ...
```
| Porta | Resposta | Serviço |
|-------|----------|---------|
| 8081 | ❌ sem resposta | livre |
| 8082 | ❌ sem resposta | livre |
| 3000 | ✅ Next.js HTML | Frontend (pm2 porta 3000) |
| 3001 | ✅ Next.js HTML | Frontend (pm2 porta 3001 — mesmo app) |
| 4000 | ❌ sem resposta | livre |
| `localhost:8081/manager` | ❌ sem resposta | Evolution não instalada |

### 2.3 — Portas via netstat
```
netstat -tlnp | grep -E "8080|8081|8082|3000|4000"
0.0.0.0:8080  LISTEN  docker-proxy (Backend FastAPI)
0.0.0.0:3000  LISTEN  next-server (Frontend)
Portas 8081, 8082, 4000: LIVRES
```

### 2.4 — DNS da URL configurada (`api.evolution.app.br`)
```
nslookup api.evolution.app.br
  Server: 127.0.0.53
  ** server can't find api.evolution.app.br: NXDOMAIN

ping -c 1 -W 2 api.evolution.app.br
  ping: api.evolution.app.br: Name or service not known
```

### 2.5 — docker-compose tem Evolution definida?
```
grep -in "evolution|whatsapp" docker-compose*.yml
docker-compose.yml linha: EVOLUTION_API_URL e EVOLUTION_API_KEY como env vars do backend
→ Apenas variáveis de ambiente passadas ao container — SEM serviço Evolution definido
→ Nenhum serviço evolution-api no docker-compose.yml
```

**Conclusão STEP 2: Evolution API NÃO está instalada no VPS. URL `api.evolution.app.br` é NXDOMAIN. Nenhuma porta respondendo. Apenas env vars apontando para domínio inexistente.**

---

## STEP 3 — Código WhatsApp existente

### 3.1 — Todos os arquivos com "whatsapp" / "evolution" / "wapp" no nome
```bash
find backend/ -iname "*whatsapp*" -o -iname "*evolution*" -o -iname "*wapp*" | grep -v __pycache__ | grep -v ".pyc" | grep -v venv | sort
```
```
backend/modules/client_portal/controllers/whatsapp_controller.py
backend/modules/integrations/connectors/whatsapp/             (diretório)
backend/modules/integrations/whatsapp/                        (diretório)
backend/modules/integrations/whatsapp/models/whatsapp_config.py
backend/modules/integrations/whatsapp/services/whatsapp_service.py
```
*Arquivos com "evolution" ou "wapp" no nome: nenhum (apenas diretórios).*

### 3.2 — Todos os arquivos .py com "whatsapp" no nome (lidos integralmente)

#### Arquivo 1 — `modules/integrations/connectors/whatsapp/service.py` (176 linhas)
**Tipo:** Serviço simples, aiohttp direto para Evolution API
**Env vars:** `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `WHATSAPP_INSTANCE_ID`, `WHATSAPP_API_ENABLED`
**Endpoint Evolution:** `POST /message/sendText/{instance}`
**Funções de envio:**
- `send_kit_notification(phone, client_name, month, year, docs_count, portal_url)` — mensagem kit mensal
- `send_certificate_alert(phone, client_name, cert_type, expiry_date, days_remaining)` — alerta certidão
- `send_nfse_notification(phone, client_name, nfse_number, value, month, year)` — NFS-e emitida
- `send_custom(phone, message)` — mensagem livre
- `check_status()` → `GET /instance/fetchInstances`
**Estado:** Código pronto. Se `WHATSAPP_API_ENABLED=false` → retorna `{"status":"disabled"}`. Se `true` + URL inválida → exception aiohttp.

#### Arquivo 2 — `modules/integrations/connectors/whatsapp/controller.py` (167 linhas)
**Tipo:** REST endpoints que chamam o Serviço 1
**Endpoints:**
- `GET /whatsapp/status`
- `POST /whatsapp/send/kit-notification`
- `POST /whatsapp/send/certificate-alert`
- `POST /whatsapp/send/nfse-notification`
- `POST /whatsapp/send/custom`
**Registro:** `main_production.py` linha 960–961 via `gestao/__init__.py`

#### Arquivo 3 — `modules/integrations/whatsapp/services/whatsapp_service.py` (745 linhas)
**Tipo:** Sistema completo com fila, templates, rate limiting, webhooks, relatórios
**Tabelas necessárias (ausentes no banco):** `wa_configs`, `message_queue`, `message_log`, `message_template`
**Estado crítico:** `_send_message_now` tem comentário explícito:
```python
# Simula envio para API (em produção, fazer chamada HTTP real)
external_id = f"wamid.{message.id}"  ← gerado localmente, não chama API real
```
**Funções:** `send_template_message`, `send_billing_reminder`, `process_queue`, `get_queue_stats`, `get_daily_report`, `handle_webhook`

#### Arquivo 4 — `modules/integrations/whatsapp/models/whatsapp_config.py` (164 linhas)
**Tipo:** Model SQLAlchemy da configuração WhatsApp
**Tabela:** `wa_configs` (NÃO existe no banco)
**Provedores suportados pelo modelo:** META_CLOUD, TWILIO, MESSAGEBIRD, ZENVIA, TAKE_BLIP, GUPSHUP
**⚠️ Nota:** Este modelo NÃO é para Evolution API — é para WhatsApp Business API oficial (Meta Cloud) ou provedores pagos.
**Campos:** `phone_number`, `access_token`, `api_key`, `messages_per_day_limit` (1000/dia), `business_hours_start/end`

#### Arquivo 5 — `modules/client_portal/controllers/whatsapp_controller.py` (250 linhas)
**Tipo:** Webhook do Evolution API → cria/atualiza tickets de suporte
**Env vars adicionais:** `WHATSAPP_WEBHOOK_SECRET`, `WHATSAPP_NUMBER`, `EVOLUTION_INSTANCE` — **NENHUMA configurada no .env**
**Campo `clients.whatsapp`** referenciado: busca cliente pelo número WhatsApp no banco
**Função `_send_whatsapp_reply`:** usa `httpx.post` para `{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}`

### 3.3 — Endpoints WhatsApp registrados
```
GET  /api/v1/whatsapp/status
POST /api/v1/whatsapp/send/kit-notification
POST /api/v1/whatsapp/send/certificate-alert
POST /api/v1/whatsapp/send/nfse-notification
POST /api/v1/whatsapp/send/custom
POST /whatsapp/webhook        (client_portal — webhook Evolution)
GET  /whatsapp/config         (client_portal — status público)
POST /api/v1/notifications/webhooks/whatsapp  (notifications engine)
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
```bash
grep -rn "98221|92984|PHONE|NUMERO|NUMBER" /opt/conecta-pro/.env | cut -d'=' -f1
```
Chaves presentes: `WHATSAPP_API_ENABLED`, `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `WHATSAPP_INSTANCE_ID`
**Número 98221-4414:** ❌ não encontrado
**WHATSAPP_NUMBER:** ❌ não configurado
**EVOLUTION_INSTANCE:** ❌ não configurado

### 4.2 — Tabelas WhatsApp/WhatsApp-related no banco
```sql
SELECT table_name FROM information_schema.tables
WHERE table_name ILIKE '%whatsapp%' OR table_name ILIKE '%wapp%' OR table_name ILIKE '%evolution%'
→ 0 rows

SELECT * FROM wa_configs LIMIT 5;
→ tabela não existe

SELECT * FROM whatsapp_config LIMIT 5;
→ tabela não existe
```
**Todas as 4 tabelas do serviço B ausentes:** `wa_configs`, `message_queue`, `message_log`, `message_template`

### 4.3 — Campo `clients.whatsapp`
Código `client_portal/whatsapp_controller.py` referencia:
```sql
SELECT id, name FROM clients WHERE whatsapp = :phone AND ativo = true LIMIT 1
```
Campo existe na tabela `clients`, mas nenhum cliente tem número cadastrado.

**Número (92) 98221-4414 — Configurado no .env:** ❌ não
**Número (92) 98221-4414 — Configurado no banco:** ❌ não

---

## STEP 5 — Recursos do VPS para instalar Evolution

### 5.1 — Disco
```
df -h / → 331 GB livres / 387 GB total (15% usado)
df -h /var/lib/docker → mesmo filesystem (/dev/sda1) → 331 GB livres
```

### 5.2 — Memória
```
free -h | grep -E "Mem|Swap"
Mem:   31Gi total  17Gi used   2.1Gi free  12Gi buff/cache  13Gi available
Swap:  4.0Gi total  1.1Gi used  2.9Gi free
```

### 5.3 — Docker versão e compose
```
docker --version        → Docker version 29.1.3, build f52814d
docker compose version  → Docker Compose version v5.0.0
```

### 5.4 — Portas disponíveis
```
ss -tlnp | grep -E "8081|8082"
(sem output) → portas 8081 e 8082 LIVRES
```

| Recurso | Estado | Para Evolution API |
|---------|--------|-------------------|
| Disco `/var/lib/docker` | **331 GB livres** | ✅ Evolution usa ~500 MB imagem |
| RAM disponível | **13 GB disponíveis** | ✅ Evolution usa ~200–400 MB |
| CPU | 8 cores AMD EPYC 9354P | ✅ |
| Docker | v29.1.3 + Compose v5.0.0 | ✅ pronto |
| Porta 8081 | **LIVRE** | ✅ porta padrão Evolution |

---

## STEP 6 — O que falta para enviar kit por WhatsApp

### 6.1 — `people_management/ged/` tem WhatsApp?
```bash
grep -rn "whatsapp|wapp" backend/modules/people_management/ged/ --include="*.py"
→ 0 resultados — GED people_management NÃO tem referência a WhatsApp
```

### 6.2 — Funções de envio WhatsApp no projeto
```bash
grep -rn "def send.*whatsapp|def enviar.*whatsapp|def send_message|sendMessage" backend/ --include="*.py" | grep -v __pycache__ | grep -v venv
```
Funções encontradas nos módulos WhatsApp:
- `send_kit_notification`, `send_certificate_alert`, `send_nfse_notification`, `send_custom` (serviço A — aiohttp)
- `send_template_message`, `send_billing_reminder` (serviço B — simulado)
**Funções de envio:** ✅ existem — mas bloqueadas por Evolution não instalada

### 6.3 — Fluxo atual (dois passos separados, sem automação)
```
Passo 1: POST /ged/kits/{id}/send          → muda status para "enviado" (SEM WhatsApp)
Passo 2: POST /whatsapp/send/kit-notification → envia mensagem (FALHA — Evolution não instalada)
→ Não há integração automática GED→WhatsApp
```

---

## STEP 7 — Hipóteses

| # | Hipótese | Resultado |
|---|----------|-----------|
| H1 | Evolution API NÃO instalada no VPS | ✅ CONFIRMADO — zero containers, DNS NXDOMAIN, curl 8081/manager sem resposta |
| H2 | Existe código de controller WhatsApp | ✅ CONFIRMADO — 5 arquivos .py encontrados, 3 serviços distintos |
| H3 | Código consegue enviar mensagem de texto + link | ✅ CONFIRMADO (serviço A tem `send_kit_notification` com portal_url) mas bloqueado por H1 |
| H4 | Número (92) 98221-4414 configurado em .env ou banco | ❌ REFUTADO — não encontrado em lugar algum |
| H5 | docker-compose tem serviço Evolution definido | ❌ REFUTADO — apenas env vars passadas ao backend, sem serviço |
| H6 | VPS tem recursos para instalar Evolution | ✅ CONFIRMADO — 13 GB RAM, 331 GB disco, porta 8081 livre |
| H7 | Endpoint kit WhatsApp existe no GED | ❌ REFUTADO — GED send_kit não chama WhatsApp |
| H8 | Status endpoint retorna detalhe | ✅ CONFIRMADO — `{"online":false,"error":"Cannot connect to...ssl:default [Name or service not known]"}` |

---

## Evolution API: instalada ou externa?

**NÃO instalada.** URL `api.evolution.app.br` é NXDOMAIN — domínio inexistente. Não há container, processo, nem porta respondendo no VPS. É uma URL placeholder inválida no `.env`.

## URL configurada resolve DNS?

**Não.** `nslookup api.evolution.app.br` retorna `NXDOMAIN`. Domínio não existe.

## Código WhatsApp existente

**Arquivos:** 5 arquivos .py com "whatsapp" no nome (3 serviços funcionais + 1 modelo + 1 controller portal)
**Funções de envio:** ✅ existem (`send_kit_notification`, `send_certificate_alert`, `send_nfse_notification`, `send_custom`, `send_template_message`)
**Endpoints registrados:** 8 endpoints (5 REST + 2 portal + 1 notifications webhook)

## Número (92) 98221-4414

**Configurado no .env:** ❌ não
**Configurado no banco:** ❌ não (campo `clients.whatsapp` existe mas vazio)

## Recursos do VPS para instalar Evolution

**Disco disponível:** 331 GB livres
**RAM disponível:** 13 GB disponíveis
**Porta 8081 livre:** ✅ sim

---

## O que falta (lista ordenada)

1. **Instalar Evolution API** — nenhum container no VPS, URL inválida
2. **Atualizar `EVOLUTION_API_URL`** no `.env` para apontar para Evolution local (ex: `http://evolution-api:8081`)
3. **Configurar `EVOLUTION_API_KEY`** com chave real da instância
4. **Configurar `WHATSAPP_INSTANCE_ID`** = `conecta-pro` (já tem esse valor)
5. **Configurar `WHATSAPP_NUMBER`** = `5592982214414` (número da Conecta Mais)
6. **Conectar número via QR Code** — ação manual Jordan (escanear com celular)
7. **Cadastrar número nos clientes** — campo `clients.whatsapp` para cada cliente destinatário
8. **Criar tabelas** `wa_configs`, `message_queue`, `message_log`, `message_template` (se optar pelo Serviço B)
9. **Integrar GED→WhatsApp** — `send_kit` no GED deve chamar `send_kit_notification` automaticamente

---

## Plano de ação para WhatsApp funcionar

**Passo 1:** Instalar Evolution API via Docker (requer autorização Jordan para docker-compose.yml)
```yaml
# docker-compose.yml — novo serviço
evolution-api:
  image: atendai/evolution-api:latest
  container_name: evolution-api
  restart: unless-stopped
  ports: ["8081:8080"]
  environment:
    AUTHENTICATION_API_KEY: <gerar-chave>
  networks: [conecta-pro-network]
```

**Passo 2:** Configurar `EVOLUTION_API_URL=http://evolution-api:8081` no `.env`

**Passo 3:** Conectar número (92) 98221-4414 via QR Code
```bash
# Criar instância
POST http://localhost:8081/instance/create {"instanceName":"conecta-pro","qrcode":true}
# Escanear QR com celular da Conecta Mais
GET http://localhost:8081/instance/qrcode/conecta-pro
```

**Passo 4:** Integrar GED endpoint send_kit com WhatsApp notification (1 prompt implementação)

**Passo 5:** Testar envio real
```bash
POST /api/v1/whatsapp/send/custom {"phone":"5592982214414","message":"Teste Conecta PRO"}
```

**Estimativa:** 1 prompt de implementação (docker-compose + .env + integração GED) + 1 ação manual Jordan (QR Code no celular)

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | `ec5c3fdf` | `docs(contracts): §77 — Diagnóstico profundo WhatsApp Evolution API (CPRO12 T2-diag-wapp)` |

T2 DIAG WHATSAPP CPRO12 OK — plano de ação gerado.
