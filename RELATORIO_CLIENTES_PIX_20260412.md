# RELATÓRIO — CLIENTES ATIVOS × COBERTURA PIX
**Data:** 2026-04-12
**Gerado por:** Claude Code — Conecta PRO ERP
**Banco:** conecta_pro (PostgreSQL)

---

## RESUMO EXECUTIVO

| Métrica | Valor |
|---------|-------|
| Total de clientes ativos | 12 |
| Com chave PIX cadastrada | **10** (83%) |
| Sem chave PIX | **2** (registros internos — sem CNPJ real) |
| MRR total (clientes reais) | **R$ 270.586,96** |
| MRR coberto por PIX | **R$ 270.586,96** (100% dos clientes reais) |

---

## CLIENTES COM PIX ✅

| # | Nome | CNPJ | MRR | Chave PIX | Segmento |
|---|------|------|-----|-----------|----------|
| 1 | CONDOMINIO IDEAL FLORES DA CIDADE | 23.147.782/0001-91 | R$ 65.842,42 | 23147782000191 | Enterprise |
| 2 | RESIDENCIAL LARANJEIRAS VILLAGE | 24.632.786/0001-28 | R$ 42.544,50 | 24632786000128 | Large |
| 3 | CONDOMINIO MIRANTE DAS FLORES | 52.605.708/0001-70 | R$ 42.255,80 | 52605708000170 | Large |
| 4 | CONDOMINIO PRIME ARENA | 47.405.340/0001-66 | R$ 40.466,50 | 47405340000166 | Large |
| 5 | CONDOMINIO RESIDENCIAL VILLA DOS PASSAROS | 13.221.953/0001-21 | R$ 37.338,33 | 13221953000121 | Large |
| 6 | CONDOMINIO VILLA DEI FIORI | 02.153.384/0001-08 | R$ 25.592,71 | 02153384000108 | Large |
| 7 | CONDOMINIO DO EDIFICIO MICHELANGELO | 04.911.208/0001-13 | R$ 8.346,70 | 04911208000113 | Small |
| 8 | CONDOMINIO PARQUE RESIDENCIAL GELAIN | 00.736.037/0001-82 | R$ 6.000,00 | 00736037000182 | Small |
| 9 | CONDOMINIO RESIDENCIAL PARISE VILLAGE | 34.857.941/0001-68 | R$ 1.700,00 | 34857941000168 | Small |
| 10 | CONDOMINIO RESIDENCIAL GREEN HILLS | 08.063.476/0001-83 | R$ 500,00 | 08063476000183 | Small |

---

## CLIENTES SEM PIX ⚠️

| # | Nome | CNPJ | MRR | Observação |
|---|------|------|-----|------------|
| 1 | Conecta Mais - Segurança e Tecnologia | 00000000000000 | — | Registro interno (seed) |
| 2 | Matriz escritório | 00000000000000 | — | Registro interno (seed) |

> **Conclusão:** Os 2 registros sem PIX são entradas internas com CNPJ fictício (00000000000000) e sem MRR.
> **Todos os 10 clientes reais possuem chave PIX cadastrada** — cobertura 100%.

---

## DISTRIBUIÇÃO POR SEGMENTO

| Segmento | Qtd | MRR Total | % do MRR |
|----------|-----|-----------|----------|
| Enterprise | 1 | R$ 65.842,42 | 24,3% |
| Large | 5 | R$ 148.197,84 | 54,7% |
| Small | 4 | R$ 16.546,70 | 6,1% |
| Interno (sem MRR) | 2 | R$ 0,00 | 0% |
| **TOTAL** | **12** | **R$ 270.586,96** | **100%** |

---

## QUERY EXECUTADA

```sql
-- Clientes sem PIX
SELECT id, name, document_number AS cnpj, mrr, pix_key
FROM clients
WHERE status = 'active'
AND (pix_key IS NULL OR pix_key = '')
ORDER BY mrr DESC NULLS LAST;

-- Resumo por status de PIX
SELECT status,
  COUNT(*) AS total,
  COUNT(CASE WHEN pix_key IS NOT NULL AND pix_key != '' THEN 1 END) AS com_pix,
  COUNT(CASE WHEN pix_key IS NULL OR pix_key = '' THEN 1 END) AS sem_pix
FROM clients GROUP BY status;
```

> Nota: o campo `status` usa enum inglês (`'active'`), não `'ativo'`.

---

## DOWNLOAD
```bash
scp root@82.25.75.74:/opt/conecta-pro/RELATORIO_CLIENTES_PIX_20260412.md ~/Downloads/
```
