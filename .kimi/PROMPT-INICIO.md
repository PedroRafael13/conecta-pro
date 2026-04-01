# Prompt de Início — Copiar e Colar no Kimi

Copie o bloco abaixo e cole como primeira mensagem em qualquer sessão nova do Kimi.

---

```
Você é o Kimi K2.5 trabalhando no projeto Conecta PRO. O Plano Mestre de Produção foi CONCLUÍDO em 100%. Agora estamos executando o PLANO DE DEPLOY PARA PRODUÇÃO.

Antes de fazer QUALQUER coisa, execute estes comandos na ordem e leia cada output:

1. cat /opt/conecta-pro/AGENTS.md
2. cat /opt/conecta-pro/.kimi/SESSION-START.md
3. cat /opt/conecta-pro/.kimi/ENVIRONMENT.md
4. cat /opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md
5. cat /opt/conecta-pro/.kimi/ERROS-PASSADOS.md
6. cat /opt/conecta-pro/.comms/HANDOFF.md
7. cat /opt/conecta-pro/.comms/BACKLOG.md
8. cat /opt/conecta-pro/.comms/INSTRUCOES-KIMI-DEPLOY.md
9. tail -10 /opt/conecta-pro/.comms/messages/claude-out.jsonl

Depois de ler tudo, rode a verificação inicial:
/opt/conecta-pro/scripts/verify-all.sh

BASELINE (NÃO regredir):
- Pytest: 6287 passed, 0 failed
- ESLint: 0 warnings, 0 errors
- TypeScript: 0 errors
- Vitest: 1985/1985 passed
- Bandit: 0 High
- Next.js build: OK

Se QUALQUER número estiver pior que o baseline, PARE e reporte antes de trabalhar.

Suas fases: F3 (AlertManager), F4 (Logrotate), F6 (Load Testing).
NÃO toque no código da aplicação — só infraestrutura de monitoramento.

Diga: "Contexto carregado. Baseline verificado. Pronto para Fase 3." e comece.
```

---

## Variação curta:

```
Leia /opt/conecta-pro/.comms/INSTRUCOES-KIMI-DEPLOY.md e todos os arquivos .kimi/ e .comms/. Rode verify-all.sh. Baseline: Pytest 6287/0fail, ESLint 0warn, TS 0err, Vitest 1985/1985, Bandit 0High, Build OK. Suas fases: F3 AlertManager, F4 Logrotate, F6 Load Test. NÃO toque no código da app.
```
