# PLANO DE MELHORIA CONTÍNUA - CODE QUALITY SCORE
## Meta: 72/100 → >99/100

**Data:** 2026-01-04
**Projeto:** ERP Conecta Mais V3.0
**Status:** EM EXECUÇÃO

---

## ANÁLISE DO GAP

### Score Atual vs Meta

```
╔════════════════════════════════════════════════════════════════╗
║  DIMENSÃO          │ ATUAL │ META  │ GAP   │ PESO │ IMPACTO   ║
╠════════════════════════════════════════════════════════════════╣
║  Arquitetura       │  95   │  98   │  -3   │ 20%  │  -0.6     ║
║  Complexidade      │  98   │  99   │  -1   │ 15%  │  -0.15    ║
║  Manutenibilidade  │  90   │  95   │  -5   │ 15%  │  -0.75    ║
║  Segurança         │  88   │  95   │  -7   │ 20%  │  -1.4     ║
║  Testes            │  32   │  95   │  -63  │ 20%  │  -12.6    ║
║  Dependências      │  55   │  90   │  -35  │ 10%  │  -3.5     ║
╠════════════════════════════════════════════════════════════════╣
║  TOTAL             │  72   │  99   │  -27  │ 100% │  -27      ║
╚════════════════════════════════════════════════════════════════╝
```

### Priorização por Impacto

| Prioridade | Dimensão | Gap | Impacto no Score | Esforço |
|------------|----------|-----|------------------|---------|
| 1 | **Testes** | -63 | -12.6 pts | Alto |
| 2 | **Dependências** | -35 | -3.5 pts | Baixo |
| 3 | **Segurança** | -7 | -1.4 pts | Médio |
| 4 | **Manutenibilidade** | -5 | -0.75 pts | Médio |
| 5 | **Arquitetura** | -3 | -0.6 pts | Baixo |
| 6 | **Complexidade** | -1 | -0.15 pts | Baixo |

**Conclusão: 80% do gap está em TESTES e DEPENDÊNCIAS**

---

## PLANO DE EXECUÇÃO EM 5 ETAPAS

### ETAPA 1: Triagem e Limpeza (Score: 72 → 80)

**Objetivo:** Remover testes irrecuperáveis e organizar a base

#### Ações:
- [ ] 1.1 Identificar testes completamente obsoletos
- [ ] 1.2 Mover para `tests/_obsolete/`
- [ ] 1.3 Atualizar `pyproject.toml` para ignorar `_obsolete`
- [ ] 1.4 Rodar testes e validar melhoria

#### Critérios de Teste Obsoleto:
- Módulo foi removido/renomeado
- Funcionalidade não existe mais
- Mais de 50% do teste precisa reescrita

#### Meta:
- Testes passando: 854 → ~1.200 (remover ~800 obsoletos)
- Score Testes: 32 → 55
- **Score Total: 72 → 80**

---

### ETAPA 2: Correção Automatizada de Debt (Score: 80 → 88)

**Objetivo:** Eliminar debt técnico com scripts automatizados

#### Ações:
- [ ] 2.1 Script para `datetime.utcnow()` → `datetime.now(UTC)` (1.707 ocorrências)
- [ ] 2.2 Script para `class Config:` → `model_config` (76 ocorrências)
- [ ] 2.3 Corrigir enums conhecidos em massa
- [ ] 2.4 Atualizar dependências não-breaking

#### Scripts a Criar:
```python
# fix_datetime.py - Substituição em massa
# fix_pydantic_config.py - Migração Pydantic v2
# fix_enums.py - Correção de enums desatualizados
```

#### Meta:
- DeprecationWarnings: 964 → <100
- Testes passando: ~1.200 → ~1.600
- Score Testes: 55 → 70
- Score Dependências: 55 → 75
- **Score Total: 80 → 88**

---

### ETAPA 3: Correção Manual de Testes Críticos (Score: 88 → 94)

**Objetivo:** Corrigir testes de módulos críticos manualmente

#### Priorização de Módulos:
| Ordem | Módulo | Testes Falhando | Criticidade |
|-------|--------|-----------------|-------------|
| 1 | core/ | ~50 | CRÍTICO |
| 2 | crm/ | ~150 | ALTA |
| 3 | financial/ | ~200 | ALTA |
| 4 | hr/ | ~180 | MÉDIA |
| 5 | clients/ | ~100 | MÉDIA |
| 6 | operations/ | ~120 | MÉDIA |

#### Ações por Módulo:
- [ ] 3.1 Corrigir testes de `core/` (autenticação, base)
- [ ] 3.2 Corrigir testes de `crm/` (leads, opportunities, contracts)
- [ ] 3.3 Corrigir testes de `financial/` (contas, fluxo, custos)
- [ ] 3.4 Corrigir testes de `hr/` (ponto, folha, portal)
- [ ] 3.5 Corrigir testes de `clients/` (cadastros, integrações)
- [ ] 3.6 Corrigir testes de `operations/` (escalas, postos)

#### Meta:
- Testes passando: ~1.600 → ~2.200
- Score Testes: 70 → 85
- **Score Total: 88 → 94**

---

### ETAPA 4: Atualização de Dependências (Score: 94 → 97)

**Objetivo:** Atualizar todas as dependências de forma segura

#### Grupos de Atualização:
| Grupo | Pacotes | Risco |
|-------|---------|-------|
| 1 - Seguros | black, isort, pylint, pytest | Baixo |
| 2 - Moderados | fastapi, pydantic, sqlalchemy | Médio |
| 3 - Críticos | redis, starlette, uvicorn | Alto |

#### Processo por Grupo:
```
1. Atualizar pacotes do grupo
2. Rodar testes
3. Verificar breaking changes
4. Ajustar código se necessário
5. Commit do grupo
```

#### Ações:
- [ ] 4.1 Atualizar grupo 1 (ferramentas dev)
- [ ] 4.2 Atualizar grupo 2 (framework)
- [ ] 4.3 Atualizar grupo 3 (runtime)
- [ ] 4.4 Validar compatibilidade
- [ ] 4.5 Rodar suite completa

#### Meta:
- Dependências desatualizadas: 28 → 0
- Score Dependências: 75 → 95
- **Score Total: 94 → 97**

---

### ETAPA 5: Polimento Final (Score: 97 → >99)

**Objetivo:** Alcançar excelência técnica inquestionável

#### Ações:
- [ ] 5.1 Resolver imports circulares (26 potenciais)
- [ ] 5.2 Aumentar cobertura de testes para 85%+
- [ ] 5.3 Implementar rate limiting completo
- [ ] 5.4 Revisar e melhorar docstrings
- [ ] 5.5 Executar auditoria final completa
- [ ] 5.6 Gerar relatório de certificação

#### Checklist Final:
- [ ] Pylint > 9.8/10
- [ ] Radon CC média < 3
- [ ] Radon MI média > 80
- [ ] Bandit 0 vulnerabilidades
- [ ] Testes > 95% passando
- [ ] Cobertura > 85%
- [ ] 0 DeprecationWarnings
- [ ] 0 dependências desatualizadas críticas

#### Meta:
- Score Testes: 85 → 95
- Score Segurança: 88 → 95
- **Score Total: 97 → >99**

---

## CRONOGRAMA DE EXECUÇÃO

```
╔═══════════════════════════════════════════════════════════════════╗
║  ETAPA                    │ SCORE │ AÇÕES │ CHECKPOINT            ║
╠═══════════════════════════════════════════════════════════════════╣
║  Início                   │  72   │   -   │ Diagnóstico completo  ║
╠═══════════════════════════════════════════════════════════════════╣
║  Etapa 1: Triagem         │  80   │  4    │ Testes organizados    ║
║  Etapa 2: Automatização   │  88   │  4    │ Debt eliminado        ║
║  Etapa 3: Correção Manual │  94   │  6    │ Testes funcionais     ║
║  Etapa 4: Dependências    │  97   │  5    │ Stack atualizado      ║
║  Etapa 5: Polimento       │  99+  │  6    │ CERTIFICAÇÃO FINAL    ║
╠═══════════════════════════════════════════════════════════════════╣
║  TOTAL                    │  +27  │  25   │ Meta atingida         ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## MÉTRICAS DE ACOMPANHAMENTO

### Dashboard de Progresso

| Métrica | Inicial | Atual | Meta | Status |
|---------|---------|-------|------|--------|
| Score Total | 72 | - | >99 | 🔴 |
| Testes Passando | 854 | - | >2.500 | 🔴 |
| Testes Falhando | 1.386 | - | <50 | 🔴 |
| datetime.utcnow | 1.707 | - | 0 | 🔴 |
| class Config | 76 | - | 0 | 🔴 |
| Deps Desatualiz. | 28 | - | 0 | 🔴 |
| Warnings | 964 | - | <50 | 🔴 |

### Checkpoints de Validação

Após cada etapa:
1. Rodar `pytest -q --tb=no`
2. Rodar `pylint modules/ core/`
3. Rodar `radon cc modules/ -a`
4. Calcular novo score
5. Atualizar dashboard
6. Commit com tag de versão

---

## REGRAS DE EXECUÇÃO

### Princípios
1. **Não pular etapas** - Cada etapa é pré-requisito da próxima
2. **Validar antes de avançar** - Checkpoint obrigatório
3. **Commits incrementais** - Um commit por ação concluída
4. **Zero regressão** - Score nunca pode diminuir

### Critérios de Conclusão de Etapa
- [ ] Todas as ações da etapa concluídas
- [ ] Score atingido ou superado
- [ ] Testes de regressão passando
- [ ] Documentação atualizada

---

## PRÓXIMO PASSO

**Iniciar ETAPA 1: Triagem e Limpeza**

Ações imediatas:
1. Identificar testes obsoletos
2. Criar diretório `tests/_obsolete/`
3. Mover testes irrecuperáveis
4. Validar melhoria no score

---

**Aguardando aprovação para iniciar execução.**
