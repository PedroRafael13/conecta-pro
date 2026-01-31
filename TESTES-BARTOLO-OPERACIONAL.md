# 🧪 TESTES BARTOLO - MÓDULO OPERACIONAL
## 5 Cenários de Complexidade Crescente

**Data:** 31/01/2026  
**Módulo:** Operacional  
**Objetivo:** Validar Bartolo com usuário real

---

## 📋 PREPARAÇÃO

### Credenciais
- **URL:** http://localhost:8080 (ou seu domínio)
- **Usuário:** egonzaga@conectamais.pro
- **Senha:** Admin@123

### Como Executar
1. Abra o frontend do Conecta Plus
2. Acesse o chat do Bartolo
3. Cole cada teste e observe as respostas
4. Anote comportamentos inesperados

---

## 🟢 TESTE 1 - NÍVEL SIMPLES (Consulta Básica)

**Objetivo:** Verificar consulta básica de alertas  
**Complexidade:** ⭐ (Simples)  
**Tempo estimado:** 30 segundos

### Comando:
```
/alerta
```

### Resultado Esperado:
- ✅ Bartolo lista alertas do sistema
- ✅ Mostra prioridades (altos, médios, baixos)
- ✅ Dados em tempo real
- ✅ Formatação clara

### O Que Validar:
- [ ] Resposta em < 3 segundos
- [ ] Dados são do sistema real (não mock)
- [ ] Mensagem é clara e objetiva
- [ ] Não há erros técnicos visíveis

---

## 🟡 TESTE 2 - NÍVEL MÉDIO (Skill com Parâmetros)

**Objetivo:** Listar postos de trabalho com filtro  
**Complexidade:** ⭐⭐ (Médio)  
**Tempo estimado:** 1 minuto

### Comando:
```
/posto listar
```

### Resultado Esperado:
- ✅ Lista de postos cadastrados
- ✅ Informações: nome, tipo, status
- ✅ Possibilidade de ver detalhes
- ✅ Sugestões de próximos comandos

### Sequência de Teste:
1. Execute: `/posto listar`
2. Observe a lista retornada
3. Se houver postos, execute: `/posto help`
4. Veja outros comandos disponíveis

### O Que Validar:
- [ ] Lista completa de postos
- [ ] Dados corretos (compare com banco)
- [ ] Help mostra outros comandos
- [ ] Formatação está legível

---

## 🟠 TESTE 3 - NÍVEL INTERMEDIÁRIO (Consulta Multi-Step)

**Objetivo:** Consultar saldo de banco de horas e ver extrato  
**Complexidade:** ⭐⭐⭐ (Intermediário)  
**Tempo estimado:** 2 minutos

### Sequência de Comandos:

**Passo 1: Ver resumo geral**
```
/banco_horas resumo
```

**Passo 2: Ver saldo de funcionário específico (ajuste o ID)**
```
/banco_horas saldo
```
*Nota: Se pedir ID, use um ID real do seu sistema*

**Passo 3: Ver ajuda para mais opções**
```
/banco_horas help
```

### Resultado Esperado:
- ✅ Resumo mostra total de créditos/débitos
- ✅ Saldo individual mostra dados corretos
- ✅ Help lista todos os comandos
- ✅ Navegação entre comandos é fluida

### O Que Validar:
- [ ] Dados batem com o sistema
- [ ] Formatação de horas está correta
- [ ] Bartolo sugere próximas ações
- [ ] Não há erros de cálculo

---

## 🔴 TESTE 4 - NÍVEL AVANÇADO (Wizard Completo)

**Objetivo:** Criar um comunicado usando wizard  
**Complexidade:** ⭐⭐⭐⭐ (Avançado)  
**Tempo estimado:** 5 minutos

### Comando Inicial:
```
Preciso criar um comunicado informativo sobre mudança de procedimento
```
*Ou use o comando direto:*
```
/comunicado criar
```

### Fluxo do Wizard:

**Step 1: Tipo de Comunicado**
- Responda: `Informativo`

**Step 2: Título**
- Digite: `Novo procedimento de registro de ponto`

**Step 3: Conteúdo**
- Digite: `A partir de segunda-feira (03/02), o registro de ponto será feito exclusivamente pelo aplicativo mobile. O relógio de ponto físico será desativado para manutenção.`

**Step 4: Prioridade**
- Escolha: `Normal`

**Step 5: Destinatários**
- Escolha: `Todos os funcionários` (ou opção similar)

**Continue respondendo os steps seguintes conforme o wizard solicitar**

### Resultado Esperado:
- ✅ Wizard inicia corretamente
- ✅ Cada step tem pergunta clara
- ✅ Opções são apresentadas quando aplicável
- ✅ Progress bar mostra evolução
- ✅ Possibilidade de cancelar a qualquer momento
- ✅ Ao final, comunicado é criado ou preview é mostrado

### O Que Validar:
- [ ] Todas as perguntas fazem sentido
- [ ] Validações impedem dados inválidos
- [ ] Progress tracking funciona (1/10, 2/10, etc)
- [ ] Help contextual está disponível
- [ ] Botão "Cancelar" funciona
- [ ] Comunicado é criado no banco ao final

---

## 🔴 TESTE 5 - NÍVEL COMPLEXO (Fluxo Completo Multi-Skill)

**Objetivo:** Analisar cobertura de postos e criar escala  
**Complexidade:** ⭐⭐⭐⭐⭐ (Complexo)  
**Tempo estimado:** 10 minutos

### Cenário:
"Você é o gestor operacional e precisa verificar a cobertura de postos para a próxima semana e, se necessário, criar uma nova escala para cobrir vagas abertas."

### Sequência de Comandos:

**Etapa 1: Análise de Cobertura**
```
/cobertura hoje
```
*Observe quais postos têm problemas*

**Etapa 2: Verificar Alertas**
```
/alerta
```
*Veja se há alertas sobre vagas abertas*

**Etapa 3: Verificar Detalhes de Posto Específico**
```
/posto listar
```
*Escolha um posto da lista*

```
/posto detalhes [NOME_DO_POSTO]
```
*Substitua [NOME_DO_POSTO] pelo nome real*

**Etapa 4: Consultar Disponibilidade de Funcionários**
```
Quais funcionários estão disponíveis para cobrir turnos na próxima semana?
```
*Ou use:*
```
/substituto buscar
```

**Etapa 5: Verificar Banco de Horas**
```
/banco_horas resumo
```
*Para ver quem pode fazer horas extras*

**Etapa 6: Criar Escala (Wizard)**
```
Preciso criar uma nova escala para o posto [NOME] na próxima semana
```
*Ou comando direto:*
```
/escala gerar
```

**Complete o wizard fornecendo:**
- Posto: [escolha da lista]
- Período: [próxima semana]
- Funcionários: [selecione da lista]
- Turnos: [configure conforme necessidade]

**Etapa 7: Validar Escala Criada**
```
/escala help
```
*Veja comandos para otimizar ou publicar*

### Resultado Esperado:
- ✅ Bartolo fornece análise completa da situação
- ✅ Dados de múltiplas fontes são combinados
- ✅ Sugestões são contextuais e úteis
- ✅ Fluxo é natural como uma conversa
- ✅ Wizard de escala funciona perfeitamente
- ✅ Validações da CCT são aplicadas
- ✅ Escala é criada e pode ser otimizada

### O Que Validar:
- [ ] Bartolo conecta informações entre skills
- [ ] Respostas são contextuais (lembra conversa anterior)
- [ ] Sugestões são inteligentes baseadas nos dados
- [ ] Wizard valida regras da CCT
- [ ] Conflitos são detectados (ex: funcionário já escalado)
- [ ] Escala pode ser otimizada após criação
- [ ] Preview da escala antes de publicar
- [ ] Dados persistem no banco de dados

---

## 📊 MATRIZ DE VALIDAÇÃO

Após executar os 5 testes, preencha:

| Teste | Complexidade | Funcionou | Tempo | Observações |
|-------|--------------|-----------|-------|-------------|
| 1. Alerta | ⭐ | [ ] Sim [ ] Não | ___s | |
| 2. Posto | ⭐⭐ | [ ] Sim [ ] Não | ___s | |
| 3. Banco Horas | ⭐⭐⭐ | [ ] Sim [ ] Não | ___s | |
| 4. Wizard Comunicado | ⭐⭐⭐⭐ | [ ] Sim [ ] Não | ___min | |
| 5. Fluxo Completo | ⭐⭐⭐⭐⭐ | [ ] Sim [ ] Não | ___min | |

---

## 🐛 BUGS ENCONTRADOS

Use esta seção para anotar problemas:

### Bug 1
- **Teste:** [número do teste]
- **Descrição:** 
- **Esperado:**
- **Obtido:**
- **Severidade:** [ ] Crítico [ ] Alto [ ] Médio [ ] Baixo

### Bug 2
- **Teste:**
- **Descrição:**
- **Esperado:**
- **Obtido:**
- **Severidade:** [ ] Crítico [ ] Alto [ ] Médio [ ] Baixo

---

## 💡 OBSERVAÇÕES GERAIS

### Pontos Positivos
- 
- 
- 

### Pontos de Melhoria
- 
- 
- 

### Sugestões
- 
- 
- 

---

## 🎯 CRITÉRIOS DE SUCESSO

O teste será considerado **APROVADO** se:
- [ ] Todos os 5 testes executam sem erros críticos
- [ ] Performance é aceitável (< 5s por resposta)
- [ ] Dados retornados são corretos
- [ ] UX é fluida e intuitiva
- [ ] Wizards completam sem travar
- [ ] Dados persistem no banco

**Taxa mínima de aprovação:** 80% (4/5 testes OK)

---

## 📞 PRÓXIMOS PASSOS

Após executar os testes:

1. **Se tudo passou (5/5):**
   - ✅ Bartolo está pronto para uso geral
   - Libere para equipe operacional
   - Colete feedback contínuo

2. **Se 4/5 passou:**
   - ⚠️ Corrija o problema encontrado
   - Re-teste apenas o caso que falhou
   - Libere com ressalvas

3. **Se < 4/5 passou:**
   - ❌ Investigue os bugs encontrados
   - Corrija antes de liberar
   - Execute todos os 5 testes novamente

---

**Criado por:** Claude Sonnet 4.5  
**Data:** 31/01/2026  
**Versão:** 1.0  
**Status:** Pronto para execução
