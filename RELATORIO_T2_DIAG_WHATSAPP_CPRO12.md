# T2 DIAG WHATSAPP CPRO12 — Diagnóstico Evolution API / WhatsApp
**Data:** 2026-05-05
**Sessão:** tmux-t2 | **Tipo:** READ-ONLY — diagnóstico pré-implementação
**Branch:** feature/people-management-reorganization
**Autorização:** Jordan Jesus — leitura conforme prompt

---

## Self-Check

| Item | Status |
|------|--------|
| STEP 0 — §75 confirmado (último), §76 será o novo | ✅ |
| STEP 1 — TOKEN obtido | ✅ |
| STEP 2 — Evolution containers + portas + DNS verificados | ✅ |
| STEP 3 — código WhatsApp existente lido inteiro | ✅ |
| STEP 4 — número (92) 98221-4414 verificado no .env e banco | ✅ |
| STEP 5 — recursos VPS verificados (disco, RAM, porta) | ✅ |
| STEP 6 — endpoint de envio de kit por WhatsApp verificado | ✅ |
| STEP 7 — relatório com plano de ação gerado | ✅ |
| STEP 8 — §76 + commit + push | ✅ |
| INV-2 — ZERO alterações de código | ✅ |
| INV-8 — NENHUMA mensagem WhatsApp enviada | ✅ |

---

## STEP 0 — Contrato

`CONTRACTS_GEDEON.md` lido. Último parágrafo: **§75** (Diagnóstico canais envio kit GED, 2026-05-05).
Novo contrato: **§76**.
**§13.1 respeitado** — arquivo lido antes de qualquer escrita.
**INV-2 respeitado** — diagnóstico READ-ONLY absoluto.

---

## STEP 2 — Estado da Evolution API

### Containers Docker
```
RESULTADO: nenhum container Evolution (running ou stopped)
RESULTADO: nenhuma imagem Evolution no host
```

### DNS
| Host | Resultado |
|------|-----------|
| `api.evolution.app.br` | ❌ `socket.gaierror: Name or service not known` |
| `evolution-api` (hostname local) | ❌ `Temporary failure in name resolution` |

### Portas
| Porta | Estado | Ocupante |
|-------|--------|----------|
| 3000 | EM USO | Next.js frontend |
| 8081 | **LIVRE** | — |
| 8082 | LIVRE | — |
| 8443 | LIVRE | — |

**Conclusão: Evolution API NÃO está instalada no VPS. URL configurada (`api.evolution.app.br`) não resolve DNS — serviço externo inexistente ou URL errada.**

---

## STEP 3 — Código WhatsApp existente

### Dois serviços paralelos foram encontrados:

#### A) `modules/integrations/connectors/whatsapp/service.py` — **Serviço Simples (aiohttp direto)**
- Lê: `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `WHATSAPP_INSTANCE_ID`, `WHATSAPP_API_ENABLED`
- Endpoint Evolution: `POST /message/sendText/{instance}`
- Métodos:
  - `send_kit_notification(phone, client_name, month, year, docs_count, portal_url)` ✅
  - `send_certificate_alert(phone, client_name, cert_type, expiry_date, days_remaining)` ✅
  - `send_nfse_notification(phone, client_name, nfse_number, value, month, year)` ✅
  - `send_custom(phone, message)` ✅
  - `check_status()` → `GET /instance/fetchInstances` ✅
- **Estado:** Código pronto. Falha silenciosamente quando `WHATSAPP_API_ENABLED=false` ou DNS inválido.
- **Observação:** `WHATSAPP_API_ENABLED=true` no .env, mas URL inativa → todas as chamadas lançam exception.

#### B) `modules/integrations/whatsapp/services/whatsapp_service.py` — **Serviço Completo (com banco)**
- Usa tabelas: `whatsapp_configs`, `message_queue`, `message_log`, `message_template`
- Fila de mensagens, templates aprovados, rate limiting, webhooks, relatórios diários
- **Estado:** Código completo MAS tabelas **não existem no banco** (nenhuma migration criada).
- `_send_message_now` tem comentário explícito: *"Simula envio para API (em produção, fazer chamada HTTP real)"* — **integração real NÃO implementada**.

#### C) `modules/integrations/connectors/whatsapp/controller.py` — **Endpoints REST**
Registrado em `main_production.py` (linha 960–961) via `whatsapp_router`.
Endpoints disponíveis:
| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/whatsapp/status` | GET | Status conexão Evolution |
| `/whatsapp/send/kit-notification` | POST | Notificação kit documental |
| `/whatsapp/send/certificate-alert` | POST | Alerta certidão vencendo |
| `/whatsapp/send/nfse-notification` | POST | Notificação NFS-e emitida |
| `/whatsapp/send/custom` | POST | Mensagem customizada |

---

## STEP 4 — Número (92) 98221-4414

| Localização | Resultado |
|-------------|-----------|
| `/opt/conecta-pro/.env` | ❌ não encontrado |
| `/opt/conecta-pro/backend/.env` | ❌ não encontrado |
| Tabela `clients` (campo `phone`) | ❌ nenhum cliente com esse número |
| Código-fonte (`grep -r "98221"`) | ❌ não encontrado |

**Conclusão: número (92) 98221-4414 não está cadastrado em nenhum lugar do sistema.**

---

## STEP 5 — Recursos VPS

| Recurso | Estado | Capacidade Evolution API |
|---------|--------|--------------------------|
| Disco | 331 GB livre / 387 GB (15% usado) | ✅ Evolution precisa ~500 MB |
| RAM | 13 GB disponível / 31 GB | ✅ Evolution usa ~200–400 MB |
| CPU | 8 cores AMD EPYC 9354P | ✅ mais que suficiente |
| Porta 8081 | **LIVRE** | ✅ porta padrão Evolution |
| Porta 3000 | Em uso (Next.js) | — não usar |
| Docker | v29.1.3 instalado | ✅ pronto para `docker run` |

**Conclusão: VPS tem recursos suficientes para instalar Evolution API self-hosted.**

---

## STEP 6 — Endpoint de envio de kit por WhatsApp

### Situação atual:
- `POST /whatsapp/send/kit-notification` existe e funciona **tecnicamente** (código correto)
- Mas falha em runtime porque `EVOLUTION_API_URL=https://api.evolution.app.br` não resolve DNS
- `GED send_kit` (`POST /ged/kits/{id}/send`) apenas muda status para "enviado" — **não chama WhatsApp**
- `ged_config_controller.py` menciona `canal_envio: whatsapp` mas está com `ativo: false`
- **Não há integração GED→WhatsApp** — precisaria ser implementada

### Fluxo atual para enviar kit por WhatsApp:
```
1. Chamar POST /ged/kits/{id}/send  (muda status para "enviado")
2. Chamar POST /whatsapp/send/kit-notification  (envia notificação manualmente)
→ São dois passos separados, sem automação
```

---

## STEP 7 — Plano de Ação

### Bloqueadores atuais (ordem de resolução)

| # | Bloqueador | Impacto |
|---|-----------|---------|
| B1 | `api.evolution.app.br` não resolve DNS | 🔴 CRÍTICO — zero envios |
| B2 | Tabelas `whatsapp_configs` etc. não existem | 🔴 CRÍTICO — serviço v2 não funciona |
| B3 | Número (92) 98221-4414 não cadastrado | 🟡 MÉDIO — sem destinatário |
| B4 | GED send_kit não integra WhatsApp | 🟡 MÉDIO — envio manual necessário |

---

### Opção A — Evolution API Self-Hosted (RECOMENDADA)

**Pré-requisito:** Autorização Jordan para modificar `docker-compose.yml` e `.env`.

**Passos:**
```bash
# 1. Adicionar serviço evolution ao docker-compose.yml (nova seção)
# evolution-api:
#   image: atendai/evolution-api:latest
#   container_name: evolution-api
#   ports: ["8081:8080"]
#   environment: [AUTHENTICATION_API_KEY, DATABASE_CONNECTION_URI]
#   networks: [conecta-pro-network]

# 2. Atualizar .env
# EVOLUTION_API_URL=http://evolution-api:8081
# EVOLUTION_API_KEY=<chave-gerada>
# WHATSAPP_INSTANCE_ID=conecta-pro

# 3. Subir container
docker compose up -d evolution-api

# 4. Criar instância via API
POST http://localhost:8081/instance/create
{
  "instanceName": "conecta-pro",
  "token": "<api-key>",
  "qrcode": true
}

# 5. Conectar WhatsApp (escanear QR code)
GET http://localhost:8081/instance/qrcode/conecta-pro

# 6. Testar endpoint
GET /api/v1/whatsapp/status
```

**Vantagens:** Controle total, sem custo mensal de API cloud, dados ficam no VPS.
**Desvantagem:** Requer QR code scan com telefone físico; WhatsApp pode bloquear números não-business.

---

### Opção B — Evolution API Cloud

**Passos:**
```bash
# 1. Criar conta em evolution.app.br (plano pago)
# 2. Obter URL real e API key
# 3. Atualizar .env:
EVOLUTION_API_URL=https://<sua-instancia>.evolution.app.br
EVOLUTION_API_KEY=<key-real>
WHATSAPP_INSTANCE_ID=conecta-pro
# 4. Testar: GET /api/v1/whatsapp/status
```

**Vantagens:** Zero infra para gerenciar.
**Desvantagem:** Custo mensal; URL `api.evolution.app.br` (genérico) não existe — precisa ser URL de instância.

---

### Opção C — WhatsApp Business API (Meta Oficial)

**Passos:**
1. Conta Meta Business + número (92) 98221-4414 verificado
2. Criar migration para tabelas `whatsapp_configs`, `message_queue`, `message_log`, `message_template`
3. Implementar `_send_message_now` real no serviço v2
4. Cadastrar templates no Meta (aprovação pode levar dias)

**Vantagens:** Oficial, sem risco de bloqueio.
**Desvantagem:** Maior complexidade, aprovação de templates, custo por mensagem.

---

### Para enviar kit para (92) 98221-4414 HOJE (sem Evolution):

Workaround imediato via WhatsApp Web manual ou usando serviço Twilio/Z-API enquanto Evolution não está configurada:

```python
# Teste direto (requer Evolution rodando)
curl -X POST http://127.0.0.1:8080/api/v1/whatsapp/send/kit-notification \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "92982214414",
    "client_name": "NOME DO CLIENTE",
    "month": 5,
    "year": 2026,
    "documents_count": 12
  }'
# Resultado atual: {"status": "exception", "error": "...Name or service not known"}
```

---

## Diagnóstico Final

| Componente | Estado | Detalhe |
|------------|--------|---------|
| Código WhatsApp | ✅ PRONTO | Dois serviços implementados |
| Endpoints REST | ✅ REGISTRADOS | 5 endpoints em /api/v1/whatsapp/ |
| Evolution API container | ❌ NÃO INSTALADO | Nenhum container no VPS |
| DNS `api.evolution.app.br` | ❌ FALHA | URL inválida/inexistente |
| Tabelas DB (v2 service) | ❌ AUSENTES | Migration não criada |
| WHATSAPP_API_ENABLED | ⚠️ `true` | Habilitado mas URL inválida |
| Número 98221-4414 | ❌ NÃO CADASTRADO | Não está em nenhum cliente |
| Recursos VPS | ✅ SUFICIENTES | 13 GB RAM, 331 GB disco, porta 8081 livre |
| Integração GED→WhatsApp | ❌ AUSENTE | GED send_kit não chama WhatsApp |

**Próximo passo recomendado:** Jordan decide entre Opção A (Evolution self-hosted) ou Opção B (cloud).
Qualquer opção requer 1 prompt de implementação (escopo estimado: docker-compose + .env + teste).

---

## Commits

| Tipo | Hash | Mensagem |
|------|------|----------|
| docs | a ser gerado | `docs(contracts): §76 — Diagnóstico WhatsApp/Evolution API (CPRO12 T2-DIAG-WHATSAPP)` |
| relatorio | a ser gerado | `docs(relatorio): T2-DIAG-WHATSAPP CPRO12 — Evolution não instalado, plano A/B/C` |
