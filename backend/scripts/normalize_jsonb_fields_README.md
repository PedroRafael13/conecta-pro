# Script de Normalização de Campos JSONB - Conecta Pro

## 📋 Visão Geral

Este script SQL normaliza campos JSONB críticos no banco de dados PostgreSQL do Conecta Pro, garantindo consistência e integridade dos dados.

## ✨ Características

- **Idempotente**: Pode ser executado múltiplas vezes sem problemas
- **Seguro**: Utiliza transações para garantir consistência
- **Eficiente**: Atualiza apenas registros com dados inconsistentes
- **Flexível**: Detecta automaticamente tabelas e colunas existentes

## 🔧 Tabelas Afetadas

### Principais
| Tabela | Campos JSONB |
|--------|-------------|
| `employees` | `dados_adicionais`, `competencias`, `certificacoes`, `perfil_disc`, `dependentes` |
| `audit_logs` | `details`, `old_values`, `new_values`, `changed_fields`, `metadata`, `tags` |
| `access_history` | `context`, `headers`, `risk_factors`, `metadata`, `tags`, `alert_ids` |
| `scales` | `config` |
| `occurrences` | `attachments` |
| `guardian_occurrences` | `involved_persons`, `witnesses`, `images`, `videos`, `attachments`, `tags` |

### Adicionais
- `scale_templates` (config, template_data)
- `posts` (required_certifications, metadata)
- `allocations` (qualifications)
- `solides_occurrences` (anexos, dados_adicionais)
- `solides_employees` (endereco, dependentes, perfil_disc)
- `disciplinary_actions` (ai_recommendation, extra_data)
- Tabelas de compliance e retenção de dados

## 🚀 Como Usar

### Opção 1: Executar via psql
```bash
# Conectar ao banco de dados e executar
psql -U conecta_user -d conecta_pro -f /opt/conecta-pro/backend/scripts/normalize_jsonb_fields.sql
```

### Opção 2: Executar via Docker
```bash
# Se estiver usando Docker
docker exec -i conecta-postgres psql -U conecta_user -d conecta_pro < /opt/conecta-pro/backend/scripts/normalize_jsonb_fields.sql
```

### Opção 3: Executar via aplicação Python
```python
import psycopg2

# Ler o script
with open('/opt/conecta-pro/backend/scripts/normalize_jsonb_fields.sql', 'r') as f:
    script = f.read()

# Conectar e executar
conn = psycopg2.connect(
    host="localhost",
    database="conecta_pro",
    user="conecta_user",
    password="sua_senha"
)
cursor = conn.cursor()
cursor.execute(script)
conn.commit()
conn.close()
```

## 📊 O que o Script Faz

1. **Normaliza campos NULL**: Converte campos JSONB NULL para `{}` (objeto vazio) ou `[]` (array vazio)
2. **Remove duplicatas**: Elimina chaves duplicadas em objetos JSONB
3. **Padroniza estrutura**: Adiciona metadados de normalização quando necessário
4. **Limpa valores inválidos**: Corrige strings vazias e valores "null" como texto
5. **Registra execução**: Cria tabela de log `_jsonb_normalization_log` para auditoria

## 🔍 Verificação Pós-Execução

Após executar o script, verifique o log:

```sql
-- Ver histórico de normalizações
SELECT * FROM _jsonb_normalization_log ORDER BY executed_at DESC;

-- Verificar campos normalizados na tabela employees
SELECT id, dados_adicionais, competencias
FROM employees
WHERE dados_adicionais IS NULL OR competencias IS NULL;
-- Resultado esperado: 0 registros
```

## ⚠️ Precauções

- **Backup**: Sempre faça backup do banco antes de executar scripts de normalização
- **Teste**: Execute primeiro em ambiente de desenvolvimento
- **Transação**: O script usa transações, então em caso de erro nenhuma alteração será aplicada
- **Idempotência**: É seguro executar o script múltiplas vezes

## 🔄 Rollback

O script é idempotente, mas se precisar reverter alterações específicas:

```sql
-- Exemplo: restaurar campos NULL (se necessário)
UPDATE employees SET dados_adicionais = NULL WHERE dados_adicionais = '{}';
UPDATE employees SET competencias = NULL WHERE competencias = '[]';

-- Remover tabela de log
DROP TABLE IF EXISTS _jsonb_normalization_log;
```

## 📝 Versões

| Versão | Data | Descrição |
|--------|------|-----------|
| 1.0.0 | 2026-02-06 | Versão inicial |

## 📞 Suporte

Em caso de dúvidas ou problemas, entre em contato com a equipe de desenvolvimento.
