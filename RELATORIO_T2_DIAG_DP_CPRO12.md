# T2-DIAG-DP CPRO12 — Diagnóstico Profundo: Dados DP para Matching GEDEON
**Data:** 2026-05-05
**Terminal:** T3
**Branch:** feature/people-management-reorganization
**Tipo:** READ-ONLY (zero alterações)

---

## Objetivo

Mapear a estrutura de dados do Departamento Pessoal para responder:
**"Dado um nome ou CPF de colaborador, em qual condomínio ele está alocado?"**

Essa informação é necessária para o GEDEON classificar documentos do Onvio corretamente.

---

## Tabelas Relevantes

| Tabela | Rows | Propósito |
|--------|------|-----------|
| `employees` | 58 | Cadastro de colaboradores (nome, CPF, matrícula) |
| `employee_alocacoes` | 47 ativas | Vínculo employee → condomínio + função |
| `condominios` | 7 distintos | Clientes (condomínios) atendidos |
| `onvio_documents` | 605 | Documentos importados do Onvio |

---

## Schema employees (campos-chave para matching)

| Campo | Preenchimento | Observação |
|-------|---------------|-----------|
| `nome` | 58/58 (100%) | UPPERCASE, pode ter variações de grafia |
| `cpf` | 58/58 (100%) | Único, sem pontuação — **melhor chave de match** |
| `matricula` | 58/58 (100%) | Única |
| `solides_id` | parcial | ID externo do sistema Sólides |
| `posto_atual_nome` | 0/58 (0%) | **NÃO USAR** — coluna existe mas está vazia |
| `cliente_nome` | 0/58 (0%) | **NÃO USAR** — coluna existe mas está vazia |

---

## Schema employee_alocacoes (estrutura de vínculo)

```sql
CREATE TABLE employee_alocacoes (
    id          UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),  -- FK direta
    condominio_id UUID REFERENCES condominios(id), -- FK direta
    funcao      VARCHAR,  -- ex: "AGENTE DE PORTARIA", "LÍDER DE PORTARIA"
    data_inicio DATE,
    ativo       BOOLEAN DEFAULT true,
    created_at  TIMESTAMP,
    updated_at  TIMESTAMP
);

-- Índices existentes (consultas rápidas)
ix_employee_alocacoes_employee   → employee_id
ix_employee_alocacoes_condominio → condominio_id
ix_employee_alocacoes_ativo      → ativo
```

---

## Distribuição de colaboradores por condomínio (ativo=true)

| Condomínio | Colaboradores |
|-----------|--------------|
| IDEAL FLORES | 11 |
| MIRANTE | 10 |
| PRIME ARENA | 7 |
| VILLA DEI FIORI | 6 |
| VILLA PÁSSAROS | 6 |
| LARANJEIRAS | 6 |
| MICHELANGELO | 1 |
| **Total** | **47** |

---

## onvio_documents — Campos de vínculo ao DP

| Campo | Preenchimento | Uso |
|-------|---------------|-----|
| `referente_a_employee_id` | 39/93 employee docs | FK direta → employees.id (39 já vinculados) |
| `condominio_id` | 116/605 | FK direta → condominios.id |
| `doc_scope` | 605/605 | 'funcionario'(93), 'condominio'(236), 'empresa_matriz'(107), null(169) |

---

## Query GEDEON para lookup colaborador → condomínio

### Via CPF (recomendado — mais preciso)

```sql
SELECT e.nome, c.nome AS condominio, ea.funcao
FROM employee_alocacoes ea
JOIN employees e ON e.id = ea.employee_id
JOIN condominios c ON c.id = ea.condominio_id
WHERE ea.ativo = true
  AND e.cpf = :cpf_sem_pontuacao;
```

### Via nome (fallback — usar ILIKE para case-insensitive)

```sql
SELECT e.nome, c.nome AS condominio, ea.funcao
FROM employee_alocacoes ea
JOIN employees e ON e.id = ea.employee_id
JOIN condominios c ON c.id = ea.condominio_id
WHERE ea.ativo = true
  AND LOWER(TRIM(e.nome)) = LOWER(TRIM(:nome));
```

### Via referente_a_employee_id (para documentos já vinculados)

```sql
SELECT e.nome, c.nome AS condominio
FROM onvio_documents od
JOIN employees e ON e.id = od.referente_a_employee_id
JOIN employee_alocacoes ea ON ea.employee_id = e.id AND ea.ativo = true
JOIN condominios c ON c.id = ea.condominio_id
WHERE od.id = :doc_id;
```

---

## Existe serviço/função dedicada?

**Não existe** nenhuma função Python do tipo `get_condominio_by_colaborador()` ou view SQL para esse lookup.
O código existente usa queries raw SQL ou ORM direto.

Referências encontradas:
- `ops_agent.py` — `calcular_cobertura()`, `desalocar()` (foco em operacional, não em DP)
- `erp_integration_service.py` — `_get_alocacoes_ativas_por_contrato()` (foco em contratos)
- `backfill_doc_scope_fase_3_5.py` — usa `referente_a_employee_id` em batch

**Conclusão:** GEDEON deve implementar a query diretamente, sem serviço existente.

---

## Resposta à pergunta central

> **GEDEON consegue perguntar ao DP onde está alocado o colaborador X?**

**SIM.** Via join direto:
```
employees → employee_alocacoes → condominios
```

Prioridade de matching:
1. **CPF** (58/58 preenchido, único, sem ambiguidade)
2. **Nome** (UPPERCASE, ILIKE para tolerância de case)
3. **Matrícula** (58/58 preenchido, único — se disponível no documento)
4. **referente_a_employee_id** (39/93 employee docs já têm FK preenchida)

---

## Exemplo real de lookup

```
nome: GRACIENE SILVA MAIA
cpf: 07126591282
condominio: PRIME ARENA
funcao: AGENTE DE PORTARIA

nome: BIANCA BARBOSA
cpf: (preenchido)
condominio: LARANJEIRAS
funcao: AGENTE DE PORTARIA
```

---

## STATUS FINAL

| Step | Status |
|------|--------|
| STEP 0: §86 verificado | ✅ |
| STEP 1: Token + acesso DB | ✅ |
| STEP 2: Tabelas mapeadas | ✅ |
| STEP 3: employees — 58 rows, CPF 100% | ✅ |
| STEP 4: Join employees→alocacoes→condominios | ✅ |
| STEP 5: onvio_documents campos de vínculo | ✅ |
| STEP 6: Endpoints operacionais (leitura) | ✅ |
| STEP 7: Serviços/views para lookup | ✅ (não existe — GEDEON faz direto) |
| STEP 8: Relatório + §88 | ✅ |

**Zero alterações em banco, código ou arquivos de configuração.**
