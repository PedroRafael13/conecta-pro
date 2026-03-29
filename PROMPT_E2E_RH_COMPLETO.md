# Testes E2E — Módulo Recursos Humanos (RH) Completo

**URL Base:** https://erp.conectamais.pro/modulos/rh
**Data:** 29/03/2026 | **Executor:** QA (Claude in Chrome)

Execute cada submódulo na ordem. Para cada teste, registre: ✅ PASSOU | ⚠️ PARCIAL | ❌ FALHOU + observação.

---

## 1. DASHBOARD RH (/modulos/rh/dashboard)

### Acesso e Carregamento
1. Acesse /modulos/rh — verifique se o hub carrega com cards de navegação para todos os submódulos
2. Clique no card "Dashboard" — verifique se navega para /modulos/rh/dashboard
3. Verifique se os KPIs carregam com dados reais (Total Funcionários, Turnover, Satisfação, Treinamentos)
4. Verifique se não há erros no console (DevTools F12)

### Dados
5. Os números nos KPIs devem ser coerentes (ex: turnover não pode ser 500%, satisfação entre 0-100)
6. Se houver gráficos, verifique se renderizam sem erro

---

## 2. RECRUTAMENTO (/modulos/recrutamento)

### 2A. Hub do Recrutamento
7. Acesse /modulos/recrutamento — verifique se carrega com cards (Vagas, Candidatos, Candidaturas, Entrevistas)
8. Verifique se os contadores nos cards mostram números reais

### 2B. Vagas (/modulos/recrutamento/vagas)
9. Acesse a página — verifique se lista vagas com colunas (Título, Departamento, Status, Tipo, Candidatos)
10. Teste a busca: digite o nome de uma vaga ou departamento
11. Teste filtro por status: Rascunho, Aberta, Pausada, Fechada, Preenchida
12. Clique "Nova Vaga" — preencha: título="Vigilante Noturno", departamento="Operações", tipo=CLT, nível=Júnior
13. Salve e verifique se aparece na lista com toast de sucesso
14. Clique em uma vaga para ver detalhes
15. Teste ações: Publicar, Pausar, Reabrir, Fechar, Duplicar
16. Verifique paginação se houver mais de 15 registros

### 2C. Candidatos (/modulos/recrutamento/candidatos)
17. Acesse — verifique se lista candidatos (Nome, Email, Telefone, Status, Fonte)
18. Teste busca por nome
19. Teste filtro por status: Ativo, Inativo, Bloqueado, Contratado, Arquivado
20. Clique "Novo Candidato" — preencha dados de teste
21. Salve e verifique toast + lista atualizada
22. Clique em candidato para detalhes
23. Teste ações: Bloquear (com motivo), Desbloquear, Arquivar

### 2D. Candidaturas (/modulos/recrutamento/candidaturas)
24. Acesse — verifique se lista candidaturas (Candidato, Vaga, Status, Data)
25. Teste filtro por status: Inscrito, Triagem, Entrevista RH, etc.
26. Clique "Nova Candidatura" — associe candidato a vaga
27. Teste ação "Avançar Etapa" — deve mudar status para próxima fase
28. Teste "Rejeitar" — deve pedir motivo antes de confirmar
29. Teste "Enviar Proposta" — deve pedir valor e benefícios

### 2E. Entrevistas (/modulos/recrutamento/entrevistas)
30. Acesse — verifique se lista entrevistas (Candidato, Vaga, Tipo, Data, Status)
31. Clique "Nova Entrevista" — preencha: candidato, vaga, tipo (Presencial/Vídeo/Telefone), data/hora
32. Salve e verifique toast
33. Teste ações: Iniciar, Concluir (com resultado: Aprovado/Reprovado), Cancelar, Reagendar, Marcar No-Show

---

## 3. TREINAMENTOS (/modulos/rh/treinamentos)

34. Acesse — verifique se lista treinamentos (Título, Tipo, Status, Vagas, Inscritos)
35. Teste busca por título
36. Clique "Novo Treinamento" — preencha: título, tipo, vagas, data início/fim
37. Salve e verifique toast + lista
38. Verifique se paginação funciona
39. Teste ações de um treinamento: Inscrever funcionário, Concluir

---

## 4. AVALIAÇÕES (/modulos/rh/avaliacoes)

### Avaliação de Desempenho
40. Acesse — verifique se lista avaliações (Funcionário, Tipo, Status, Período)
41. Teste busca e filtro por status
42. Clique "Nova Avaliação" — preencha dados
43. Salve e verifique

### Avaliação 360°
44. Verifique se há seção/tab de "Ciclos 360°" na mesma página
45. Se houver, verifique se lista ciclos com status
46. Teste criar novo ciclo 360°

---

## 5. PLANO DE CARREIRA (/modulos/rh/carreira)

47. Acesse — verifique se lista planos de carreira (Funcionário, Status, Mentor, Progresso)
48. Teste busca por nome de funcionário
49. Clique "Novo Plano" — preencha: funcionário, mentor, objetivo, marcos (milestones)
50. Salve e verifique
51. Teste ação: Completar marco (milestone)
52. Verifique se progresso atualiza visualmente

---

## 6. CLIMA ORGANIZACIONAL (/modulos/rh/clima)

53. Acesse — verifique se carrega dados reais do endpoint /climate/dashboard
54. Verifique se mostra métricas: score de satisfação, engajamento, NPS
55. Verifique se lista pesquisas de clima (/climate/surveys)
56. Verifique se mostra alertas de clima (/climate/alerts)
57. Teste busca/filtro se disponível
58. Verifique paginação

---

## 7. TURNOVER (/modulos/rh/turnover)

59. Acesse — verifique se carrega dados do endpoint /turnover/dashboard
60. Verifique métricas: taxa de turnover, média permanência, risco previsto
61. Verifique se lista motivos de saída (/turnover/motivos)
62. Verifique se há gráficos/visualizações de tendência
63. Teste busca/filtro se disponível

---

## 8. ONBOARDING (/modulos/rh/onboarding)

64. Acesse — verifique se carrega dados do endpoint /onboarding/dashboard
65. Verifique métricas: total em onboarding, concluídos, pendentes
66. Verifique se lista pendências (/onboarding/pendencias)
67. Se houver checklist de onboarding, teste marcar itens como concluídos
68. Teste busca/filtro

---

## 9. IA DE PESSOAS (/modulos/rh/ia)

69. Acesse — verifique se a página carrega sem erros
70. Verifique se mostra status dos serviços de IA (Turnover Prediction, Climate Analysis)
71. Se houver funcionalidade de consulta/análise, teste com uma pergunta
72. Verifique se os dados vêm dos endpoints reais

---

## VERIFICAÇÕES GLOBAIS (aplicar em TODAS as páginas)

Para cada página acima, verificar também:

73. **Loading state**: Aparece spinner enquanto carrega?
74. **Empty state**: Se não há dados, mostra mensagem adequada?
75. **Toast notifications**: Após criar/editar, aparece toast visível por 3-5 segundos?
76. **Busca**: Campo de busca filtra em tempo real?
77. **Paginação**: Se houver mais de 15 registros, controles de página aparecem?
78. **Responsividade**: A página funciona em tela menor (redimensionar janela)?
79. **Botão voltar**: Seta de retorno navega para o hub correto?
80. **Console limpo**: Sem erros JS (apenas avisos de WS são aceitáveis)?

---

## FORMATO DO RELATÓRIO

### Para cada submódulo:
```
## [Nome do Submódulo]
Score: X/10

### Testes
| # | Resultado | Observação |
|---|-----------|------------|
| N | ✅/⚠️/❌ | Detalhe... |

### Bugs encontrados
- BUG-XX: [Descrição] — Severidade: CRÍTICO/MÉDIO/BAIXO
```

### No final:
```
## RESUMO GERAL
| Submódulo | Score | Testes Pass | Bugs |
|-----------|-------|-------------|------|
| Dashboard | X/10  | Y/Z         | N    |
| Recrutamento | X/10 | Y/Z      | N    |
| ...       |       |             |      |

Total: XX/80 testes | YY bugs encontrados
```
