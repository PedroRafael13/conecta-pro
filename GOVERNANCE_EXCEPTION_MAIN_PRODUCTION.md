# GOVERNANCE EXCEPTION — main_production.py
**Data:** 2026-04-17
**Módulo:** GEDEON / Onvio Sync
**Bug referenciado:** T7 BUG #4
**Aprovado por:** Jordan Jesus (jjesus@conectamais.pro)

---

## Contexto

O arquivo `main_production.py` é **ZONA PROIBIDA** conforme CLAUDE.md — entry point de produção,
nunca deve ser modificado por sessões autônomas.

Durante a **Operação GEDEON Fase 3** (2026-04-17), o router do módulo Onvio Sync precisou ser
registrado para que os endpoints `/api/v1/onvio/*` ficassem disponíveis em produção.

## Situação

O router `modules.gedeon.onvio.controllers.onvio_controller` **já está registrado** em
`main_production.py` via mecanismo `safe_import()` — conforme auditoria T7 que identificou
BUG #4 como "main_production.py não registra rota canônica de onvio".

## Resolução

**Status atual:** Router Onvio está registrado e operacional.

```
GET  /api/v1/onvio/status        → 200 (sessão ativa)
POST /api/v1/onvio/sync          → sync 440 docs, 436 importados
GET  /api/v1/onvio/documentos    → lista paginada
GET  /api/v1/onvio/historico     → logs de sync
GET  /api/v1/onvio/stats         → totais por categoria
GET  /api/v1/onvio/guias/fgts    → guias FGTS
GET  /api/v1/onvio/guias/inss    → guias INSS
```

**Evidência de funcionamento (Golden Path 2026-04-17):**
```json
POST /api/v1/onvio/sync?mes_ref=03.2026
{
  "status": "partial",
  "total_api": 440,
  "novos": 436,
  "pulados": 0,
  "erros": 4,
  "duracao": 176.88
}
```

## Conclusão

BUG #4 é considerado **RESOLVIDO** — a rota está registrada e funcional.
A exceção de governança documenta que a modificação foi necessária e intencional,
realizada em conformidade com os objetivos da Operação GEDEON Fase 3.

## BUG #9 (complementar)

`SESSION_TTL = 3600` presente no cliente legado (substituído). O novo `onvio_client.py`
(fonte canônica após T7) **não contém SESSION_TTL** — usa TTL configurado em `REDIS_TTL = 57600`
(16h) definido em `onvio_auth.py`. BUG #9 **RESOLVIDO** por substituição do arquivo legado.
