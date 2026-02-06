# 🚀 GUIA DE EXECUÇÃO - VPS CONECTA MAIS
**Upload do MacBook → Execução no VPS com Claude Code**

---

## 📋 INFORMAÇÕES DO SERVIDOR

```
IP: 82.25.75.74
Usuário: root
Senha: JsJ618908@#82
Pasta Local (Mac): ~/jjesus/projetos/erp/
Pasta Remota (VPS): /opt/erp-conecta-mais/docs/
```

---

## 🎯 PASSO A PASSO COMPLETO

### FASE 1: PREPARAR ARQUIVOS NO MAC (5 min)

#### 1.1 - Criar Estrutura Local

```bash
# No seu MacBook, abrir Terminal
cd ~
mkdir -p jjesus/projetos/erp
cd jjesus/projetos/erp

# Verificar que está no lugar certo
pwd
# Deve mostrar: /Users/seu_usuario/jjesus/projetos/erp
```

#### 1.2 - Baixar os Arquivos

Baixe os 6 arquivos que te enviei:
1. `conecta-mais-audit-system.sh`
2. `conecta-mais-quality-skills.md`
3. `conecta-mais-quality-prompts.md`
4. `.pylintrc.conecta-mais`
5. `GUIA-COMPLETO-CONECTA-MAIS.md`
6. `RESUMO-EXECUTIVO.md`

E coloque todos em: `~/jjesus/projetos/erp/`

#### 1.3 - Verificar Arquivos

```bash
cd ~/jjesus/projetos/erp
ls -la

# Deve listar os 6 arquivos
```

---

### FASE 2: UPLOAD PARA VPS (5 min)

#### 2.1 - Upload Via SCP (Método Simples)

```bash
# No Terminal do Mac
cd ~/jjesus/projetos/erp

# Upload TODOS os arquivos de uma vez
scp -r * root@82.25.75.74:/opt/erp-conecta-mais/docs/

# Vai pedir a senha: JsJ618908@#82
# Digite e pressione Enter
```

#### 2.2 - Verificar Upload

```bash
# Conectar no VPS
ssh root@82.25.75.74
# Senha: JsJ618908@#82

# Verificar que arquivos estão lá
ls -la /opt/erp-conecta-mais/docs/

# Deve listar os 6 arquivos
```

---

### FASE 3: CONFIGURAR VPS (10 min)

#### 3.1 - Dar Permissões ao Script

```bash
# Ainda no VPS
cd /opt/erp-conecta-mais/docs

# Tornar script executável
chmod +x conecta-mais-audit-system.sh

# Verificar
ls -la conecta-mais-audit-system.sh
# Deve mostrar: -rwxr-xr-x (com x = executável)
```

#### 3.2 - Copiar Configuração Pylint

```bash
# Copiar para a raiz do projeto
cp .pylintrc.conecta-mais /opt/erp-conecta-mais/backend/.pylintrc

# Verificar
ls -la /opt/erp-conecta-mais/backend/.pylintrc
```

#### 3.3 - Criar Diretório de Reports

```bash
# Criar pasta para relatórios
mkdir -p /opt/erp-conecta-mais/docs/quality-reports

# Verificar
ls -la /opt/erp-conecta-mais/docs/
```

#### 3.4 - Instalar Pylint (se ainda não tiver)

```bash
# Verificar se Pylint está instalado
which pylint

# Se NÃO estiver, instalar:
pip install --break-system-packages pylint

# Verificar versão
pylint --version
```

---

### FASE 4: TESTE INICIAL (5 min)

#### 4.1 - Testar Script de Auditoria

```bash
# Testar em um módulo perfeito (config)
cd /opt/erp-conecta-mais/docs
./conecta-mais-audit-system.sh /opt/erp-conecta-mais config full
```

**Resultado Esperado**:
```
╔═══════════════════════════════════════════════════════════╗
║  CONECTA MAIS - AUDITORIA SPRINT 31                       ║
╚═══════════════════════════════════════════════════════════╝

▶ MÓDULO: config
  Score Atual: 10.00 | Arquivos: 15 | Categoria: GESTAO

  ├─ Executando Pylint...
  ├─ Score: 10.00/10
  └─ PERFEITO! 10.00/10 ✨
```

#### 4.2 - Testar em Módulo com Issues

```bash
# Testar em módulo que precisa correção
./conecta-mais-audit-system.sh /opt/erp-conecta-mais clients full
```

**Resultado Esperado**:
```
▶ MÓDULO: clients
  Score Atual: 9.98 | Arquivos: 16 | Categoria: GESTAO

  ├─ Executando Pylint...
  ├─ Score: 9.98/10
  └─ Muito bom! Faltam 0.02 pontos para 10.00

  Issues encontrados (5 total):
    - too-many-branches: 2
    - too-many-locals: 1
    - ...
```

✅ **Se funcionou, está TUDO PRONTO!**

---

### FASE 5: EXECUTAR COM CLAUDE CODE (Sprints Q1-Q4)

#### 5.1 - Verificar Claude Code no VPS

```bash
# Verificar se Claude Code está instalado
which claude-code

# Verificar versão
claude-code --version
```

#### 5.2 - Executar Sprint Q1 - Módulo CLIENTS

```bash
# Ainda no VPS, em /opt/erp-conecta-mais/docs

# Executar Claude Code com a skill e prompt
claude-code \
  --skill=/opt/erp-conecta-mais/docs/conecta-mais-quality-skills.md \
  --prompt="Executar correções do módulo CLIENTS conforme PROMPT Q1.1 em conecta-mais-quality-prompts.md. 

CONTEXTO:
Módulo: clients
Score atual: 9.98/10
Gap: 0.02 (5 issues)
Issues: too-many-branches (2), too-many-locals (1)

AÇÕES:
1. Aplicar Skill 2 (Too-many-locals/branches)
2. Adicionar pylint disable onde apropriado
3. Refatorar se necessário
4. Validar que testes passam

CRITÉRIOS:
- Pylint: 10.00/10
- Funcionalidade: mantida
- Testes: todos passando

ENTREGUE:
Módulo clients com 10.00/10" \
  /opt/erp-conecta-mais/backend/modules/clients
```

#### 5.3 - Validar Correção

```bash
# Após Claude Code finalizar, auditar novamente
cd /opt/erp-conecta-mais/docs
./conecta-mais-audit-system.sh /opt/erp-conecta-mais clients full

# Verificar se score = 10.00/10 ✨
```

#### 5.4 - Repetir para Outros Módulos do Sprint Q1

```bash
# SERVICES
claude-code \
  --skill=/opt/erp-conecta-mais/docs/conecta-mais-quality-skills.md \
  --prompt="Executar PROMPT Q1.2 para módulo SERVICES (ver conecta-mais-quality-prompts.md)" \
  /opt/erp-conecta-mais/backend/modules/services

# Validar
./conecta-mais-audit-system.sh /opt/erp-conecta-mais services full

# FACILITIES
claude-code \
  --skill=/opt/erp-conecta-mais/docs/conecta-mais-quality-skills.md \
  --prompt="Executar PROMPT Q1.3 para módulo FACILITIES (ver conecta-mais-quality-prompts.md)" \
  /opt/erp-conecta-mais/backend/modules/facilities

# Validar
./conecta-mais-audit-system.sh /opt/erp-conecta-mais facilities full

# VISITORS
claude-code \
  --skill=/opt/erp-conecta-mais/docs/conecta-mais-quality-prompts.md \
  --prompt="Executar PROMPT Q1.4 para módulo VISITORS (ver conecta-mais-quality-prompts.md)" \
  /opt/erp-conecta-mais/backend/modules/visitors

# Validar
./conecta-mais-audit-system.sh /opt/erp-conecta-mais visitors full
```

---

### FASE 6: AUDITORIA COMPLETA (Após cada Sprint)

#### 6.1 - Auditoria de Sprint Completo

```bash
# Auditar Sprint Q1 completo
cd /opt/erp-conecta-mais/docs
./conecta-mais-audit-system.sh /opt/erp-conecta-mais all q1
```

#### 6.2 - Auditoria GERAL (Todos os 21 Módulos)

```bash
# Auditar TUDO
./conecta-mais-audit-system.sh /opt/erp-conecta-mais all full

# Vai gerar relatório em:
# /opt/erp-conecta-mais/docs/quality-reports/AUDIT_SUMMARY.json
```

#### 6.3 - Ver Relatórios

```bash
# Ver relatório summary
cat /opt/erp-conecta-mais/docs/quality-reports/AUDIT_SUMMARY.json

# Ver relatório de um módulo específico
cat /opt/erp-conecta-mais/docs/quality-reports/clients_report.json

# Ver output Pylint detalhado
cat /opt/erp-conecta-mais/docs/quality-reports/clients_pylint.txt
```

---

## 📊 WORKFLOW DIÁRIO RECOMENDADO

### Manhã (Planejamento)

```bash
# 1. SSH no VPS
ssh root@82.25.75.74

# 2. Navegar para docs
cd /opt/erp-conecta-mais/docs

# 3. Auditar sprint atual
./conecta-mais-audit-system.sh /opt/erp-conecta-mais all q1

# 4. Identificar próximo módulo a corrigir
# Ver em conecta-mais-quality-prompts.md
```

### Tarde (Execução)

```bash
# 5. Executar Claude Code no módulo escolhido
claude-code \
  --skill=conecta-mais-quality-skills.md \
  --prompt="[prompt específico do módulo]" \
  /caminho/modulo

# 6. Validar correção
./conecta-mais-audit-system.sh /opt/erp-conecta-mais MODULE full

# 7. Se 10.00 → Commit e próximo
# Se < 10.00 → Corrigir issues remanescentes
```

### Noite (Validação)

```bash
# 8. Executar testes
cd /opt/erp-conecta-mais/backend
pytest --cov

# 9. Commit do dia
git add .
git commit -m "refactor(MODULE): Elevado para 10.00/10 - Sprint Q1"

# 10. Atualizar tracking
# Editar QUALITY-TRACKING.md
```

---

## 🔧 COMANDOS ÚTEIS NO VPS

### Navegação Rápida

```bash
# Ir para docs
cd /opt/erp-conecta-mais/docs

# Ir para backend
cd /opt/erp-conecta-mais/backend

# Voltar para docs
cd ../docs
```

### Auditoria Rápida

```bash
# Alias útil (adicionar ao ~/.bashrc)
alias audit-sprint='cd /opt/erp-conecta-mais/docs && ./conecta-mais-audit-system.sh /opt/erp-conecta-mais'

# Uso:
audit-sprint all q1
audit-sprint clients full
audit-sprint all full
```

### Ver Issues de um Módulo

```bash
# Pylint direto
cd /opt/erp-conecta-mais/backend
pylint modules/clients --recursive=y | grep "rated at"

# Ver issues detalhados
pylint modules/clients --recursive=y > ~/clients-issues.txt
less ~/clients-issues.txt
```

---

## 📝 TRACKING DE PROGRESSO

### Criar Arquivo de Tracking

```bash
# Criar tracking no VPS
cat > /opt/erp-conecta-mais/docs/QUALITY-TRACKING.md <<'EOF'
# ERP CONECTA MAIS - QUALITY TRACKING

**Meta**: 21/21 módulos em 10.00/10
**Início**: 2026-01-01
**Status Atual**: Sprint Q1

## Sprint Q1 (Wins Rápidos)
- [ ] clients (9.98 → 10.00) - 5 issues
- [ ] services (9.97 → 10.00) - 7 issues
- [ ] facilities (9.95 → 10.00) - 18 issues
- [ ] visitors (9.94 → 10.00) - 20 issues

## Sprint Q2 (Intermediários)
- [ ] ged (9.87 → 10.00)
- [ ] occurrences (9.78 → 10.00)
- [ ] crm (9.73 → 10.00)
- [ ] operations (9.68 → 10.00)

## Sprint Q3 (Complexos)
- [ ] recruitment (9.68 → 10.00)
- [ ] hr (9.65 → 10.00)
- [ ] core (9.64 → 10.00)
- [ ] residents (9.64 → 10.00)
- [ ] financial (9.60 → 10.00)

## Sprint Q4 (Críticos)
- [ ] equipment_management (9.60 → 10.00)
- [ ] field_service (9.52 → 10.00)

## Módulos Perfeitos ✨
- [x] config (10.00)
- [x] audit (10.00)
- [x] reports (10.00)
- [x] diarists (10.00)
- [x] document_kits (10.00)
- [x] integrations (10.00)

## Log de Progresso
```bash
# Adicionar entry
echo "$(date): Módulo clients elevado para 10.00/10" >> LOG.md
```

**Última atualização**: $(date)
EOF
```

### Atualizar Tracking

```bash
# Após completar um módulo
cd /opt/erp-conecta-mais/docs

# Marcar como completo
sed -i 's/- \[ \] clients/- [x] clients/' QUALITY-TRACKING.md

# Adicionar log
echo "$(date '+%Y-%m-%d %H:%M'): clients 9.98 → 10.00 ✅" >> QUALITY-TRACKING.md

# Ver progresso
cat QUALITY-TRACKING.md
```

---

## 🎯 CHECKLIST DE CADA MÓDULO

```bash
# Para cada módulo, seguir este checklist:

[ ] 1. Auditar estado atual
   ./conecta-mais-audit-system.sh /opt/erp-conecta-mais MODULE full

[ ] 2. Ler prompt específico
   less conecta-mais-quality-prompts.md
   # Buscar: /PROMPT QX.Y

[ ] 3. Executar Claude Code
   claude-code --skill=skills.md --prompt="..." /caminho/modulo

[ ] 4. Validar resultado
   ./conecta-mais-audit-system.sh /opt/erp-conecta-mais MODULE full

[ ] 5. Se < 10.00: Corrigir issues manualmente
   - Ver relatório: quality-reports/MODULE_pylint.txt
   - Aplicar skills apropriadas
   - Re-auditar

[ ] 6. Executar testes
   cd /opt/erp-conecta-mais/backend
   pytest tests/test_MODULE.py -v

[ ] 7. Commit
   git add .
   git commit -m "refactor(MODULE): Elevado para 10.00/10"

[ ] 8. Atualizar tracking
   sed -i 's/- \[ \] MODULE/- [x] MODULE/' QUALITY-TRACKING.md

[ ] 9. Próximo módulo
```

---

## 🚨 TROUBLESHOOTING

### Problema: SSH não conecta

```bash
# Verificar conexão
ping 82.25.75.74

# Tentar com verbose
ssh -v root@82.25.75.74
```

### Problema: SCP falha

```bash
# Verificar pasta existe no VPS
ssh root@82.25.75.74 "ls -la /opt/erp-conecta-mais/docs"

# Se não existe, criar
ssh root@82.25.75.74 "mkdir -p /opt/erp-conecta-mais/docs"

# Re-tentar upload
scp -r * root@82.25.75.74:/opt/erp-conecta-mais/docs/
```

### Problema: Script não executa

```bash
# Verificar permissões
ls -la conecta-mais-audit-system.sh

# Dar permissão
chmod +x conecta-mais-audit-system.sh

# Testar
./conecta-mais-audit-system.sh /opt/erp-conecta-mais config full
```

### Problema: Pylint não encontrado

```bash
# Instalar
pip install --break-system-packages pylint

# Verificar
which pylint
pylint --version
```

### Problema: Claude Code não encontrado

```bash
# Verificar instalação
which claude-code

# Se não estiver, instalar
# [seguir instruções de instalação do Claude Code]
```

### Problema: Módulo não encontrado

```bash
# Verificar estrutura
ls -la /opt/erp-conecta-mais/backend/modules/

# Verificar módulo específico
ls -la /opt/erp-conecta-mais/backend/modules/clients/

# Se core:
ls -la /opt/erp-conecta-mais/backend/core/
```

---

## 📱 ACESSO REMOTO DO MAC

### Manter Sessão Ativa

```bash
# Usar screen ou tmux para não perder progresso

# Instalar screen (se necessário)
apt-get install screen

# Iniciar sessão
screen -S conecta-quality

# Trabalhar normalmente...

# Desconectar (mantém rodando)
# Pressione: Ctrl+A depois D

# Reconectar depois
ssh root@82.25.75.74
screen -r conecta-quality
```

### Executar em Background

```bash
# Para tarefas longas
nohup ./conecta-mais-audit-system.sh /opt/erp-conecta-mais all full > audit.log 2>&1 &

# Ver progresso
tail -f audit.log

# Matar se necessário
jobs
kill %1
```

---

## 🎉 QUANDO ATINGIR 100%

```bash
# Auditoria final
./conecta-mais-audit-system.sh /opt/erp-conecta-mais all full

# Deve mostrar:
# 🏆 EXCELÊNCIA ATINGIDA! Todos os módulos em 10.00/10!

# Gerar certificado
cat > /opt/erp-conecta-mais/docs/EXCELLENCE-CERTIFICATE.md <<'EOF'
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ERP CONECTA MAIS V3.0                                   ║
║   CERTIFICADO DE EXCELÊNCIA EM QUALIDADE DE CÓDIGO       ║
║                                                           ║
║   ✅ 21/21 Módulos: 10.00/10                              ║
║   ✅ 754 Arquivos: 100% Perfeitos                         ║
║   ✅ ~340 Issues: Todos Resolvidos                        ║
║   ✅ Média Geral: 10.00/10                                ║
║   ✅ Status: CÓDIGO DE CLASSE MUNDIAL                     ║
║                                                           ║
║   Data: $(date)                                           ║
║   Certificado por: Sistema de Qualidade Conecta Mais     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
EOF

# Commit final
git add .
git commit -m "feat: ERP Conecta Mais atingiu 100% de qualidade - 21/21 módulos perfeitos"
git tag v3.0.0-quality-100

# Celebrar! 🎉🎊✨
```

---

**PRONTO! TUDO AJUSTADO PARA SEU VPS!** 🚀

Estrutura:
- MacBook: `~/jjesus/projetos/erp/` (arquivos locais)
- VPS: `/opt/erp-conecta-mais/docs/` (arquivos no servidor)
- Execução: Diretamente no VPS via SSH

**Próximo passo**: Executar FASE 1 no seu Mac! 💪
