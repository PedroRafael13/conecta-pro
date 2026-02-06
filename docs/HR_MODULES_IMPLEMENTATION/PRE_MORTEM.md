# PRE-MORTEM: 8 MÓDULOS DE RH AVANÇADO

**Data:** 23/01/2026
**Projeto:** Conecta PRO - Domínio Total RH
**Objetivo:** Superar Solides em TODAS as funcionalidades

---

## RESUMO EXECUTIVO

Este documento analisa os riscos críticos, pontos de falha e mitigações para a implementação dos 8 módulos de RH que faltam para superar completamente o Solides:

1. **Clima** - Pesquisa de Clima Organizacional
2. **DISC** - Avaliação Comportamental (Profiler)
3. **360°** - Avaliação de Desempenho
4. **Nine Box** - Matriz de Talentos
5. **PDI** - Plano de Desenvolvimento Individual
6. **Sucessão** - Plano de Sucessão
7. **Recrutamento** - ATS Avançado com IA
8. **Onboarding** - Integração Estruturada

---

## CENÁRIO DE FALHA IMAGINADO

> **É janeiro de 2027. O projeto falhou. O que aconteceu?**

### Causas Prováveis de Falha

#### 1. COMPLEXIDADE SUBESTIMADA
- Avaliação DISC requer validação científica
- Avaliação 360° tem workflow complexo com múltiplos avaliadores
- Nine Box precisa de dados históricos para ser útil
- Integração entre módulos foi negligenciada

#### 2. FALTA DE DADOS DE TREINAMENTO PARA IA
- Modelos de análise de sentimento sem dados em português
- IA comportamental sem dataset validado
- Predição de turnover sem histórico suficiente

#### 3. UX/UI COMPLEXA DEMAIS
- Gestores não adotaram por ser complicado
- Tempo de preenchimento de avaliações muito alto
- Dashboards confusos para RH

#### 4. RESISTÊNCIA ORGANIZACIONAL
- Funcionários desconfiados com testes comportamentais
- Gestores não dando feedback no prazo
- Cultura de "apenas cumprir obrigação"

#### 5. INTEGRAÇÃO FALHA COM MÓDULOS EXISTENTES
- Dados de funcionários duplicados
- Histórico não sincronizado
- Performance degradada do sistema

---

## ANÁLISE DE RISCOS POR MÓDULO

### MÓDULO 1: CLIMA (Pesquisa Organizacional)

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Baixa taxa de resposta | Alta | Alto | Gamificação + anonimato garantido |
| Respostas enviesadas | Média | Médio | IA detecta padrões suspeitos |
| Análise superficial | Média | Alto | NLP avançado para respostas abertas |
| Falta de ação pós-pesquisa | Alta | Crítico | Plano de ação automático com IA |
| Benchmark inexistente | Média | Médio | Criar base com dados anônimos multi-tenant |

**Dependências Críticas:**
- Módulo de funcionários (base de dados)
- Sistema de notificações (push, email, SMS)
- IA de análise de sentimento

---

### MÓDULO 2: DISC (Avaliação Comportamental)

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Questionário não validado cientificamente | Alta | Crítico | Parceria com psicólogos ou usar metodologia aberta |
| Resultados imprecisos | Média | Alto | Validação cruzada com outros dados |
| Uso inadequado (rotulação) | Alta | Alto | Educação de gestores + alertas de uso |
| Dependência do Solides | Média | Médio | Desenvolver metodologia própria |
| Tempo de teste muito longo | Média | Médio | Versão adaptativa com IA |

**Dependências Críticas:**
- Motor de questionários dinâmicos
- Algoritmo de classificação DISC
- Gerador de relatórios PDF

---

### MÓDULO 3: AVALIAÇÃO 360°

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Avaliadores não respondem | Alta | Crítico | Lembretes automáticos + gamificação |
| Avaliações políticas/enviesadas | Média | Alto | Detecção de outliers por IA |
| Calibração inconsistente | Alta | Alto | Algoritmo de normalização |
| Workflow complexo demais | Média | Médio | UX simplificada por persona |
| Feedback não construtivo | Média | Médio | IA sugere melhorias no texto |

**Dependências Críticas:**
- Engine de workflows
- Hierarquia organizacional
- Competências por cargo
- Sistema de notificações

---

### MÓDULO 4: NINE BOX

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Dados insuficientes para plotar | Alta | Crítico | Integração com 360° e metas |
| Classificação subjetiva | Média | Alto | Métricas objetivas combinadas |
| Resistência dos gestores | Média | Médio | Treinamento + simplicidade |
| Estagnação do quadro | Baixa | Médio | Histórico e tendências |

**Dependências Críticas:**
- Módulo de Avaliação 360°
- Módulo de Metas/OKRs
- Dados históricos de performance

---

### MÓDULO 5: PDI (Plano de Desenvolvimento)

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| PDIs não executados | Alta | Crítico | Lembretes + micro-metas |
| Metas genéricas | Alta | Alto | IA sugere metas SMART personalizadas |
| Sem acompanhamento | Média | Alto | Check-ins automáticos |
| Recursos de desenvolvimento limitados | Média | Médio | Integração com LMS/cursos |

**Dependências Críticas:**
- Avaliação de desempenho
- Competências por cargo
- Catálogo de cursos/ações

---

### MÓDULO 6: SUCESSÃO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Dados de potencial inexistentes | Alta | Crítico | Derivar de Nine Box + PDI |
| Resistência política | Alta | Alto | Visibilidade configurável |
| Planos não atualizados | Média | Médio | Revisão periódica automática |
| Candidatos saem antes | Média | Alto | Alertas de risco de turnover |

**Dependências Críticas:**
- Nine Box
- Risco de turnover (retention module)
- Competências e gaps

---

### MÓDULO 7: RECRUTAMENTO AVANÇADO

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Parser de CV impreciso | Alta | Alto | Múltiplos modelos + validação humana |
| Integração LinkedIn falha | Média | Médio | Fallback manual + Indeed |
| Viés algorítmico | Alta | Crítico | Auditoria de fairness + explainability |
| Candidatos duplicados | Média | Médio | Matching inteligente |
| Pipeline abandonado | Média | Médio | Automação de follow-up |

**Dependências Críticas:**
- OCR/NLP para currículos
- APIs externas (LinkedIn, Indeed)
- Sistema de emails transacionais
- Portal público (careers page)

---

### MÓDULO 8: ONBOARDING

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Checklists não seguidos | Alta | Alto | Gamificação + lembretes |
| Documentos não assinados | Média | Crítico | Assinatura digital integrada |
| Experiência fria/burocrática | Média | Alto | Portal interativo + buddy system |
| Pesquisa 30/60/90 ignorada | Alta | Médio | Automação + incentivos |

**Dependências Críticas:**
- GED (documentos)
- Assinatura digital
- Sistema de notificações
- Treinamentos (LMS)

---

## MATRIZ DE PRIORIZAÇÃO

| Módulo | Esforço | Impacto | Dependências | Prioridade |
|--------|---------|---------|--------------|------------|
| Clima | Médio | Alto | Baixas | **1º** |
| DISC | Médio | Alto | Baixas | **2º** |
| 360° | Alto | Alto | Médias | **3º** |
| Nine Box | Baixo | Médio | Altas (360°) | **5º** |
| PDI | Médio | Alto | Médias (360°) | **4º** |
| Sucessão | Médio | Médio | Altas (Nine Box) | **7º** |
| Recrutamento | Alto | Alto | Baixas | **6º** |
| Onboarding | Médio | Médio | Baixas | **8º** |

---

## RISCOS TRANSVERSAIS

### 1. PERFORMANCE DO SISTEMA
- **Risco:** 8 novos módulos = queries complexas
- **Mitigação:**
  - Cache agressivo (Redis)
  - Processamento assíncrono (Celery)
  - Views materializadas no PostgreSQL
  - Índices otimizados

### 2. SEGURANÇA E LGPD
- **Risco:** Dados comportamentais são sensíveis
- **Mitigação:**
  - Criptografia em repouso
  - Logs de acesso
  - Consentimento explícito
  - Direito ao esquecimento

### 3. INTEGRAÇÃO COM IA
- **Risco:** Modelos de IA podem ser lentos ou imprecisos
- **Mitigação:**
  - Cache de predições
  - Fallback para regras
  - Retreinamento contínuo
  - Explicabilidade

### 4. ADOÇÃO PELO USUÁRIO
- **Risco:** Módulos avançados requerem mudança cultural
- **Mitigação:**
  - Onboarding progressivo
  - Gamificação
  - Métricas de uso
  - Treinamento in-app

---

## PLANO DE CONTINGÊNCIA

### Se o DISC não funcionar:
1. Manter integração com Solides RH como fallback
2. Usar metodologia Big Five (aberta)
3. Contratar consultoria de psicologia organizacional

### Se o 360° tiver baixa adesão:
1. Simplificar para avaliação 180° (gestor + auto)
2. Reduzir número de competências
3. Implementar avaliação contínua vs ciclo anual

### Se a IA de CV falhar:
1. Interface de correção manual
2. Crowdsourcing de validação
3. Parceria com serviço especializado

---

## MÉTRICAS DE SUCESSO

| Módulo | Métrica Chave | Meta |
|--------|--------------|------|
| Clima | Taxa de resposta | > 80% |
| DISC | Precisão do perfil | > 85% |
| 360° | Ciclos completados no prazo | > 90% |
| Nine Box | Cobertura de funcionários | > 95% |
| PDI | Taxa de conclusão de ações | > 70% |
| Sucessão | Posições-chave com backup | > 80% |
| Recrutamento | Time-to-hire | < 30 dias |
| Onboarding | NPS do novo funcionário | > 70 |

---

## CONCLUSÃO

A implementação dos 8 módulos é **viável**, mas requer:

1. **Ordem correta de implementação** (Clima → DISC → 360° → PDI → Nine Box → Recrutamento → Sucessão → Onboarding)

2. **IA como diferencial** (não como feature secundária)

3. **UX excepcional** (simplicidade > completude)

4. **Dados de qualidade** (garbage in = garbage out)

5. **Cultura de feedback** (tecnologia sozinha não resolve)

**Próximo passo:** Iniciar pelo módulo de Clima (menor risco, alto impacto, poucas dependências).

---

**Documento criado por:** Claude Opus 4.5
**Data:** 23/01/2026
**Versão:** 1.0
