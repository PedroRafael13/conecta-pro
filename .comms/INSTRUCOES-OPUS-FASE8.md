# CONTEXTO OPUS — Sessão Nova (Fase 8 - Validação Final)

## Quem você é
Você é o **Opus Executor** no projeto Conecta PRO. Trabalha em coordenação com:
- **Claude Opus (outro terminal):** Auditor e coordenador
- **Kimi K2.5 (outro terminal):** Executor frontend

## O que já foi feito (NÃO repita)
O Plano Mestre de Produção tem 8 fases. **Fases 1-7 estão CONCLUÍDAS:**

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | Pytest 6232 passed, 0 failed | ✅ CONCLUÍDA |
| 2 | Alembic 1 head | ✅ CONCLUÍDA |
| 3 | ESLint 0 errors, 0 warnings | ✅ CONCLUÍDA |
| 4 | Bandit 0 High | ✅ CONCLUÍDA |
| 5 | EmailTemplate | ✅ NÃO PRECISA |
| 6 | JWT 0 jose imports | ✅ CONCLUÍDA |
| 7 | console.log (0 reais, 6 JSDoc) | ✅ CONCLUÍDA |
| 8 | Validação Final | ⬅️ AGORA |

### Seus commits desta sessão (já feitos):
- `7c41766` — fix(backend): Bandit B501 + 2 bugs produção
- `077067f` — fix(frontend): 86+ ESLint warnings eliminados (52 arquivos)

## SUA TAREFA AGORA: Fase 8 — Validação Final (sua parte)

Rode estes 3 checks e reporte os resultados EXATOS:

### Check 4 — Bandit Segurança
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate && bandit -r . -q --severity-level high 2>&1 | tail -10
```
**Esperado:** 0 High severity issues (ou apenas com nosec justificado)

### Check 5 — Alembic Heads
```bash
cd /opt/conecta-pro/backend && source venv/bin/activate && alembic heads 2>&1
```
**Esperado:** 1 única head

### Check 9 — Frontend Build
```bash
cd /opt/conecta-pro/frontend && npx next build 2>&1 | tail -10
```
**Esperado:** Build completed successfully

## Comunicação
Reporte resultados no canal:
```bash
cat >> /opt/conecta-pro/.comms/messages/opus-exec-out.jsonl << 'EOF'
{"ts":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","from":"opus-exec","type":"validation","checks":"4,5,9","result":"RESULTADO AQUI"}
EOF
```

## REGRAS
1. NÃO modifique nenhum arquivo — apenas rode os checks
2. Reporte resultados exatos (copie o output)
3. Se algum check falhar, reporte o erro exato — NÃO tente corrigir sem aprovação

## Branch e diretório
- **Branch:** feature/openclaw-v2
- **Backend:** /opt/conecta-pro/backend
- **Frontend:** /opt/conecta-pro/frontend
