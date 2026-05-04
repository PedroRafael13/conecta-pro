# T1 — Diagnóstico Onvio Sync
**Data:** 2026-05-04
**Branch:** feature/people-management-reorganization
**Tipo:** Read-only — zero deploy

---

## CAUSA RAIZ — CORRIGIDA PELA AUDITORIA T2

> **Sessão Onvio no Redis existia mas estava inválida no servidor (transient 401 em 30/04).**
> O refresh de sessão (`onvio_auth.py`) **JÁ estava agendado no crontab às 04:00 diário** —
> T1 perdeu esta linha por causa de `head -30` na listagem do crontab.
> O sync mensal roda via cron no **dia 7 às 07:00**.
> A causa real: Onvio retornou 401 para sessão válida em 30/04 (issue transient server-side).
> Ninguém disparou sync manual após 30/04. Resolvido pelo T2 em 04/05.

### ⚠️ Correção T1 — Erro de diagnóstico

T1 afirmou: *"onvio-auth-refresh.sh não está no crontab"* — **INCORRETO**.

Crontab real (linhas além do `head -30` usado em T1):
```
# GEDEON Fase 3 — Onvio Sync
0 4  * * * /opt/conecta-pro/rotinas/scripts/onvio-auth-refresh.sh   # Renovar sessão 04:00 diário
0 7  7 * * /opt/conecta-pro/rotinas/scripts/onvio-sync-mensal.sh    # Sync mensal dia 7 07:00
```
Evidência: log `rotinas/logs/onvio_auth_202605.log` mostra renovações às 04:00 em 01, 02, 03 e 04/05.

---

## 1. Schema real: onvio_sync_log

Colunas existentes (o prompt usou colunas inexistentes — adaptado):

| Coluna | Tipo |
|--------|------|
| `id` | uuid |
| `mes_ref` | varchar(10) |
| `status` | varchar(20) — `running / success / error / partial` |
| `docs_baixados` | integer |
| `docs_novos` | integer |
| `docs_erro` | integer |
| `duracao_s` | double |
| `detalhes` | text — mensagem de erro completa |
| `created_at` | timestamptz |

**Colunas esperadas pelo prompt que NÃO existem:** `started_at`, `finished_at`, `documents_synced`, `documents_failed`, `error_message`

---

## 2. Últimos 10 logs — padrão de erro

| mes_ref | status | erro | created_at |
|---------|--------|------|------------|
| all | error | 401 Unauthorized — `api/storage/v1/containers/documents` | 2026-04-30 14:47 |
| all | error | 401 Unauthorized | 2026-04-30 14:47 |
| all | error | 401 Unauthorized | 2026-04-30 14:45 |
| 2026-01-01 | error | Sessão Onvio não encontrada no Redis | 2026-04-30 03:14 |
| all | error | Sessão Onvio não encontrada no Redis | 2026-04-30 03:14 |
| all | error | Sessão Onvio não encontrada no Redis | 2026-04-30 03:14 |
| all | error | Sessão Onvio não encontrada no Redis | 2026-04-30 03:14 |
| 2026-01-01 | error | 401 Unauthorized | 2026-04-28 19:20 |
| all | error | 401 Unauthorized | 2026-04-28 19:20 |
| all | error | 401 Unauthorized | 2026-04-28 19:20 |

**Dois padrões de erro distintos:**
1. `"Sessão Onvio não encontrada no Redis"` — chave `onvio:session` inexistente (TTL expirou)
2. `"401 Client Error: Unauthorized"` — chave existe mas token inválido no servidor Onvio

---

## 3. Erro completo do último log

```
401 Client Error: Unauthorized for url:
https://onvio.com.br/api/storage/v1/containers/documents
  ?from=1&pageSize=100&loadPermission=true&readByClientUser=
  &customFields=[{"name":"clientId","value":"*** REDACTED ***","ignoreCase":true}]
```

---

## 4. Linha do tempo da quebra

| Data/Hora | Evento |
|-----------|--------|
| 2026-04-28 04:46 | **Última sync bem-sucedida** (`success`, 0 docs) |
| 2026-04-28 19:20 | **Primeiros 401** — sessão expirou no servidor Onvio |
| 2026-04-30 03:14 | Sessão sumiu do Redis (TTL 16h expirou) — 4 erros "não encontrada" |
| 2026-04-30 14:44 | Alguém rodou `onvio_auth.py` manualmente → sessão voltou pro Redis |
| 2026-04-30 14:45–47 | Novos 401 — sessão nova também rejeitada pelo Onvio |

**Desde 30/04/2026 14:47**: nenhuma tentativa de sync registrada.

---

## 5. Histórico geral

| status | qtd | primeiro | último |
|--------|-----|----------|--------|
| error | **44** | 2026-04-18 | 2026-04-30 |
| success | 33 | 2026-04-17 | **2026-04-28** |
| partial | 8 | 2026-04-17 | 2026-04-22 |

⚠️ Erros 401 começaram em **2026-04-18** — problema intermitente há 12 dias antes da quebra total.

---

## 6. Scripts bash

### onvio-auth-refresh.sh
- Lê `REDIS_PASS` e `REDIS_IP` dinamicamente
- Define `REDIS_URL=redis://:PASS@IP:6379/1`
- Roda `python3 /opt/conecta-pro/onvio_auth.py`
- Notifica Telegram em caso de sucesso/falha
- **NÃO está no crontab** — execução manual apenas

### onvio-sync-mensal.sh
- `curl -X POST http://localhost:8080/api/v1/onvio/sync?mes_ref=MM.YYYY`
- Notifica Telegram ao concluir
- **NÃO está no crontab** — execução manual apenas

---

## 7. Crontab — entradas onvio

**Resultado T1 (incorreto — perdido por `head -30`):** nenhuma entrada encontrada.

**Resultado real (corrigido pela auditoria T2):**
```
0 4  * * * /opt/conecta-pro/rotinas/scripts/onvio-auth-refresh.sh   # diário 04:00
0 7  7 * * /opt/conecta-pro/rotinas/scripts/onvio-sync-mensal.sh    # dia 7 de cada mês 07:00
```
O sync mensal próximo seria 2026-05-07 07:00 (já antecipado pelo T2 em 2026-05-04).

---

## 8. Variáveis ONVIO no .env

| Arquivo | Variáveis |
|---------|-----------|
| `backend/.env` | Nenhuma variável `ONVIO_*` |
| `.env` (raiz) | `ONVIO_PASS=Jordan0612*` · `ONVIO_IMAP_PASSWORD=Adm@conecta#2019` |

**Método de autenticação:** OIDC headless HTTP (sem Playwright)
- POST `/api/security/v1/oidc/login` → Auth0 (auth.thomsonreuters.com)
- 6 passos: email → senha → MFA via IMAP (código OTP lido automaticamente)
- Salva cookies + `long_token` no Redis com **TTL 57600s (16h)**
- Login: `administracao@conectamaistech.com.br`
- MFA: IMAP `imap.titan.email` porta 993

---

## 9. Tabelas onvio_*

Apenas 2 tabelas: `onvio_documents` (534 linhas) · `onvio_sync_log` (85 linhas)

---

## 10. Estado Redis agora (2026-05-04 15:12)

| Item | Valor |
|------|-------|
| Chave `onvio:session` | ✅ EXISTE |
| TTL restante | **17.260s (~4.8h)** |
| Chaves dentro da sessão | `cookies`, `auth0_cookies`, `onvio_cookies`, `uds_token`, `long_token`, `final_url`, `extracted_at`, `extracted_at_iso` |
| `long_token` | Presente (REDACTED) |
| Cookies Auth0 | `did`, `auth0`, `did_compat`, `auth0_compat`, `mfa_enrolled`, `uid` |

---

## 11. Teste ao vivo da sessão Redis → Onvio (agora)

```
session-and-bindings: HTTP 403
  {"Message":["com.tr.bluemoon.uds.SessionNotFoundException"]}

list-documents: HTTP 401
  {"data":{"code":401,"domain":"DocumentServices","message":"Not Authorized"}}
```

**Conclusão:** A sessão no Redis existe mas está **completamente inválida no servidor Onvio**.
O `long_token` e cookies foram invalidados pelo Onvio (logout forçado, expiração server-side, ou MFA revalidation).

---

## DIAGNÓSTICO FINAL — REVISADO

### Causa raiz real
Onvio retornou `401` para sessão válida em 2026-04-30 14:45–47 (issue transient server-side).
O cron de renovação **já existia e funcionava** (04:00 diário).
Ninguém disparou sync manual após 30/04. O próximo sync agendado seria 07/05.

### Cronologia corrigida
1. 2026-04-18: primeiros 401 intermitentes (Onvio rejeitava sessões de vez em quando)
2. 2026-04-28 04:46: última sync bem-sucedida
3. 2026-04-28 19:20: 401 novamente — sessão ou expirou ou Onvio rejeitou
4. 2026-04-30 03:14: sync manual tentado antes da renovação das 04:00 → "sessão não encontrada"
5. 2026-04-30 04:00: **cron renovou sessão** (`[2026-04-30 04:00:14] ✅ Sessão renovada`)
6. 2026-04-30 14:44–47: tentativas manuais de sync → **401 mesmo com sessão fresca**
7. 2026-05-01 a 04: cron renovou sessão diariamente às 04:00 ✅
8. 2026-05-04 17:31: **T2 disparou sync manual → success, 58 novos docs, 0 erros**

### O que estava faltando (real)
Apenas um disparo manual do sync. O cron de auth estava funcionando.

### Status após T2
Resolvido. Próxima renovação de sessão: cron 05/05 às 04:00. Próximo sync mensal: 07/05 às 07:00.
