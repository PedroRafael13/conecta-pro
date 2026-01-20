# PRE-MORTEM FASE 2 - ANALISE COMPLETA DE RISCOS
## ERP CONECTA MAIS - EVOLUCAO ESTRATEGICA

**Versao:** 2.0
**Data:** Janeiro 2026
**Metodologia:** Analise Preventiva de Falhas

---

## INTRODUCAO

O Pre-Mortem e uma tecnica onde imaginamos que o projeto FALHOU e analisamos retroativamente
as causas. Isso nos permite ANTECIPAR problemas e criar mitigacoes ANTES que ocorram.

**Premissa:** "E Janeiro de 2028. A Fase 2 fracassou. O que deu errado?"

---

## CATEGORIA 1: RISCOS TECNICOS

### 1.1 Complexidade do Sistema de Propostas (CPQ)
**Risco:** O motor de precificacao (CCT, impostos, margens) e extremamente complexo
**Probabilidade:** ALTA (70%)
**Impacto:** CRITICO

**Cenario de Falha:**
- Calculos de CCT/impostos incorretos
- Margens calculadas erradas (prejuizo em contratos)
- Sistema lento (timeout ao gerar proposta)
- Templates de proposta inconsistentes

**Mitigacoes:**
```
1. TESTES EXAUSTIVOS
   - Criar 50+ casos de teste com dados reais
   - Validar contra propostas ja feitas (Smart Torquato 2, etc)
   - Homologar com contador ANTES de produzir

2. DESENVOLVIMENTO INCREMENTAL
   - Sprint 14A: Estrutura basica (sem calculo complexo)
   - Sprint 14B: Pricing engine isolado
   - Sprint 14C: Integracao e validacao

3. FALLBACK
   - Sempre permitir override manual
   - Log detalhado de cada calculo
   - Auditoria de precos
```

### 1.2 Integracao Open Banking
**Risco:** APIs bancarias sao complexas e instruturas
**Probabilidade:** MEDIA (50%)
**Impacto:** ALTO

**Cenario de Falha:**
- API do banco muda sem aviso
- Autenticacao OAuth expira durante processamento
- Timeout em conciliacao de lote grande
- Dados bancarios sensiveis vazados

**Mitigacoes:**
```
1. ABSTRACOES
   - Criar camada de abstracacao (BankingAdapter)
   - Suportar multiplos bancos (BB, Itau, Bradesco)
   - Circuit breaker para falhas

2. SEGURANCA
   - Tokens em vault seguro (AWS Secrets Manager)
   - Criptografia em transito e repouso
   - Auditoria de acessos

3. RESILIENCIA
   - Fila de processamento (retry automatico)
   - Notificacao imediata de falhas
   - Modo degradado (manual se API falhar)
```

### 1.3 Performance do Sistema
**Risco:** Sistema fica lento com volume de dados
**Probabilidade:** MEDIA (40%)
**Impacto:** ALTO

**Cenario de Falha:**
- Dashboard CEO demora 30s para carregar
- Relatorios travam com 200+ colaboradores
- Mobile app nao funciona em 3G

**Mitigacoes:**
```
1. OTIMIZACAO DESDE O INICIO
   - Indices de banco de dados planejados
   - Queries otimizadas (N+1 prevenido)
   - Cache em camadas (Redis)

2. MONITORAMENTO
   - APM (Application Performance Monitoring)
   - Alertas de latencia > 2s
   - Profiling continuo

3. ESCALABILIDADE
   - Arquitetura stateless
   - Load balancer configurado
   - CDN para assets
```

### 1.4 Integracao eSocial/SPED
**Risco:** Obrigacoes legais complexas e mutaveis
**Probabilidade:** ALTA (60%)
**Impacto:** CRITICO (multas!)

**Cenario de Falha:**
- Evento eSocial rejeitado por formato errado
- Layout SPED desatualizado
- Prazo perdido (multa de ate R$ 50k)

**Mitigacoes:**
```
1. ATUALIZACAO CONSTANTE
   - Monitorar portal eSocial para mudancas
   - Testes com ambiente de homologacao
   - Parceria com contador especializado

2. VALIDACAO PRE-ENVIO
   - Validador offline antes de enviar
   - Checklist de campos obrigatorios
   - Alerta 5 dias antes do prazo

3. CONTINGENCIA
   - Envio manual sempre disponivel
   - Documentacao de procedimentos
   - Contato direto com suporte eSocial
```

---

## CATEGORIA 2: RISCOS DE PROCESSO

### 2.1 Scope Creep (Escopo Infinito)
**Risco:** Cada sprint ganha features "extras" nao planejadas
**Probabilidade:** MUITO ALTA (80%)
**Impacto:** ALTO

**Cenario de Falha:**
- Sprint 14 de 2 semanas vira 2 meses
- Features "simples" viram monstros
- Equipe desmotivada por nunca terminar

**Mitigacoes:**
```
1. DEFINICAO RIGIDA DE ESCOPO
   - User stories escritas ANTES do sprint
   - Definition of Done clara
   - NENHUMA feature extra sem aprovacao

2. TIMEBOXING
   - Sprint = 2 semanas MAX
   - Se nao cabe, divide em 2 sprints
   - Deploy incremental (mesmo incompleto)

3. BACKLOG DISCIPLINADO
   - Feature nova? Vai pro backlog
   - Priorizar por ROI
   - "Nao agora" e uma resposta valida
```

### 2.2 Debito Tecnico Acumulado
**Risco:** Pressao por velocidade gera codigo ruim
**Probabilidade:** ALTA (65%)
**Impacto:** ALTO (longo prazo)

**Cenario de Falha:**
- Codigo espaguete impossivel de manter
- Testes faltando (bugs em producao)
- Refatoracao massiva necessaria

**Mitigacoes:**
```
1. REGRA DE OURO INEGOCIAVEL
   - Pylint 100/100 SEMPRE
   - Sem excecoes, sem "depois eu arrumo"
   - Code review obrigatorio

2. TESTES PRIMEIRO
   - TDD quando possivel
   - Cobertura minima 85%
   - Testes de integracao para fluxos criticos

3. REFATORACAO CONTINUA
   - 20% do tempo de cada sprint = refactor
   - Nunca copiar/colar codigo
   - DRY (Don't Repeat Yourself)
```

### 2.3 Falta de Documentacao
**Risco:** So o desenvolvedor original entende o codigo
**Probabilidade:** ALTA (70%)
**Impacto:** MEDIO

**Cenario de Falha:**
- Desenvolvedor sai, conhecimento perdido
- Manutencao impossivel
- Novos devs levam meses para entender

**Mitigacoes:**
```
1. DOCUMENTACAO COMO CODIGO
   - Docstrings em TODAS as funcoes
   - README.md em cada modulo
   - Diagramas atualizados

2. CONHECIMENTO COMPARTILHADO
   - Pair programming regular
   - Code review com explicacoes
   - Wiki tecnica atualizada

3. ONBOARDING DOCUMENTADO
   - Guia "como contribuir"
   - Videos de walkthrough
   - Arquitetura documentada
```

---

## CATEGORIA 3: RISCOS ORGANIZACIONAIS

### 3.1 Resistencia a Mudanca
**Risco:** Usuarios resistem ao novo sistema
**Probabilidade:** ALTA (60%)
**Impacto:** ALTO

**Cenario de Falha:**
- Vendedores continuam usando Excel
- Financeiro ignora sistema novo
- Adocao < 50%

**Mitigacoes:**
```
1. ENVOLVIMENTO DESDE O INICIO
   - Usuarios participam do design
   - Feedback incorporado rapidamente
   - "Campeoes" em cada area

2. TREINAMENTO ADEQUADO
   - Videos curtos (5min max)
   - Documentacao passo-a-passo
   - Suporte dedicado nas primeiras semanas

3. QUICK WINS
   - Mostrar valor RAPIDO
   - Primeiro sprint = dor mais urgente
   - Celebrar cada vitoria
```

### 3.2 Falta de Patrocinio Executivo
**Risco:** Jordan fica ocupado, projeto perde prioridade
**Probabilidade:** MEDIA (40%)
**Impacto:** CRITICO

**Cenario de Falha:**
- Decisoes demoram semanas
- Recursos realocados para "urgencias"
- Projeto vira "projeto secundario"

**Mitigacoes:**
```
1. GOVERNANCA CLARA
   - Reuniao semanal de status (30min max)
   - Dashboard de progresso visivel
   - Decisoes documentadas

2. ROI VISIVEL
   - Metricas de valor a cada sprint
   - "Economizamos X horas esta semana"
   - Business case atualizado

3. COMPROMISSO FORMAL
   - Roadmap aprovado por escrito
   - Recursos alocados no orcamento
   - Metas atreladas a bonificacao
```

### 3.3 Dependencia de Pessoas-Chave
**Risco:** Uma pessoa sabe tudo, outros nao
**Probabilidade:** ALTA (70%)
**Impacto:** ALTO

**Cenario de Falha:**
- Dev principal fica doente/sai
- Projeto para completamente
- Conhecimento perdido

**Mitigacoes:**
```
1. BUS FACTOR > 1
   - Pelo menos 2 pessoas em cada area
   - Rotacao de responsabilidades
   - Documentacao obsessiva

2. CROSS-TRAINING
   - Devs fazem pareamento rotativo
   - Todos conhecem arquitetura geral
   - Ninguem e "dono" de codigo

3. CONTINGENCIA
   - Processo de onboarding documentado
   - Contatos de freelancers de backup
   - Codigo legivel por qualquer dev
```

---

## CATEGORIA 4: RISCOS DE INFRAESTRUTURA

### 4.1 Falha de Servidor/Cloud
**Risco:** Sistema fica fora do ar
**Probabilidade:** BAIXA (20%)
**Impacto:** CRITICO

**Cenario de Falha:**
- AWS/VPS cai em horario critico
- Dados perdidos por falha de backup
- Restauracao demora dias

**Mitigacoes:**
```
1. ALTA DISPONIBILIDADE
   - Servidor redundante (failover)
   - Load balancer
   - Multi-AZ se possivel

2. BACKUP ROBUSTO
   - Backup diario automatico
   - Testado mensalmente (restore real)
   - Armazenamento offsite (S3)

3. DISASTER RECOVERY
   - RTO: 4 horas maximo
   - RPO: 24 horas maximo
   - Runbook documentado
```

### 4.2 Seguranca / Vazamento de Dados
**Risco:** Dados sensiveis vazam (LGPD!)
**Probabilidade:** MEDIA (35%)
**Impacto:** CRITICO (multas + reputacao)

**Cenario de Falha:**
- CPFs/salarios expostos
- Credenciais bancarias roubadas
- Multa ANPD de 2% faturamento

**Mitigacoes:**
```
1. SEGURANCA EM CAMADAS
   - WAF (Web Application Firewall)
   - Criptografia em repouso (AES-256)
   - Criptografia em transito (TLS 1.3)

2. ACESSO MINIMO
   - RBAC rigoroso
   - 2FA obrigatorio para admins
   - Logs de acesso completos

3. PENTESTING
   - Teste de penetracao trimestral
   - Bug bounty (se escalar)
   - Auditoria de codigo
```

### 4.3 Dependencia de Terceiros
**Risco:** API externa falha/muda/fecha
**Probabilidade:** MEDIA (45%)
**Impacto:** ALTO

**Cenario de Falha:**
- WhatsApp Business API muda politica
- DocuSign aumenta preco 500%
- Receita Federal API instavel

**Mitigacoes:**
```
1. ABSTRACOES
   - Interface para cada servico externo
   - Facil trocar provider
   - Multiplos fornecedores quando possivel

2. FALLBACKS
   - WhatsApp: SMS como backup
   - DocuSign: Clicksign como alternativa
   - RF: Cache de consultas

3. CONTRATOS
   - SLA documentado com fornecedores
   - Plano B para cada integracao critica
   - Reserva financeira para mudancas
```

---

## CATEGORIA 5: RISCOS DE SEGURANCA E COMPLIANCE

### 5.1 Nao Conformidade LGPD
**Risco:** Tratamento inadequado de dados pessoais
**Probabilidade:** ALTA (55%)
**Impacto:** CRITICO

**Cenario de Falha:**
- Consentimento nao coletado corretamente
- Dados retidos alem do necessario
- Solicitacao de titular nao atendida

**Mitigacoes:**
```
1. LGPD BY DESIGN
   - Privacidade desde o design
   - Consentimento explicito rastreavel
   - Retencao com prazos definidos

2. DPO DESIGNADO
   - Responsavel formal pela LGPD
   - Treinamento equipe
   - Canais de atendimento titular

3. AUDITORIA
   - Inventario de dados pessoais
   - DPIA para novos tratamentos
   - Relatorio anual de conformidade
```

### 5.2 Fraude Interna
**Risco:** Colaborador manipula dados/pagamentos
**Probabilidade:** BAIXA (15%)
**Impacto:** ALTO

**Cenario de Falha:**
- Pagamento desviado para conta falsa
- Comissao calculada fraudulentamente
- Dados de cliente vendidos

**Mitigacoes:**
```
1. SEGREGACAO DE FUNCOES
   - Quem cadastra nao aprova
   - Quem aprova nao paga
   - Limites de alcada

2. AUDIT TRAIL
   - Log imutavel de TODAS as acoes
   - Quem, quando, o que, de onde
   - Alertas de anomalias

3. RECONCILIACAO
   - Conferencia diaria automatica
   - Relatorios de excecao
   - Auditoria externa anual
```

---

## MATRIZ DE RISCOS CONSOLIDADA

| ID | Risco | Prob | Impacto | Score | Prioridade |
|----|-------|------|---------|-------|------------|
| T1 | CPQ Complexo | 70% | CRITICO | 9.8 | MAXIMA |
| T4 | eSocial/SPED | 60% | CRITICO | 8.4 | MAXIMA |
| P1 | Scope Creep | 80% | ALTO | 8.0 | ALTA |
| P2 | Debito Tecnico | 65% | ALTO | 6.5 | ALTA |
| O1 | Resistencia | 60% | ALTO | 6.0 | ALTA |
| S1 | LGPD | 55% | CRITICO | 7.7 | ALTA |
| T2 | Open Banking | 50% | ALTO | 5.0 | MEDIA |
| O3 | Pessoa-Chave | 70% | ALTO | 7.0 | MEDIA |
| I2 | Vazamento | 35% | CRITICO | 4.9 | MEDIA |
| T3 | Performance | 40% | ALTO | 4.0 | MEDIA |
| I1 | Falha Server | 20% | CRITICO | 2.8 | BAIXA |
| S2 | Fraude | 15% | ALTO | 1.5 | BAIXA |

---

## PLANO DE CONTINGENCIA

### Se Sprint Atrasar > 1 Semana
```
1. Reuniao de crise imediata
2. Identificar bloqueio
3. Simplificar escopo ou dividir sprint
4. Nunca comprometer qualidade (100/100)
```

### Se Sistema Cair em Producao
```
1. Notificar usuarios imediatamente
2. Ativar modo manual (planilhas backup)
3. Investigar causa raiz
4. Post-mortem em 24h
```

### Se Dados Vazarem
```
1. Conter vazamento (isolar sistema)
2. Notificar DPO/Jordan em 1h
3. Avaliar impacto e titulares afetados
4. Notificar ANPD em 72h se aplicavel
5. Comunicar titulares afetados
```

### Se Dev Principal Sair
```
1. Documentacao deve estar completa
2. Segundo dev assume imediatamente
3. Knowledge transfer intensivo
4. Contratar substituicao em 2 semanas
```

---

## CHECKLIST PRE-SPRINT

Antes de iniciar QUALQUER sprint:

- [ ] Riscos revisados e mitigacoes ativas
- [ ] Escopo FECHADO e documentado
- [ ] Recursos alocados e disponiveis
- [ ] Ambiente de desenvolvimento pronto
- [ ] Testes automatizados funcionando
- [ ] Backup verificado nas ultimas 24h
- [ ] Comunicacao com stakeholders feita

---

## REVISAO DO PRE-MORTEM

Este documento deve ser revisado:
- [ ] Antes de cada sprint (checklist)
- [ ] Mensalmente (riscos atualizados)
- [ ] Apos cada incidente (licoes aprendidas)
- [ ] Trimestralmente (revisao completa)

---

*Pre-Mortem Fase 2 - ERP Conecta Mais*
*"Antecipar e prevenir, nunca remediar"*
