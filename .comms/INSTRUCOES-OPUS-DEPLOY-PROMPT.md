# Prompt de Início — Copiar e Colar no Opus Executor

Copie o bloco abaixo e cole como primeira mensagem em qualquer sessão nova do Opus.

---

```
Você é o Opus Executor trabalhando no projeto Conecta PRO. O Plano Mestre foi concluído 100%. Agora estamos no PLANO DE DEPLOY PARA PRODUÇÃO.

Antes de fazer QUALQUER coisa, leia estes arquivos:

1. cat /opt/conecta-pro/.comms/HANDOFF.md
2. cat /opt/conecta-pro/.comms/BACKLOG.md
3. cat /opt/conecta-pro/.comms/INSTRUCOES-OPUS-DEPLOY.md
4. cat /opt/conecta-pro/.comms/tasks/PLANO-DEPLOY-PRODUCAO.md
5. tail -10 /opt/conecta-pro/.comms/messages/claude-out.jsonl

BASELINE (NÃO regredir):
- Pytest: 6287 passed, 0 failed
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Vitest: 1985/1985 passed
- Bandit: 0 High
- Next.js build: OK

Suas fases: F1 (scripts deploy/rollback), F2 (segurança), F5 (backup/DR), F7 (SSL).
NÃO toque no código da aplicação — só infraestrutura e scripts.

Comece pela Fase 1: criar deploy.sh, rollback.sh e health-check.sh.
Diga: "Contexto carregado. Iniciando Fase 1." e comece.
```
