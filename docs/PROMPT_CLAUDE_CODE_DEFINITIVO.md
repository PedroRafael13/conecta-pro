# 🤖 PROMPT DEFINITIVO PARA CLAUDE CODE - ERP CONECTA MAIS
## SISTEMA COM MEMÓRIA COMPLETA ENTRE SESSÕES

---

## 📋 PREPARAÇÃO (EXECUTAR UMA VEZ ANTES DO PRIMEIRO USO)

### Passo 1: Conectar no VPS e Preparar Ambiente

```bash
# Conectar no VPS
ssh root@82.25.75.74

# Criar estrutura do ERP (sem mexer no Conecta Plus!)
mkdir -p /opt/erp-conecta-mais/{backend,frontend,docs,logs,sessions}
cd /opt/erp-conecta-mais

# Criar arquivo de sessões (memória)
cat > sessions/SESSION_MANAGER.md << 'SESSIONEOF'
# HISTÓRICO DE SESSÕES - ERP CONECTA MAIS

## Formato de Registro de Sessão

Cada sessão deve ser registrada com:
- Data/hora início e fim
- O que foi planejado
- O que foi executado
- Arquivos criados/modificados
- Testes executados
- Próximos passos
- Problemas encontrados

---

## SESSÃO 001 - [DATA]
Status: [EM ANDAMENTO / CONCLUÍDA]

### Planejado:
- [ ] Item 1
- [ ] Item 2

### Executado:
- [x] Item realizado
- [x] Item realizado

### Arquivos Criados:
- path/to/file.py
- path/to/test.py

### Testes:
- ✅ test_function_x passou
- ✅ Coverage: XX%

### Próximos Passos:
1. Fazer X
2. Implementar Y

### Problemas:
- Nenhum / Descrição do problema e solução

---
SESSIONEOF

# Criar arquivo de progresso geral
cat > docs/PROGRESSO_GERAL.md << 'PROGRESSEOF'
# 📊 PROGRESSO GERAL DO PROJETO

## Sprint Atual: Sprint 0 - Core

### Progresso: 0%

## Checklist Geral

### Infraestrutura
- [ ] Estrutura de diretórios
- [ ] Python venv configurado
- [ ] PostgreSQL configurado
- [ ] Redis configurado
- [ ] Git inicializado

### Sprint 0: Core (0/5)
- [ ] Autenticação (JWT)
- [ ] User model + RBAC
- [ ] Base models
- [ ] Error handling
- [ ] Logging

### Sprint 1: CRM (0/4)
- [ ] Lead model
- [ ] Lead service (IA scoring)
- [ ] Lead APIs
- [ ] Testes

### Sprint 2-38: [A FAZER]

---

## Métricas Atuais

**Linhas de código:** 0
**Arquivos criados:** 0
**Testes escritos:** 0
**Coverage:** 0%
**Commits:** 0

---

## Última Atualização
Data: [INICIAL]
Por: Claude Code - Sessão 001

PROGRESSEOF

# Copiar documentação para o VPS
# (você vai precisar fazer upload dos arquivos .md para /opt/erp-conecta-mais/docs/)

echo "✅ Estrutura preparada!"
echo "Próximo passo: Usar o prompt do Claude Code abaixo"
```

---

## 🤖 PROMPT PARA CLAUDE CODE (COPIE E USE)

### VERSÃO 1: PRIMEIRA SESSÃO (Use na primeira vez)

```
# CONTEXTO INICIAL - ERP CONECTA MAIS V2.0

Olá! Sou o desenvolvedor do ERP Conecta Mais V2.0 e preciso da sua ajuda para desenvolver este sistema completo.

## INFORMAÇÕES DO AMBIENTE

**VPS:** Hostinger KV4
**IP:** 82.25.75.74
**OS:** Linux (verificar distribuição)
**Acesso:** SSH como root

**APLICAÇÃO EXISTENTE:** Conecta Plus (rodando)
**IMPORTANTE:** NÃO MEXER no Conecta Plus! Apenas criar ambiente para ERP Conecta Mais.

**Diretório do Projeto:** `/opt/erp-conecta-mais/`

## DOCUMENTAÇÃO DISPONÍVEL

Tenho documentação completa (~20.000 linhas) com:
- 38 módulos especificados
- Código Python real
- Arquitetura completa
- Roteiro passo a passo

Está em: `/opt/erp-conecta-mais/docs/`

## ARQUIVOS DE CONTROLE

**Sessões:** `/opt/erp-conecta-mais/sessions/SESSION_MANAGER.md`
**Progresso:** `/opt/erp-conecta-mais/docs/PROGRESSO_GERAL.md`
**Roteiro:** `/opt/erp-conecta-mais/docs/ROTEIRO_DEFINITIVO_PASSO_A_PASSO.md`

## REGRAS OBRIGATÓRIAS

### 1. COMUNICAÇÃO
- SEMPRE em Português BR
- Seja claro e objetivo
- Explique o que vai fazer ANTES de fazer
- Peça confirmação em decisões importantes

### 2. INÍCIO DE SESSÃO
Ao começar cada sessão, SEMPRE:

a) Ler `/opt/erp-conecta-mais/sessions/SESSION_MANAGER.md`
b) Identificar última sessão registrada
c) Mostrar resumo:
   ```
   📊 RESUMO DA ÚLTIMA SESSÃO
   
   Data: [data]
   Status: [concluída/pendente]
   
   O que fizemos:
   - Item 1
   - Item 2
   
   Próximos passos planejados:
   1. Passo 1
   2. Passo 2
   
   Progresso geral: X%
   ```
d) Perguntar: "Deseja continuar de onde paramos ou ajustar o plano?"

### 3. DURANTE A SESSÃO
- Seguir o roteiro em `/opt/erp-conecta-mais/docs/ROTEIRO_DEFINITIVO_PASSO_A_PASSO.md`
- NÃO pular etapas
- Validar cada etapa antes de avançar
- Manter PROGRESSO_GERAL.md atualizado
- Fazer commits Git regulares

### 4. FIM DE SESSÃO
Ao finalizar (quando eu disser "vamos encerrar" ou similar), SEMPRE:

a) Criar registro da sessão:
   ```bash
   cat >> /opt/erp-conecta-mais/sessions/SESSION_MANAGER.md << 'SESSIONEOF'
   
   ## SESSÃO XXX - $(date +%Y-%m-%d)
   Status: CONCLUÍDA
   
   ### Planejado:
   [lista do que foi planejado]
   
   ### Executado:
   [lista do que foi feito]
   
   ### Arquivos Criados/Modificados:
   [lista de arquivos]
   
   ### Testes:
   [resultados]
   
   ### Próximos Passos:
   1. [passo 1]
   2. [passo 2]
   
   ### Problemas:
   [se houver]
   
   ---
   SESSIONEOF
   ```

b) Atualizar PROGRESSO_GERAL.md

c) Fazer commit final:
   ```bash
   git add .
   git commit -m "feat: Sessão XXX - [resumo]"
   ```

d) Mostrar resumo final:
   ```
   ✅ SESSÃO ENCERRADA
   
   Hoje fizemos:
   - Item 1
   - Item 2
   
   Progresso: X% → Y%
   
   Próxima sessão faremos:
   1. Passo 1
   2. Passo 2
   
   Até a próxima! 👋
   ```

### 5. QUALIDADE E TESTES
- SEMPRE escrever testes (unitários + integração)
- Coverage mínimo: 80%
- Rodar testes ANTES de commit
- Usar linters (black, pylint, mypy)
- Validar cada funcionalidade

### 6. PROTEÇÕES CRÍTICAS
Implementar conforme roteiro:
- Cache (Redis)
- Circuit breaker
- Sanitização de logs
- Backups automáticos

### 7. SE ALGO DER ERRADO
- Consultar `/opt/erp-conecta-mais/docs/PRE_MORTEM_COMPLETO_ERP.md`
- Tem 100 problemas mapeados com soluções
- Buscar o problema específico
- Aplicar solução documentada

## TECNOLOGIAS

**Backend:**
- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis

**Ferramentas:**
- pytest
- black, isort, pylint, mypy
- Git

## PRIMEIRA TAREFA

Vamos começar pelo ROTEIRO, Fase 3: Setup do Servidor.

Especificamente:

1. Verificar ambiente atual (não mexer no Conecta Plus!)
2. Criar estrutura do ERP Conecta Mais
3. Configurar Python venv
4. Instalar dependências
5. Configurar Git

Está pronto para começar?
```

---

### VERSÃO 2: SESSÕES SUBSEQUENTES (Use nas próximas vezes)

```
# CONTINUAÇÃO - ERP CONECTA MAIS V2.0

Olá novamente! Vamos continuar o desenvolvimento do ERP Conecta Mais.

## LEMBRETE DO CONTEXTO

**Projeto:** ERP Conecta Mais V2.0
**VPS:** 82.25.75.74 (Hostinger KV4)
**Diretório:** `/opt/erp-conecta-mais/`
**Não mexer em:** Conecta Plus (aplicação existente)

## SUAS REGRAS

1. ✅ Sempre em Português BR
2. ✅ Ler última sessão ao começar
3. ✅ Mostrar resumo e próximos passos
4. ✅ Seguir roteiro (não pular etapas)
5. ✅ Registrar sessão ao finalizar
6. ✅ Manter arquivos de controle atualizados

## AÇÃO IMEDIATA

Por favor:

1. Leia `/opt/erp-conecta-mais/sessions/SESSION_MANAGER.md`
2. Mostre resumo da última sessão
3. Mostre progresso atual
4. Pergunte se continuo de onde paramos

Vamos começar! 🚀
```

---

## 📝 TEMPLATE DE SESSÃO (Para Claude Code usar)

```markdown
## SESSÃO XXX - 2024-XX-XX
**Início:** XX:XX | **Fim:** XX:XX
**Status:** [EM ANDAMENTO / CONCLUÍDA / INTERROMPIDA]
**Sprint:** Sprint X - [nome]

### 📋 PLANEJADO
- [ ] Tarefa 1
- [ ] Tarefa 2
- [ ] Tarefa 3

### ✅ EXECUTADO
- [x] Tarefa realizada 1
- [x] Tarefa realizada 2

### 📁 ARQUIVOS CRIADOS/MODIFICADOS
```
backend/core/auth/jwt.py (criado, 150 linhas)
backend/core/models/user.py (criado, 80 linhas)
tests/test_auth.py (criado, 120 linhas)
```

### 🧪 TESTES
```
pytest -v
✅ 15 passed
Coverage: 85%
```

### 📊 MÉTRICAS
- Linhas de código: +350
- Arquivos: +3
- Testes: +15
- Coverage: 0% → 85%

### 🎯 PRÓXIMOS PASSOS
1. Implementar refresh token
2. Criar endpoints de logout
3. Adicionar rate limiting

### ⚠️ PROBLEMAS ENCONTRADOS
- Nenhum / [descrição e solução]

### 💡 APRENDIZADOS
- [insights da sessão]

### 📦 COMMITS
```
feat: implementa autenticação JWT
test: adiciona testes de autenticação
```

---
```

---

## 🎯 CHECKLIST DE VALIDAÇÃO (Claude Code deve seguir)

### Início de Sessão
- [ ] Leu SESSION_MANAGER.md
- [ ] Mostrou resumo da última sessão
- [ ] Mostrou progresso atual
- [ ] Perguntou se continua ou ajusta

### Durante Sessão
- [ ] Seguindo roteiro (não pulou etapas)
- [ ] Criou arquivos com type hints
- [ ] Criou docstrings
- [ ] Criou testes (>80% coverage)
- [ ] Rodou linters
- [ ] Validou funcionalidade
- [ ] Fez commits parciais

### Fim de Sessão
- [ ] Registrou sessão em SESSION_MANAGER.md
- [ ] Atualizou PROGRESSO_GERAL.md
- [ ] Fez commit final
- [ ] Mostrou resumo
- [ ] Listou próximos passos

---

## 🔧 COMANDOS ÚTEIS PARA CLAUDE CODE

### Verificar Progresso
```bash
cat /opt/erp-conecta-mais/docs/PROGRESSO_GERAL.md
```

### Ler Última Sessão
```bash
tail -100 /opt/erp-conecta-mais/sessions/SESSION_MANAGER.md
```

### Status do Projeto
```bash
cd /opt/erp-conecta-mais/backend
source venv/bin/activate
git status
pytest --co -q  # Contar testes
```

### Validar Qualidade
```bash
cd /opt/erp-conecta-mais/backend
black --check .
pylint modules/
pytest --cov
```

---

## 🚨 ALERTAS IMPORTANTES PARA CLAUDE CODE

### ⛔ NUNCA FAZER:
- ❌ Mexer em `/var/www/conecta-plus/` ou similar
- ❌ Alterar configurações do Conecta Plus
- ❌ Pular etapas do roteiro
- ❌ Fazer commit sem testes
- ❌ Esquecer de registrar sessão

### ✅ SEMPRE FAZER:
- ✅ Verificar se não vai afetar Conecta Plus
- ✅ Seguir roteiro linearmente
- ✅ Escrever testes ANTES de commit
- ✅ Atualizar arquivos de controle
- ✅ Registrar sessão ao finalizar

---

## 📚 DOCUMENTOS DE REFERÊNCIA

**Quando tiver dúvida, consulte:**

1. **ROTEIRO_DEFINITIVO_PASSO_A_PASSO.md**
   - Guia principal, passo a passo

2. **PRE_MORTEM_COMPLETO_ERP.md**
   - 100 problemas com soluções

3. **PLANO_REALISTA_E_EFICAZ.md**
   - Como o processo funciona

4. **ERP_PARTE_X.md**
   - Especificação dos módulos

5. **SETUP_COMPLETO_DESENVOLVIMENTO.md**
   - Detalhes técnicos

---

## 💬 EXEMPLOS DE DIÁLOGOS

### Exemplo 1: Início de Sessão

**Claude Code:**
```
📊 RESUMO DA ÚLTIMA SESSÃO

Data: 2024-12-30
Status: Concluída

O que fizemos:
- ✅ Setup do servidor completo
- ✅ Python venv configurado
- ✅ PostgreSQL instalado

Próximos passos planejados:
1. Implementar autenticação JWT
2. Criar User model
3. Configurar RBAC

Progresso geral: 15%

Deseja continuar de onde paramos ou ajustar o plano?
```

**Você:**
```
Vamos continuar! Próxima tarefa: autenticação JWT
```

**Claude Code:**
```
Perfeito! Vou começar pela autenticação JWT.

Seguindo o roteiro (Fase 5, Passo 5.1), vou:

1. Criar backend/core/auth/jwt.py
2. Implementar geração de tokens
3. Implementar validação de tokens
4. Criar testes

Vamos começar criando o módulo JWT. Pronto?
```

### Exemplo 2: Durante Sessão

**Claude Code:**
```
✅ Arquivo criado: backend/core/auth/jwt.py (150 linhas)

Implementei:
- generate_access_token()
- generate_refresh_token()
- verify_token()
- get_current_user()

Agora vou criar os testes. Um momento...

[cria testes]

✅ Testes criados: tests/test_jwt.py

Rodando testes...

pytest tests/test_jwt.py -v

✅ 12 passed
Coverage: 95%

Posso fazer commit?
```

**Você:**
```
Sim, pode commitar
```

**Claude Code:**
```
git add backend/core/auth/jwt.py tests/test_jwt.py
git commit -m "feat: implementa autenticação JWT

- generate_access_token
- verify_token
- testes com 95% coverage"

✅ Commit realizado!

Próximo: Criar User model. Continuar?
```

### Exemplo 3: Fim de Sessão

**Você:**
```
Vamos encerrar por hoje
```

**Claude Code:**
```
Entendido! Vou encerrar a sessão.

Registrando...
✅ Sessão 002 registrada
✅ Progresso atualizado: 15% → 25%
✅ Commit final realizado

📊 RESUMO DA SESSÃO 002

Duração: 3h30min

Hoje fizemos:
✅ Autenticação JWT completa
✅ User model criado
✅ RBAC básico (5 roles)
✅ 35 testes escritos
✅ Coverage: 87%

Arquivos criados:
- backend/core/auth/jwt.py
- backend/core/models/user.py
- tests/test_auth.py
- tests/test_user.py

Progresso: 15% → 25%

Próxima sessão faremos:
1. Implementar refresh token
2. Criar endpoints REST
3. Adicionar rate limiting

Até a próxima! 👋
```

---

## 🎯 COMANDOS DE CONTROLE PARA VOCÊ

### Checar Progresso
```
"Qual nosso progresso atual?"
```

### Ver Sessões Anteriores
```
"Mostre as últimas 3 sessões"
```

### Pular Para Etapa Específica
```
"Vamos pular para implementar [módulo X]"
(Claude deve alertar se está pulando etapas obrigatórias)
```

### Revisar Código
```
"Revise o código que criamos hoje"
```

### Validar Qualidade
```
"Rode todos os testes e validações não aceitando códigos coma qualidade inferior a 99% ou seja 99/100, faça os comitê"
```

---

## ✅ ESTE SISTEMA GARANTE:

1. **Memória Completa**
   - Contexto preservado entre sessões
   - Histórico detalhado
   - Progresso rastreável

2. **Qualidade**
   - Testes obrigatórios
   - Linters automáticos
   - Coverage >80%

3. **Organização**
   - Commits estruturados
   - Documentação atualizada
   - Roteiro seguido

4. **Comunicação**
   - Sempre em PT-BR
   - Resumos claros
   - Próximos passos definidos

---

## 🚀 PRONTO PARA COMEÇAR!

1. Execute a preparação (criar estrutura)
2. Cole o PROMPT VERSÃO 1 no Claude Code
3. Siga as instruções do Claude
4. Nas próximas sessões, use PROMPT VERSÃO 2

**Seu ERP está prestes a nascer! 🎉**
