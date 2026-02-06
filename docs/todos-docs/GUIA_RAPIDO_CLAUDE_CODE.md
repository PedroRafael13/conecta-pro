# 🚀 GUIA RÁPIDO - COMEÇAR COM CLAUDE CODE

## ⚡ INÍCIO RÁPIDO (3 passos)

### PASSO 1: Preparar VPS (5 minutos)

```bash
# Conectar no seu VPS
ssh root@82.25.75.74

# Executar preparação
curl -sSL https://raw.githubusercontent.com/.../prepare_vps.sh | bash

# OU manualmente:
mkdir -p /opt/erp-conecta-mais/{backend,frontend,docs,logs,sessions}
cd /opt/erp-conecta-mais

# Criar gerenciador de sessões
cat > sessions/SESSION_MANAGER.md << 'EOF'
# HISTÓRICO DE SESSÕES - ERP CONECTA MAIS

Sessões registradas aqui...

---
EOF

# Criar rastreador de progresso
cat > docs/PROGRESSO_GERAL.md << 'EOF'
# 📊 PROGRESSO GERAL

Sprint Atual: Sprint 0
Progresso: 0%

---
EOF

echo "✅ VPS preparado!"
```

### PASSO 2: Upload da Documentação

```bash
# No seu computador local:
scp -r ~/erp-docs/* root@82.25.75.74:/opt/erp-conecta-mais/docs/

# Verificar:
ssh root@82.25.75.74 "ls /opt/erp-conecta-mais/docs/"
```

### PASSO 3: Iniciar Claude Code

```bash
# No terminal local, conectar no VPS
ssh root@82.25.75.74

# Navegar para projeto
cd /opt/erp-conecta-mais

# Iniciar Claude Code
claude-code
```

Agora cole o **PROMPT VERSÃO 1** do arquivo:
`PROMPT_CLAUDE_CODE_DEFINITIVO.md`

---

## 📋 FLUXO DE TRABALHO DIÁRIO

### Dia Típico:

```
9:00  - Conectar VPS + Iniciar Claude Code
9:01  - Claude mostra resumo da última sessão
9:02  - Você confirma: "vamos continuar"
9:05  - Claude começa desenvolvimento
...
12:00 - Você: "vamos encerrar"
12:01 - Claude registra sessão + mostra resumo
12:02 - Fim!
```

### Comandos Úteis:

```bash
# Ver progresso
cat /opt/erp-conecta-mais/docs/PROGRESSO_GERAL.md

# Ver última sessão
tail -50 /opt/erp-conecta-mais/sessions/SESSION_MANAGER.md

# Ver roteiro
cat /opt/erp-conecta-mais/docs/ROTEIRO_DEFINITIVO_PASSO_A_PASSO.md | less

# Status do projeto
cd /opt/erp-conecta-mais/backend
git log --oneline -10
```

---

## 💬 FRASES ÚTEIS PARA USAR COM CLAUDE CODE

### Durante Desenvolvimento:

✅ **"Explique o que vai fazer"** - Claude descreve antes de executar

✅ **"Mostre os testes"** - Claude mostra os testes que criou

✅ **"Valide tudo"** - Claude roda linters + testes

✅ **"Qual nosso progresso?"** - Claude mostra % atual

✅ **"Commita isso"** - Claude faz commit do trabalho atual

### Controle de Sessão:

✅ **"Vamos encerrar"** - Claude registra e finaliza

✅ **"Mostre resumo"** - Claude mostra o que foi feito hoje

✅ **"Próximos passos?"** - Claude lista o que vem a seguir

### Resolução de Problemas:

✅ **"Algo deu errado"** - Claude consulta PRE_MORTEM

✅ **"Revise o código"** - Claude analisa qualidade

✅ **"Refaça isso"** - Claude refaz a última ação

---

## 🎯 CHECKLIST ANTES DE CADA SESSÃO

- [ ] VPS está acessível (82.25.75.74)
- [ ] Conecta Plus NÃO foi afetado
- [ ] Última sessão foi registrada
- [ ] Git está limpo ou commitado
- [ ] Sei o que vou fazer hoje

---

## ⚠️ PROBLEMAS COMUNS

### "Claude não lembra da sessão anterior"

**Causa:** Arquivo SESSION_MANAGER.md não foi atualizado
**Solução:** 
```bash
cat /opt/erp-conecta-mais/sessions/SESSION_MANAGER.md
# Se vazio, última sessão não foi encerrada corretamente
```

### "Conecta Plus parou de funcionar"

**Causa:** Acidentalmente mexeu nos arquivos errados
**Solução:**
```bash
# Verificar Conecta Plus
systemctl status conecta-plus
# OU
pm2 list
# Reiniciar se necessário
```

### "Coverage baixo"

**Causa:** Testes insuficientes
**Solução:** Diga ao Claude:
```
"Coverage está em X%. Precisa estar >80%. Crie mais testes."
```

---

## 📊 MÉTRICAS DE SUCESSO

### Após cada sessão, você deve ter:

✅ Sessão registrada em SESSION_MANAGER.md
✅ Progresso atualizado (X% → Y%)
✅ Commits realizados
✅ Testes passando (>80% coverage)
✅ Próximos passos definidos

---

## 🚀 VOCÊ ESTÁ PRONTO!

**Arquivos que você precisa:**
1. ✅ PROMPT_CLAUDE_CODE_DEFINITIVO.md (tem os prompts)
2. ✅ ROTEIRO_DEFINITIVO_PASSO_A_PASSO.md (roteiro completo)
3. ✅ Toda documentação do ERP (38 módulos)

**Próximo passo:**
→ Execute PASSO 1 (preparar VPS)
→ PASSO 2 (upload docs)
→ PASSO 3 (iniciar Claude Code com prompt)

**Tempo até começar:** 10 minutos! ⚡

