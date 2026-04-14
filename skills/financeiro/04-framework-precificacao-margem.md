---
name: framework-precificacao-margem
agent: PricingOptimizerAgent
prioridade: ALTA
versao: 2.0
dados_referencia: abril/2026
modulo: financial
mrr_bruto: 270586.96
saldo_inter: 36476.27
---

# Skill 04 — Framework de Precificacao e Margem
## Conecta Mais | CCT SINDECOMPRESTS 2026 | Mercado Manaus

### CCT SINDECOMPRESTS 2026 (01/01/2026 a 31/12/2026)

| Componente | Valor | Base de calculo |
|-----------|-------|-----------------|
| Piso salarial vigilante | R$1.847,93/mes | |
| INSS patronal (20%) | R$369,59 | sobre salario |
| FGTS (8%) | R$147,83 | sobre salario |
| FGTS rescisao (0,5% FGTS) | R$7,39 | provisionado |
| 13o salario (1/12) | R$153,99 | sobre salario |
| Ferias + 1/3 (1/12 x 1,333) | R$205,32 | |
| VR: 22 dias x R$26,40 | R$580,80 | fixo CCT |
| VT media Manaus | R$150,00 | estimado |
| Seguro de vida (CCT) | R$12,61 | obrigatorio |
| EPI e uniforme (media) | R$30,00 | provisionado |
| **CUSTO ALL-IN POR POSTO** | **R$3.505,46** | **por vigilante/mes** |

**Custo real medio extrato (jan-mar/2026):** R$160.357,03 / 52 = R$3.083,79/funcionario
- Diferenca de R$421,67 indica mix: parte dos 52 e administrativa (salario menor)
- Usar R$3.505,46 para vigilantes | R$2.200,00 para admin

### BENCHMARKS MANAUS — SEGURANCA PATRIMONIAL 2026

| Tipo de Servico | Mercado Min | Mercado Max | Conecta Mais atual | Status |
|-----------------|-------------|-------------|-------------------|--------|
| Vigilante diurno/posto | R$3.800 | R$5.500 | ~R$4.800 medio | OK |
| Vigilante noturno/posto | R$4.200 | R$6.000 | N/A | - |
| Portaria remota/condominio | R$1.200 | R$2.500 | R$6.000 (bundled) | Premium |
| Manutencao CFTV basico | R$600 | R$1.200 | R$850 medio | OK |
| Manutencao CFTV full | R$1.200 | R$2.500 | R$1.700 | OK |

### FORMULA DE PRECIFICACAO POR TIPO

**Kit Mensal CLT (por posto de vigilante):**
```
Custo_direto_posto = R$3.505,46
Overhead_rateado  = R$197.243,54 / 52 postos = R$3.793,14/posto
Custo_total_posto = R$3.505,46 + R$3.793,14 = R$7.298,60

Preco_Minimo = Custo_total / (1 - 0,1425) / (1 - 0,10)  # MC 10%
             = R$7.298,60 / 0,8575 / 0,90 = R$9.461/posto

Preco_Target = Custo_total / (1 - 0,1425) / (1 - 0,25)  # MC 25%
             = R$7.298,60 / 0,8575 / 0,75 = R$11.353/posto

Preco_atual_medio = R$262.386,96 / 44 postos est. = R$5.963/posto
```

**ATENCAO: Preco_atual << Preco_Minimo. Contratos subprecificados.**
Causa historica: pricing pre-CCT 2026 + sem reajuste anual adequado.

**Portaria Remota (por condominio):**
```
Custo_direto = R$3.270 (Econdos + operador)
Preco_Minimo = R$3.270 / 0,8575 / 0,90 = R$4.235/condominio
Preco_Target = R$3.270 / 0,8575 / 0,75 = R$5.082/condominio
Preco_atual (Gelain) = R$6.000 — ACIMA DO TARGET ✅

Capacidade de expansao: cada novo contrato de portaria remota
tem custo incremental ~R$500/mes (apenas operador), nao R$3.270.
Segundo contrato: MC sobe para ~55%.
```

**Manutencao CFTV (por contrato/mes):**
```
Custo_variavel_hora_tecnica = R$80/hora (CLT proporcional)
Custo_fixo_por_contrato = R$150/mes (deslocamento + overhead)
Horas_medias = 4h/mes por contrato
Custo_direto = R$150 + (4 x R$80) = R$470/mes

Preco_Minimo = R$470 / 0,8575 / 0,90 = R$608/mes
Preco_Target = R$470 / 0,8575 / 0,75 = R$730/mes
Preco_atual: Parise R$1.700 e Green Hills R$500

Green Hills ABAIXO do target — renegociar para R$800 minimo.
```

### REGRAS DE PRECIFICACAO CONECTA MAIS

1. **Clausula CCT obrigatoria:** Todo contrato Kit Mensal deve ter clausula de reajuste anual
   automatico em janeiro = variacao CCT SINDECOMPRESTS.

2. **Renovacao ago/2026:** Ideal momento para reajustar contratos assinados pre-CCT 2026.
   Meta: +8% sobre contratos com MC < 20% real.

3. **Minimo Green Hills:** R$500/mes e inviavel com custo real ~R$470 + overhead.
   Proposta: R$800/mes ou incluir em pacote com Parise Village.

4. **Novo contrato minimo:** Nunca assinar Kit Mensal abaixo de R$5.000/posto.
   Portaria remota: minimo R$4.500/condominio.

5. **Desconto maximo:** 5% apenas em contratos com volume > 3 unidades ou fidelidade > 24 meses.

6. **IRPJ/CSLL (Lucro Real):** Provisionar 15% IRPJ + 9% CSLL adicional sobre lucro estimado.
   Impacto: adicionar ~R$3.000-5.000/mes nas projecoes de custo.

### SIMULADOR DE REAJUSTE

```
Cenario: reajuste medio de 8% sobre todos os 7 contratos Kit Mensal em ago/2026

Impacto no MRR:
R$262.386,96 * 1,08 = R$283.377,92 (+R$20.990,96/mes)

Novo MRR total: R$270.586,96 - R$262.386,96 + R$283.377,92 = R$291.577,92
Novo break-even com tributos: R$291.577,92 * 0,1425 = R$41.549,85 deducoes
Novo MRR liquido: R$249.228,07 vs custo total R$220.047 = R$29.181 superavit

Churn assumido: 0% (nenhum cliente perdeu contrato nos ultimos 24 meses)
```

### CONSULTAS SQL

```sql
-- Contratos para analise de pricing
SELECT
    br.name,
    br.base_value as ticket_atual,
    round(br.base_value * 1.08, 2) as ticket_reajustado_8pct,
    round(br.base_value * 0.8575, 2) as receita_liquida_atual,
    round(br.base_value * 1.08 * 0.8575, 2) as receita_liquida_reajustada
FROM billing_rules br
WHERE status = 'ativa'
ORDER BY base_value DESC;

-- Verificar se contratos tem data de vencimento/renovacao
SELECT name, base_value, start_date, end_date, status
FROM billing_rules
WHERE status = 'ativa'
ORDER BY end_date NULLS LAST;
```
