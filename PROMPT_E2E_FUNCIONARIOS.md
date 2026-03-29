Você é um QA testando o submódulo "Funcionários" do Departamento Pessoal
do ERP Conecta PRO.

URL: https://erp.conectamais.pro/modulos/dp/funcionarios
Acesse com suas credenciais normais.

Execute os testes abaixo na ordem e registre o resultado de cada um.

---

FASE 1 — Acesso e Dashboard

1. Acesse /modulos/dp e verifique se o card "Funcionários" aparece
   (deve ser o primeiro card, com ícone azul e descrição
   "Cadastro completo e dados para eSocial").
2. Clique no card e verifique se a página /modulos/dp/funcionarios carrega.
3. Verifique os 4 cards de estatísticas no topo:
   - Total (número de funcionários)
   - Cadastro Completo (quantos têm 100%)
   - Dados Incompletos (quantos têm menos de 100%)
   - Completude Média (percentual médio de todos)
4. Confirme que a soma de Completos + Incompletos = Total.

---

FASE 2 — Listagem e Indicadores de Completude

5. Verifique se a tabela lista funcionários com as colunas:
   Nome | CPF | Cargo | Completude eSocial | Campos Faltantes | Ações
6. Cada funcionário deve ter uma barra de progresso colorida:
   - Verde (100%) = cadastro completo
   - Amarelo (60-99%) = parcialmente completo
   - Vermelho (abaixo de 60%) = muitos campos faltantes
7. A coluna "Campos Faltantes" deve mostrar quais dados estão vazios
   (ex: "Nome da Mãe, RG, CEP +3").
8. Verifique se os funcionários estão ordenados do mais incompleto
   para o mais completo (prioridade de preenchimento).

---

FASE 3 — Filtros e Busca

9. Clique no badge "Incompletos" — a lista deve filtrar para mostrar
   apenas funcionários com cadastro incompleto.
10. Clique no badge "Completos" — deve mostrar apenas os 100%.
11. Clique no badge "Todos" para voltar à lista completa.
12. No campo de busca, digite o nome de um funcionário conhecido
    — a lista deve filtrar em tempo real.
13. Busque por CPF (apenas números) — deve funcionar também.
14. Verifique se a paginação aparece quando há mais de 15 registros.

---

FASE 4 — Edição de Funcionário (Fluxo Principal)

15. Escolha um funcionário com cadastro INCOMPLETO (barra amarela/vermelha).
16. Clique no botão "Editar" na linha dele.
17. Verifique se o formulário de edição abre acima da tabela com 6 abas:
    Pessoal | Documentos | Endereço | Profissional | Bancário | Vigilância
18. Verifique que na aba "Pessoal" os campos obrigatórios para eSocial
    estão destacados em amarelo quando vazios (com asterisco *):
    - Nome*, CPF*, Data de Nascimento*, Sexo*, Estado Civil*,
      Nome da Mãe*, Nacionalidade*, Naturalidade*
19. Preencha os campos vazios com dados de teste:
    - Nome da Mãe: "Maria de Teste"
    - Nacionalidade: selecione "Brasileira"
    - Naturalidade: "Manaus"
    - RG: "1234567" (aba Documentos)
    - CEP: "69000-000" (aba Endereço)
    - Logradouro: "Rua Teste" (aba Endereço)
    - Cidade: "Manaus" (aba Endereço)
    - UF: selecione "AM" (aba Endereço)
20. Clique em "Salvar Alterações".
21. Verifique se aparece o toast "Dados atualizados com sucesso!".
22. Verifique se a barra de completude do funcionário subiu
    (ex: de 40% para 87% ou 100%).

---

FASE 5 — Abas do Formulário

23. Clique na aba "Documentos" e verifique os campos:
    RG, Órgão Emissor RG, UF RG, PIS/PASEP, CTPS Número, CTPS Série,
    CTPS UF, CTPS Data Emissão, Título Eleitor, Cert. Reservista,
    CNH, Categoria CNH, Validade CNH
24. Clique na aba "Endereço" e verifique:
    CEP, Logradouro, Número, Complemento, Bairro, Cidade, UF
25. Clique na aba "Profissional" e verifique:
    Cargo, Departamento (select), Salário Base, Tipo Contrato (select),
    Regime, Data Admissão, Observações
26. Clique na aba "Bancário" e verifique:
    Banco, Agência, Conta, Tipo Conta (select), Chave PIX
27. Clique na aba "Vigilância" e verifique:
    Curso Vigilante, Validade Curso, CNV, Validade CNV

---

FASE 6 — Validações e Edge Cases

28. Abra o formulário e clique "Salvar" sem alterar nada
    — deve mostrar "Nenhuma alteração detectada" (info).
29. Clique "Cancelar" — o formulário deve fechar sem salvar.
30. Clique no X no canto do formulário — deve fechar também.
31. Edite um funcionário, mude a aba antes de salvar,
    volte à aba anterior — os dados digitados devem estar preservados.

---

FASE 7 — Network/Console

32. Abra o DevTools (F12) aba Network.
33. Ao carregar a página, verifique:
    GET /api/v1/people-management/hr/employees?page_size=200 → HTTP 200
34. Ao salvar edição, verifique:
    PATCH /api/v1/people-management/hr/employees/{id} → HTTP 200
35. Verifique que não há erros 4xx ou 5xx no console.

---

FORMATO DO RELATÓRIO:

Para cada teste, registre:
- Número do teste
- ✅ PASSOU | ⚠️ PARCIAL | ❌ FALHOU
- Observação (se houver)

No final, liste:
- Quantos testes passaram
- Bugs encontrados (com severidade: CRÍTICO/MÉDIO/BAIXO)
- Screenshots dos bugs (se possível)
