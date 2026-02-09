# PROMPT PARA KIMI — Copiar e Colar

---

Leia o arquivo `.comms/tasks/PLANO-MESTRE-PRODUCAO.md` — é o plano mestre completo com 8 fases para resolver todos os bloqueadores do Conecta PRO para produção.

## Contexto Rápido
- Projeto: /opt/conecta-pro (backend Python/FastAPI + frontend Next.js/React)
- Branch: feature/openclaw-v2
- Claude Opus está auditando tudo em tempo real
- Qualidade mínima: 99.5%

## O que você precisa resolver (em ordem):

### PARALELO (Fases 1+3+4+7 — usar sub-agentes):

**FASE 1 — 159 pytest collection errors:**
- 148/159 são `ModuleNotFoundError: No module named 'core.*'`
- Verificar se `pythonpath = .` existe no pytest.ini
- Se sim e não funciona, corrigir imports nos 159 test files
- Comando de verificação: `cd /opt/conecta-pro/backend && source venv/bin/activate && python -m pytest --collect-only -q 2>&1 | tail -5`
- Meta: 0 collection errors

**FASE 3 — 1170 ESLint errors no frontend:**
- 1115/1643 estão em `src/types/generated/` (NÃO editar esses arquivos)
- Adicionar `src/types/generated/**` ao ESLint ignore
- Rodar `--fix` para 428 warnings auto-fixáveis
- Corrigir ~385 erros manuais (maioria `react-hooks/immutability`)
- Meta: 0 errors, 0 warnings (excluindo generated)

**FASE 4 — 4 vulnerabilidades Bandit High:**
- 2x SHA1: adicionar `usedforsecurity=False` em `nfce_manager.py:162` e `xml_signer.py:262`
- 2x verify=False: adicionar `# noqa: S501` com justificativa em `sefaz_am.py:216` e `test_gov_connections.py:389`
- Corrigir permissão: `chmod 600 /opt/conecta-pro/backend/.env`
- Meta: 0 Bandit High

**FASE 7 — 38 console.log no frontend:**
- Remover todos os `console.log` em src/ (exceto .test. files)
- Meta: 0 console.log em código de produção

### SEQUENCIAL (após paralelo):

**FASE 2 — 12 alembic heads:** Merge em 1 única head
**FASE 5 — EmailTemplate duplicado:** Consolidar de 4 para 1 model
**FASE 6 — JWT divergência:** Padronizar PyJWT (remover imports de jose)

### FINAL:

**FASE 8 — Rodar os 10 checks de validação e reportar resultados**

## REGRAS
1. Nunca declare sucesso sem rodar os comandos de verificação
2. Teste DUAS vezes antes de entregar
3. Reporte cada fase via `.comms/messages/kimi-out.jsonl`
4. Se não sabe como resolver algo, PERGUNTE
5. Leia o plano completo em `.comms/tasks/PLANO-MESTRE-PRODUCAO.md`
