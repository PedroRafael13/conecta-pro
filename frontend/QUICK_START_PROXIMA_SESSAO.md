# 🚀 QUICK START - PRÓXIMA SESSÃO

**Leia isto PRIMEIRO quando retomar o trabalho!**

---

## 📍 ONDE PARAMOS

✅ **CONCLUÍDO HOJE:**
- 100% dos módulos backend mapeados
- ~15,000 arquivos TypeScript gerados
- Auditoria completa realizada
- Gaps identificados

❌ **PROBLEMA ENCONTRADO:**
- 27 módulos usam `client: 'axios'` (geram só tipos)
- 0% do código usa hooks gerados
- Todo código ainda usa services manuais

---

## 🎯 OBJETIVO DA PRÓXIMA SESSÃO

**Transformar tipos gerados em código funcional**

Atualizar 27 configs de axios → react-query para gerar hooks prontos

---

## ⚡ INÍCIO RÁPIDO (5 minutos)

### 1. Abrir Terminal
```bash
cd /opt/conecta-pro/frontend
```

### 2. Ler Plano Completo
```bash
cat /opt/conecta-pro/PLANO_TRABALHO_ORVAL.md | less
```

### 3. Ver Status Atual
```bash
# Quantos configs têm axios vs react-query
grep -c "client: 'axios'" orval.config.*.ts
grep -c "client: 'react-query'" orval.config.*.ts
```

---

## 🔥 PRIMEIRA AÇÃO (começar aqui!)

### Opção 1: Automática (Recomendada)

```bash
# 1. Criar pasta de scripts se não existir
mkdir -p scripts

# 2. Criar script de atualização
cat > scripts/update-orval-configs.sh << 'EOF'
#!/bin/bash

CONFIGS=(
  "operacional" "government" "recruitment" "audit" "notifications"
  "mobile" "clients" "security-lgpd" "scheduler" "search"
  "bidding" "health-occupational" "contracts" "diarists" "workflows"
  "financial" "ai" "equipment" "services" "integrations"
  "document-kits" "automation" "crm" "campo" "documents"
  "reimbursement" "hr"
)

echo "🚀 Atualizando ${#CONFIGS[@]} configurações Orval..."
echo ""

for module in "${CONFIGS[@]}"; do
  config="orval.config.${module}.ts"

  if [ -f "$config" ]; then
    echo "📝 Atualizando $config..."

    # Substituir client: 'axios' por client: 'react-query'
    sed -i "s/client: 'axios'/client: 'react-query'/g" "$config"

    echo "   ✅ Concluído"
  else
    echo "   ⚠️  Arquivo não encontrado: $config"
  fi
done

echo ""
echo "🎉 Atualização completa!"
echo ""
echo "Próximo passo: Regenerar módulos com 'npm run orval:all'"
EOF

# 3. Dar permissão
chmod +x scripts/update-orval-configs.sh

# 4. Executar
./scripts/update-orval-configs.sh

# 5. Validar (deve mostrar 35 = total de configs)
grep -c "client: 'react-query'" orval.config.*.ts
```

### Opção 2: Manual (Exemplo - 1 módulo)

```bash
# Abrir config do módulo operacional
vim orval.config.operacional.ts

# Procurar por "client: 'axios'"
# Substituir por "client: 'react-query'"

# Adicionar override.query se não existir:
override: {
  mutator: {
    path: './src/lib/api-client.ts',
    name: 'customInstance',
  },
  query: {
    useQuery: true,
    useMutation: true,
    signal: true,
  },
}

# Salvar e sair
```

---

## ✅ VALIDAR MUDANÇAS

```bash
# Verificar quantidade de configs react-query
grep -c "client: 'react-query'" orval.config.*.ts
# Esperado: 35 (era 11, agora todos)

# Ver exemplo de config atualizado
grep -A5 -B5 "client:" orval.config.operacional.ts

# Ver lista de módulos atualizados
grep -l "client: 'react-query'" orval.config.*.ts
```

---

## 🔄 REGENERAR MÓDULOS

### Opção A: Todos de uma vez (cuidado com memória!)

```bash
# Criar script se não existir
cat > scripts/regenerate-all.sh << 'EOF'
#!/bin/bash
for config in orval.config.*.ts; do
  module=$(echo $config | sed 's/orval.config.//' | sed 's/.ts//')
  echo "Gerando $module..."
  npm run orval:$module
done
EOF

chmod +x scripts/regenerate-all.sh
./scripts/regenerate-all.sh
```

### Opção B: Sequencial (mais seguro)

```bash
# Regenerar módulos grandes primeiro
npm run orval:financial  # 3,270 arquivos
npm run orval:audit      # 7,409 arquivos
npm run orval:crm        # 574 arquivos
npm run orval:hr         # 1,490 arquivos

# Depois os médios
npm run orval:campo
npm run orval:operacional
npm run orval:ged

# Por último os pequenos
npm run orval:search
npm run orval:notifications
npm run orval:mobile
```

### Opção C: Testar com 1 módulo primeiro

```bash
# Testar com módulo pequeno
npm run orval:search

# Verificar se hooks foram gerados
ls src/types/generated/search/
grep "useQuery" src/types/generated/search/*.ts
```

---

## 🧪 VALIDAR GERAÇÃO

```bash
# Contar hooks gerados (deve ser > 100)
find src/types/generated -name "*.ts" -exec grep -l "useQuery" {} \; | wc -l

# Ver exemplo de hook gerado
grep -n "export.*use.*Query" src/types/generated/ged/ged-documentos/ged-documentos.ts | head -5

# Build para verificar erros
npm run build
```

---

## 📋 CHECKLIST DA SESSÃO

- [ ] Lido plano completo (PLANO_TRABALHO_ORVAL.md)
- [ ] Atualizado 27 configs (axios → react-query)
- [ ] Regenerado pelo menos 10 módulos
- [ ] Validado que hooks foram gerados
- [ ] Build sem erros TypeScript
- [ ] (Bônus) Migrado 1 página para usar hook gerado
- [ ] (Bônus) Configurado error handling global
- [ ] (Bônus) Criado documentação de uso

---

## 📚 DOCUMENTOS DE REFERÊNCIA

```bash
# Plano completo (PRINCIPAL - ler primeiro!)
cat /opt/conecta-pro/PLANO_TRABALHO_ORVAL.md

# Resumo da sessão anterior
cat /opt/conecta-pro/RESUMO_SESSAO_31JAN.md

# Relatório de auditoria
cat /opt/conecta-pro/frontend/ORVAL_AUDIT_REPORT.md
```

---

## 🆘 SE ALGO DER ERRADO

### Erro ao regenerar módulo
```bash
# Limpar pasta generated do módulo
rm -rf src/types/generated/[modulo]

# Tentar novamente
npm run orval:[modulo]
```

### Erro de TypeScript
```bash
# Ver erros
npm run type-check

# Limpar build
rm -rf .next
npm run build
```

### Erro de memória
```bash
# Aumentar limite do Node.js
export NODE_OPTIONS="--max-old-space-size=8192"

# Regenerar
npm run orval:[modulo]
```

### Reverter mudanças
```bash
# Ver mudanças
git diff orval.config.*.ts

# Reverter tudo
git checkout -- orval.config.*.ts

# Reverter só 1 arquivo
git checkout -- orval.config.operacional.ts
```

---

## 💡 DICAS

1. **Começar pequeno**: Teste com 1-2 módulos antes de regenerar todos
2. **Fazer backup**: `git add . && git commit -m "wip: antes de regenerar orval"`
3. **Validar incrementalmente**: Regenerou 5 módulos? Faça build e valide
4. **Documentar problemas**: Se encontrar erro, anotar para resolver depois
5. **Pausar se necessário**: Melhor fazer bem feito do que rápido e quebrado

---

## 🎯 META DA SESSÃO

**MÍNIMO (2h):**
- ✅ Atualizar 27 configs
- ✅ Regenerar pelo menos 15 módulos
- ✅ Validar hooks gerados

**IDEAL (4h):**
- ✅ Tudo do mínimo
- ✅ Regenerar TODOS os 35 módulos
- ✅ Migrar 1 página para usar hooks gerados (piloto GED)
- ✅ Configurar error handling global

**EXCELENTE (5h+):**
- ✅ Tudo do ideal
- ✅ Criar documentação de uso
- ✅ Criar script orval:all
- ✅ Atualizar CLAUDE.md

---

## 🚀 COMEÇAR AGORA!

```bash
cd /opt/conecta-pro/frontend
./scripts/update-orval-configs.sh
npm run orval:search  # Testar com módulo pequeno
```

**Boa sorte! 🍀**

---

**Criado em:** 2026-01-31
**Para:** Próxima sessão
**Prioridade:** CRÍTICA
**Tempo estimado:** 2-4 horas
