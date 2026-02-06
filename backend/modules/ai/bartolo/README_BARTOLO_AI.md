# Bartolo - Assistente de IA Conversacional

## Visão Geral

O Bartolo é o assistente inteligente oficial do Conecta PRO. Ele conhece **profundamente** todo o sistema e pode ajudar usuários a:

- Navegar no sistema
- Consultar dados em tempo real
- Calcular valores trabalhistas/financeiros
- Guiar processos complexos passo a passo (wizards)
- Responder dúvidas sobre qualquer funcionalidade
- Gerar relatórios e análises

## Modos de Operação

### 1. Modo LLM (Recomendado) ✨

Usa modelos de linguagem avançados (Anthropic Claude ou OpenAI GPT) para conversas naturais e contextuais.

**Vantagens:**
- Conversação natural e fluida
- Entende contexto e nuances
- Aprende com a conversa
- Respostas personalizadas
- Pode inferir intenções

**Requisitos:**
- API key da Anthropic ou OpenAI
- Configuração no `.env`

### 2. Modo Fallback Local

Usa respostas pré-definidas baseadas em palavras-chave.

**Vantagens:**
- Não requer API key
- Gratuito
- Funciona offline
- Rápido

**Desvantagens:**
- Respostas limitadas
- Não entende contexto
- Não aprende
- Menos natural

## Configuração

### Passo 1: Obter API Key

**Opção A: Anthropic Claude (Recomendado)**

1. Acesse: https://console.anthropic.com/
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Clique em "Create Key"
5. Copie a key (começa com `sk-ant-`)

**Opção B: OpenAI GPT**

1. Acesse: https://platform.openai.com/
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Clique em "Create new secret key"
5. Copie a key (começa com `sk-`)

### Passo 2: Configurar `.env`

Edite o arquivo `/opt/conecta-pro/.env` (ou crie a partir do `.env.example`):

**Para Anthropic Claude:**
```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-api03-sua-key-aqui
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
LLM_FALLBACK_ENABLED=true
```

**Para OpenAI GPT:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-sua-key-aqui
LLM_MODEL=gpt-4
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
LLM_FALLBACK_ENABLED=true
```

**Para Modo Local (sem API):**
```bash
LLM_PROVIDER=local
LLM_FALLBACK_ENABLED=true
```

### Passo 3: Reiniciar o Backend

```bash
cd /opt/conecta-pro
docker compose restart backend
```

Ou se não estiver usando Docker:
```bash
cd /opt/conecta-pro/backend
# Pare o processo atual (Ctrl+C)
# Reinicie:
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

### Passo 4: Verificar

1. Acesse o frontend
2. Abra o Bartolo (ícone do chat)
3. Pergunte: "Olá Bartolo, você está usando IA?"
4. Ele deve responder de forma natural e mencionar qual modelo está usando

## Modelos Disponíveis

### Anthropic Claude

| Modelo | Velocidade | Inteligência | Custo | Recomendado Para |
|--------|-----------|--------------|-------|------------------|
| `claude-3-5-sonnet-20241022` | ⚡⚡⚡ | 🧠🧠🧠🧠 | 💰💰 | **Produção** (melhor custo-benefício) |
| `claude-3-opus-20240229` | ⚡⚡ | 🧠🧠🧠🧠🧠 | 💰💰💰 | Tarefas complexas |
| `claude-3-sonnet-20240229` | ⚡⚡⚡ | 🧠🧠🧠 | 💰 | Uso intenso |

### OpenAI GPT

| Modelo | Velocidade | Inteligência | Custo | Recomendado Para |
|--------|-----------|--------------|-------|------------------|
| `gpt-4` | ⚡⚡ | 🧠🧠🧠🧠🧠 | 💰💰💰 | Máxima qualidade |
| `gpt-4-turbo-preview` | ⚡⚡⚡ | 🧠🧠🧠🧠 | 💰💰 | **Produção** |
| `gpt-3.5-turbo` | ⚡⚡⚡⚡ | 🧠🧠🧠 | 💰 | Alto volume |

## Parâmetros de Ajuste

### LLM_MAX_TOKENS

Define tamanho máximo da resposta.

- **1000-1500**: Respostas concisas
- **2000**: Padrão (recomendado)
- **3000-4000**: Respostas detalhadas

### LLM_TEMPERATURE

Controla criatividade/aleatoriedade.

- **0.0-0.3**: Muito determinístico (sempre responde igual)
- **0.5-0.7**: Balanceado (recomendado)
- **0.8-1.0**: Criativo (pode inventar coisas)

### LLM_FALLBACK_ENABLED

Se `true`, usa respostas locais quando API falhar.

**Recomendação:** Sempre deixar `true` em produção.

## Conhecimento do Bartolo

O Bartolo possui conhecimento COMPLETO sobre:

### Módulos do Sistema
- ✅ CRM (Leads, Clientes, Propostas)
- ✅ Operacional (Escalas 12x36, Postos, Turnos, Ocorrências)
- ✅ RH (Admissão, Folha, Ponto, Férias)
- ✅ Financeiro (Pagar, Receber, Fluxo Caixa, DRE)
- ✅ Licitações (Editais, PNCP, BDI)
- ✅ Contratos (Gestão, Aditivos, Reajustes)
- ✅ Saúde Ocupacional (PCMSO, EPIs, ASO)
- ✅ Integrações (eSocial, SEFAZ, Ponto Eletrônico)

### Legislação
- ✅ CLT (Consolidação das Leis do Trabalho)
- ✅ CCT SINDCOND 2026 (pisos salariais, benefícios)
- ✅ NR-7 (PCMSO), NR-9 (PPRA), NR-6 (EPIs)
- ✅ Lei 14.133/2021 (Nova Lei de Licitações)
- ✅ LGPD (Lei Geral de Proteção de Dados)

### Cálculos
- ✅ Férias (1/3 constitucional, proporcionais)
- ✅ 13º Salário
- ✅ Rescisão (aviso prévio, FGTS 40%)
- ✅ Horas Extras (50%, 100%)
- ✅ Adicional Noturno (20%)
- ✅ Encargos Sociais (~72%)
- ✅ BDI para licitações

### Processos de Negócio
- ✅ Criação de propostas comerciais
- ✅ Montagem de escalas 12x36
- ✅ Aplicação de medidas disciplinares
- ✅ Admissão e demissão de funcionários
- ✅ Faturamento de contratos
- ✅ Participação em licitações

## Integração com Solides DP

O Bartolo conhece a integração bidirecional com o Solides:

- Envio de admissões, horas extras, medidas disciplinares
- Recebimento de folha fechada, férias programadas
- Sincronização automática de dados

## Exemplos de Uso

### Consultas
```
"Quem está trabalhando no posto Central agora?"
"Qual o saldo de banco de horas do João Silva?"
"Mostre as propostas em aberto"
"Quantas faltas tivemos essa semana?"
```

### Cálculos
```
"Calcule as férias do funcionário CPF 123.456.789-00"
"Quanto de hora extra fizemos no cliente Condomínio ABC?"
"Calcule a rescisão do João que trabalhou 2 anos"
```

### Orientação
```
"Como monto uma escala 12x36?"
"O que preciso para admitir um funcionário?"
"Como funciona o banco de horas?"
"Explique o processo de advertência"
```

### Wizards
```
"Quero criar uma proposta comercial"
"Preciso aplicar uma advertência"
"Vou demitir um funcionário"
"Como faço para faturar?"
```

### Navegação
```
"Onde cadastro um cliente?"
"Como acesso as escalas?"
"Onde vejo o histórico disciplinar?"
```

## Monitoramento

### Logs

Os logs do Bartolo aparecem em:
```bash
docker logs -f conecta-pro-backend
```

Procure por:
```
OpenAI provider inicializado com modelo gpt-4
```
ou
```
Anthropic Claude provider inicializado com modelo claude-3-5-sonnet-20241022
```
ou
```
Usando LocalFallbackProvider (respostas pre-definidas)
```

### Métricas

O Bartolo registra para cada conversa:
- Modelo usado
- Tokens consumidos
- Tempo de resposta (ms)
- Intent detectado
- Confidence

Esses dados ficam disponíveis para análise de uso e otimização.

## Custos Estimados

### Anthropic Claude (Claude 3.5 Sonnet)
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens
- **Conversa típica**: ~2000 tokens = $0.03
- **100 conversas/dia**: ~$3/dia = $90/mês

### OpenAI GPT-4
- Input: $10 / 1M tokens
- Output: $30 / 1M tokens
- **Conversa típica**: ~2000 tokens = $0.06
- **100 conversas/dia**: ~$6/dia = $180/mês

### Modo Local
- **Gratuito** ✨

## Solução de Problemas

### Bartolo usa respostas genéricas

**Problema:** Bartolo responde de forma limitada, sempre as mesmas coisas.

**Solução:**
1. Verifique se a API key está configurada no `.env`
2. Verifique se o provider está correto (`anthropic` ou `openai`)
3. Reinicie o backend
4. Veja os logs: `docker logs -f conecta-pro-backend`

### Erro "API key inválida"

**Problema:** Logs mostram erro de autenticação.

**Solução:**
1. Confirme que a API key está correta (sem espaços extras)
2. Verifique se a key não expirou no console da Anthropic/OpenAI
3. Confirme que há créditos disponíveis na conta

### Respostas muito lentas

**Problema:** Bartolo demora muito para responder.

**Solução:**
1. Use modelo mais rápido (`gpt-3.5-turbo` ou `claude-3-sonnet`)
2. Reduza `LLM_MAX_TOKENS` para 1500
3. Verifique latência da API (pode ser região geográfica)

### Respostas inventadas

**Problema:** Bartolo inventa dados que não existem.

**Solução:**
1. Reduza `LLM_TEMPERATURE` para 0.3-0.5
2. Use modelos mais precisos (GPT-4, Claude 3.5 Sonnet)
3. Isso é "hallucination" do LLM - reporte ao suporte

## Roadmap

### Futuro Próximo
- [ ] Busca em base de conhecimento (RAG)
- [ ] Execução de ações (criar registros, gerar relatórios)
- [ ] Integração com WhatsApp
- [ ] Voz (speech-to-text)

### Futuro Distante
- [ ] Aprendizado contínuo
- [ ] Personalização por usuário
- [ ] Sugestões proativas
- [ ] Automações inteligentes

## Suporte

Dúvidas ou problemas com o Bartolo?

- **Documentação Completa:** `/opt/conecta-pro/docs/`
- **Email:** suporte@conectapro.com.br
- **Slack:** #bartolo-ai

---

**Desenvolvido com ❤️ pela equipe Conecta PRO**
