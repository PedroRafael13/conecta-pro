# Testes E2E - Módulo CRM

Este diretório contém os testes end-to-end completos para o módulo CRM do Conecta Pro.

## Estrutura dos Testes

```
e2e/crm/
├── clientes-list.spec.ts    # Testes de listagem de clientes
├── clientes-create.spec.ts  # Testes de criação de clientes
├── clientes-edit.spec.ts    # Testes de edição e exclusão de clientes
├── leads.spec.ts            # CRUD completo de leads
├── oportunidades.spec.ts    # Pipeline de oportunidades
├── propostas.spec.ts        # Gestão de propostas comerciais
├── contatos.spec.ts         # Gestão de contatos
└── README.md                # Este arquivo
```

## Cobertura de Testes

### Clientes
- ✅ Carregamento da página e título
- ✅ Cards de estatísticas (Total, Ativos, Condomínios, Bloqueados)
- ✅ Tabela com colunas corretas
- ✅ Filtros por texto (nome, CNPJ, email)
- ✅ Filtros por status
- ✅ Badges de status e tipo com cores
- ✅ Menu de ações (Ver detalhes, Editar, Deletar)
- ✅ Estado vazio
- ✅ Loading e erro na API

### Criação de Clientes
- ✅ Abertura do modal
- ✅ Todos os campos do formulário
- ✅ Validação de campos obrigatórios
- ✅ Criação com sucesso
- ✅ Cancelamento sem salvar
- ✅ Fechar com ESC
- ✅ Estado de loading
- ✅ Tratamento de erro da API

### Edição de Clientes
- ✅ Abertura do modal de edição
- ✅ Preenchimento com dados existentes
- ✅ Alteração de dados
- ✅ Modal de detalhes
- ✅ Modal de confirmação de exclusão
- ✅ Exclusão com sucesso
- ✅ Tratamento de erros

### Leads
- ✅ Listagem com métricas
- ✅ Filtros por status
- ✅ Filtros por texto
- ✅ Badges de status coloridos
- ✅ Valores formatados como moeda
- ✅ Estado vazio e erro
- ✅ Skeleton loading

### Oportunidades
- ✅ Pipeline com cards de estatísticas
- ✅ Filtros por estágio
- ✅ Filtros por texto
- ✅ Badges de estágio (Qualificado, Proposta, Negociação, Ganho, Perdido)
- ✅ Probabilidade formatada
- ✅ Modal de criação/edição
- ✅ Paginação
- ✅ Erros e loading

### Propostas
- ✅ Listagem com estatísticas
- ✅ Filtros por status
- ✅ Formulário inline para criação
- ✅ Modo de edição inline
- ✅ Detalhes da proposta
- ✅ Badges de status (Rascunho, Enviada, Aprovada, Rejeitada)
- ✅ Formatação de valores e datas

### Contatos
- ✅ Listagem
- ✅ Formulário inline
- ✅ CRUD completo (local)
- ✅ Filtros por busca
- ✅ Ícones de contato
- ✅ Detalhes do contato

## Executando os Testes

### Executar todos os testes do CRM
```bash
cd /opt/conecta-pro/frontend
npx playwright test e2e/crm/
```

### Executar testes específicos
```bash
# Apenas clientes
npx playwright test e2e/crm/clientes-

# Apenas leads
npx playwright test e2e/crm/leads.spec.ts

# Apenas oportunidades
npx playwright test e2e/crm/oportunidades.spec.ts
```

### Executar com interface gráfica
```bash
npx playwright test e2e/crm/ --ui
```

### Executar com relatório HTML
```bash
npx playwright test e2e/crm/ --reporter=html
```

## Padrões Utilizados

### Fixtures
Todos os testes utilizam o arquivo `../fixtures.ts` que:
- Injeta autenticação válida automaticamente
- Mocka o endpoint `/api/v1/auth/me`

### Mocks de API
Cada teste faz mock dos endpoints relevantes:
- `**/api/v1/clients*` - Clientes
- `**/api/v1/crm/leads*` - Leads
- `**/api/v1/crm/opportunities*` - Oportunidades
- `**/api/v1/crm/proposals*` - Propostas

### Seletores
Os testes utilizam seletores baseados em:
- Texto visível (`text=Novo Cliente`)
- Placeholders (`input[placeholder*="Buscar"]`)
- Roles ARIA (`[role="dialog"], [role="combobox"]`)
- Hierarquia (`table tbody tr`)

## Manutenção

### Adicionar novos testes
1. Criar arquivo `.spec.ts` na pasta `e2e/crm/`
2. Importar fixtures: `import { test, expect } from '../fixtures';`
3. Usar `test.beforeEach` para mocks e navegação
4. Agrupar testes relacionados com `test.describe`

### Atualizar seletores
Se a interface mudar, atualize os seletores nos arquivos de teste:
- Verifique o `data-testid` nos componentes
- Use inspeção de elemento para encontrar novos seletores
- Prefira seletores semânticos (roles, textos) em vez de classes CSS

## Relatórios

Os relatórios são gerados automaticamente em:
```
/opt/conecta-pro/reports/playwright/
```

Para visualizar:
```bash
npx playwright show-report ../reports/playwright
```
