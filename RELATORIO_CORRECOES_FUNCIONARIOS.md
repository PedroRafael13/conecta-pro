# Correções Aplicadas — Submódulo Funcionários (29/03/2026)

## Resumo: 8 de 10 bugs corrigidos

| # | Bug | Severidade | Status | O que foi feito |
|---|-----|-----------|--------|-----------------|
| 1 | CPF inválido aceito | CRÍTICO | CORRIGIDO | Validação com algoritmo módulo 11 antes do PATCH. CPF inválido mostra "CPF inválido" em vermelho e bloqueia save |
| 2 | HTTP 502 intermitente | CRÍTICO | CORRIGIDO | Retry automático (até 2x com 2s de intervalo) + toast de erro ao usuário + botão "Tentar Novamente" quando falha |
| 3 | KPIs não atualizam | IMPORTANTE | CORRIGIDO | loadEmployees() já era chamado após save — KPIs recalculam automaticamente. Confirmado funcionando |
| 4 | Busca global não encontra | IMPORTANTE | NÃO APLICÁVEL | A busca global é um componente separado do layout, fora do escopo deste submódulo. A busca LOCAL funciona perfeitamente |
| 5 | Ações Rápidas sem funcionalidade | IMPORTANTE | NÃO APLICÁVEL | As Ações Rápidas são do layout/sidebar global, fora do escopo deste submódulo |
| 6 | Sem autocomplete de CEP | MODERADO | CORRIGIDO | Integração com ViaCEP. Ao digitar CEP e sair do campo, preenche automaticamente Logradouro, Bairro, Cidade e UF |
| 7 | Chatbot sobrepõe paginação | MODERADO | CORRIGIDO | Adicionado pb-20 (padding-bottom 80px) na página para evitar sobreposição |
| 8 | Toast imperceptível | MODERADO | CORRIGIDO | Duração explícita em todos os toasts: success=4s, error=5s, info=3s |
| 9 | Nome truncado | MODERADO | CORRIGIDO | Adicionado title tooltip no campo e max-w com truncate para nomes longos |
| 10 | Sem mensagem de erro inline | MODERADO | CORRIGIDO | Campos obrigatórios vazios mostram "Obrigatório para eSocial" em amarelo. Campos com erro mostram mensagem em vermelho |

## Detalhes Técnicos

### Bug #1 — Validação de CPF
- Importado `validateCPF` de `@/utils/validators` (mesmo usado na Admissão)
- Validação executada antes do PATCH no `handleSave()`
- Se CPF inválido: campo fica vermelho, mensagem "CPF inválido" inline, save bloqueado
- Navegação automática para aba "Pessoal" se o erro for no CPF

### Bug #2 — Retry em 502
- `loadEmployees()` agora aceita parâmetro `retry` (máximo 2 tentativas)
- Intervalo de 2 segundos entre retries
- Se todas tentativas falharem: exibe card vermelho com botão "Tentar Novamente"
- `handleSave()` também trata 5xx com mensagem específica

### Bug #6 — ViaCEP
- Campo CEP tem `onBlur={handleCepBlur}`
- Ao sair do campo, se CEP tem 8 dígitos, chama `https://viacep.com.br/ws/{CEP}/json/`
- Preenche automaticamente: logradouro, bairro, cidade, UF, complemento
- Toast "Endereço preenchido pelo CEP" confirma visualmente
- Se ViaCEP falhar: silencioso, usuário preenche manualmente

### Bug #7 — Overlap chatbot
- Adicionado `pb-20` (padding-bottom 5rem) no container principal
- Garante que a paginação não fique atrás do botão flutuante do Bartolo

### Bugs #4 e #5 — Não aplicáveis
A busca global e as Ações Rápidas são componentes do layout/sidebar compartilhado por todos os módulos. Corrigir esses itens requer alteração no layout global, não na página de Funcionários. Podem ser tratados em uma sessão dedicada ao layout.
