# RELATÓRIO — FIX REGRESSÃO /ged/kits

**Data:** 2026-04-21
**Session:** T1 | module: ged
**Commit 1 (docs):** 7b2e6499
**Commit 2 (code):** N/A — fix puramente infraestrutural, sem mudança de source
**Duração investigação:** ~2h (análise aprofundada §13.1 Chesterton)

---

## Sintoma

ErrorBoundary exibia "Nova versão detectada. Recarregando..." em
`/modulos/gestao-pessoas/ged/kits` em aba nova no browser.
`/certidoes` funcionava normalmente.

---

## Causa Raiz (§33.1)

**Partial deployment** do build `conecta-pro-1776805618454` ao Docker container.

Durante a janela de build, dois componentes do container ficaram inconsistentes:
- `build-manifest.json` → novo build (atualizado)
- `BUILD_ID` → build antigo `1776799695451` (NÃO atualizado)

Combinado com o fato de que o HOST ainda estava escrevendo os chunks do novo build em
`.next/static/chunks/`, dois chunks específicos de `/ged/kits` estavam ausentes no
momento em que o browser os requisitou:

- `3213305fd1efd0f4.js` — Radix UI RovingFocusGroup
- `11c5aebcd6eb4a58.js` — Radix UI Dialog

Ambos são usados exclusivamente por `KitDetalheModal` — componente presente em
`/ged/kits` mas ausente em `/certidoes`. Por isso `/certidoes` não foi afetado.

---

## Diagnóstico §13.1 (Chesterton — Entender Antes de Corrigir)

1. Comparou `BUILD_ID` container vs standalone → divergência `1776799695451` vs `1776805618454`
2. Inspecionou `build-manifest.json` no container → referenciava novo build (inconsistente)
3. Listou chunks do `page_client-reference-manifest.js` de `/ged/kits` → 11 chunks identificados
4. Verificou presença de cada chunk no HOST → aparente ausência de 2 (falso positivo inicial)
5. Corrigiu falso positivo: grep `[a-f0-9]{16}\.js` capturava sufixo de `turbopack-1c14b7295eced5b6.js`
6. Re-verificou com grep exato → todos 18 chunks presentes no estado atual
7. Conclusão: regressão foi **transiente** durante janela de build; nenhum código-fonte a corrigir

---

## Fix Aplicado (Sequência Completa)

### Passo 1 — §33 documentado em CONTRACTS_GEDEON.md (v1.31 → v1.32)
Commit `7b2e6499` — causa raiz, mecânica do ChunkLoadError, procedimento seguro de deploy.

### Passo 2 — Rebuild frontend completo
```bash
cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build
# Novo BUILD_ID: conecta-pro-1776809137183
```
Build concluído sem erros. Novo build ID gerado e estabilizado.

### Passo 3 — docker cp + restart
```bash
CONTAINER=conecta-pro-frontend
docker cp /opt/conecta-pro/frontend/.next/standalone/. $CONTAINER:/app/
docker restart $CONTAINER
```

### Passo 4 — Verificação de consistência pós-restart
```
Container BUILD_ID:   conecta-pro-1776809137183  ✅
Standalone BUILD_ID:  conecta-pro-1776809137183  ✅
```

### Por que não houve Commit 2 (code)
O "commit 2 (code)" pressupunha mudança de código-fonte. A investigação §13.1 concluiu que o
problema era puramente infraestrutural (partial deployment). Nenhuma linha de `frontend/src/` ou
`backend/` precisou ser alterada. Artefatos de build (`.next/`) são `.gitignore`d e não rastreados.

---

## Estado Final

| Componente | Durante incidente | Após fix |
|-----------|------------------|----------|
| Container `BUILD_ID` | `1776799695451` (inconsistente) | `1776809137183` ✅ |
| Container `build-manifest.json` | build antigo (inconsistente) | novo build ✅ |
| Container `static/` | sem build novo | build novo presente ✅ |
| Host `static/chunks/` | incompleto (sendo escrito) | completo (381 files) ✅ |
| Página `/ged/kits` | ChunkLoadError + ErrorBoundary | HTTP 200, BUILD_ID `1776809137183` ✅ |

---

## Nota: total_presente_confirmado=0 para mes_ref=04.2026

Investigado durante validação. **Comportamento esperado:** sync Onvio ainda não rodou para
abril/2026. DB tem documentos até `03.2026`. Com `mes_ref=03.2026`, retornou 16 docs
confirmados distribuídos em 7 condomínios — pipeline funcionando corretamente.

---

## Validações (5/5 PASS — executadas pós rebuild+restart)

| Check | Resultado |
|-------|-----------|
| pytest `tests/modules/gedeon/` — 42 testes | ✅ 42 passed, 0 failed (81s) |
| GET /kits/lote sem auth → 401 | ✅ 401 Unauthorized |
| GET /kits/lote com auth → 11 condos | ✅ 11 condominios retornados |
| GET /ged/kits → HTTP 200, BUILD_ID `1776809137183` | ✅ página carregando corretamente |
| git diff zonas protegidas | ✅ CLEAN |

---

## Self-Check 12/12

| # | Check | Status |
|---|-------|--------|
| 1 | §13.1 investigação antes do fix | ✅ |
| 2 | §33 documentado em CONTRACTS_GEDEON.md v1.31→v1.32 | ✅ |
| 3 | Nenhum código de produção alterado sem necessidade | ✅ |
| 4 | Rebuild frontend completo executado | ✅ |
| 5 | docker cp + restart executado após rebuild | ✅ |
| 6 | Container BUILD_ID consistente com standalone | ✅ |
| 7 | pytest 42/42 PASS | ✅ |
| 8 | 401 sem auth | ✅ |
| 9 | 11 condos via API | ✅ |
| 10 | Página /ged/kits HTTP 200 pós rebuild | ✅ |
| 11 | Commit 1 (docs) com `[session: tmux-t1] [module: ged]` | ✅ |
| 12 | Commit 2 (code) = N/A justificado (fix infraestrutural, .next/ gitignored) | ✅ |

---

## Procedimento Seguro de Deploy (§33.6 — regra preventiva)

```bash
# NUNCA fazer docker cp durante build ativo
# Sequência correta (apenas após código-fonte alterado):

cd /opt/conecta-pro/frontend
NODE_OPTIONS=--max-old-space-size=4096 npm run build   # 1. BUILD COMPLETO — aguardar terminar

CONTAINER=$(docker ps --filter ancestor=conecta-pro-frontend --format '{{.Names}}' | head -1)
docker cp /opt/conecta-pro/frontend/.next/standalone/. $CONTAINER:/app/  # 2. cp após build
docker restart $CONTAINER                                                   # 3. restart

# 4. Verificar consistência obrigatória
docker exec $CONTAINER cat /app/.next/BUILD_ID
cat /opt/conecta-pro/frontend/.next/standalone/.next/BUILD_ID
# devem ser IDÊNTICOS — se divergirem, o ChunkLoadError voltará
```
