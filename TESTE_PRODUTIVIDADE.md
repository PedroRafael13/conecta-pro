# Checklist de Testes - Sistema de Produtividade

## Status da Implementação

✅ **Backend**
- [x] Módulo search criado
- [x] Controller search_controller.py
- [x] Router registrado no main
- [x] Endpoint /api/v1/search funcionando
- [x] Busca em 5 entidades (colaborador, posto, escala, ocorrência, ronda)

✅ **Frontend - Hooks**
- [x] useKeyboardShortcuts.ts criado
- [x] useGlobalShortcuts implementado
- [x] Suporte a Ctrl/Alt/Shift
- [x] Ignorar inputs automaticamente

✅ **Frontend - Componentes**
- [x] CommandPalette.tsx criado
- [x] GlobalSearch.tsx criado
- [x] HelpOverlay.tsx criado
- [x] SearchTrigger.tsx criado
- [x] ProductivityProvider.tsx criado

✅ **Frontend - Integração**
- [x] ProductivityProvider no providers.tsx
- [x] SearchTrigger no layout de módulos
- [x] Atalhos globais funcionais

✅ **Documentação**
- [x] ATALHOS_TECLADO.md criado
- [x] README_PRODUTIVIDADE.md criado
- [x] Este checklist de testes

## Testes Manuais

### 1. Atalhos de Teclado

#### 1.1 Busca Global (/)
- [ ] Pressionar `/` fora de input abre modal de busca
- [ ] Pressionar `/` dentro de input NÃO abre modal
- [ ] Input de busca recebe foco automaticamente
- [ ] Modal tem backdrop escuro com blur
- [ ] Esc fecha o modal

#### 1.2 Command Palette (Ctrl+K)
- [ ] Ctrl+K abre command palette
- [ ] Cmd+K funciona no Mac
- [ ] Input recebe foco automaticamente
- [ ] Comandos aparecem agrupados por categoria
- [ ] Busca fuzzy funciona (digitar "novo" filtra comandos)
- [ ] Esc fecha o modal

#### 1.3 Toggle Sidebar (Ctrl+B)
- [ ] Ctrl+B alterna sidebar (apenas desktop)
- [ ] Animação suave
- [ ] Ícones se ajustam
- [ ] Não funciona em mobile

#### 1.4 Help Overlay (Shift+?)
- [ ] Shift+? abre overlay de ajuda
- [ ] Lista todos os atalhos
- [ ] Atalhos agrupados por categoria
- [ ] Formatação visual das teclas
- [ ] Esc fecha o modal

#### 1.5 Navegação entre Módulos
- [ ] Alt+1 navega para Dashboard
- [ ] Alt+2 navega para Operacional
- [ ] Alt+3 navega para Financeiro
- [ ] Alt+4 navega para CRM

#### 1.6 ESC Universal
- [ ] Esc fecha busca se estiver aberta
- [ ] Esc fecha command palette se estiver aberto
- [ ] Esc fecha help se estiver aberto
- [ ] Esc funciona mesmo em inputs

### 2. Busca Global

#### 2.1 Interface
- [ ] SearchTrigger visível no header (desktop e tablet)
- [ ] Botão mostra ícone de lupa
- [ ] Botão mostra texto "Buscar..." em desktop
- [ ] Botão mostra atalho "/" em desktop
- [ ] Click no botão abre modal

#### 2.2 Funcionalidade
- [ ] Debounce de 300ms funciona (não busca a cada letra)
- [ ] Loading spinner aparece durante busca
- [ ] Resultados aparecem agrupados por tipo
- [ ] Ícones corretos para cada tipo
- [ ] Máximo 20 resultados
- [ ] Tempo de resposta < 200ms mostrado

#### 2.3 Navegação com Teclado
- [ ] ↓ seleciona próximo resultado
- [ ] ↑ seleciona resultado anterior
- [ ] Enter abre resultado selecionado
- [ ] Mouse hover também seleciona
- [ ] Indicador visual de seleção

#### 2.4 Tipos de Busca
- [ ] Busca colaborador por nome
- [ ] Busca colaborador por CPF
- [ ] Busca colaborador por matrícula
- [ ] Busca posto por nome
- [ ] Busca posto por código
- [ ] Busca escala por nome
- [ ] Busca ocorrência por título
- [ ] Busca ronda por código

#### 2.5 Resultados
- [ ] Title correto
- [ ] Description informativa
- [ ] URL funcional (navega corretamente)
- [ ] Ícone apropriado para tipo
- [ ] Label de categoria correto

### 3. Command Palette

#### 3.1 Comandos de Navegação
- [ ] "Novo Posto" navega para /postos/novo
- [ ] "Novo Colaborador" navega para /colaboradores/novo
- [ ] "Nova Ocorrência" navega para /ocorrencias/nova

#### 3.2 Comandos de Ação
- [ ] "Nova Escala" navega para /escalas/nova
- [ ] "Exportar Dados" (implementar lógica)

#### 3.3 Comandos de Busca
- [ ] "Buscar Colaborador" navega para colaboradores com flag search

#### 3.4 Interface
- [ ] Ícones aparecem para cada comando
- [ ] Descrições aparecem
- [ ] Categorias separadas visualmente
- [ ] Busca fuzzy funciona
- [ ] Footer com dicas de navegação

### 4. Help Overlay

#### 4.1 Conteúdo
- [ ] Categoria "Geral" com 5 atalhos
- [ ] Categoria "Navegação" com 4 atalhos
- [ ] Categoria "Ações Contextuais" (vazia por ora)
- [ ] Total de atalhos correto no footer

#### 4.2 Formatação
- [ ] Teclas formatadas corretamente (Ctrl+K, Alt+1, etc)
- [ ] Descrições claras
- [ ] Header com título e descrição
- [ ] Footer com dica Esc

### 5. Backend

#### 5.1 Endpoint
```bash
# Testar endpoint manualmente
curl "http://localhost:8080/api/v1/search?q=teste&limit=5"
```

- [ ] Status 200 OK
- [ ] Response JSON válido
- [ ] Schema correto (results, total, took_ms)
- [ ] took_ms < 200ms

#### 5.2 Validação
- [ ] Query vazia retorna erro 422
- [ ] Limit > 100 é aceito mas limitado
- [ ] Caracteres especiais são sanitizados
- [ ] SQL injection não funciona

#### 5.3 Performance
- [ ] Busca simples < 100ms
- [ ] Busca complexa < 200ms
- [ ] Máximo 20 resultados respeitado
- [ ] LIMIT aplicado no SQL

### 6. Responsividade

#### 6.1 Desktop (> 1024px)
- [ ] SearchTrigger visível no header
- [ ] Atalho "/" mostrado
- [ ] Todos os modais centralizados
- [ ] Sidebar toggle funciona

#### 6.2 Tablet (768px - 1024px)
- [ ] SearchTrigger visível
- [ ] Modais adaptados
- [ ] Navegação com teclado funciona

#### 6.3 Mobile (< 768px)
- [ ] SearchTrigger oculto (usar menu mobile)
- [ ] Modais em tela cheia ou adaptados
- [ ] Touch navigation funciona

### 7. Acessibilidade

#### 7.1 ARIA
- [ ] Botões têm aria-label
- [ ] Modais têm role="dialog"
- [ ] Inputs têm labels apropriados

#### 7.2 Keyboard
- [ ] Tab navega entre elementos
- [ ] Enter ativa botões/comandos
- [ ] Esc fecha modais
- [ ] Foco visível em todos os elementos

#### 7.3 Screen Readers
- [ ] Títulos são anunciados
- [ ] Estados são anunciados (aberto/fechado)
- [ ] Resultados são anunciados

### 8. Compatibilidade

#### 8.1 Navegadores
- [ ] Chrome/Edge (Windows)
- [ ] Firefox (Windows)
- [ ] Safari (Mac)
- [ ] Chrome (Mac)

#### 8.2 Sistemas Operacionais
- [ ] Ctrl vs Cmd detectado automaticamente
- [ ] Atalhos funcionam no Mac
- [ ] Atalhos funcionam no Windows
- [ ] Atalhos funcionam no Linux

### 9. Edge Cases

#### 9.1 Busca
- [ ] Query muito longa (> 100 chars)
- [ ] Caracteres especiais (!@#$%)
- [ ] Unicode (中文, العربية)
- [ ] SQL keywords (SELECT, DROP, etc)
- [ ] Sem resultados mostra mensagem
- [ ] Erro de API mostra mensagem

#### 9.2 Atalhos
- [ ] Múltiplos modais não abrem simultaneamente
- [ ] Atalhos não conflitam entre si
- [ ] Atalhos em inputs são ignorados
- [ ] Atalhos desabilitados não executam

### 10. Integração

#### 10.1 Providers
- [ ] ProductivityProvider no topo da árvore
- [ ] Context acessível em toda aplicação
- [ ] Múltiplos useProductivity() funcionam

#### 10.2 Navegação
- [ ] URLs geradas estão corretas
- [ ] Navegação fecha modais
- [ ] Browser back funciona normalmente

## Comandos de Teste

### Rebuild e Restart

```bash
# Backend
cd /opt/conecta-pro/backend
docker compose build backend --no-cache
docker compose up -d backend

# Frontend
cd /opt/conecta-pro/frontend
npm run build
```

### Verificar Logs

```bash
# Backend
docker logs -f conecta-backend

# Frontend
npm run dev
```

### Testar API

```bash
# Busca simples
curl "http://localhost:8080/api/v1/search?q=silva"

# Busca com limite
curl "http://localhost:8080/api/v1/search?q=teste&limit=10"

# Busca vazia (deve dar erro)
curl "http://localhost:8080/api/v1/search?q="
```

## Critérios de Aceitação

- [ ] Todos os atalhos funcionam
- [ ] Busca retorna resultados < 200ms
- [ ] Command palette tem todos os comandos
- [ ] Help overlay mostra todos os atalhos
- [ ] Navegação com teclado 100% funcional
- [ ] Responsivo em todos os breakpoints
- [ ] Acessível (ARIA, keyboard, screen readers)
- [ ] Sem erros no console
- [ ] Documentação completa

## Status Final

Data: _____________
Testador: _____________

- [ ] Aprovado para produção
- [ ] Necessita correções (listar abaixo)

### Correções Necessárias:
1.
2.
3.

---

**Versão:** 1.0.0
**Data:** 2026-01-26
