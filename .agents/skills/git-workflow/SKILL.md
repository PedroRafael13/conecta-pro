---
title: Git Workflow
description: Fluxo de trabalho Git com commits em português
language: português
---

# Git Workflow

Fluxo de trabalho Git para equipe Conecta PRO.

## Estrutura de Branches

```
main        # Produção (protegida)
develop     # Integração (protegida)
feature/*   # Novas funcionalidades
hotfix/*    # Correções urgentes
release/*   # Preparação de release
```

## Commits em Português

### Padrão
```
<tipo>(<escopo>): <descrição>

[corpo opcional]

[rodapé opcional]
```

### Tipos

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| feat | Nova funcionalidade | `feat(faturamento): adiciona exportação PDF` |
| fix | Correção de bug | `fix(escala): corrige cálculo de horas` |
| docs | Documentação | `docs(api): atualiza swagger` |
| style | Formatação | `style: remove espaços em branco` |
| refactor | Refatoração | `refactor(esocial): simplifica parser` |
| test | Testes | `test(nfse): adiciona testes de integração` |
| chore | Manutenção | `chore: atualiza dependências` |

### Exemplos

```bash
# Feature
feat(relatorios): adiciona dashboard financeiro mensal

# Bugfix
fix(escala): corrige fuso horário em rondas noturnas

# Breaking change
feat(api)!: altera formato de resposta do endpoint /faturas

# Com referência
fix(esocial): corrige envio S-1200

Closes #1234
```

## Comandos

```bash
# Nova feature
git checkout -b feature/nome-da-feature develop

# Finalizar feature
git checkout develop
git merge --no-ff feature/nome-da-feature
git branch -d feature/nome-da-feature

# Hotfix
git checkout -b hotfix/corrigir-bug main
# ... correção ...
git checkout main
git merge --no-ff hotfix/corrigir-bug
git checkout develop
git merge --no-ff hotfix/corrigir-bug
```

## Checklist de PR

- [ ] Branch atualizada com develop
- [ ] Commits seguem padrão em português
- [ ] Testes passando
- [ ] Code review aprovado
- [ ] Sem conflitos
- [ ] Changelog atualizado (se necessário)
