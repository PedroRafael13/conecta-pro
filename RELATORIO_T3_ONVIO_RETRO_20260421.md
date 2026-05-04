# RELATÓRIO T3 — Sync Retroativo Onvio 01-03/2026
**Data:** 2026-04-21 (executado 18:40–18:47)
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## Contexto

T2 rodou sync de 04.2026 hoje (58 docs novos, sessão Onvio renovada).
Jordan confirmou envio retroativo pela contadora. Objetivo: rodar 01/02/03.2026.

---

## AUDITORIA DE EXECUÇÃO — linha a linha

| Linha/Bloco | Status | Desvio documentado |
|---|---|---|
| `cd /opt/conecta-pro` | ✅ | — |
| `echo "═══ T3 ONVIO RETRO..."` | ✅ | — |
| STEP 1: `REDIS_PASS=$(grep ^REDIS_PASS ...)` | ⚠️ verbatim falhou | `grep ^REDIS_PASS` captura `REDIS_PASSWORD` + `REDIS_PASSWORD_STAGING` (dois valores concatenados) → redis-cli recebe senha inválida → TTL = string de erro |
| STEP 1: `if [ "$TTL" -lt 600 ]` | ⚠️ comparação numérica falhou | TTL era string de erro, não número — bash retornou "integer expression expected". Bloco if não executou. |
| STEP 1: TTL real (suplemento) | ✅ corrigido | `REDIS_PASSWORD` correto → TTL = **53.284s (~14,8h)** — sessão válida |
| STEP 1: TOKEN login | ✅ | form-urlencoded, token obtido |
| STEP 1: `[ -z "$TOKEN" ] && exit 1` | ✅ | TOKEN válido, não saiu |
| STEP 2: COUNT(*) ANTES | ✅ | 592 |
| STEP 3: for loop — 01.2026 sync | ✅ | Executado como bash separado (não loop único) |
| STEP 3: for loop — sleep 10 | ⚠️ posição diferente | Prompt: sleep 10 antes da query DB. Execução real: sleep antes do próximo sync. Resultado idêntico. |
| STEP 3: for loop — DB log query 01 | ✅ | |
| STEP 3: for loop — 02.2026 sync | ✅ | Token renovado (rate limit) |
| STEP 3: for loop — DB log query 02 | ✅ | |
| STEP 3: for loop — 03.2026 sync | ✅ | |
| STEP 3: for loop — DB log query 03 | ✅ | |
| STEP 4: COUNT(*) DEPOIS | ✅ | 605 |
| STEP 4: Resumo 3 syncs (INTERVAL 1h) | ✅ | Query executada dentro da janela de 1h |
| STEP 5: doc_scope distribuição | ✅ | |
| DECISÃO preenchida | ✅ | |
| STOP CONDITIONS respeitadas | ✅ | Nenhum HTTP 401/500, nenhuma parada antecipada |
| REGRAS DE OURO respeitadas | ✅ | Sequencial, 1 sync/vez, sem modificação de código |
| `👉 Reportar volume por mês + erros` | ✅ | |

**Desvios que NÃO afetaram os resultados:**
1. `REDIS_PASS` falhou verbatim → sessão verificada com variável correta (válida)
2. For loop → bash calls separados (mesmos resultados, mesma ordem)
3. `sleep 10` reposicionado → mesma pausa total entre syncs

---

## STEP 1 — Pré-condições

| Item | Resultado |
|---|---|
| TTL onvio:session | **53.284s (~14,8h)** — sessão válida |
| Variável Redis no .env | `REDIS_PASSWORD` (prompt usa `REDIS_PASS` — não existe isolado) |
| Token API | ✅ obtido via form-urlencoded |

---

## STEP 2 — Estado inicial

```
onvio_documents ANTES = 592 linhas
```

---

## STEP 3 — Sync sequencial

### 01.2026 — 18:42:19

```
HTTP_CODE: 200
{"status":"success","total_api":597,"novos":0,"pulados":595,"erros":0,"duracao":11.67s}
```

```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
01.2026  success       0              0           0       12    2026-05-04 18:42:19
```

595 documentos já existiam. 0 novos.

### 02.2026 — 18:45:57

```
HTTP_CODE: 200
{"status":"success","total_api":597,"novos":1,"pulados":595,"erros":0,"duracao":5.01s}
```

```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
02.2026  success       1              1           0        5    2026-05-04 18:45:57
```

**1 documento novo** — retroativo fevereiro/2026.

### 03.2026 — 18:46:55

```
HTTP_CODE: 200
{"status":"success","total_api":609,"novos":12,"pulados":596,"erros":0,"duracao":11.77s}
```

```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
03.2026  success      12             12           0       12    2026-05-04 18:46:56
```

**12 documentos novos** — retroativo março/2026.

---

## STEP 4 — Estado final

```
onvio_documents DEPOIS = 605 linhas  (+13 em relação a 592)
```

Resumo dos 3 syncs (query `INTERVAL '1 hour'` — executada às 18:56, dentro da janela):

| mes_ref | status  | docs_baixados | docs_novos | docs_erro | duracao_s |
|---------|---------|--------------|------------|-----------|-----------|
| 03.2026 | success | 12           | 12         | 0         | 12        |
| 02.2026 | success | 1            | 1          | 0         | 5         |
| 01.2026 | success | 0            | 0          | 0         | 12        |

---

## STEP 5 — Distribuição doc_scope após sync

| doc_scope      | count |
|----------------|-------|
| condominio     | 236   |
| (null/vazio)   | 169   |
| empresa_matriz | 107   |
| funcionario    | 93    |
| **TOTAL**      | **605** |

169 docs com `doc_scope` vazio — pré-existentes, não relacionados aos +13 deste sync.

---

## DECISÃO

```
[x] 01.2026: docs_novos =  0, erros = 0
[x] 02.2026: docs_novos =  1, erros = 0
[x] 03.2026: docs_novos = 12, erros = 0
[x] Total final onvio_documents: 605  (era 592 → +13)
[x] Algum status='error'? NÃO — todos success
```
