# Conecta PRO vs Sólides - Análise Comparativa

## Visão Geral

Este documento apresenta uma análise comparativa entre as funcionalidades do Conecta PRO e da plataforma Sólides, destacando os ganhos obtidos com a integração e os diferenciais competitivos do Conecta PRO.

---

## Arquitetura da Integração

```
┌─────────────────────────────────────────────────────────────────┐
│                    SÓLIDES DP (Tangerino)                       │
│  • Ponto eletrônico básico                                      │
│  • Cadastro de funcionários                                     │
│  • Escalas manuais                                              │
│  • Controle de jornada                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Bidirecional
                              │ Webhooks Real-time
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CONECTA PRO                                │
│  • Sincronização automática de funcionários                     │
│  • Gestão completa de postos/clientes                          │
│  • Escalas com otimização por IA                               │
│  • Ponto avançado (geo + foto + biometria)                     │
│  • Substituições inteligentes                                   │
│  • Ocorrências com workflow e SLA                              │
│  • Medidas disciplinares com assinatura digital                │
│  • Comunicação multi-canal em tempo real                       │
│  • Previsões e alertas por Machine Learning                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## O que Ganhamos com a Integração

### Antes da Integração

| Processo | Como era feito |
|----------|----------------|
| Cadastro de funcionário | Manual em ambos sistemas |
| Admissão | Digitação dupla, risco de inconsistência |
| Demissão | Atualização manual, atrasos |
| Atualização de dados | Sincronização manual periódica |
| Cargos e funções | Manutenção separada |

### Depois da Integração

| Processo | Como é feito agora |
|----------|-------------------|
| Cadastro de funcionário | Único no Sólides, replica automático |
| Admissão | Webhook notifica Conecta PRO instantaneamente |
| Demissão | Sincronização em tempo real |
| Atualização de dados | Automática via sync incremental (15 min) |
| Cargos e funções | Importados e sincronizados do Sólides |

### Benefícios Quantificáveis

| Métrica | Impacto |
|---------|---------|
| Tempo de cadastro | -50% (elimina digitação dupla) |
| Erros de dados | -90% (fonte única de verdade) |
| Delay em demissões | De dias para minutos |
| Manutenção de cargos | Centralizada, sem duplicação |

---

## Funcionalidades Exclusivas do Conecta PRO

### 1. Gestão de Postos e Clientes

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Cadastro de postos/locais | ✅ Completo | ❌ Não tem |
| Geolocalização de postos | ✅ Com raio de cobertura | ❌ Não tem |
| Contratos por cliente | ✅ Integrado | ❌ Não tem |
| SLA por posto | ✅ Configurável | ❌ Não tem |
| Cobertura mínima | ✅ Automatizada | ❌ Não tem |

### 2. Escalas Inteligentes

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Geração de escalas | ✅ Automática com IA | ⚠️ Manual |
| Otimização de custos | ✅ Algoritmo considera distância, HE | ❌ Não tem |
| Preferências do funcionário | ✅ Turnos e locais preferidos | ❌ Não tem |
| Balanceamento de carga | ✅ Distribuição equitativa | ❌ Não tem |
| Conflitos automáticos | ✅ Detecta e sugere resolução | ❌ Não tem |

### 3. Ponto Avançado

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Registro de ponto | ✅ App mobile | ✅ App mobile |
| Geolocalização | ✅ GPS + Geofencing | ⚠️ GPS básico |
| Validação por foto | ✅ Reconhecimento facial | ⚠️ Foto simples |
| Biometria | ✅ Digital/facial | ⚠️ Limitado |
| Validação multi-fator | ✅ Geo + Foto + Bio | ❌ Não tem |
| Offline mode | ✅ Sincroniza depois | ⚠️ Limitado |
| Anti-fraude | ✅ Detecção de anomalias | ⚠️ Básico |

### 4. Substituições

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Registro de ausência | ✅ Com motivo e previsão | ⚠️ Básico |
| Sugestão de substitutos | ✅ IA ranqueia candidatos | ❌ Não tem |
| Critérios de seleção | ✅ Distância, custo, disponibilidade | ❌ Não tem |
| Aceite pelo funcionário | ✅ Notificação + confirmação | ❌ Não tem |
| Histórico de substituições | ✅ Completo | ❌ Não tem |

### 5. Ocorrências Operacionais

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Registro de ocorrências | ✅ Completo com anexos | ❌ API não expõe |
| Classificação automática | ✅ IA categoriza | ❌ Não tem |
| Workflow de resolução | ✅ Com escalação | ❌ Não tem |
| SLA configurável | ✅ Por categoria/prioridade | ❌ Não tem |
| Análise de padrões | ✅ IA detecta recorrências | ❌ Não tem |
| Vinculação a medidas | ✅ Gera advertências | ❌ Não tem |

### 6. Medidas Disciplinares

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Advertências | ✅ Workflow completo | ❌ Não tem |
| Suspensões | ✅ Com aprovação multi-nível | ❌ Não tem |
| Templates de documentos | ✅ Personalizáveis | ❌ Não tem |
| Assinatura digital | ✅ Com validade jurídica | ❌ Não tem |
| Recomendação por IA | ✅ Sugere medida proporcional | ❌ Não tem |
| Histórico disciplinar | ✅ Por funcionário | ❌ Não tem |
| Conformidade legal | ✅ Validação automática | ❌ Não tem |

### 7. Comunicação Operacional

| Funcionalidade | Conecta PRO | Sólides DP |
|----------------|-------------|------------|
| Comunicados | ✅ Com agendamento | ❌ Não tem |
| Confirmação de leitura | ✅ Rastreamento individual | ❌ Não tem |
| Push notifications | ✅ Firebase/OneSignal | ❌ Não tem |
| SMS | ✅ Integrado | ❌ Não tem |
| WhatsApp | ✅ API Evolution | ❌ Não tem |
| Email | ✅ Templates | ❌ Não tem |
| Alertas real-time | ✅ WebSocket | ❌ Não tem |
| Targeting por grupo | ✅ Departamento/cargo/posto | ❌ Não tem |

### 8. Relatórios Operacionais

| Relatório | Conecta PRO | Sólides DP |
|-----------|-------------|------------|
| Cobertura por posto | ✅ Com gaps e alertas | ❌ Não tem |
| Horas extras por cliente | ✅ Consolidado | ⚠️ Geral |
| Banco de horas detalhado | ✅ Por posto/cliente | ⚠️ Por funcionário |
| Estatísticas disciplinares | ✅ Com breakdown | ❌ Não tem |
| Custo operacional | ✅ Por cliente/posto | ❌ Não tem |
| Produtividade | ✅ Métricas customizáveis | ❌ Não tem |

---

## Diferenciais de Inteligência Artificial

O Conecta PRO possui módulo de IA operacional que o Sólides não oferece:

### Scale Optimizer (Otimizador de Escalas)

```
Entrada:
  - Lista de postos com requisitos
  - Funcionários disponíveis
  - Preferências e restrições

Processamento:
  - Algoritmo de otimização multi-objetivo
  - Minimiza custos (distância, HE)
  - Maximiza satisfação (preferências)
  - Respeita legislação trabalhista

Saída:
  - Escala otimizada
  - Score de qualidade
  - Alertas de conflitos
```

### Substitution Optimizer (Sugestão de Substitutos)

```
Entrada:
  - Posto descoberto
  - Data/horário necessário
  - Funcionários potenciais

Processamento:
  - Calcula distância geográfica
  - Avalia histórico de aceites
  - Estima custo adicional
  - Verifica disponibilidade

Saída:
  - Ranking de substitutos
  - Probabilidade de aceite
  - Custo estimado por opção
```

### Predictive Analyzer (Análise Preditiva)

```
Capacidades:
  - Previsão de faltas (3-7 dias antecedência)
  - Risco de turnover por funcionário
  - Previsão de horas extras
  - Detecção de anomalias
  - Alertas de concentração de overtime
```

### Occurrence Analyzer (Análise de Ocorrências)

```
Capacidades:
  - Classificação automática por conteúdo
  - Busca de ocorrências similares
  - Sugestão de ações corretivas
  - Avaliação de risco/gravidade
  - Estimativa de tempo de resolução
```

### Disciplinary Advisor (Consultor Disciplinar)

```
Capacidades:
  - Análise de histórico do funcionário
  - Recomendação de medida proporcional
  - Validação de conformidade legal
  - Sugestão de texto para documentos
```

---

## Matriz de Decisão

### Quando usar apenas Sólides DP

- Empresa com operação fixa (escritório)
- Sem necessidade de gestão de campo
- Ponto eletrônico básico suficiente
- Sem múltiplos clientes/postos

### Quando usar Conecta PRO + Sólides

- Empresas de segurança patrimonial
- Facilities e limpeza
- Portaria e recepção
- Vigilância
- Qualquer operação com equipes em campo
- Necessidade de escalas inteligentes
- Gestão de múltiplos clientes/contratos
- Compliance e auditoria rigorosos

---

## Resumo Competitivo

| Aspecto | Sólides DP | Conecta PRO | Vencedor |
|---------|------------|-------------|----------|
| Cadastro de RH | ✅ Bom | ✅ Sincronizado | Empate |
| Ponto básico | ✅ Bom | ✅ Avançado | Conecta PRO |
| Escalas | ⚠️ Manual | ✅ IA | **Conecta PRO** |
| Gestão de postos | ❌ | ✅ Completo | **Conecta PRO** |
| Substituições | ❌ | ✅ Inteligente | **Conecta PRO** |
| Ocorrências | ❌ | ✅ Com SLA | **Conecta PRO** |
| Disciplinar | ❌ | ✅ Workflow | **Conecta PRO** |
| Comunicação | ❌ | ✅ Multi-canal | **Conecta PRO** |
| IA/Automação | ❌ | ✅ Completo | **Conecta PRO** |
| Relatórios operacionais | ⚠️ Básico | ✅ Avançado | **Conecta PRO** |

---

## Conclusão

A integração Sólides + Conecta PRO oferece o **melhor dos dois mundos**:

1. **Sólides DP** cuida do cadastro centralizado de RH, folha de pagamento e controle básico de jornada

2. **Conecta PRO** adiciona toda a camada de **gestão operacional inteligente** que empresas de serviços em campo necessitam

O resultado é uma solução completa que:
- Elimina retrabalho de cadastro
- Mantém dados sincronizados
- Oferece gestão operacional de classe mundial
- Automatiza decisões com IA
- Reduz custos operacionais
- Aumenta compliance e auditabilidade

---

## Referências

- [Documentação Sólides DP](./backend/modules/integrations/connectors/solides/README.md)
- [Módulo Operacional](./backend/modules/operacional/)
- [API de Integração](./backend/modules/integrations/)

---

*Documento criado em Janeiro 2026*
*Versão: 1.0*
