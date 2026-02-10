# Prompt de Início — Copiar e Colar no Kimi

Copie o bloco abaixo e cole como primeira mensagem em qualquer sessão nova do Kimi.

---

```
Você é o Kimi K2.5 trabalhando no projeto Conecta PRO. Antes de fazer QUALQUER coisa, execute estes comandos na ordem e leia cada output:

1. cat /opt/conecta-pro/AGENTS.md
2. cat /opt/conecta-pro/.kimi/SESSION-START.md
3. cat /opt/conecta-pro/.kimi/ENVIRONMENT.md
4. cat /opt/conecta-pro/.kimi/REGRAS-OPERACIONAIS.md
5. cat /opt/conecta-pro/.kimi/ERROS-PASSADOS.md
6. cat /opt/conecta-pro/.comms/HANDOFF.md
7. cat /opt/conecta-pro/.comms/BACKLOG.md
8. cat /opt/conecta-pro/.comms/BASELINE.json
9. tail -10 /opt/conecta-pro/.comms/messages/claude-out.jsonl

Depois de ler tudo, rode a verificação inicial:
/opt/conecta-pro/scripts/verify-all.sh

Só então me diga: "Contexto carregado. Pronto para trabalhar." e liste as tarefas do BACKLOG em ordem de prioridade.
```

---

## Variação curta (se quiser economizar contexto):

```
Leia todos os arquivos em /opt/conecta-pro/.kimi/ e /opt/conecta-pro/.comms/ (HANDOFF.md, BACKLOG.md, BASELINE.json, messages/claude-out.jsonl). Depois rode /opt/conecta-pro/scripts/verify-all.sh. Só então comece a trabalhar.
```
