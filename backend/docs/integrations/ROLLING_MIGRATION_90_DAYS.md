# Plano de Migração 90 Dias - Conecta PRO Integrações

**Estratégia:** Rodar em paralelo, sem big-bang, cutover gradual.

---

## VISÃO GERAL

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           TIMELINE 90 DIAS                              │
├─────────────────────────────────────────────────────────────────────────┤
│  MÊS 1 (Sem 1-4)      │  MÊS 2 (Sem 5-8)      │  MÊS 3 (Sem 9-12)     │
│  ─────────────────    │  ─────────────────    │  ─────────────────    │
│  READ-ONLY            │  DUAL-WRITE           │  CUTOVER              │
│  + Observabilidade    │  + Controlado         │  + Gradual            │
│  + Mapeamento         │  + Feature Flags      │  + Validação          │
│  + Zero impacto       │  + Aprovação humana   │  + Desligamento       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## MÊS 1: READ-ONLY + OBSERVABILIDADE + MAPEAMENTO

### Semana 1: Foundation

**Objetivo:** Framework base funcionando

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Models criados | Dev | Migration executa |
| 3-4 | Base connector | Dev | Testes passam |
| 5 | Endpoints REST | Dev | OpenAPI funcional |

**Métricas de sucesso:**
- [ ] Migration sem erros
- [ ] 100% cobertura nos models
- [ ] Endpoints respondendo

### Semana 2: Bling Discovery + Pull

**Objetivo:** Bling conectado em modo leitura

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1 | Discovery API Bling | Dev | Doc de endpoints |
| 2-3 | Connector Bling | Dev | Health OK |
| 4-5 | Pull de Produtos | Dev | Dados no banco |

**Métricas de sucesso:**
- [ ] Rate limit não atingido
- [ ] 100+ produtos sincronizados
- [ ] Zero duplicatas

### Semana 3: Sólides Discovery + Pull

**Objetivo:** Sólides conectado em modo leitura

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1 | OAuth2 configurado | Dev | Token obtido |
| 2-3 | Connector Sólides | Dev | Health OK |
| 4-5 | Pull de Colaboradores | Dev | Dados no banco |

**Métricas de sucesso:**
- [ ] Token refresh automático
- [ ] Colaboradores sincronizados
- [ ] LGPD compliance OK

### Semana 4: Dashboard + Comparação

**Objetivo:** Visibilidade completa do estado de sync

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Métricas Prometheus | Dev | Grafana funcionando |
| 3-4 | Relatório de divergências | Dev | Diff Conecta vs Externo |
| 5 | Documentação | Dev | README atualizado |

**Métricas de sucesso:**
- [ ] Dashboard mostrando métricas
- [ ] Divergências documentadas
- [ ] < 5% de inconsistências

**Entregáveis Mês 1:**
```
✓ Framework base funcionando
✓ Bling em pull mode (Produtos, Clientes)
✓ Sólides em pull mode (Colaboradores)
✓ Dashboard de observabilidade
✓ Relatório de mapeamento e divergências
✓ ZERO impacto em produção
```

---

## MÊS 2: BI-DIRECIONAL CONTROLADO + DUAL-WRITE

### Semana 5: Feature Flags + Dual-Write Bling

**Objetivo:** Escrever no Bling de forma controlada

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Sistema de feature flags | Dev | Flags funcionando |
| 3-4 | Dual-write Produtos | Dev | Criação no Bling |
| 5 | Validação | Ops | Dados corretos |

**Configuração:**
```python
FEATURE_FLAGS = {
    "bling_write_products": False,  # Ativar por tenant
    "bling_write_clients": False,
    "solides_write_employees": False,  # Sempre False no Mês 2
}
```

**Fluxo Dual-Write:**
```
1. Usuário cria Produto no Conecta PRO
2. Salva no banco local
3. SE flag ativa E tenant habilitado:
   4. Enfileira para sync
   5. Envia para Bling
   6. Atualiza ID Map
7. Log de auditoria
```

### Semana 6: Bling Write Controlado

**Objetivo:** 2-3 tenants piloto com write no Bling

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Seleção de tenants piloto | PM | Lista aprovada |
| 3-4 | Ativação controlada | Dev | Flags ativas |
| 5 | Monitoramento | Ops | Sem erros |

**Critérios para piloto:**
- Tenant de baixo volume
- Stakeholder disponível
- Ambiente de teste similar

### Semana 7: Domínio Discovery + Decisão

**Objetivo:** Definir caminho para integração contábil

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Resultado contato comercial | PM | Resposta do fornecedor |
| 3-4 | Avaliação Plano A vs B | Dev/PM | Decisão documentada |
| 5 | Início implementação | Dev | POC |

**Decisão esperada:**
- Plano A: API Domínio disponível → implementar
- Plano B: Usar provedor (Omie/Nibo) → implementar connector alternativo

### Semana 8: GOV Certificado + Homologação

**Objetivo:** Certificado A1 funcionando, 1 fluxo gov testado

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Certificado A1 configurado | Infra | Teste de assinatura |
| 3-4 | Teste eSocial homologação | Dev | Evento aceito |
| 5 | Documentação | Dev | Runbook |

**Entregáveis Mês 2:**
```
✓ Feature flags funcionando
✓ Bling dual-write em 2-3 tenants piloto
✓ Decisão Domínio documentada
✓ Certificado A1 configurado
✓ 1 fluxo GOV em homologação
✓ Aprovação humana em operações críticas
```

---

## MÊS 3: CUTOVER GRADUAL + SISTEMA DE REFERÊNCIA

### Semana 9: Expansão Bling + Validação

**Objetivo:** Mais tenants em dual-write, validação de consistência

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Expansão para 50% tenants | PM/Ops | Sem erros |
| 3-4 | Validação de consistência | Dev | < 1% divergência |
| 5 | Ajustes finos | Dev | Fixes aplicados |

**Checklist de validação:**
- [ ] Totais batem (estoque, financeiro)
- [ ] IDs mapeados corretamente
- [ ] Sem duplicatas
- [ ] Logs limpos

### Semana 10: Sólides Controlado + RH

**Objetivo:** Sólides em modo write controlado (se aprovado)

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Avaliação de write Sólides | PM/RH | Decisão |
| 3-4 | Implementação ou documentação | Dev | Funcional ou doc |
| 5 | Treinamento RH | PM | Time treinado |

**Nota:** Write no Sólides pode não ser necessário se Conecta PRO for o sistema de referência para RH.

### Semana 11: Cutover Bling

**Objetivo:** Bling em modo "Conecta PRO é referência"

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Comunicação a usuários | PM | Todos informados |
| 3-4 | Ativação 100% tenants | Ops | Sem incidentes |
| 5 | Monitoramento intensivo | Ops | SLA mantido |

**Fluxo pós-cutover:**
```
ANTES: Bling → Conecta PRO (pull)
DEPOIS: Conecta PRO → Bling (push)
        Bling fica como "espelho" para consulta
```

### Semana 12: Validação Final + Documentação

**Objetivo:** Projeto entregue, documentado, operacional

| Dia | Entrega | Responsável | Validação |
|-----|---------|-------------|-----------|
| 1-2 | Validação final de dados | QA | 100% correto |
| 3-4 | Documentação completa | Dev | Runbooks prontos |
| 5 | Retrospectiva | Time | Lições aprendidas |

**Entregáveis Mês 3:**
```
✓ Bling em modo push (Conecta PRO é referência)
✓ Sólides em modo adequado (pull ou push conforme decisão)
✓ Domínio em operação (API ou provedor)
✓ GOV funcionando onde viável
✓ Documentação completa
✓ Time operacional treinado
✓ Runbooks de incidentes
```

---

## ESTRATÉGIA DE ROLLBACK

### Por Conector

```python
# Desativar write para um conector
FEATURE_FLAGS["bling_write_products"] = False
FEATURE_FLAGS["bling_write_clients"] = False

# Conector volta a modo pull-only
# Dados existentes mantidos
# Novos dados só no Conecta PRO
```

### Por Tenant

```python
# Desativar para tenant específico
TENANT_OVERRIDES["tenant_xyz"] = {
    "bling_write": False,
    "solides_write": False,
}
```

### Rollback Completo

```bash
# Em caso de falha crítica
1. Desativar todas as feature flags
2. Pausar workers de sync
3. Notificar stakeholders
4. Investigar causa raiz
5. Corrigir e reativar gradualmente
```

---

## PLANO DE TREINAMENTO

### Semana 4: Treinamento Inicial

| Público | Conteúdo | Duração |
|---------|----------|---------|
| Operacional | Visão geral do framework | 1h |
| Suporte | Dashboard e logs | 2h |
| Gestores | Métricas e relatórios | 1h |

### Semana 8: Treinamento Dual-Write

| Público | Conteúdo | Duração |
|---------|----------|---------|
| Operacional | Novos fluxos de trabalho | 2h |
| Suporte | Troubleshooting de sync | 2h |
| Gestores | Aprovação de operações | 1h |

### Semana 12: Treinamento Final

| Público | Conteúdo | Duração |
|---------|----------|---------|
| Todos | Sistema completo | 3h |
| Suporte | Runbooks de incidentes | 2h |
| Gestores | Relatórios e KPIs | 1h |

---

## KPIs DE SUCESSO

| KPI | Meta Mês 1 | Meta Mês 2 | Meta Mês 3 |
|-----|------------|------------|------------|
| Uptime do framework | 99% | 99.5% | 99.9% |
| Taxa de sync sucesso | 95% | 98% | 99% |
| Divergência de dados | < 10% | < 3% | < 1% |
| Tempo médio de sync | < 5min | < 3min | < 1min |
| Incidentes críticos | < 5 | < 2 | 0 |
| Satisfação usuário | 3/5 | 4/5 | 4.5/5 |

---

## GATES DE APROVAÇÃO

### Gate 1: Fim do Mês 1 (Read-Only)
- [ ] Framework funcionando
- [ ] Dados sincronizando
- [ ] Dashboard operacional
- [ ] Aprovação: PM + Tech Lead

### Gate 2: Fim do Mês 2 (Dual-Write)
- [ ] Pilotos sem incidentes
- [ ] Decisões documentadas
- [ ] Treinamento concluído
- [ ] Aprovação: PM + Tech Lead + Ops

### Gate 3: Fim do Mês 3 (Cutover)
- [ ] KPIs atingidos
- [ ] Documentação completa
- [ ] Time treinado
- [ ] Aprovação: PM + Tech Lead + Ops + Direção

---

*Documento criado em: 2026-01-15*
*Revisão: Semanal durante o projeto*
