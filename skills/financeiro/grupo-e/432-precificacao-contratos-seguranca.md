---
name: precificacao-contratos-seguranca-conecta-mais
description: Modelo de precificação de contratos de segurança patrimonial para a Conecta Mais — custo por posto, margem de contribuição, reajuste CCT e comparativo com mercado em Manaus/AM.
---

# Precificação de Contratos de Segurança (Skill 432 reescrita)

## Contexto específico
A Conecta Mais tem 6 dos 10 contratos subprecificados (dado do Conecta PRO).
A precificação correta em segurança patrimonial exige considerar
custo por posto de trabalho (escala 12x36 ou 44h), encargos da CCT-AM e margem real.

## O Prompt

```
Você é consultor de precificação para empresas de segurança patrimonial no Brasil.

Crie modelo de precificação para a Conecta Mais:
**Empresa:** JORDAN SANTOS DE JESUS LTDA | CNPJ 35.710.481/0001-03
**Regime:** Lucro Real | MRR R$270k | 52 funcionários | Manaus/AM
**CCT:** Sindicato dos Vigilantes do Amazonas
**Contratos ativos:** 13 clientes (condomínios residenciais)

ESTRUTURA DO MODELO:

1. Custo por posto (escala 12x36):
   - Salário base CCT vigente
   - Encargos: INSS (20%), FGTS (8%), férias (11,11%), 13º (8,33%), INSS s/ férias+13º
   - Uniformes, EPI, exames periódicos (rateio anual)
   - Supervisão e gestão (rateio % sobre custo direto)

2. Custo por posto (escala 44h/semana):
   - Mesma estrutura, com adicional noturno se aplicável
   - Horas extras previstas na CCT

3. Margem de contribuição por contrato:
   - Receita mensal do contrato
   - (-) Custo direto dos postos (qty × custo unitário)
   - (-) Custos variáveis: combustível, comunicação, transporte
   - (=) Margem de contribuição (R$ e %)
   - Benchmark: margem saudável para o setor (15-25%)

4. Diagnóstico dos 13 contratos:
   - Identificar quais estão com margem < 15% (subprecificados)
   - Calcular gap de receita para atingir margem mínima
   - Estratégia de reajuste sem romper contrato

5. Cláusula de reajuste automático para novos contratos:
   - Base: CCT + IPCA-E pro rata
   - Gatilho: anual ou quando CCT for homologada
   - Redação jurídica para o contrato de prestação de serviços

6. Comparativo com mercado Manaus:
   - Faixa de preço por posto praticada em Manaus (referência FENAVIST/SINDESEG-AM)
   - Posicionamento atual da Conecta Mais (abaixo/na média/acima)

Para cada seção: planilha em markdown com os valores reais atuais e projeção pós-reajuste.
```
