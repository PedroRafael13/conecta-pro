---
name: contrato-prestacao-servicos-conecta-mais
description: Gerar contrato de prestação de serviços da Conecta Mais para condomínios — mão de obra de portaria, portaria remota, manutenção CFTV ou facilities. Cláusulas adaptadas para o setor de segurança patrimonial em Manaus/AM, CCT SINDECOMPRESTS 2026, CNPJ 35.710.481/0001-03.
---

# Contrato de Prestação de Serviços — Conecta Mais

## Contexto da Empresa
- **Prestador:** CONECTAMAIS ELETRONICA LTDA | CNPJ 35.710.481/0001-03 | Manaus/AM
- **Regime Tributário:** Lucro Real (ISS 5%, PIS/COFINS 9,25%, CSLL 9%, IRPJ 15%)
- **CCT Aplicável:** SINDECOMPRESTS 2026 (agentes de portaria e facilities — NÃO vigilância armada)
- **Serviços oferecidos:** Portaria presencial, portaria remota, manutenção CFTV, facilities

## Quando usar
- Ao fechar novo cliente condomínio
- Para renovação anual de contratos existentes
- Quando cliente solicita formalização antes do início
- Para aditivos de escopo (novo posto, novo serviço)

## Tipos de contrato disponíveis

### Tipo A — Kit Mensal (Mão de Obra Presencial)
Fornecimento de agentes de portaria + facilities para o condomínio.
Inclui: seleção, admissão, folha, encargos, EPI, fardamento, exames.

### Tipo B — Portaria Remota
Monitoramento remoto via câmeras + interação por interfone/app.
Inclui: central de monitoramento 24h, protocolo de ocorrências, relatórios.

### Tipo C — Manutenção CFTV
Manutenção preventiva e corretiva de câmeras, gravadores, cabeamento.
Inclui: visita mensal, peças de reposição (até R$X), relatório técnico.

## O Prompt Adaptado

```
Você é especialista em contratos para empresas de facilities e serviços condominiais no AM.

IMPORTANTE: Para contratos acima de R$50.000/mês, recomenda-se revisão por advogado.

Gere o contrato de prestação de serviços com:

**Prestador:** CONECTAMAIS ELETRONICA LTDA
CNPJ: 35.710.481/0001-03
Endereço: [endereço completo Manaus/AM]
Responsável: Jordan Santos de Jesus

**Contratante (Condomínio):**
Nome: [nome do condomínio]
CNPJ: [CNPJ]
Endereço: [endereço]
Síndico/Responsável: [nome]

**Tipo de serviço:** [Kit Mensal / Portaria Remota / Manutenção CFTV / Misto]

**Escopo detalhado:**
- Número de postos: [X]
- Turnos: [diurno 12x36 / noturno 12x36 / 44h semanais]
- Serviços inclusos: [portaria, facilities, limpeza de área comum]
- Serviços NÃO inclusos: [vigilância armada — serviço não fornecido]

**Prazo:** [12 meses com renovação automática]
**Valor mensal:** R$[valor]
**Reajuste anual:** INPC ou CCT SINDECOMPRESTS (o que for maior)
**Pagamento:** Até dia [5/10/15] do mês seguinte à competência
**Multa por atraso:** 2% + 1% ao mês pro rata die

Estruture o contrato com cláusulas específicas para:
1. Identificação das partes
2. Objeto e escopo detalhado
3. Obrigações da Conecta Mais (seleção, admissão, folha, EPI, fardamento, exames)
4. Obrigações do contratante (espaço, alimentação se houver, documentação do condomínio)
5. Sigilo sobre rotinas de segurança do condomínio
6. Substituição de funcionários (prazo máximo 24h para posto crítico)
7. Ocorrências e responsabilidades (o que cobre e o que não cobre)
8. Valor, reajuste e condições de pagamento
9. Multa por rescisão antecipada (aviso prévio 30 dias ou multa equivalente a 1 mês)
10. Confidencialidade das informações do condomínio
11. LGPD — tratamento de dados de moradores, câmeras, biometria
12. Rescisão e encerramento
13. Foro: Manaus/AM
14. Assinaturas com testemunhas
```

## Integração com Conecta PRO
Após geração, o contrato pode ser:
- Salvo no GED como kit documental do cliente
- Vinculado ao cliente via CRM (clients.id)
- Enviado por email via SMTP noreply@conectamais.pro
- Armazenado no Google Drive do cliente
