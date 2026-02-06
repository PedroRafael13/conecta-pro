# 🧪 GUIA DE TESTES - MÓDULO LICITAÇÕES

## 📋 Informações de Acesso

**URL Base:** http://localhost:3002/modulos/licitacoes
**Status:** ✅ Servidor rodando na porta 3002
**Credenciais:** admin@conectaplus.com.br

---

## 🎯 ROTEIRO DE TESTES COMPLETO

### 1️⃣ DASHBOARD (5 min)

**URL:** http://localhost:3002/modulos/licitacoes

#### Checklist Visual:
- [ ] 4 cards de KPIs aparecem corretamente
  - Editais Ativos
  - Propostas em Análise
  - Contratos Vigentes
  - Certidões Válidas
- [ ] 3 atalhos rápidos funcionam
  - Novo Edital
  - Nova Proposta
  - Sincronizar PNCP
- [ ] Layout responsivo (testar resize da janela)
- [ ] Skeleton loaders aparecem durante carregamento

#### Ações:
1. Clicar em cada KPI → deve navegar para a página correspondente
2. Clicar em "Novo Edital" → modal deve abrir
3. Clicar em "Sincronizar PNCP" → deve mostrar confirmação

---

### 2️⃣ EDITAIS (10 min)

**URL:** http://localhost:3002/modulos/licitacoes/editais

#### Checklist Listagem:
- [ ] Tabela carrega com dados (ou estado vazio)
- [ ] Filtros funcionam:
  - [ ] Busca por número/objeto
  - [ ] Filtro por modalidade
  - [ ] Filtro por status
- [ ] Paginação funciona corretamente
- [ ] Botão "Novo Edital" visível

#### Teste CRUD:
1. **Criar Edital**
   - [ ] Clicar "Novo Edital"
   - [ ] Preencher formulário:
     - Número: `001/2026`
     - Objeto: `Teste de Edital`
     - Modalidade: Pregão Eletrônico
     - Valor estimado: `100000`
     - Data abertura: (data futura)
   - [ ] Validação funciona (campos obrigatórios)
   - [ ] Toast de sucesso aparece
   - [ ] Edital aparece na lista

2. **Visualizar Detalhe**
   - [ ] Clicar no edital criado
   - [ ] URL muda para `/editais/[id]`
   - [ ] Todas as informações aparecem
   - [ ] Tabs funcionam (Informações, Itens, Documentos)

3. **Editar Edital**
   - [ ] Clicar botão "Editar"
   - [ ] Modal abre com dados preenchidos
   - [ ] Alterar objeto para `Teste de Edital - EDITADO`
   - [ ] Salvar e verificar alteração

4. **Deletar Edital**
   - [ ] Clicar botão "Deletar"
   - [ ] Modal de confirmação aparece
   - [ ] Confirmar exclusão
   - [ ] Edital removido da lista

#### Funcionalidades Especiais:
- [ ] Sincronizar PNCP → deve mostrar modal
- [ ] Status badges com cores corretas
- [ ] Filtros podem ser combinados
- [ ] Limpar filtros funciona

---

### 3️⃣ PROPOSTAS (10 min)

**URL:** http://localhost:3002/modulos/licitacoes/propostas

#### Checklist Listagem:
- [ ] Tabela carrega corretamente
- [ ] Filtros disponíveis:
  - [ ] Busca por edital
  - [ ] Filtro por status
  - [ ] Data de envio
- [ ] Botão "Nova Proposta"

#### Teste CRUD:
1. **Criar Proposta**
   - [ ] Clicar "Nova Proposta"
   - [ ] Selecionar edital (se houver)
   - [ ] Preencher:
     - Valor proposto: `95000`
     - Prazo execução: `90`
     - Observações: `Proposta teste`
   - [ ] Adicionar itens (se aplicável)
   - [ ] Salvar proposta

2. **Visualizar Detalhe**
   - [ ] Clicar na proposta
   - [ ] Ver todas as informações
   - [ ] Verificar itens da proposta
   - [ ] Documentos anexados

3. **Submeter Proposta**
   - [ ] Botão "Submeter Proposta" visível
   - [ ] Clicar e confirmar
   - [ ] Status muda para "Em Análise"
   - [ ] Toast de sucesso

4. **Gerenciar Itens**
   - [ ] Adicionar item à proposta
   - [ ] Editar item
   - [ ] Remover item
   - [ ] Valores recalculados automaticamente

---

### 4️⃣ CONTRATOS (10 min)

**URL:** http://localhost:3002/modulos/licitacoes/contratos

#### Checklist Listagem:
- [ ] Tabela com contratos
- [ ] Filtros:
  - [ ] Busca por número
  - [ ] Status (vigente, rescindido, etc)
  - [ ] Fornecedor
- [ ] Indicadores visuais (vigência, alertas)

#### Teste Visualização:
1. **Detalhe do Contrato**
   - [ ] Clicar em contrato
   - [ ] Ver informações completas
   - [ ] Valor total e saldo
   - [ ] Vigência e prazo

2. **Aditivos**
   - [ ] Listar aditivos do contrato
   - [ ] Ver detalhes de cada aditivo
   - [ ] Impacto no valor/prazo

3. **Documentos**
   - [ ] Ver documentos anexados
   - [ ] Download de documento
   - [ ] Upload de novo documento

---

### 5️⃣ CERTIDÕES (10 min)

**URL:** http://localhost:3002/modulos/licitacoes/certidoes

#### Checklist Listagem:
- [ ] Tabela de certidões
- [ ] Filtros por tipo e status
- [ ] Alertas de vencimento
- [ ] Badge de status (válida, vencida, a vencer)

#### Teste Funcionalidades:
1. **Upload Certidão**
   - [ ] Clicar "Nova Certidão"
   - [ ] Selecionar tipo
   - [ ] Upload de arquivo (PDF)
   - [ ] Definir validade
   - [ ] Salvar

2. **Renovação**
   - [ ] Clicar "Renovar" em certidão vencida
   - [ ] Upload novo arquivo
   - [ ] Atualizar validade
   - [ ] Verificar histórico

3. **Alertas**
   - [ ] Ver certidões a vencer (< 30 dias)
   - [ ] Badge visual diferenciado
   - [ ] Filtro "A Vencer" funciona

4. **Visualização**
   - [ ] Clicar para ver detalhes
   - [ ] Ver arquivo anexado
   - [ ] Download do PDF
   - [ ] Histórico de renovações

---

### 6️⃣ DOCUMENTOS (8 min)

**URL:** http://localhost:3002/modulos/licitacoes/documentos

#### Checklist Listagem:
- [ ] Tabela de documentos
- [ ] Filtros por tipo e categoria
- [ ] Busca por nome
- [ ] Tamanho do arquivo exibido

#### Teste Funcionalidades:
1. **Upload Documento**
   - [ ] Clicar "Upload Documento"
   - [ ] Selecionar arquivo
   - [ ] Definir:
     - Nome
     - Tipo
     - Categoria
     - Descrição (opcional)
   - [ ] Upload com progresso
   - [ ] Sucesso e aparece na lista

2. **Visualização**
   - [ ] Clicar no documento
   - [ ] Modal/preview abre
   - [ ] Ver metadados
   - [ ] Data de upload

3. **Download**
   - [ ] Botão download visível
   - [ ] Clicar e arquivo baixa
   - [ ] Nome correto do arquivo

4. **Deletar**
   - [ ] Botão deletar
   - [ ] Confirmação
   - [ ] Documento removido

---

## 🔧 TESTES DE EXPERIÊNCIA

### Responsividade
- [ ] Desktop (> 1024px) → Layout completo
- [ ] Tablet (768-1024px) → Layout adaptado
- [ ] Mobile (< 768px) → Menu colapsado, cards empilhados

### Performance
- [ ] Primeira carga < 3s
- [ ] Navegação entre páginas suave
- [ ] Filtros respondem instantaneamente
- [ ] Skeleton loaders aparecem

### Validações
- [ ] Campos obrigatórios marcados
- [ ] Mensagens de erro claras
- [ ] Validação em tempo real (Zod)
- [ ] Formatação de valores (R$, datas)

### Feedback ao Usuário
- [ ] Toast notifications aparecem
- [ ] Confirmações antes de deletar
- [ ] Loading states visíveis
- [ ] Estados vazios (empty states) informativos

### Navegação
- [ ] Breadcrumbs corretos
- [ ] Voltar funciona
- [ ] URLs amigáveis
- [ ] Deep links funcionam

---

## 🐛 CHECKLIST DE BUGS COMUNS

### Verificar se NÃO ocorre:
- [ ] ❌ Erro de console no navegador
- [ ] ❌ Layout quebrado ou sobreposto
- [ ] ❌ Formulário submete vazio
- [ ] ❌ Filtros não aplicam
- [ ] ❌ Paginação pula páginas
- [ ] ❌ Modal não fecha
- [ ] ❌ Toast não desaparece
- [ ] ❌ Dados não recarregam após CRUD
- [ ] ❌ Loading infinito
- [ ] ❌ Imagens/ícones quebrados

---

## 📊 CRITÉRIOS DE ACEITAÇÃO

### ✅ APROVADO se:
1. Todas as páginas carregam sem erros
2. CRUD funciona em todas as entidades
3. Filtros e busca retornam resultados corretos
4. Formulários validam corretamente
5. Feedback visual adequado (toasts, loaders)
6. Responsivo em diferentes resoluções
7. Performance aceitável (< 3s primeira carga)
8. Zero erros no console do navegador

### ⚠️ ATENÇÃO se:
- Alguma funcionalidade não responde
- Erros no console
- Layout quebrado em alguma resolução
- Dados não persistem
- Validações permitem dados inválidos

---

## 🎯 RESUMO FINAL

Após concluir todos os testes, preencha:

**Total de itens testados:** ___ / ___
**Itens OK:** ___
**Itens com problema:** ___
**Bugs críticos:** ___
**Bugs menores:** ___

**Status Final:**
- [ ] ✅ APROVADO - Produção Ready
- [ ] ⚠️ APROVADO COM RESSALVAS - Pequenos ajustes necessários
- [ ] ❌ REPROVADO - Correções críticas necessárias

---

## 📝 OBSERVAÇÕES

Use este espaço para anotar bugs, melhorias ou observações durante os testes:

```
Bug #1: [descreva aqui]
Solução: [proposta]

Melhoria #1: [descreva aqui]

Observação #1: [descreva aqui]
```

---

**Última atualização:** 02/02/2026
**Versão do módulo:** 1.0.0
**Testador:** _____________
**Data do teste:** ___/___/______
