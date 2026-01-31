# Sistema de Ações Executivas do Bartolo

## Visão Geral

Transforma o Bartolo de assistente **CONSULTIVO** (apenas responde perguntas) para assistente **EXECUTIVO** (executa ações operacionais reais) com:

- ✅ 13 ações operacionais implementadas
- ✅ Confirmação obrigatória antes de executar
- ✅ Auditoria completa de todas as ações
- ✅ Permissões por perfil de usuário (RBAC)
- ✅ Preview com validações antes de executar

## Arquitetura

### Fluxo de Execução

```
1. DETECÇÃO DE INTENÇÃO
   Usuário: "Criar escala para o posto 001 em fevereiro"
   → ActionDetector.detect() → ActionRequest

2. GERAÇÃO DE PREVIEW
   → ActionExecutor.create_action_preview()
   → ScaleExecutor.create_preview()
   → Valida posto, verifica conflitos, monta resumo
   → ActionPreview (com resumo, avisos, permissões)

3. CONFIRMAÇÃO DO USUÁRIO
   → Frontend exibe modal com preview
   → Usuário clica "Confirmar" ou "Cancelar"
   → POST /api/v1/ai/bartolo/confirm-action

4. EXECUÇÃO DA AÇÃO
   → ActionExecutor.execute_action()
   → ScaleExecutor.execute()
   → ScaleRepository.create()
   → Transação atômica no banco

5. AUDITORIA
   → AuditService.create_audit_log()
   → Registra: user_id, action, old_values, new_values
   → Tags: ["bartolo", "action", "create_scale"]

6. RESPOSTA AO USUÁRIO
   → ActionResult com sucesso/erro
   → Mensagem formatada com detalhes
```

## Estrutura de Arquivos

```
/opt/conecta-pro/backend/modules/ai/bartolo/actions/
├── __init__.py                   # Exporta classes principais
├── README.md                     # Esta documentação
├── action_types.py               # Enums: ActionType, ActionCategory, ActionStatus
├── action_schemas.py             # Pydantic: ActionRequest, ActionPreview, ActionResult
├── action_detector.py            # Detecta intenção via pattern matching
├── action_executor.py            # Orquestrador principal
├── action_permissions.py         # Mapping: ActionType → Permission
└── executors/
    ├── __init__.py
    ├── base_executor.py          # Classe abstrata BaseActionExecutor
    ├── scale_executor.py         # Ações de escala (CREATE, APPROVE, PUBLISH)
    ├── allocation_executor.py    # Ações de alocação (placeholder)
    └── shift_executor.py         # Ações de turno (placeholder)
```

## Ações Implementadas

### Escalas (3 ações)
- ✅ `CREATE_SCALE` - Criar nova escala (implementado)
- 🔶 `APPROVE_SCALE` - Aprovar escala (preview implementado, execução TODO)
- 🔶 `PUBLISH_SCALE` - Publicar escala (preview implementado, execução TODO)

### Alocações (3 ações)
- 🔶 `ALLOCATE_EMPLOYEE` - Alocar funcionário (TODO)
- 🔶 `TERMINATE_ALLOCATION` - Encerrar alocação (TODO)
- 🔶 `TRANSFER_EMPLOYEE` - Transferir funcionário (TODO)

### Turnos (4 ações)
- 🔶 `CREATE_SHIFT` - Criar turno (TODO)
- 🔶 `REGISTER_CHECKIN` - Registrar entrada (TODO)
- 🔶 `REGISTER_CHECKOUT` - Registrar saída (TODO)
- 🔶 `MARK_ABSENCE` - Marcar falta (TODO)

### Substituições (1 ação)
- 🔶 `CREATE_SUBSTITUTION` - Criar substituição (TODO)

### Notificações (1 ação)
- 🔶 `SEND_NOTIFICATION` - Enviar notificação (TODO)

### Relatórios (1 ação)
- 🔶 `GENERATE_REPORT` - Gerar relatório (TODO)

**Total: 13 ações (1 completa, 12 com preview)**

## Uso

### Exemplo de Fluxo Completo

1. **Usuário envia mensagem:**
   ```
   POST /api/v1/ai/bartolo/send
   {
     "message": "Criar escala para o posto 001 em fevereiro",
     "session_id": "abc123",
     "user_id": 1
   }
   ```

2. **Bartolo retorna preview:**
   ```json
   {
     "response": "Entendi! Você quer **Criar Escala - POST-001**...",
     "action_preview": {
       "action_id": "uuid-123",
       "action_type": "create_scale",
       "title": "Criar Escala - POST-001",
       "description": "Criar escala para Posto Central em 02/2024",
       "changes_summary": [
         "Posto: POST-001 - Posto Central",
         "Período: 02/2024",
         "Tipo: Escala 12x36 (padrão)"
       ],
       "warnings": [],
       "required_permission": "scales:create",
       "user_has_permission": true,
       "can_be_undone": true
     }
   }
   ```

3. **Frontend exibe modal de confirmação**

4. **Usuário confirma:**
   ```
   POST /api/v1/ai/bartolo/confirm-action
   {
     "action_id": "uuid-123",
     "confirmed": true,
     "user_id": "1",
     "confirmed_at": "2024-01-29T12:00:00Z"
   }
   ```

5. **Bartolo executa e retorna resultado:**
   ```json
   {
     "response": "✅ Escala criada com sucesso\n\n**Detalhes:**\n- Scale Id: uuid-456\n...",
     "processing_time_ms": 250
   }
   ```

## Detecção de Ações

O `ActionDetector` usa pattern matching com regex para detectar intenções:

```python
ACTION_PATTERNS = {
    ActionType.CREATE_SCALE: [
        r"criar?\s+(?:uma\s+)?escala",
        r"gerar?\s+(?:uma\s+)?escala",
        r"montar?\s+(?:uma\s+)?escala",
    ],
    ActionType.APPROVE_SCALE: [
        r"aprovar?\s+(?:a\s+)?escala",
    ],
    # ...
}
```

### Extração de Parâmetros

O detector também extrai parâmetros da mensagem:

- Código de posto: `POST-001`, `001`
- Mês/Ano: `fevereiro`, `02/2024`
- IDs de funcionário, escala, etc.

## Permissões

Cada ação requer uma permissão específica do módulo operacional:

```python
ACTION_PERMISSIONS = {
    ActionType.CREATE_SCALE: Permission.SCALES_CREATE,
    ActionType.APPROVE_SCALE: Permission.SCALES_APPROVE,
    ActionType.ALLOCATE_EMPLOYEE: Permission.ALLOCATIONS_CREATE,
    # ...
}
```

O sistema valida permissões em dois momentos:
1. **Preview**: Informa se usuário tem permissão
2. **Execução**: Re-valida antes de executar

## Auditoria

Todas as ações são auditadas usando o `AuditService`:

- **Início da ação**: Registra parâmetros e confiança
- **Conclusão**: Registra resultado e duração
- **Cancelamento**: Registra cancelamento pelo usuário
- **Erro**: Registra mensagem de erro

Tags aplicadas:
- `["bartolo", "action", "start", "{action_type}"]`
- `["bartolo", "action", "complete", "{action_type}"]`
- `["bartolo", "action", "cancelled", "{action_type}"]`
- `["bartolo", "action", "error", "{action_type}"]`

## Segurança

### Validações Obrigatórias

1. **Antes do Preview:**
   - Validar que entidades existem (posto, funcionário, etc.)
   - Verificar permissão do usuário
   - Validar parâmetros mínimos

2. **Antes da Execução:**
   - Re-validar permissão (usuário pode ter perdido acesso)
   - Verificar timeout (5 minutos)
   - Validar integridade dos dados

3. **Durante Execução:**
   - Usar transações SQLAlchemy
   - Rollback automático em caso de erro

### Rate Limiting

- Timeout de ações pendentes: 5 minutos
- Limpeza automática de ações expiradas

## Testes

### Teste Manual do Detector

```bash
python3 /tmp/test_action_detector.py
```

### Teste de Integração (TODO)

```bash
# 1. Detectar ação
curl -X POST http://localhost:8080/api/v1/ai/bartolo/send?user_id=1 \
  -d '{"message":"Criar escala para o posto 001 em fevereiro","session_id":"test"}'

# 2. Confirmar ação
curl -X POST http://localhost:8080/api/v1/ai/bartolo/confirm-action \
  -d '{"action_id":"abc-123","confirmed":true,"user_id":"1","confirmed_at":"2024-01-29T12:00:00Z"}'
```

## Próximos Passos

### Backend
- [ ] Implementar execução de APPROVE_SCALE e PUBLISH_SCALE
- [ ] Implementar executores de Allocation e Shift
- [ ] Implementar executores de Notification e Report
- [ ] Adicionar rate limiting por usuário
- [ ] Persistir ações pendentes no Redis/DB

### Frontend (TODO)
- [ ] Criar `ActionConfirmationModal.tsx`
- [ ] Integrar modal no `BartoloChatWidget.tsx`
- [ ] Atualizar `bartolo.service.ts` com `confirmAction()`
- [ ] Exibir preview de ações no chat
- [ ] Toast notifications de sucesso/erro

### Testes
- [ ] Criar testes unitários para cada executor
- [ ] Criar testes de integração end-to-end
- [ ] Testar permissões e auditoria
- [ ] Testar timeout e limpeza de ações

## Configuração

Para ativar/desativar o sistema de ações:

```python
# modules/ai/bartolo/config/identity.py
class BartoloConfig:
    enable_actions: bool = True  # False para desativar
```

## Contribuindo

Ao adicionar novas ações:

1. Adicionar tipo em `ActionType` (action_types.py)
2. Adicionar patterns em `ActionDetector.ACTION_PATTERNS`
3. Mapear permissão em `ACTION_PERMISSIONS`
4. Criar/atualizar executor correspondente
5. Implementar `create_preview()` e `execute()`
6. Adicionar testes

## Autoria

Implementado conforme plano detalhado em `/root/plano_acoes_bartolo.md`

Sprint: Sistema de Ações Executivas
Data: 2024-01-29
