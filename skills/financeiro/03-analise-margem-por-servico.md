---
name: analise-margem-por-servico
agent: CostingAnalyzerAgent
prioridade: ALTA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
mrr_bruto: 270586.96
saldo_inter: 36476.27
---

# Skill 03 — Analise de Margem por Tipo de Servico
## Conecta Mais — Custeio ABC por Contrato | 10 Ativos

### PORTFOLIO REAL (billing_rules status='ativa' em 14/04/2026)

#### GRUPO 1: KIT MENSAL CLT (7 contratos | R$262.386,96 | 96,9% do MRR)

| Contrato | Ticket | Postos est. | Custo CLT | MC R$ | MC % | Status |
|----------|--------|-------------|-----------|-------|------|--------|
| Ideal Flores da Cidade | R$65.842,42 | 13 | R$44.921,00 | R$11.444,86 | 20,3% | ATENCAO |
| Laranjeiras Village | R$42.544,50 | 8 | R$27.643,68 | R$7.038,39 | 19,6% | ATENCAO |
| Mirante das Flores | R$42.255,80 | 8 | R$27.643,68 | R$6.749,69 | 19,0% | ATENCAO |
| Prime Arena | R$40.466,50 | 8 | R$27.643,68 | R$4.960,39 | 14,5% | RISCO |
| Villa dos Passaros | R$37.338,33 | 7 | R$24.188,22 | R$5.317,68 | 16,8% | RISCO |
| Villa Dei Fiori | R$25.592,71 | 5 | R$17.277,30 | R$3.938,74 | 18,2% | ATENCAO |
| Michelangelo | R$8.346,70 | 2 | R$6.910,92 | R$586,52 | 8,3% | DEFICITARIO |

**Nota custo CLT:** R$3.455,46/posto (CCT SINDECOMPRESTS 2026)
**Nota MC:** nao inclui ISS 5% + PIS/COFINS 9,25% sobre ticket (reduz ainda mais)

**MC real apos deducoes fiscais (14,25%):**

| Contrato | Ticket | Rec. Liquida | Custo CLT | MC Real | MC% Real |
|----------|--------|-------------|-----------|---------|---------|
| Ideal Flores | R$65.842,42 | R$56.453,80 | R$44.921,00 | R$11.532,80 | 17,5% |
| Laranjeiras | R$42.544,50 | R$36.483,38 | R$27.643,68 | R$8.839,70 | 20,8% |
| Mirante das Flores | R$42.255,80 | R$36.235,99 | R$27.643,68 | R$8.592,31 | 20,3% |
| Prime Arena | R$40.466,50 | R$34.700,01 | R$27.643,68 | R$7.056,33 | 17,4% |
| Villa dos Passaros | R$37.338,33 | R$32.022,67 | R$24.188,22 | R$7.834,45 | 21,0% |
| Villa Dei Fiori | R$25.592,71 | R$21.945,88 | R$17.277,30 | R$4.668,58 | 18,2% |
| Michelangelo | R$8.346,70 | R$7.157,37 | R$6.910,92 | R$246,45 | 2,9% |

**MICHELANGELO DEFICITARIO quando incluido overhead administrativo (~R$2.500/contrato).**

#### GRUPO 2: PORTARIA REMOTA (1 contrato | R$6.000 | 2,2% do MRR)

| Contrato | Ticket | Composicao | Custo Direto | MC R$ | MC % |
|----------|--------|------------|-------------|-------|------|
| Gelain | R$6.000,00 | R$5.200 portaria + R$800 infra | R$3.270,00 | R$2.730,00 | 45,5% |

**Custo direto Gelain:**
- Plataforma Econdos: ~R$1.770/mes (rateio)
- Operador parcial: ~R$1.500/mes (CLT reduzido)
- **Total: R$3.270/mes**

**MC real apos impostos:** R$6.000 * 0,8575 = R$5.145 - R$3.270 = R$1.875 (31,3%)
**ESTRELA do portfolio: menor esforco, melhor margem relativa**

#### GRUPO 3: MANUTENCAO CFTV (2 contratos | R$2.200 | 0,8% do MRR)

| Contrato | Ticket | Custo Variavel | MC R$ | MC % |
|----------|--------|---------------|-------|------|
| Parise Village | R$1.700,00 | ~R$595 (35%) | R$1.105,00 | 65,0% |
| Green Hills | R$500,00 | ~R$175 (35%) | R$325,00 | 65,0% |

**Composicao custo CFTV:** hora tecnica (R$80/h x 4h) + deslocamento + pecas (~R$200)
**MC real apos impostos:** Parise R$813,50 (47,9%) | Green Hills R$253,63 (50,7%)
**Volume pequeno mas margem excelente — escalar este servico**

### MATRIZ BCG ADAPTADA

```
ESTRELA (alta margem, potencial crescimento):
  Portaria Remota — Gelain: MC 31% real, modelo replicavel

VACA LEITEIRA (alta receita, margem apertada):
  Ideal Flores: R$65.842/mes, MC 17,5% — manter, reajustar anualmente
  Laranjeiras + Mirante: ~R$42k/mes — monitorar custo CCT

INTERROGACAO (baixo volume, boa margem):
  Manutencao CFTV: MC 47-50%, mas apenas R$2.200/mes — ampliar base

ABACAXI (margem critica, renegociar ou encerrar):
  Michelangelo: MC 2,9% — deficitario com overhead
  Prime Arena + Villa dos Passaros: MC 17% — renegociar reajuste ago/2026
```

### IMPACTO DO REAJUSTE CCT 2027

Assumindo reajuste CCT +6% em jan/2027 (historico SINDECOMPRESTS):
- Piso novo: R$1.847,93 * 1,06 = R$1.958,81
- Custo novo por posto: R$3.662,79 (+R$207,33/posto)
- Impacto total (52 funcionarios): +R$10.781,16/mes
- Margem Kit Mensal sem reajuste de preco: cai de 17-21% para 13-17%

**Acao necessaria:** Incluir clausula de reajuste anual CCT+2% nos contratos de renovacao (ago/set/2026).

### CONSULTAS SQL

```sql
-- MRR e margem estimada por contrato
SELECT
    br.name as contrato,
    br.base_value as ticket,
    round(br.base_value * 0.8575, 2) as receita_liquida_estimada,
    CASE
        WHEN br.name ILIKE '%Portaria Remota%' OR br.name ILIKE '%Seg. Eletr%'
            THEN 3270.00
        WHEN br.name ILIKE '%CFTV%'
            THEN round(br.base_value * 0.35, 2)
        ELSE round(3455.46 * GREATEST(round(br.base_value / 5037.72), 1), 2)
    END as custo_direto_estimado,
    round(br.base_value * 0.8575 - CASE
        WHEN br.name ILIKE '%Portaria Remota%' OR br.name ILIKE '%Seg. Eletr%'
            THEN 3270.00
        WHEN br.name ILIKE '%CFTV%'
            THEN round(br.base_value * 0.35, 2)
        ELSE round(3455.46 * GREATEST(round(br.base_value / 5037.72), 1), 2)
    END, 2) as mc_estimada
FROM billing_rules br
WHERE status = 'ativa'
ORDER BY br.base_value DESC;

-- Total MRR por tipo de servico
SELECT
    CASE
        WHEN name ILIKE '%Portaria Remota%' OR name ILIKE '%Seg. Eletr%' THEN 'portaria_remota'
        WHEN name ILIKE '%CFTV%' THEN 'manutencao_cftv'
        ELSE 'kit_mensal_clt'
    END as tipo,
    count(*) as contratos,
    round(sum(base_value)::numeric, 2) as mrr,
    round(sum(base_value) / (SELECT sum(base_value) FROM billing_rules WHERE status='ativa') * 100, 1) as pct_mrr
FROM billing_rules
WHERE status = 'ativa'
GROUP BY 1;
```
