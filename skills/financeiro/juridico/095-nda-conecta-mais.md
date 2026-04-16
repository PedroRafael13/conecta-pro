---
name: nda-conecta-mais
description: NDA (Acordo de Confidencialidade) da Conecta Mais para três cenários reais — fornecedores com acesso ao Conecta PRO, parceiros de licitação (R$6,65M em editais) e prestadores de serviços técnicos. CNPJ 35.710.481/0001-03, Manaus/AM.
---

# NDA — Acordo de Confidencialidade (Skill 095)

## Contexto
A Conecta Mais possui informações altamente sensíveis:
- Rotinas de segurança de 13 condomínios (risco direto aos moradores)
- Código-fonte do Conecta PRO (sistema ERP proprietário em desenvolvimento)
- Dados financeiros e operacionais de R$270k MRR
- Estratégia para licitações públicas (R$6,65M em editais monitorados)
- Dados pessoais de 52 funcionários e seus dependentes

## Três modelos de NDA

### Modelo 1 — Fornecedor com acesso ao Conecta PRO
Para: empresas de TI, consultores, desenvolvedores freelancers

```
Partes:
- Divulgadora: JORDAN SANTOS DE JESUS LTDA (CNPJ 35.710.481/0001-03)
- Receptora: [nome/CNPJ do fornecedor]

Informações confidenciais (específicas):
- Código-fonte do Conecta PRO e arquitetura do sistema
- Credenciais de acesso ao VPS e banco de dados
- Dados de funcionários e clientes no ERP
- Chaves de API do Banco Inter e certificados digitais
- Estratégia de produto e roadmap

Obrigações:
- Não acessar além do necessário para o serviço contratado
- Não copiar, exportar ou fazer backup sem autorização
- Reportar qualquer incidente de segurança em até 2 horas
- Destruir cópias ao término do contrato (certificado de destruição)

Prazo de confidencialidade: 5 anos após término do contrato
Multa por violação: R$50.000 + danos
Foro: Manaus/AM
```

### Modelo 2 — Parceiro de Licitação
Para: empresas parceiras em consórcios para editais públicos

```
Informações confidenciais:
- Estratégia de precificação para o edital específico
- Composição de custos e margens
- Subcontratados e estrutura operacional

Prazo: Durante a licitação + 2 anos após resultado
Multa: 20% do valor do edital ou R$100.000 (o que for maior)
```

### Modelo 3 — Prestador de Serviços no Condomínio
Para: técnicos, prestadores com acesso às instalações dos clientes

```
Informações confidenciais:
- Rotinas e horários de segurança do condomínio
- Vulnerabilidades identificadas no sistema
- Dados pessoais de moradores e funcionários
- Localização de câmeras e pontos cegos

Prazo: Indeterminado (enquanto as informações forem relevantes)
Multa: R$30.000 por violação + responsabilidade civil e criminal
```

## O Prompt

```
Você é especialista em NDAs para empresas de segurança patrimonial e tecnologia.

Gere o NDA para:
**Modelo:** [1 — Fornecedor TI / 2 — Parceiro Licitação / 3 — Prestador Condomínio]
**Divulgadora:** JORDAN SANTOS DE JESUS LTDA | CNPJ: 35.710.481/0001-03
**Receptora:** [nome, CNPJ, representante]
**Contexto:** [descrever o que será compartilhado]
**Prazo do projeto/relação:** [duração]

Use linguagem técnica e precisa, cláusulas executáveis no Brasil,
foro em Manaus/AM, referência ao Marco Civil da Internet quando aplicável.
```
