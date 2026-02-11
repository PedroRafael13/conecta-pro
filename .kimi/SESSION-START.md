# SESSION START — LEIA ISTO PRIMEIRO

**OBRIGATÓRIO:** Leia este arquivo INTEIRO antes de fazer QUALQUER coisa.

## Estado: PLANO MESTRE 100% CONCLUÍDO (2026-02-10)

O baseline atual é estável. Sua prioridade é NÃO regredir.

### Baseline (não aceitar valores piores):
- Pytest: 6287 passed, 0 failed
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Vitest: 1985/1985 passed
- Bandit: 0 High
- Alembic: 1 head
- Next.js build: OK

---

## Passo 1: Contexto
```bash
cat /opt/conecta-pro/.comms/HANDOFF.md
cat /opt/conecta-pro/.comms/BACKLOG.md
tail -20 /opt/conecta-pro/.comms/messages/claude-out.jsonl
```

## Passo 2: Baseline atual
```bash
cat /opt/conecta-pro/.comms/BASELINE.json
```
Compare com os números acima. Se algo piorou, PARE e reporte.

## Passo 3: Estado do ambiente
```bash
cat /opt/conecta-pro/.kimi/ENVIRONMENT.md
```

## Passo 4: Regras operacionais
```bash
cat /opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md
```

## Passo 5: Registrar início de sessão
```bash
echo '{"ts":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","from":"kimi","to":"claude","type":"status","id":"kimi-'$(date +%s)'","reply_to":null,"priority":"normal","subject":"Session Start","content":"Sessão iniciada. Baseline lido. Ambiente verificado."}' >> /opt/conecta-pro/.comms/messages/kimi-out.jsonl
```

## Passo 6: Verificação pré-trabalho
```bash
/opt/conecta-pro/scripts/verify-all.sh
```
Guardar este output. É seu ANTES. Ao final, comparar com o DEPOIS.

---

**SÓ DEPOIS de completar todos os 6 passos, comece a trabalhar.**
