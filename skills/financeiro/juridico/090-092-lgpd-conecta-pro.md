---
name: lgpd-conecta-pro
description: Política de privacidade e checklist de conformidade LGPD para o Conecta PRO — plataforma ERP que processa dados de 52 funcionários CLT, 13 clientes condomínios, biometria de ponto, geolocalização de batidas e dados financeiros sensíveis. CNPJ 35.710.481/0001-03.
---

# LGPD — Conecta PRO (Skills 090 + 092 unificadas)

## Contexto crítico
O Conecta PRO processa dados especialmente sensíveis:
- **Biometria:** reconhecimento facial para ponto eletrônico (dado sensível LGPD art. 11)
- **Geolocalização:** coordenadas GPS de batidas de ponto (localização em tempo real)
- **Dados trabalhistas:** salários, benefícios, atestados, afastamentos de 52 funcionários
- **Dados de moradores:** acesso ao condomínio registrado via portaria
- **Dados bancários:** PIX de 46 funcionários, NFS-e de 13 clientes
- **Câmeras CFTV:** imagens de áreas comuns dos condomínios

## Prompt — Política de Privacidade Conecta PRO

```
Você é especialista em LGPD para plataformas SaaS B2B com dados trabalhistas e biométricos.

Crie a Política de Privacidade completa para:

**Controlador dos dados:** CONECTAMAIS ELETRONICA LTDA
CNPJ: 35.710.481/0001-03 | Manaus/AM
Plataforma: Conecta PRO (erp.conectamais.pro)
Encarregado (DPO): Jordan Santos de Jesus | jjesus@conectamais.pro

**Categorias de dados tratados:**

DADOS DOS FUNCIONÁRIOS (base legal: contrato de trabalho + obrigação legal):
- Identificação: nome, CPF, RG, data nascimento, endereço
- Trabalhistas: cargo, salário, benefícios, férias, FGTS, INSS
- Biométricos (SENSÍVEIS): foto facial para reconhecimento de ponto
- Localização: coordenadas GPS no momento da batida de ponto
- Saúde (SENSÍVEIS): atestados médicos, exames ocupacionais, ASO
- Bancários: chave PIX para pagamento de salário

DADOS DOS CLIENTES/CONDOMÍNIOS (base legal: contrato + legítimo interesse):
- Identificação: CNPJ, razão social, responsável, endereço
- Financeiros: NF-e recebidas, contratos, valores pagos
- Operacionais: escalas de portaria, ocorrências, relatórios

DADOS DE MORADORES (base legal: legítimo interesse de segurança):
- Registro de acesso: data/hora, veículo, acompanhantes
- Imagens: câmeras CFTV em áreas comuns (não em áreas privadas)

**Terceiros que recebem dados:**
- Banco Inter (077): processamento de PIX e boletos
- Portal NFS-e Nacional (governo): emissão de notas fiscais
- Google Drive: armazenamento de documentos de GED
- Portte Contábil / Domínio Sistemas: folha de pagamento
- Solides: gestão de admissões e cadastro de funcionários

**Retenção dos dados:**
- Trabalhistas: mínimo 5 anos após demissão (obrigação legal)
- Biométricos: enquanto ativo + 90 dias após desligamento
- Financeiros: 5 anos (Lucro Real + Receita Federal)
- Imagens CFTV: 30 dias (padrão segurança patrimonial)

Estruture a política com linguagem Clara e acessível cobrindo:
1. Quem somos e como contatar o DPO
2. Dados coletados por categoria (funcionários / clientes / moradores)
3. Base legal para cada categoria (LGPD art. 7 e 11)
4. Finalidade específica de cada dado
5. Dados biométricos — consentimento explícito + direito de revogação
6. Compartilhamento com terceiros
7. Transferência internacional (se aplicável)
8. Prazo de retenção
9. Direitos dos titulares (acesso, correção, exclusão, portabilidade)
10. Segurança (criptografia, acesso por perfil, logs de auditoria)
11. Cookies e sessões do ERP
12. Canal de exercício de direitos: privacidade@conectamais.pro
13. Vigência e atualizações
```

## Prompt — Checklist LGPD Conecta PRO

```
Crie um checklist executivo de conformidade LGPD para o Conecta PRO com:

**Empresa:** CONECTAMAIS ELETRONICA LTDA | CNPJ 35.710.481/0001-03
**Contexto:** ERP com dados biométricos, GPS e trabalhistas de 52 funcionários

Avalie e liste ações por categoria:

1. MAPEAMENTO DE DADOS
   [ ] Inventário de todos os dados pessoais tratados
   [ ] Base legal documentada para cada categoria
   [ ] Registro de operações de tratamento (ROPA)

2. CONSENTIMENTO BIOMÉTRICO
   [ ] Termo de consentimento específico para uso de biometria
   [ ] Canal para revogação do consentimento
   [ ] Alternativa ao biométrico (funcionário que não aceita)

3. SEGURANÇA TÉCNICA
   [ ] Dados em trânsito criptografados (HTTPS/TLS)
   [ ] Dados em repouso criptografados no PostgreSQL
   [ ] Controle de acesso por perfil (admin, gestor, funcionário)
   [ ] Logs de auditoria de acesso a dados sensíveis
   [ ] Backup seguro com retenção controlada

4. DIREITOS DOS TITULARES
   [ ] Canal para solicitações: privacidade@conectamais.pro
   [ ] Prazo de resposta: 15 dias úteis
   [ ] Processo documentado para exclusão de dados

5. TERCEIROS E CONTRATOS
   [ ] DPA (Data Processing Agreement) com Google Drive
   [ ] DPA com Banco Inter
   [ ] DPA com Portte Contábil / Solides

6. TREINAMENTO
   [ ] Time treinado sobre dados que pode e não pode acessar
   [ ] Política interna de uso dos dados do ERP

7. INCIDENTES
   [ ] Plano de resposta a incidentes documentado
   [ ] Prazo ANPD: 72h para notificação de vazamento grave

Prioridade: CRÍTICO | ALTO | MÉDIO | BAIXO
```
