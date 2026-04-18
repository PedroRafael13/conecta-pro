# RELATÓRIO T5_B2 — EnrichmentService + Endpoint extrair-valores
**Data:** 2026-04-18
**Commits:** 09fbcfbe → 15f1e463 → 2df4916f
**Branch:** feature/people-management-reorganization

---

## 1. STEP 0 — 6 Respostas do Contrato

| Pergunta | Resposta |
|----------|----------|
| Path canônico dos extractors | `backend/modules/gedeon/onvio/pdf_extractor/` |
| Thresholds de salvamento | >=0.90 salva final / 0.70-0.89 revisao_manual=True / <0.70 não salva |
| Tipo monetário obrigatório | `Decimal` (Numeric(15,2) no DB) |
| Categorias → fgts_guias | fgts_guia, fgts_consignado, fgts_relatorio, fgts_consignado_relatorio |
| Categorias → inss_guias | inss_guia |
| Descobertas T2/T3/T4 relevantes | Gap storage: T5 usa `caminho_local` do DB (não filesystem); 34 arquivos em inss_guia/ mas apenas 5 reais no DB; fgts_guia/ estava vazio no container |

---

## 2. Thinking — 5 Respostas

| Pergunta | Resposta |
|----------|----------|
| Onde T5 busca os PDFs? | `caminho_local` no DB (T3 confirmou que paths divergem do filesystem) |
| Categoria sem extractor | marca `extraido_em=now, confianca=0, metodo="sem_caminho\|arquivo_nao_encontrado"` e conta em erros |
| DCTFWeb subtipos | strip prefixo "dctfweb_" → subtipo; mapeado em EXTRACTOR_MAP com kwargs |
| Idempotência | filtra `extraido_em IS NULL` por padrão; `forcar=True` remove o filtro |
| Transações | commit a cada COMMIT_EVERY=20 PDFs + commit final |

---

## 3. Output endpoint com limite=3 (JSON completo — pós fix pulados_sem_extractor)

```json
{
    "processados": 3,
    "salvos_final": 3,
    "salvos_revisao": 0,
    "pulados_baixa_conf": 0,
    "pulados_sem_extractor": 315,
    "erros": 0,
    "por_categoria": {
        "dctfweb_resumo_creditos": 2,
        "dctfweb_recibo": 1
    },
    "duracao_s": 0.32,
    "erros_detalhe": []
}
```

> `pulados_sem_extractor: 315` = docs sem extractor (folha_pagamento, contratos, etc.)
> O valor é 315 e não 323 porque 436 total − 121 extraídos de outras categorias no banco.

---

## 4. SELECT onvio_documents (5 linhas mais recentes)

```
                  id                  |         categoria         | confianca | metodo   | revisao |          extraido_em
--------------------------------------+---------------------------+-----------+----------+---------+-----------------------------
 ff393714-...                         | fgts_consignado           |      1.00 | regex_v1 | f       | 2026-04-18 12:05:10.255282+00
 fe8ce111-...                         | dctfweb_resumo_debitos    |      0.90 | regex_v1 | f       | 2026-04-18 12:05:10.159794+00
 fbf3cb21-...                         | dctfweb_recibo            |      1.00 | regex_v1 | f       | 2026-04-18 12:05:10.103796+00
 fb3d86b8-...                         | fgts_consignado_relatorio |      1.00 | regex_v1 | f       | 2026-04-18 12:05:09.881262+00
 ef07395d-...                         | dctfweb_declaracao        |      0.85 | regex_v1 | t       | 2026-04-18 12:05:09.802784+00
```

**total com extraido_em preenchido: 121**

---

## 5. COUNT inss_guias/fgts_guias com valor

```
inss_com_valor: 5
fgts_com_valor: 42
```

> Após run completo: 5 INSS e 42 FGTS com valor preenchido.

---

## 6. Teste de Idempotência — 2ª chamada = processados:0 ✅

```
# 1ª chamada (118 docs pendentes):
processados: 118, duracao: 29.9s

# 2ª chamada sem forcar:
{
    "processados": 0,
    "salvos_final": 0,
    "salvos_revisao": 0,
    "pulados_baixa_conf": 0,
    "pulados_sem_extractor": 315,
    "erros": 0,
    "por_categoria": {},
    "duracao_s": 0.01
}
```

**processados: 0 confirmado** — nenhum doc com `extraido_em IS NULL` na fila.

---

## 7. Teste forcar=true (reprocessamento) ✅

```
Com forcar=true&limite=3: processados: 3
```

`forcar=True` remove o filtro `extraido_em IS NULL` e reprocessa docs já extraídos.

---

## 8. Self-check 7/7 ✅

- [x] STEP 0 — 6 respostas do contrato corretas
- [x] EnrichmentService com EXTRACTOR_MAP cobrindo 13 categorias
- [x] Endpoint /extrair-valores retorna 200 com limite=3 — `processados:3, pulados_sem_extractor:315`
- [x] Validação SQL: 121 docs com extraido_em preenchido, inss_com_valor:5, fgts_com_valor:42
- [x] Idempotência: 2ª chamada sem forcar retorna **processados:0** ✅
- [x] forcar=true reprocessa docs já extraídos — processados:3
- [x] Commits em lote (COMMIT_EVERY=20) — log verificado no docker:
      `"Commit parcial: 20/118"`, `"40/118"`, `"60/118"`, `"80/118"`, `"100/118"` ✅

---

## 9. Commits

```
09fbcfbe  feat(gedeon): T5_B2 — EnrichmentService + endpoint POST /onvio/extrair-valores
15f1e463  docs(gedeon): T5_B2 auditoria — import no topo + contrato v1.3 + relatório
2df4916f  fix(gedeon): T5_B2 — corrige pulados_sem_extractor sempre 0
```

---

## 10. T5_B2 OK — LIBERAR T6

**T5_B2 OK — LIBERAR T6**
