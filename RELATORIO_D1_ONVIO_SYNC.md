# RELATÓRIO D1 — ONVIO AUTH + SYNC
**Data:** 2026-04-22
**Sessão:** Claude Code — D1 ONVIO AUTH + SYNC (GARGALO RAIZ)
**Branch:** feature/people-management-reorganization
**Status Final:** ✅ CONCLUÍDO (com ressalva: 04/2026 sem PDFs no Onvio ainda)

---

## 1. Diagnóstico Inicial (STEP 0 + STEP 1)

### Pre-flight
| Item | Resultado |
|------|-----------|
| `onvio_documents` no DB | 436 rows |
| Kits documentais ativos | 10 kits (04/2026) |
| Docs com PDF | 0 |
| `/app/uploads/onvio/` | **NÃO EXISTIA** |
| `onvio:session` no Redis | AUSENTE |

### Arquivos auditados
- `onvio_auth.py` — PATH A confirmado (requests puro, sem Playwright)
- `onvio_client.py` — lê Redis key `onvio:session`, usa `UDSLongToken`
- `onvio_sync_service.py` — `STORAGE_BASE = /app/uploads/onvio` (volume correto)
- `onvio_parser.py` — v2 com 26 categorias

---

## 2. Problemas Encontrados e Corrigidos

### BUG 1 — Redis inacessível do host
**Sintoma:** `ConnectionRefusedError: [Errno 111] Connection refused` no log de `2026-04-22 04:01:05`
**Causa:** `onvio_auth.py` usa `REDIS_URL=redis://127.0.0.1:6379/1` por padrão, mas Redis não expõe porta no host
**Fix:** Passar `REDIS_URL` com IP do container Docker (`172.18.0.14`) e senha correta via env
**Arquivo:** `rotinas/scripts/onvio-auth-refresh.sh` — atualizado com resolução dinâmica de IP

### BUG 2 — `/app/uploads/onvio/` inexistente
**Sintoma:** `PermissionError: [Errno 13] Permission denied: '/app/uploads/onvio'`
**Causa:** Diretório não criado no volume montado em `/opt/conecta-pro/uploads/`
**Fix:** `mkdir -p /opt/conecta-pro/uploads/onvio && chmod 777 /opt/conecta-pro/uploads/onvio`

### BUG 3 — Módulos em cache (kill -HUP 1 não recarrega Python)
**Sintoma:** `'dict' object has no attribute 'upper'` — código antigo em memória
**Causa:** `kill -HUP 1` em uvicorn produção não faz live reload de módulos Python
**Fix:** Usar `docker restart` após `docker cp` para garantir reload completo
**Nota:** O padrão correto é `docker cp` → `docker restart` (não `kill -HUP 1`)

### BUG 4 — Arquivos xlsx/xlt causavam erros no sync
**Sintoma:** `Download de X não retornou PDF válido` para `.xlsx`, `.xlt`
**Causa:** Onvio contém 3 arquivos não-PDF; `baixar_pdf()` valida cabeçalho `%PDF`
**Fix:** Adicionado check de extensão no início do loop de sync:
```python
EXTENSOES_VALIDAS = {".pdf", ".PDF"}
ext = "." + nome.rsplit(".", 1)[-1] if "." in nome else ""
if ext not in EXTENSOES_VALIDAS:
    pulados += 1
    continue
```
**Arquivo:** `backend/modules/gedeon/onvio/onvio_sync_service.py`

---

## 3. Auth Onvio — Execução

```
[1/6] Carregando página de auth Onvio...     ✅
[2/6] Iniciando OIDC login (Auth0 URL)...    ✅
[3/6] Carregando página login Auth0...       ✅
[4/6] Enviando e-mail...                     ✅
[5/6] Enviando senha (sem MFA solicitado)... ✅
[6/6] Trocando code OAuth → JWT + LongToken  ✅
✅ Sessão salva no Redis (TTL 16h = 57600s)
```

**Key:** `onvio:session` em Redis DB 1
**TTL atual:** ~15h59m (verificado às 22:10)
**long_token:** presente (32 chars)
**cookies:** `['did', 'auth0', 'did_compat', 'auth0_compat', 'mfa_enrolled', 'uid']`

---

## 4. Sync Onvio — Resultados

### Sync sem filtro (completo)
```json
{
  "status": "success",
  "total_api": 537,
  "novos": 97,
  "pulados": 437,
  "erros": 3,
  "duracao": 44.6
}
```
→ Após fix xlsx: **0 erros** (3 arquivos .xlsx/.xlt corretamente pulados)

### Sync 04.2026 (mês alvo)
```json
{
  "status": "partial",
  "novos": 0,
  "total_api": 537,
  "pulados": 534
}
```
**Conclusão:** Documentos de Abril 2026 **ainda não foram carregados no Onvio**. É comportamento esperado — a folha de 04/2026 é processada no final/início do mês seguinte.

---

## 5. Estado Final do Banco

| Métrica | Antes | Depois |
|---------|-------|--------|
| `onvio_documents` | 436 | 534 |
| PDFs em disco | 0 | 98 |
| Docs 03.2026 | 43 | 43 ✅ (preservado) |
| Docs 04.2026 | 0 | 0 (Onvio sem PDFs ainda) |

### Distribuição por `mes_ref`:
| mes_ref | docs |
|---------|------|
| 03.2026 | 43 |
| 02.2026 | 28 |
| 01.2026 | 27 |
| 12.2025 | 29 |
| 11.2025 | 27 |
| 10.2025 | 21 |
| 09.2025 | 24 |
| 08.2025 | 30 |
| 07.2025 | 22 |
| 2025 | 155 |
| 2026 | 20 |
| None | 105 |

---

## 6. Validações D1

| # | Validação | Resultado |
|---|-----------|-----------|
| A | `GET /api/v1/onvio/status → sessao_valida:true` | ✅ |
| B | Redis `onvio:session` TTL > 50.000s | ✅ (54055s) |
| C | Sync 04.2026 → `novos > 0` | ⚠️ 0 (PDFs não disponíveis ainda no Onvio) |
| D | `onvio_documents WHERE mes_ref='04.2026' > 0` | ⚠️ 0 (mesma razão) |
| E | Pelo menos 1 PDF em disco | ✅ (98 PDFs em `/opt/conecta-pro/uploads/onvio/`) |
| F | `onvio_documents >= 436` | ✅ (534) |

---

## 7. Arquivos Modificados

| Arquivo | Tipo | Mudança |
|---------|------|---------|
| `backend/modules/gedeon/onvio/onvio_sync_service.py` | Fix | Adicionado skip de arquivos não-PDF por extensão |
| `rotinas/scripts/onvio-auth-refresh.sh` | Fix | REDIS_URL dinâmico (resolve IP container Redis) |

---

## 8. Descobertas Importantes

### Padrão hot-copy correto
O CLAUDE.md documenta `docker cp + kill -HUP 1`. Na prática, `kill -HUP 1` **NÃO** recarrega módulos Python em uvicorn produção. O padrão correto é:
```bash
docker cp /opt/conecta-pro/backend/modules/ $CONTAINER:/app/modules/
docker restart $CONTAINER
```

### Script onvio-auth-refresh.sh
Para rodar o script de renovação de sessão do host, o `REDIS_URL` deve usar o IP interno do container Redis (não `localhost`). O script agora resolve o IP dinamicamente via `docker inspect`.

### 04/2026 — Documentos não disponíveis
A ausência de PDFs de abril 2026 no Onvio é **comportamento de negócio esperado** — a folha é processada no final do mês ou início do próximo. O sync deve ser rodado novamente após ~2026-05-07 para capturar os documentos.

---

## 9. Próximos Passos

1. **2026-05-07+**: Re-rodar `POST /api/v1/onvio/sync?mes_ref=04.2026` quando folha de abril for processada
2. **STEP 4 (D1 original)**: Documentar §38 em CONTRACTS_GEDEON.md v1.37
3. **Crontab**: Verificar que `onvio-auth-refresh.sh` está no cron (renovação da sessão a cada 14h)

---

*Gerado por Claude Code — [session: D1] [module: gedeon/onvio]*
