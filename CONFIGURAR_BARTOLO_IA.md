# Como Configurar o Bartolo como Agente de IA Real

## 🎯 O Que Foi Feito

O Bartolo foi transformado de um chatbot com respostas pré-prontas em um **agente de IA conversacional real** usando LLMs (Large Language Models).

### Mudanças Implementadas:

✅ **System Prompt Rico** (`/opt/conecta-pro/backend/modules/ai/bartolo/config/system_prompt.py`)
   - Conhecimento COMPLETO do Conecta PRO (28+ módulos)
   - Todos os processos de negócio
   - CLT, CCT SINDCOND 2026, eSocial, LGPD
   - Cálculos trabalhistas e financeiros
   - Integração com Solides DP
   - Hardware integrado (Control iD, Intelbras, Hikvision)

✅ **Configurações de LLM** (`/opt/conecta-pro/backend/core/config/settings.py`)
   - Suporte para OpenAI GPT
   - Suporte para Anthropic Claude
   - Fallback local automático

✅ **LLMProvider Atualizado** (`/opt/conecta-pro/backend/modules/ai/conversation/services/llm_provider.py`)
   - Usa settings para API keys
   - Seleciona provider automaticamente
   - Fallback inteligente

✅ **BartoloEngine Atualizado** (`/opt/conecta-pro/backend/modules/ai/bartolo/services/bartolo_engine.py`)
   - Usa system prompt rico
   - Mantém histórico de conversa
   - Contexto do usuário e módulo

✅ **Variáveis de Ambiente** (`.env.example`)
   - Documentação completa
   - Exemplos de configuração

## 🚀 Como Ativar o Bartolo com IA

### Opção 1: Anthropic Claude (Recomendado)

**Passo 1:** Obtenha uma API key em https://console.anthropic.com/

**Passo 2:** Edite `/opt/conecta-pro/.env` e adicione:

```bash
# AI/LLM Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-SUA_KEY_AQUI
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
LLM_FALLBACK_ENABLED=true
```

**Passo 3:** Reinicie o backend:

```bash
cd /opt/conecta-pro
docker compose restart backend
```

### Opção 2: OpenAI GPT

**Passo 1:** Obtenha uma API key em https://platform.openai.com/

**Passo 2:** Edite `/opt/conecta-pro/.env` e adicione:

```bash
# AI/LLM Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-SUA_KEY_AQUI
LLM_MODEL=gpt-4
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
LLM_FALLBACK_ENABLED=true
```

**Passo 3:** Reinicie o backend:

```bash
cd /opt/conecta-pro
docker compose restart backend
```

### Opção 3: Modo Local (Sem API)

Se não quiser usar IA por enquanto, mantenha:

```bash
LLM_PROVIDER=local
LLM_FALLBACK_ENABLED=true
```

O Bartolo continuará funcionando com respostas pré-definidas.

## 🧪 Como Testar

1. Acesse o frontend do Conecta PRO
2. Abra o chat do Bartolo (ícone do cachorro)
3. Pergunte: **"Olá Bartolo, você está usando IA? Qual modelo?"**

**Resposta Esperada (com IA):**
```
Olá! Sim, estou usando IA conversacional com o modelo Claude 3.5 Sonnet
da Anthropic. Isso me permite conversar de forma natural e entender
contexto. Como posso ajudar?
```

**Resposta Esperada (sem IA):**
```
Olá! Sou o Bartolo, seu assistente no Conecta PRO. Como posso ajudar?
```

## 📊 Verificar Status nos Logs

```bash
docker logs -f conecta-pro-backend | grep -i "provider\|bartolo"
```

**Com API configurada:**
```
INFO: Anthropic Claude provider inicializado com modelo claude-3-5-sonnet-20241022
```

**Sem API configurada:**
```
WARNING: Provider 'anthropic' configurado mas API key nao encontrada. Usando fallback local.
INFO: Usando LocalFallbackProvider (respostas pre-definidas)
```

## 💡 O Que o Bartolo Sabe Agora

O Bartolo possui conhecimento profundo sobre:

### Módulos do Sistema
- Operacional: Escalas 12x36, Postos, Turnos, Ocorrências, Medidas Disciplinares
- CRM: Leads, Propostas, Contratos, Comissões
- RH: Admissão, Folha, Ponto, Férias, Treinamentos
- Financeiro: Pagar, Receber, Fluxo Caixa, DRE
- Licitações: Editais, PNCP, BDI, Certidões

### Legislação
- CLT completa
- CCT SINDCOND 2026 (pisos salariais, benefícios)
- NR-7 (PCMSO), NR-9 (PPRA), NR-6 (EPIs)
- Lei 14.133/2021 (Licitações)
- LGPD

### Cálculos Automáticos
- Férias (1/3, proporcionais, abono)
- 13º Salário
- Rescisão (aviso prévio, FGTS 40%)
- Horas Extras (50%, 100%)
- Adicional Noturno (20%)
- Encargos Sociais (~72%)

### Integração Solides DP
- Fluxo bidirecional de dados
- Admissões e demissões
- Horas extras para folha
- Medidas disciplinares

## 📝 Exemplos de Conversas

### Antes (Respostas Pré-Prontas)

**Você:** "Como funciona o banco de horas?"

**Bartolo:** "O banco de horas e gerenciado em Operacional > Banco de Horas. Acompanhe saldos, lancamentos, compensacoes e relatorios por funcionario."

### Depois (IA Conversacional)

**Você:** "Como funciona o banco de horas?"

**Bartolo:** "O banco de horas no Conecta PRO funciona conforme a CLT:

**Créditos:**
- Horas extras trabalhadas são creditadas automaticamente
- Limite: 2 horas extras por dia

**Débitos:**
- Compensação mediante acordo
- Pode ser usado para cobrir atrasos ou faltas

**Validade:**
- 6 meses (acordo individual)
- 12 meses (acordo coletivo/CCT)

**Alertas Automáticos:**
- Sistema avisa 30 dias antes de horas vencerem
- Notifica quando saldo fica alto

Você pode consultar o saldo de qualquer funcionário em **Operacional > Banco de Horas**.
Quer que eu mostre o saldo de algum funcionário específico?"

## 🎛️ Parâmetros Ajustáveis

### LLM_MAX_TOKENS (Tamanho da Resposta)
- `1000`: Respostas curtas
- `2000`: **Padrão** (recomendado)
- `4000`: Respostas muito detalhadas

### LLM_TEMPERATURE (Criatividade)
- `0.0-0.3`: Muito consistente
- `0.5-0.7`: **Padrão** (balanceado)
- `0.8-1.0`: Criativo (cuidado com invenções)

## 💰 Custos Estimados

### Anthropic Claude 3.5 Sonnet
- **Input:** $3 por 1M tokens
- **Output:** $15 por 1M tokens
- **Conversa típica:** ~2000 tokens ≈ $0.03
- **100 conversas/dia:** ~$90/mês

### OpenAI GPT-4
- **Input:** $10 por 1M tokens
- **Output:** $30 por 1M tokens
- **Conversa típica:** ~2000 tokens ≈ $0.06
- **100 conversas/dia:** ~$180/mês

### Modo Local
- **Gratuito** ✨

## 🔒 Segurança

- API keys ficam apenas no `.env` (nunca commita isso no Git!)
- Bartolo respeita permissões do usuário
- Dados sensíveis são mascarados (CPF: ***.123.456-**)
- Todas as conversas são logadas para auditoria

## 🐛 Solução de Problemas

### Bartolo usa respostas genéricas

**Causa:** API key não configurada ou inválida

**Solução:**
1. Verifique o `.env`
2. Confirme que a key está correta
3. Reinicie o backend
4. Veja os logs

### Erro "API key inválida"

**Causa:** Key incorreta ou expirada

**Solução:**
1. Gere nova key no console da Anthropic/OpenAI
2. Atualize o `.env`
3. Reinicie o backend

### Respostas muito lentas

**Causa:** Modelo pesado ou tokens altos

**Solução:**
1. Use `gpt-3.5-turbo` ou `claude-3-sonnet`
2. Reduza `LLM_MAX_TOKENS` para 1500

## 📚 Documentação Completa

Para mais detalhes, veja:

```
/opt/conecta-pro/backend/modules/ai/bartolo/README_BARTOLO_AI.md
```

## ✅ Checklist de Configuração

- [ ] API key obtida (Anthropic ou OpenAI)
- [ ] `.env` configurado com as variáveis corretas
- [ ] Backend reiniciado
- [ ] Logs verificados (provider inicializado)
- [ ] Teste no frontend realizado
- [ ] Bartolo responde de forma natural

## 🎉 Pronto!

O Bartolo agora é um verdadeiro assistente de IA que:

- ✅ Conversa naturalmente
- ✅ Entende contexto
- ✅ Lembra da conversa
- ✅ Conhece TODO o sistema
- ✅ É proativo em ajudar
- ✅ Tem personalidade de cachorro salsicha amigável

**Dúvidas?** Pergunte ao próprio Bartolo! 🐕

---

**Desenvolvido com ❤️ pela equipe Conecta PRO**
