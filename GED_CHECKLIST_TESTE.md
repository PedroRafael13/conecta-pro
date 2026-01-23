# ✅ CHECKLIST DE TESTE - MÓDULO GED

## 🎯 TESTES OBRIGATÓRIOS (5 minutos)

### 1. Página Arquivos
- [ ] Abrir https://erp.conectamais.pro/modulos/documentos/arquivos
- [ ] ✅ Página carrega sem erros
- [ ] ✅ Filtros visíveis (Busca, Pasta, Tipo, Status)
- [ ] ✅ Botão "Upload" presente
- [ ] ✅ Console sem erros

### 2. Criação de Pasta
- [ ] Abrir https://erp.conectamais.pro/modulos/documentos/pastas
- [ ] Clicar em "Nova Pasta"
- [ ] Preencher:
  - Nome: "Teste [Seu Nome]"
  - Descrição: "Pasta de teste"
  - Tipo: Qualquer
  - Público: Sim/Não
- [ ] Clicar "Criar Pasta"
- [ ] ✅ Toast de sucesso aparece?
- [ ] ✅ Pasta aparece na lista?
- [ ] ✅ Contador atualiza?

### 3. Menu de Ações
- [ ] Passar mouse sobre uma pasta (NÃO sistema)
- [ ] ✅ Botão ⋮ aparece no canto?
- [ ] Clicar no botão ⋮
- [ ] ✅ Menu abre com: Editar, Mover, Excluir?

### 4. Upload de Documento
- [ ] Abrir https://erp.conectamais.pro/modulos/documentos/arquivos
- [ ] Clicar em "Upload"
- [ ] ✅ Modal "Upload de Documentos" abre?
- [ ] Arrastar um arquivo PDF
- [ ] ✅ Arquivo aparece na lista?
- [ ] Selecionar pasta, tipo e categoria
- [ ] Clicar "Enviar"
- [ ] ✅ Progress bar aparece?
- [ ] ✅ Toast de sucesso aparece?

### 5. Ações em Documento
- [ ] Localizar um documento na tabela
- [ ] Clicar no ícone 👁️
- [ ] ✅ Abre em nova aba?
- [ ] Clicar no ícone ⬇️
- [ ] ✅ Toast "Download iniciado" aparece?
- [ ] ✅ Arquivo baixa?
- [ ] Clicar no ícone ⋮
- [ ] ✅ Menu abre?
- [ ] Clicar em "Excluir"
- [ ] ✅ AlertDialog de confirmação aparece?

## 🚨 PROBLEMAS CONHECIDOS (Reportar se encontrar)

### Problema: Toast não aparece
**O que fazer:**
1. Abrir DevTools (F12)
2. Verificar aba Console
3. Procurar erros
4. Reportar com screenshot

### Problema: Menu não aparece no hover
**Possíveis causas:**
1. Pasta é do sistema (não deve ter menu)
2. CSS não carregou
3. Browser cache

**Solução:**
1. Ctrl + Shift + R (hard refresh)
2. Testar em pasta não-sistema
3. Verificar se há classe "group" no card

### Problema: Upload não funciona
**O que verificar:**
1. Tamanho do arquivo (<10MB)
2. Tipo de arquivo (PDF, DOC, XLS, IMG)
3. Pasta de destino selecionada
4. Console de erros

## 🎖️ TESTES AVANÇADOS (Opcional)

### 6. Editar Pasta
- [ ] Clicar em ⋮ > Editar
- [ ] Modificar nome
- [ ] Salvar
- [ ] ✅ Toast de sucesso?
- [ ] ✅ Nome atualiza na lista?

### 7. Excluir Pasta Vazia
- [ ] Criar pasta teste
- [ ] Clicar em ⋮ > Excluir
- [ ] Confirmar no AlertDialog
- [ ] ✅ Toast de sucesso?
- [ ] ✅ Pasta desaparece?

### 8. Filtros Combinados
- [ ] Selecionar uma pasta no filtro
- [ ] Selecionar um tipo
- [ ] Selecionar um status
- [ ] ✅ Lista filtra corretamente?
- [ ] Digitar busca
- [ ] ✅ Filtro adicional funciona?

### 9. Navegação Hierárquica
- [ ] Entrar em uma pasta
- [ ] ✅ Breadcrumb atualiza?
- [ ] Criar subpasta
- [ ] Entrar na subpasta
- [ ] ✅ Path correto?
- [ ] Clicar em nível anterior no breadcrumb
- [ ] ✅ Volta para nível correto?

### 10. Kits de Documentos
- [ ] Abrir https://erp.conectamais.pro/modulos/documentos/kits
- [ ] ✅ Página carrega?
- [ ] ✅ 3 kits visíveis?
- [ ] ✅ Informações completas?
- [ ] Filtrar por categoria
- [ ] ✅ Filtro funciona?

## 📊 RESULTADO ESPERADO

✅ **10/10 testes passam** = Sistema 100% funcional
⚠️ **8-9/10 testes passam** = Funcional com pequenos ajustes
❌ **<8/10 testes passam** = Investigar problemas

## 🐛 COMO REPORTAR BUGS

1. **Screenshot do erro**
2. **Console do DevTools (F12 > Console)**
3. **Passos para reproduzir**
4. **Browser e versão**
5. **URL da página**

---

**Tempo estimado de teste:** 5-10 minutos
**Última atualização:** 23/01/2026
**Versão testada:** GED v2.0
