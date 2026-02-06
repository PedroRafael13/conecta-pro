# Exemplos de Uso do Bartolo IA

Este documento mostra exemplos reais de conversas com o Bartolo depois de configurado como agente de IA.

## 🎯 Consultas Operacionais

### Exemplo 1: Consultar Escalas

**Você:**
```
Quem está trabalhando no posto Central agora?
```

**Bartolo:**
```
Consultando o posto Central...

**Turno Atual (14:30):**
- João Silva (Porteiro)
  • Check-in: 07:05
  • Turno: 07:00 - 19:00 (Diurno)
  • Status: ✅ No posto

- Maria Santos (Recepcionista)
  • Check-in: 07:00
  • Turno: 07:00 - 19:00 (Diurno)
  • Status: ✅ No posto

**Próximo Turno (19:00):**
- Carlos Oliveira (Vigilante Noturno)
- Pedro Costa (Vigilante Noturno - Reserva)

Tudo normal no posto. Quer ver a escala completa da semana?
```

### Exemplo 2: Banco de Horas

**Você:**
```
Qual o saldo de banco de horas do João Silva?
```

**Bartolo:**
```
Consultando banco de horas de João Silva (CPF ***.456.789-**)...

**Saldo Atual:** +12h30min (crédito)

**Últimas Movimentações:**
- 20/01: +2h (HE 50%) - Posto Central
- 18/01: +2h (HE 50%) - Posto Shopping
- 15/01: +1h30min (HE 50%) - Posto Central
- 10/01: +3h (HE 100% - Domingo) - Cobertura emergencial
- 08/01: +2h (HE 50%) - Posto Central

**Alertas:**
⚠️ 4h vencerão em 15 dias (créditos de julho/2025)

**Sugestões:**
- Programar compensação das 4h antes do vencimento
- João pode sair mais cedo ou folgar meio período

Quer que eu monte um plano de compensação?
```

### Exemplo 3: Faltas e Ocorrências

**Você:**
```
Quantas faltas tivemos essa semana?
```

**Bartolo:**
```
Analisando faltas da semana (20/01 a 26/01)...

**Total:** 8 faltas (7 funcionários)

**Por Motivo:**
- 🤒 Atestado médico: 4
- 👤 Falta não justificada: 2
- 🚗 Atraso (>30min): 2

**Funcionários com Faltas:**
- José Santos: 2 faltas não justificadas (22/01 e 24/01)
- Ana Paula: 1 atestado médico (23/01)
- Carlos Ferreira: 1 atestado médico (21/01)
- Outros: 1 falta cada

**Impacto:**
- 3 postos precisaram de substituição emergencial
- Custo adicional: ~R$ 850 (substituições)

**Ações Sugeridas:**
- José Santos: Verificar histórico (2 faltas não justificadas)
- Postos críticos: Aumentar reserva técnica de 10% para 15%

Quer ver o histórico completo de algum funcionário?
```

## 💼 Cálculos Trabalhistas

### Exemplo 4: Calcular Férias

**Você:**
```
Calcule as férias do funcionário João Silva
```

**Bartolo:**
```
Calculando férias de João Silva...

**Dados do Funcionário:**
- Nome: João Silva
- Cargo: Porteiro
- Salário base: R$ 2.100,00
- Admissão: 15/03/2024
- Período aquisitivo: 15/03/2024 a 14/03/2025

**Cálculo (30 dias de férias):**

1. Salário base: R$ 2.100,00
2. 1/3 Constitucional: R$ 700,00
   (R$ 2.100 ÷ 3)

**Total a receber:** R$ 2.800,00

**Descontos:**
- INSS (9%): R$ 189,00
- IRRF: Isento

**Valor líquido:** R$ 2.611,00

**Opções de Abono Pecuniário (vender até 10 dias):**
- Vender 10 dias: Trabalhar 20 dias + receber R$ 933,33 extras
- Total com abono: R$ 3.544,33

**Importante:**
- João tem direito às férias a partir de 15/03/2025
- Deve tirar até 14/03/2026 (11 meses após aquisição)
- Avisar com 30 dias de antecedência

Quer que eu programe as férias dele?
```

### Exemplo 5: Calcular Rescisão

**Você:**
```
Calcule a rescisão do funcionário Maria Santos que trabalhou 2 anos e 3 meses
```

**Bartolo:**
```
Calculando rescisão de Maria Santos...

**Dados:**
- Nome: Maria Santos
- Cargo: Recepcionista
- Salário: R$ 1.950,00
- Tempo de casa: 2 anos e 3 meses (27 meses)
- Tipo: Demissão sem justa causa

**Verbas Rescisórias:**

1. **Saldo de Salário (15 dias)**
   R$ 975,00

2. **Aviso Prévio Indenizado**
   - 30 dias base: R$ 1.950,00
   - +6 dias adicionais (2 anos): R$ 390,00
   - Total: R$ 2.340,00

3. **Férias Vencidas** (período 2024)
   - Salário: R$ 1.950,00
   - +1/3: R$ 650,00
   - Total: R$ 2.600,00

4. **Férias Proporcionais** (3 meses de 2025)
   - Proporcional: R$ 487,50
   - +1/3: R$ 162,50
   - Total: R$ 650,00

5. **13º Proporcional** (3 meses)
   R$ 487,50

6. **FGTS 40%** (sobre saldo FGTS)
   - Saldo FGTS estimado: R$ 4.368,00
   - Multa 40%: R$ 1.747,20

**Total Bruto:** R$ 8.800,20

**Descontos:**
- INSS (12%): R$ 702,00
- IRRF: Isento

**Valor Líquido:** R$ 8.098,20

**FGTS a Sacar:** R$ 6.115,20 (saldo + multa)

**Total Geral a Receber:** R$ 14.213,40

**Documentos Necessários:**
- TRCT (Termo de Rescisão)
- Homologação sindicato (>1 ano)
- Chave conectividade social
- Guias FGTS/GRRF

Quer que eu gere os documentos da rescisão?
```

## 💰 Consultas Financeiras

### Exemplo 6: Fluxo de Caixa

**Você:**
```
Como está nosso fluxo de caixa esse mês?
```

**Bartolo:**
```
Analisando fluxo de caixa de Janeiro/2026...

**Resumo:**
💰 Saldo Inicial: R$ 125.430,00
📈 Entradas: R$ 487.200,00
📉 Saídas: R$ 423.150,00
💵 Saldo Projetado: R$ 189.480,00

**Principais Entradas:**
- Faturamento contratos: R$ 456.800,00 (94%)
- Outros recebimentos: R$ 30.400,00 (6%)

**Principais Saídas:**
- Folha de pagamento: R$ 285.600,00 (67%)
- Fornecedores: R$ 78.350,00 (19%)
- Impostos: R$ 42.500,00 (10%)
- Outras despesas: R$ 16.700,00 (4%)

**Contas a Receber:**
✅ Dentro do prazo: R$ 412.000,00
⚠️ Vencidas (até 30 dias): R$ 45.200,00
🔴 Inadimplência (>30 dias): R$ 28.900,00

**Contas a Pagar:**
✅ Em dia: R$ 398.150,00
⚠️ Vence em 7 dias: R$ 25.000,00

**Análise:**
- Margem operacional: 13% ✅
- Cobertura de caixa: 2.8 meses ✅
- Taxa de inadimplência: 6% ⚠️ (meta: 5%)

**Recomendações:**
1. Intensificar cobrança dos R$ 28.900,00 em atraso
2. Negociar prazo dos R$ 25.000,00 que vencem
3. Manter reserva mínima de R$ 150.000,00

Quer ver detalhamento por cliente ou categoria?
```

## 🏛️ Licitações

### Exemplo 7: Análise de Edital

**Você:**
```
Temos um edital de pregão para vigilância em um hospital público.
Vale a pena participar?
```

**Bartolo:**
```
Vou ajudar a analisar o edital. Preciso de algumas informações:

📋 **Dados do Edital:**
1. Valor estimado da licitação?
2. Quantidade de vigilantes necessários?
3. Turnos (diurno/noturno)?
4. Prazo do contrato?
5. Exigências específicas (armado, curso, etc)?

Com base nisso posso:
- ✅ Calcular custo real (mão de obra + encargos)
- ✅ Aplicar BDI adequado
- ✅ Verificar se temos habilitação (certidões)
- ✅ Calcular margem de lucro viável
- ✅ Comparar com nossa capacidade operacional
- ✅ Avaliar risco x retorno

**Pré-Análise:**

**Vantagens Hospital Público:**
- Pagamento geralmente pontual
- Contrato de longo prazo (12-60 meses)
- Reajuste anual garantido
- Boa referência

**Desafios:**
- Margem mais apertada (licitação competitiva)
- Exigências rigorosas
- Fiscalização intensa
- Necessário equipe experiente

**Nossa Capacidade:**
- ✅ Certidões válidas
- ✅ Experiência em hospitais
- ✅ Equipe treinada
- ⚠️ Verificar headcount disponível

Me passa os dados do edital para fazer a análise completa e montar a proposta?
```

## 🎓 Orientações e Treinamento

### Exemplo 8: Como Montar Escala 12x36

**Você:**
```
Como monto uma escala 12x36 correta?
```

**Bartolo:**
```
Vou te ensinar a montar uma escala 12x36 perfeita!

**Entendendo o 12x36:**

🕐 **12 horas trabalhadas** + ⏰ **36 horas de folga** = ♻️ ciclo de 48h

**Exemplo:**
- Segunda 07h-19h → trabalha
- Terça 07h-19h → folga
- Quarta 07h-19h → trabalha
- Quinta 07h-19h → folga
- (repete...)

**Vantagens:**
- ✅ Cobertura 24h com apenas 2 funcionários
- ✅ Funcionário trabalha dia sim, dia não
- ✅ Mais descanso que regime tradicional
- ✅ Menos deslocamentos

**Cálculo de Horas (CLT):**

**Horas Mensais:**
- 15 dias trabalhados (média)
- 15 dias × 12h = 180 horas/mês
- Média semanal: 42h (dentro do limite 44h)

**Adicional Noturno:**
Se trabalhar entre 22h-05h:
- 20% sobre hora diurna
- Hora noturna reduzida (52min30s)

**Passo a Passo para Montar:**

**1. Defina o Posto:**
- Local: ?
- Cargo: ?
- Turnos: Diurno/Noturno?
- Quantidade de vagas: ?

**2. Calcule Headcount:**
- 1 posto 24h = 2 funcionários fixos + 1 reserva (150%)
- Exemplo: 5 postos = 15 funcionários (10 fixos + 5 reservas)

**3. Monte a Estrutura:**

**Equipe A (Dias Ímpares):**
- 01, 03, 05, 07, 09, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31

**Equipe B (Dias Pares):**
- 02, 04, 06, 08, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30

**4. Atenção aos Domingos:**
- Domingo conta como dia útil trabalhado
- Hora extra 100% se exceder 44h semanais
- Compensação ou pagamento

**5. Feriad
os:**
- Funcionário que trabalhar: HE 100%
- Funcionário que folgar: normal (já é a folga dele)

**6. No Sistema Conecta PRO:**

```
Menu > Operacional > Escalas > Nova Escala

1. Tipo: 12x36
2. Posto: Selecione
3. Período: Mês inteiro
4. Funcionários: Equipe A e B
5. Clique em "Gerar Automaticamente"
6. Revise conflitos
7. Publique
```

**Regras Importantes:**

⚠️ **Respeite 11h entre jornadas**
- Se sair às 19h, próxima entrada após 06h

⚠️ **Máximo 2h extras por dia**
- Limite CLT

⚠️ **Domingos e Feriados**
- Pagar HE 100% ou compensar

⚠️ **Férias e Afastamentos**
- Sempre ter reserva para cobrir

**Quer que eu monte uma escala 12x36 para algum posto específico?**
Me passa os dados e eu faço passo a passo com você!
```

## 🔍 Dúvidas Sobre o Sistema

### Exemplo 9: Onde Encontrar Funcionalidade

**Você:**
```
Onde vejo o histórico disciplinar de um funcionário?
```

**Bartolo:**
```
O histórico disciplinar fica em dois lugares:

**Opção 1: Pelo Módulo Operacional (Recomendado)**
```
Menu > Operacional > Medidas Administrativas

1. Use o filtro de funcionário
2. Digite o nome ou CPF
3. Clique em "Buscar"
4. Verá todas as medidas:
   - Advertências verbais
   - Advertências escritas
   - Suspensões
   - Demissão por justa causa (se houver)
```

**Opção 2: Pelo Cadastro do Funcionário**
```
Menu > Operacional > Funcionários

1. Busque o funcionário
2. Clique no nome
3. Aba "Histórico Disciplinar"
4. Ver linha do tempo completa
```

**Informações Disponíveis:**
- 📅 Data da ocorrência
- ⚠️ Tipo da medida
- 📝 Motivo detalhado
- 👤 Quem aplicou
- ✍️ Status da assinatura
- 📎 Documentos anexos

**Busca Rápida:**
Use o atalho **Ctrl+K** e digite:
"Medidas administrativas [Nome do Funcionário]"

**Relatórios:**
Menu > Relatórios > Operacional > Histórico Disciplinar

Posso gerar relatório com:
- Todos os funcionários com medidas
- Período específico
- Por tipo de medida
- Por posto/cliente

**Quer que eu consulte o histórico de algum funcionário específico?**
```

## 🤝 Processos Guiados (Wizards)

### Exemplo 10: Criar Proposta Comercial

**Você:**
```
Preciso criar uma proposta para um condomínio
```

**Bartolo:**
```
Ótimo! Vou te guiar passo a passo na criação da proposta.

🧙 **Wizard: Proposta Comercial para Condomínio**

**Passo 1 de 8: Dados do Cliente**

Preciso de algumas informações básicas:

1. **Nome do Condomínio:**
   Ex: Condomínio Residencial Jardins

2. **CNPJ:** (se já for cliente cadastrado)
   Ou digite "novo" para cadastrar

3. **Responsável pelo Contato:**
   Nome do síndico ou administrador

4. **Contato:**
   Email e telefone

---

Me passa essas informações e vou para o próximo passo!

💡 **Dica:** Se o condomínio já for cliente, posso importar os dados automaticamente.
```

**Você:**
```
Nome: Condomínio Residencial Jardins
CNPJ: 12.345.678/0001-90
Responsável: João Silva (Síndico)
Contato: joao@condominiosjardins.com.br / (11) 98765-4321
```

**Bartolo:**
```
Perfeito! ✅

🔍 Encontrei o cadastro! Condomínio Residencial Jardins já é cliente.

**Dados Confirmados:**
- Nome: Condomínio Residencial Jardins
- CNPJ: 12.345.678/0001-90
- Endereço: Rua das Flores, 123 - São Paulo/SP
- Síndico: João Silva
- Contato: joao@condominiosjardins.com.br

---

**Passo 2 de 8: Serviços Desejados**

Quais serviços o condomínio precisa?

1. 🏢 **Portaria e Controle de Acesso**
2. 👁️ **Vigilância Patrimonial**
3. 🧹 **Limpeza e Conservação**
4. 🔧 **Manutenção Predial**
5. 📋 **Facilities Completo** (todos acima)

Digite o número ou os números separados por vírgula:
Ex: "1,2" para Portaria e Vigilância
```

**Você:**
```
1,2
```

**Bartolo:**
```
Ótimo! ✅

Serviços selecionados:
- 🏢 Portaria e Controle de Acesso
- 👁️ Vigilância Patrimonial

---

**Passo 3 de 8: Postos de Trabalho - Portaria**

Vamos detalhar a portaria:

1. **Quantidade de portarias:**
   (geralmente 1 ou 2)

2. **Horário de funcionamento:**
   - 24 horas (recomendado)
   - Comercial (08h-20h)
   - Personalizado

3. **Perfil desejado:**
   - Porteiro
   - Porteiro + Recepcionista
   - Controlador de Acesso

Me passa essas informações:
```

*[O wizard continua guiando passo a passo até a proposta completa estar montada com todos os cálculos de custo, BDI, valores finais, etc]*

---

## 💡 Dicas de Uso

### O Bartolo Entende Contexto

**Você pode perguntar de forma natural:**

✅ "Quanto custaria contratar mais 3 vigilantes?"
✅ "O João pode folgar na sexta que vem?"
✅ "Temos alguém disponível para cobrir o posto do shopping amanhã?"
✅ "Quais funcionários estão com férias vencidas?"
✅ "Mostre os clientes inadimplentes"

### O Bartolo Lembra da Conversa

**Conversa contínua:**

```
Você: "Mostre o saldo de banco de horas do João"
Bartolo: [mostra saldo de +12h30]

Você: "Ele pode compensar na sexta?"
Bartolo: "Sim! João pode usar as 8h de crédito para folgar na sexta..."

Você: "Então agenda isso pra ele"
Bartolo: "Vou agendar a compensação do João Silva para sexta 31/01..."
```

### O Bartolo É Proativo

Ele oferece sugestões sem você pedir:

```
Bartolo: "⚠️ Notei que o posto Central está com 4 faltas esse mês.
Isso está acima da média. Quer que eu analise as causas e sugira ações?"
```

---

**🎉 Aproveite o Bartolo!**

Ele está aqui para facilitar sua vida no Conecta PRO.

**Qualquer dúvida, é só perguntar a ele mesmo! 🐕**

---

**Desenvolvido com ❤️ pela equipe Conecta PRO**
