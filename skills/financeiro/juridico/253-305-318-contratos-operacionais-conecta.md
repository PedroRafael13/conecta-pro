# SKILL 253+305+318 — Contratos Operacionais: OS Rápida, Padrão e Completo
**Versão:** 2026-01
**Empresa:** JORDAN SANTOS DE JESUS LTDA (Conecta Mais — Segurança e Tecnologia)
**CNPJ:** 35.710.481/0001-03 | Manaus/AM
**Aplicação:** Ordens de Serviço e Contratos para operações técnicas de campo

---

## Contexto Operacional Conecta Mais

- **Equipe de campo:** Técnicos CLT (regime CCT SINDECOMPRESTS 2026)
- **Equipamentos:** Intelbras, Hikvision, Dahua, TP-Link, Axis
- **Tipo de serviço:** Instalação, manutenção e suporte de sistemas de segurança eletrônica
- **Clientes:** 13 condomínios residenciais e empresariais em Manaus/AM
- **Sistema de gestão:** Conecta PRO ERP — módulo Operacional (OS, escalas, campo)

---

## SKILL 253 — OS Rápida (Chamado Corretivo Urgente)

**Quando usar:** Chamados de manutenção corretiva com prazo ≤ 4h, falha parcial ou total do sistema.

### Template OS Rápida

```
ORDEM DE SERVIÇO — CONECTA MAIS
OS Nº: [AUTO/ERP]          DATA: ___/___/2026    HORA ABERTURA: ___h___
TIPO: ☒ CORRETIVA URGENTE  PRIORIDADE: ☒ ALTA  ☐ MÉDIA  ☐ BAIXA

CLIENTE: _______________________________  CNPJ/CPF: __________________
ENDEREÇO: _____________________________________________________________
CONTATO: ________________________  TELEFONE: _________________________

PROBLEMA RELATADO:
__________________________________________________________________
__________________________________________________________________

TÉCNICO DESIGNADO: ______________________  MATRÍCULA: ______________
HORA CHEGADA: ___h___    HORA SAÍDA: ___h___    TOTAL: ___h___

SERVIÇO EXECUTADO:
__________________________________________________________________
__________________________________________________________________

PEÇAS/MATERIAIS UTILIZADOS:
Item  Qtd  Descrição                    Valor Unit.    Total
____  ___  ____________________________  R$_________  R$_______
____  ___  ____________________________  R$_________  R$_______

TOTAL PEÇAS: R$ _____________

PENDÊNCIAS (se houver): ____________________________________________

ASSINATURA TÉCNICO: _______________________  DATA: ___/___/2026
ASSINATURA CLIENTE: _______________________  CARGO: ______________

STATUS FINAL:  ☐ RESOLVIDO  ☐ PARCIAL (aguardando peça)  ☐ REABRIR
```

### Regras de uso da OS Rápida
1. Preencher no ERP antes de sair para o campo (número automático)
2. Foto obrigatória: equipamento com defeito (antes) + funcionando (depois)
3. SLA: técnico no local em 4h (urgente) / 24h (padrão)
4. Peças acima de R$ 200,00: aguardar aprovação do cliente antes de instalar
5. Fechar no ERP ao retornar (status + foto + assinatura digital do cliente)

---

## SKILL 305 — Contrato de Serviço Padrão

**Quando usar:** Novos contratos de serviço único ou eventual (instalação pontual, adequação, upgrade).
Não confundir com contratos recorrentes (Kit Mensal/Portaria Remota — usar Skill 089).

### Template Contrato Padrão

**CONTRATO DE PRESTAÇÃO DE SERVIÇOS AVULSOS Nº [___]/2026**

**CONTRATANTE:** [Razão Social], CNPJ [___], com sede em [Endereço], representado por [Nome], [Cargo], CPF [___].

**CONTRATADA:** JORDAN SANTOS DE JESUS LTDA, inscrita no CNPJ 35.710.481/0001-03, com sede em Manaus/AM, doravante denominada **Conecta Mais**.

**DATA:** ___/___/2026

---

**CLÁUSULA 1 — OBJETO**
A Contratada se obriga a executar os serviços de [DESCRIÇÃO DETALHADA DOS SERVIÇOS], nas dependências do Contratante, no endereço [ENDEREÇO DA PRESTAÇÃO].

**CLÁUSULA 2 — ESCOPO TÉCNICO**
Estão inclusos neste contrato:
- [ITEM 1 — ex: Instalação de 8 câmeras IP Hikvision 4MP]
- [ITEM 2 — ex: Configuração de NVR 8 canais]
- [ITEM 3 — ex: Treinamento de 1h para operador]

**NÃO estão inclusos:** Obras civis, cabeamento elétrico além de [___]m, licenças de software de terceiros.

**CLÁUSULA 3 — PRAZO DE EXECUÇÃO**
Os serviços serão executados em até [___] dias úteis a partir da confirmação de pagamento/sinal.

**CLÁUSULA 4 — VALOR E FORMA DE PAGAMENTO**
Valor total: R$ [___] ([por extenso])
Condições: [ex: 50% de entrada + 50% na entrega] / [PIX/Boleto/Transferência]
NFS-e emitida após cada parcela (ISS 5%, código 11.02, Manaus/AM)

**CLÁUSULA 5 — GARANTIA**
A Contratada garante os serviços pelo prazo de [90 dias] para mão de obra. Equipamentos possuem garantia de fábrica (Intelbras: 3 anos; Hikvision/Dahua: 2 anos).

**CLÁUSULA 6 — RESPONSABILIDADES DO CONTRATANTE**
- Fornecer acesso ao local nos horários combinados
- Disponibilizar energia elétrica e ponto de rede (quando aplicável)
- Providenciar autorização de condomínio se necessário

**CLÁUSULA 7 — RESCISÃO**
Rescisão pelo Contratante após início dos serviços: reembolso do sinal menos os custos já incorridos e 10% de taxa administrativa.

**CLÁUSULA 8 — LGPD**
Os dados do Contratante serão tratados conforme a Política de Privacidade da Conecta Mais (skill 090), disponível em [conectamais.pro/privacidade].

**CLÁUSULA 9 — FORO**
Comarca de Manaus/AM.

Manaus, ___/___/2026.

_______________________      _______________________
**CONTRATANTE**               **CONTRATADA — CONECTA MAIS**
[Nome/Cargo]                  Jordan Santos de Jesus — Sócio

_______________________      _______________________
Testemunha 1: [Nome/CPF]      Testemunha 2: [Nome/CPF]

---

## SKILL 318 — Contrato Operacional Completo

**Quando usar:** Projetos de maior porte: instalação de sistema completo (>16 câmeras), implantação de Portaria Remota, integração de sistemas, contratos com prefeitura ou empresas públicas.

### Estrutura do Contrato Completo

O Contrato Completo inclui todos os elementos do Padrão + os seguintes adicionais:

**CLÁUSULA ADICIONAL A — CRONOGRAMA E MILESTONES**
| Fase | Descrição | Prazo | Entrega |
|------|-----------|-------|---------|
| 1 | Projeto técnico e aprovação | D+5 | Planta layout câmeras |
| 2 | Fornecimento de materiais | D+10 | Nota fiscal equipamentos |
| 3 | Instalação física | D+20 | Fotos + laudo instalação |
| 4 | Configuração e testes | D+25 | Relatório de testes |
| 5 | Treinamento e aceite | D+30 | Termo de aceite assinado |

**CLÁUSULA ADICIONAL B — GESTÃO DE MUDANÇAS**
Qualquer alteração no escopo deve ser formalizada por **Aditivo Contratual** assinado por ambas as partes. Mudanças orais não geram obrigação.

**CLÁUSULA ADICIONAL C — EQUIPE TÉCNICA**
A Contratada designará responsável técnico ([NOME/CREA se aplicável]) para o projeto. Substituição por profissional de qualificação equivalente deve ser comunicada com 48h de antecedência.

**CLÁUSULA ADICIONAL D — ACEITE FORMAL (TERMO DE ENTREGA)**
Ao final de cada fase, o Contratante assina Termo de Aceite Parcial. O Aceite Final libera o pagamento da última parcela e inicia a garantia.

**Template Termo de Aceite:**
```
TERMO DE ACEITE — CONECTA MAIS
Contrato nº: ___   OS nº: ___   Data: ___/___/2026

Eu, [Nome], representante do [Condomínio/Empresa], declaro que os
serviços contratados foram executados conforme especificações acordadas
e que o sistema está funcionando adequadamente.

Observações: ____________________________________________

Assinatura: _________________________  Data: ___/___/2026
```

**CLÁUSULA ADICIONAL E — SEGURO**
Para contratos acima de R$ 50.000,00, a Contratada apresentará Apólice de Responsabilidade Civil Profissional (RCP) com cobertura mínima de R$ 100.000,00.

**CLÁUSULA ADICIONAL F — SIGILO E NDA**
As partes assinam NDA específico (Skill 095, Modelo C) quando o projeto envolver acesso a dados de moradores ou sistemas de segurança existentes.

**CLÁUSULA ADICIONAL G — LGPD — DPA (Data Processing Agreement)**
Em projetos com câmeras ou biometria, o Contrato Completo inclui obrigatoriamente o DPA como **Anexo III**, especificando:
- Dados tratados e finalidade
- Medidas de segurança adotadas
- Suboperadores autorizados
- Direitos dos titulares e prazo de resposta

---

## Quadro Resumo: Quando usar cada instrumento

| Situação | Instrumento | Skill |
|----------|------------|-------|
| Chamado corretivo urgente | OS Rápida | 253 |
| Manutenção preventiva programada | OS Rápida | 253 |
| Instalação pontual (até 8 câmeras) | Contrato Padrão | 305 |
| Upgrade ou adequação de sistema existente | Contrato Padrão | 305 |
| Projeto completo (>16 câmeras, Portaria Remota) | Contrato Completo | 318 |
| Contrato recorrente (mensalidade) | Contrato A/B/C | 089 |
| Compartilhar dados com prestador terceiro | NDA Modelo C | 095 |
| Qualquer câmera com face identificável | DPA + LGPD checklist | 090+092 |

---

## Referências e Normas

- ABNT NBR 5410:2004 (instalações elétricas de baixa tensão)
- ABNT NBR 16268:2014 (sistemas de alarme e CFTV)
- Lei 13.874/2019 (Liberdade Econômica — contratos)
- CCT SINDECOMPRESTS 2026 (jornada técnicos de campo)
- NFS-e Manaus: código 11.02, ISS 5%
