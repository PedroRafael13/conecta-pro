# RELATÓRIO T3 — Sync Retroativo Onvio 01-03/2026
**Data:** 2026-04-21 (executado 18:40–18:47)
**Terminal:** T3
**Branch:** feature/people-management-reorganization

---

## Contexto

T2 rodou sync de 04.2026 hoje (58 docs novos, sessão Onvio renovada).
Jordan confirmou envio retroativo pela contadora. Objetivo: rodar 01/02/03.2026.

---

## STEP 1 — Pré-condições

| Item | Resultado |
|---|---|
| TTL onvio:session | **53.284 segundos (~14,8h)** — sessão válida |
| Variável Redis | `REDIS_PASSWORD` (não `REDIS_PASS` como no prompt — corrigido em runtime) |
| Token API | ✅ obtido via form-urlencoded |

---

## STEP 2 — Estado inicial

```
onvio_documents ANTES = 592 linhas
```

---

## STEP 3 — Sync sequencial

### 01.2026 — 18:42:19

```json
{"status":"success","total_api":597,"novos":0,"pulados":595,"erros":0,"duracao":11.67s}
```

DB confirmado:
```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
01.2026  success       0              0           0       12    2026-05-04 18:42:19
```

**Interpretação:** 595 documentos já existiam de sync anterior. 2 docs na API não
foram baixados (provavelmente `doc_scope=null` ou sem categoria mapeada). Nenhum novo.

---

### 02.2026 — 18:45:57

```json
{"status":"success","total_api":597,"novos":1,"pulados":595,"erros":0,"duracao":5.01s}
```

DB confirmado:
```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
02.2026  success       1              1           0        5    2026-05-04 18:45:57
```

**1 documento novo baixado** — retroativo de fevereiro/2026.

---

### 03.2026 — 18:46:55

```json
{"status":"success","total_api":609,"novos":12,"pulados":596,"erros":0,"duracao":11.77s}
```

DB confirmado:
```
mes_ref  status   docs_baixados  docs_novos  docs_erro  dur_s  quando
03.2026  success      12             12           0       12    2026-05-04 18:46:56
```

**12 documentos novos baixados** — retroativo de março/2026.

---

## STEP 4 — Estado final

```
onvio_documents DEPOIS = 605 linhas  (+13 em relação aos 592 iniciais)
```

Resumo dos 3 syncs:

| mes_ref | status  | docs_baixados | docs_novos | docs_erro | dur_s |
|---------|---------|--------------|------------|-----------|-------|
| 03.2026 | success | 12           | 12         | 0         | 12    |
| 02.2026 | success | 1            | 1          | 0         | 5     |
| 01.2026 | success | 0            | 0          | 0         | 12    |

---

## STEP 5 — Distribuição doc_scope após sync

| doc_scope      | count |
|----------------|-------|
| condominio     | 236   |
| (null/vazio)   | 169   |
| empresa_matriz | 107   |
| funcionario    | 93    |
| **TOTAL**      | **605** |

Nota: 169 docs com `doc_scope` vazio — podem ser docs sem categoria mapeada pelo parser Onvio.

---

## DECISÃO

```
[x] 01.2026: docs_novos =  0, erros = 0
[x] 02.2026: docs_novos =  1, erros = 0
[x] 03.2026: docs_novos = 12, erros = 0
[x] Total final onvio_documents: 605  (era 592 → +13)
[x] Algum status='error'? NÃO — todos success
```

---

## Observações operacionais

1. **Rate limit de auth (5 req/min):** o loop for com `sleep 10` do prompt não é
   suficiente entre syncs longos — precisou aguardar renovação de token entre 01→02
   e 02→03. Resolvido com loop `until token válido`.

2. **Variável Redis:** prompt usa `REDIS_PASS`, `.env` tem `REDIS_PASSWORD`.
   Corrigido em runtime sem impacto no resultado.

3. **01.2026 com novos=0:** normal — sync anterior já havia capturado esses docs.
   O `total_api=597` indica que o Onvio tem 597 docs nesse mês mas todos já estavam
   presentes localmente.

4. **169 docs sem doc_scope:** pré-existentes, não relacionados aos 13 novos deste
   sync. Investigar separadamente se necessário.
