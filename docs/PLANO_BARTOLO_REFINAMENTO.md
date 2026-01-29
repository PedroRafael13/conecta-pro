# Plano de Refinamento do Bartolo - Módulo Operacional

**Data:** 2026-01-29
**Status:** Pendente
**Prioridade:** Alta

---

## 1. Diagnóstico dos Problemas Atuais

### 1.1 Problemas Identificados

| Problema | Impacto | Causa Raiz |
|----------|---------|------------|
| Patterns incompletos | Consultas não detectadas | Lista criada de forma ad-hoc, sem metodologia |
| Sem testes automatizados | Bugs descobertos em produção | Falta de cobertura de testes |
| Sem fallback inteligente | Respostas genéricas quando não detecta | Arquitetura rígida |
| Agentes não inicializados | Agentes não processam mensagens | Dependência de `db` para inicialização |
| Variações verbais não cobertas | "Crie" vs "Criar" não funciona | Patterns muito específicos |

### 1.2 Arquitetura Atual (Fluxo)

```
Mensagem → Skills (/) → Agentes Especializados → DataConnector → Wizard → LLM
                ↓              ↓                      ↓
           Retorna se      Retorna se            Retorna se
           match           keyword + intent       query detectada
```

**Problema:** Se nenhum pattern der match, vai direto para o LLM sem contexto de dados.

---

## 2. Revisão Sistemática dos Patterns

### 2.1 Metodologia

Para cada funcionalidade, mapear:
1. **Forma imperativa:** "Gere a escala", "Crie a escala"
2. **Forma interrogativa:** "Qual a escala?", "Como está a escala?"
3. **Forma descritiva:** "Quero ver a escala", "Preciso da escala"
4. **Variações verbais:** crie/criar/gere/gerar/monte/montar/faça/fazer
5. **Sinônimos:** escala/grade/programação/agenda
6. **Erros comuns de digitação:** escalas/escla/cobertrua

### 2.2 Lista Exaustiva de Patterns por Categoria

#### 2.2.1 COBERTURA_CRITICA

```python
PATTERNS_COBERTURA = [
    # Forma direta
    r"cobertura\s+critica",
    r"cobertura\s+baixa",
    r"gaps?\s+(?:de\s+)?cobertura",
    r"buracos?\s+(?:na\s+)?(?:escala|cobertura)",

    # Postos
    r"postos?\s+(?:sem|com\s+baixa)\s+cobertura",
    r"postos?\s+descobertos?",
    r"postos?\s+criticos?",
    r"postos?\s+(?:com\s+)?problema",
    r"postos?\s+(?:em\s+)?alerta",
    r"postos?\s+vazios?",
    r"postos?\s+(?:sem\s+)?funcionarios?",

    # Interrogativas
    r"(?:quais?|quantos?)\s+postos?\s+(?:estao\s+)?(?:sem|descobertos?)",
    r"(?:tem|ha)\s+(?:algum\s+)?posto\s+(?:sem|descoberto)",
    r"como\s+(?:esta|ta)\s+(?:a\s+)?cobertura",
    r"situacao\s+(?:da\s+)?cobertura",

    # Ações
    r"(?:ver|mostrar|exibir|listar)\s+(?:postos?\s+)?(?:sem\s+)?cobertura",
    r"(?:verificar|checar|analisar)\s+cobertura",
    r"cobertura\s+(?:de\s+|dos?\s+)?postos?",
    r"cobertura\s+(?:em\s+)?tempo\s+real",

    # Sinônimos
    r"vagas?\s+(?:em\s+)?aberto",
    r"posicoes?\s+(?:sem\s+)?preencher",
    r"locais?\s+(?:sem\s+)?cobertura",
]
```

#### 2.2.2 FUNCIONARIOS_TRABALHANDO

```python
PATTERNS_TRABALHANDO = [
    # Direto
    r"quem\s+(?:esta|ta|está)\s+trabalhando",
    r"quem\s+(?:esta|ta|está)\s+(?:em\s+)?servico",
    r"quem\s+(?:esta|ta|está)\s+(?:no\s+)?turno",
    r"quem\s+(?:esta|ta|está)\s+(?:em\s+)?(?:campo|posto)",

    # Funcionários
    r"funcionarios?\s+(?:em\s+)?(?:servico|turno|trabalho)",
    r"funcionarios?\s+(?:agora|atualmente|hoje)",
    r"funcionarios?\s+trabalhando",
    r"funcionarios?\s+ativos?\s+(?:agora|hoje)",

    # Equipe
    r"equipe\s+(?:em\s+)?servico",
    r"equipe\s+(?:de\s+)?(?:hoje|plantao)",
    r"equipe\s+(?:no\s+)?turno",
    r"equipe\s+trabalhando",

    # Interrogativas
    r"quantos?\s+(?:estao\s+)?trabalhando",
    r"quantos?\s+(?:funcionarios?\s+)?(?:em\s+)?servico",

    # Sinônimos
    r"colaboradores?\s+(?:em\s+)?(?:servico|turno)",
    r"vigilantes?\s+(?:em\s+)?(?:servico|turno)",
    r"porteiros?\s+(?:em\s+)?(?:servico|turno)",
]
```

#### 2.2.3 FUNCIONARIOS_FOLGA (Disponíveis)

```python
PATTERNS_FOLGA = [
    # Folga
    r"quem\s+(?:esta|ta|está)\s+(?:de\s+)?folga",
    r"quem\s+(?:esta|ta|está)\s+folgando",
    r"funcionarios?\s+(?:de\s+|em\s+)?folga",
    r"folgas?\s+(?:de\s+)?hoje",

    # Disponíveis
    r"funcionarios?\s+disponiveis?",
    r"quem\s+(?:esta|ta|está)\s+disponivel",
    r"disponiveis?\s+(?:para\s+)?(?:hoje|trabalhar|cobrir)",
    r"quem\s+pode\s+(?:trabalhar|cobrir|substituir)",
    r"quem\s+(?:esta|ta|está)\s+livre",

    # Para convocação
    r"funcionarios?\s+(?:para\s+)?convocar",
    r"quem\s+(?:posso|pode)\s+(?:chamar|convocar)",
    r"lista\s+(?:de\s+)?(?:convocacao|disponiveis)",

    # Banco de reserva
    r"reservas?\s+(?:disponiveis?)?",
    r"plantonistas?\s+(?:disponiveis?)?",
]
```

#### 2.2.4 ESCALAS_PENDENTES

```python
PATTERNS_ESCALAS_PENDENTES = [
    # Pendentes
    r"escalas?\s+pendentes?",
    r"escalas?\s+(?:para\s+)?aprovar",
    r"escalas?\s+aguardando",
    r"escalas?\s+(?:em\s+)?rascunho",
    r"escalas?\s+(?:nao\s+)?publicadas?",

    # Atuais
    r"escalas?\s+atuais?",
    r"escalas?\s+(?:em\s+)?vigor",
    r"escalas?\s+(?:da\s+)?semana",
    r"escalas?\s+(?:do\s+)?mes",

    # Verificar
    r"(?:ver|verificar|mostrar|listar)\s+(?:as\s+)?escalas?",
    r"(?:quais?|quantas?)\s+escalas?\s+(?:pendentes?|aguardando)",

    # Status
    r"status\s+(?:das?\s+)?escalas?",
    r"situacao\s+(?:das?\s+)?escalas?",
]
```

#### 2.2.5 HORA_EXTRA_RANKING

```python
PATTERNS_HORA_EXTRA = [
    # Hora extra
    r"horas?\s+extras?",
    r"hora\s+extra",
    r"HE\s+(?:do\s+)?mes",

    # Ranking
    r"ranking\s+(?:de\s+)?horas?\s+extras?",
    r"quem\s+(?:tem|fez)\s+(?:mais\s+)?horas?\s+extras?",
    r"funcionarios?\s+(?:com\s+)?(?:mais\s+)?horas?\s+extras?",

    # Banco de horas
    r"banco\s+(?:de\s+)?horas",
    r"saldo\s+(?:de\s+)?horas",
    r"credito\s+(?:de\s+)?horas",
    r"debito\s+(?:de\s+)?horas",

    # Limites
    r"quem\s+(?:esta|ta)\s+(?:no\s+)?limite",
    r"funcionarios?\s+(?:no\s+)?limite\s+(?:de\s+)?(?:HE|horas)",
    r"excesso\s+(?:de\s+)?horas",
]
```

#### 2.2.6 SUBSTITUICOES_PENDENTES

```python
PATTERNS_SUBSTITUICOES = [
    # Substituições
    r"substituicoes?\s+pendentes?",
    r"substituicoes?\s+(?:em\s+)?aberto",
    r"substituicoes?\s+(?:nao\s+)?resolvidas?",

    # Trocas
    r"trocas?\s+pendentes?",
    r"trocas?\s+(?:de\s+)?turno",
    r"trocas?\s+(?:em\s+)?aberto",

    # Coberturas
    r"coberturas?\s+pendentes?",
    r"coberturas?\s+(?:em\s+)?aberto",

    # Aguardando
    r"(?:aguardando|esperando)\s+(?:substituto|cobertura|troca)",
    r"precisando\s+(?:de\s+)?(?:substituto|cobertura)",
]
```

#### 2.2.7 ATRASOS_HOJE

```python
PATTERNS_ATRASOS = [
    # Atrasos
    r"atrasos?\s+(?:de\s+)?hoje",
    r"atrasos?\s+(?:do\s+)?dia",
    r"atrasados?",
    r"quem\s+(?:esta|ta|atrasou)",
    r"funcionarios?\s+atrasados?",

    # Check-in
    r"(?:sem\s+)?check-?in",
    r"(?:nao\s+)?(?:fez|fizeram)\s+check-?in",
    r"(?:falta|faltou)\s+check-?in",

    # Chegadas
    r"chegadas?\s+(?:com\s+)?atraso",
    r"chegadas?\s+atrasadas?",
    r"(?:nao\s+)?chegou\s+(?:ainda|no\s+horario)",

    # Ausências
    r"ausencias?\s+(?:de\s+)?hoje",
    r"faltas?\s+(?:de\s+)?hoje",
    r"quem\s+(?:faltou|nao\s+veio)",
]
```

#### 2.2.8 OPERACAO_GERAL (Resumo)

```python
PATTERNS_OPERACAO = [
    # Resumo
    r"resumo\s+(?:do\s+)?dia",
    r"resumo\s+(?:da\s+)?operacao",
    r"resumo\s+operacional",
    r"resumo\s+diario",

    # Status
    r"como\s+(?:esta|ta)\s+(?:a\s+)?operacao",
    r"status\s+(?:da\s+)?operacao",
    r"situacao\s+(?:da\s+)?operacao",
    r"visao\s+geral\s+(?:da\s+)?operacao",
    r"panorama\s+(?:da\s+)?operacao",

    # Dashboard
    r"dashboard\s+(?:operacional)?",
    r"painel\s+(?:operacional)?",
    r"indicadores?\s+(?:do\s+)?dia",

    # Dia
    r"como\s+(?:esta|foi)\s+(?:o\s+)?dia",
    r"(?:o\s+)?que\s+(?:esta\s+)?acontecendo",
    r"novidades?\s+(?:do\s+)?dia",
]
```

#### 2.2.9 ALERTAS

```python
PATTERNS_ALERTAS = [
    # Alertas
    r"alertas?\s+pendentes?",
    r"alertas?\s+(?:do\s+)?(?:dia|sistema)",
    r"alertas?\s+(?:em\s+)?aberto",
    r"alertas?\s+(?:nao\s+)?resolvidos?",

    # Pendências
    r"pendencias?",
    r"(?:o\s+que|quais?)\s+(?:esta|estao)\s+pendente",
    r"itens?\s+pendentes?",

    # Problemas
    r"problemas?\s+(?:pendentes?|abertos?)",
    r"(?:tem|ha)\s+(?:algum\s+)?(?:problema|alerta)",
    r"(?:algo|alguma\s+coisa)\s+(?:errada?|pendente)",

    # Urgente
    r"(?:urgente|critico|importante)",
    r"(?:preciso|precisamos)\s+(?:resolver|atender)",
    r"(?:atencao|atenção)\s+(?:imediata)?",
]
```

#### 2.2.10 KPIs

```python
PATTERNS_KPIS = [
    # KPIs
    r"kpis?\s+(?:principais?|do\s+sistema)?",
    r"indicadores?\s+(?:principais?|chave)?",
    r"metricas?\s+(?:principais?|do\s+sistema)?",

    # Números
    r"numeros?\s+(?:do\s+sistema|gerais?)",
    r"estatisticas?\s+(?:do\s+)?(?:dia|sistema)",

    # Performance
    r"performance\s+(?:do\s+)?(?:dia|sistema)",
    r"desempenho\s+(?:do\s+)?(?:dia|sistema)",

    # Dashboard
    r"dashboard",
    r"painel\s+(?:de\s+)?(?:controle|indicadores)",
]
```

### 2.3 Patterns para Agentes Especializados

#### EscalaAgent - INTENT_PATTERNS

```python
ESCALA_INTENT_PATTERNS = [
    # GERAR_ESCALA - todas as variações verbais
    (r"(?:gerar|gere|criar|crie|cria|monte|montar|fazer|faca|faz|elaborar|elabore)\s+(?:a\s+|uma\s+)?escala", GERAR_ESCALA),
    (r"nova\s+escala", GERAR_ESCALA),
    (r"escala\s+(?:para|de|do|da)\s+\w+", GERAR_ESCALA),
    (r"preciso\s+(?:de\s+)?(?:uma\s+)?escala", GERAR_ESCALA),
    (r"quero\s+(?:uma\s+)?escala", GERAR_ESCALA),
    (r"montar\s+(?:a\s+)?(?:grade|programacao)", GERAR_ESCALA),

    # OTIMIZAR_ESCALA
    (r"(?:otimizar|otimize|melhorar|melhore|ajustar|ajuste|refinar|refine)\s+(?:a\s+)?escala", OTIMIZAR_ESCALA),
    (r"(?:reduzir|diminuir)\s+(?:custo|hora\s+extra)\s+(?:da\s+)?escala", OTIMIZAR_ESCALA),
    (r"escala\s+(?:mais\s+)?(?:eficiente|barata|otimizada)", OTIMIZAR_ESCALA),

    # VALIDAR_ESCALA
    (r"(?:validar|valide|verificar|verifique|checar|cheque|conferir|confira)\s+(?:a\s+)?escala", VALIDAR_ESCALA),
    (r"escala\s+(?:esta\s+)?(?:correta|certa|ok|valida)", VALIDAR_ESCALA),
    (r"(?:tem|ha)\s+(?:algum\s+)?(?:problema|erro|conflito)\s+(?:na\s+)?escala", VALIDAR_ESCALA),

    # PUBLICAR_ESCALA
    (r"(?:publicar|publique|aprovar|aprove|liberar|libere|ativar|ative)\s+(?:a\s+)?escala", PUBLICAR_ESCALA),
    (r"(?:colocar|por)\s+escala\s+(?:em\s+)?(?:vigor|producao)", PUBLICAR_ESCALA),

    # CALCULAR_CUSTO
    (r"(?:custo|valor|preco)\s+(?:da\s+)?escala", CALCULAR_CUSTO),
    (r"quanto\s+(?:custa|vai\s+custar)\s+(?:a\s+)?escala", CALCULAR_CUSTO),
    (r"(?:calcular|calcule|estimar|estime)\s+(?:o\s+)?custo", CALCULAR_CUSTO),
    (r"(?:simular|simule)\s+(?:custo|valor)", CALCULAR_CUSTO),

    # LISTAR_CONFLITOS
    (r"conflitos?\s+(?:na\s+|da\s+|de\s+)?escala", LISTAR_CONFLITOS),
    (r"escala\s+(?:com\s+)?conflitos?", LISTAR_CONFLITOS),
    (r"(?:problemas?|erros?)\s+(?:na\s+)?escala", LISTAR_CONFLITOS),
    (r"(?:sobreposicao|choque)\s+(?:de\s+)?(?:horario|turno)", LISTAR_CONFLITOS),

    # ESCALA_SEMANA
    (r"escala\s+(?:da\s+|desta\s+)?semana", ESCALA_SEMANA),
    (r"(?:ver|veja|mostrar|mostre)\s+(?:a\s+)?escala\s+(?:da\s+)?semana", ESCALA_SEMANA),
    (r"(?:proximos?\s+)?(?:7|sete)\s+dias", ESCALA_SEMANA),

    # ESCALA_MES
    (r"escala\s+(?:do\s+|deste\s+)?mes", ESCALA_MES),
    (r"(?:ver|veja|mostrar|mostre)\s+(?:a\s+)?escala\s+(?:do\s+)?mes", ESCALA_MES),
    (r"escala\s+(?:de\s+)?(?:janeiro|fevereiro|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)", ESCALA_MES),
]
```

#### SubstituicaoAgent - INTENT_PATTERNS

```python
SUBSTITUICAO_INTENT_PATTERNS = [
    # BUSCAR_SUBSTITUTO
    (r"(?:buscar|busque|encontrar|encontre|achar|ache)\s+(?:um\s+)?substituto", BUSCAR_SUBSTITUTO),
    (r"(?:preciso|precisamos)\s+(?:de\s+)?(?:um\s+)?substituto", BUSCAR_SUBSTITUTO),
    (r"quem\s+(?:pode|consegue)\s+(?:cobrir|substituir)", BUSCAR_SUBSTITUTO),
    (r"(?:tem|ha)\s+(?:alguem\s+)?(?:para\s+)?(?:cobrir|substituir)", BUSCAR_SUBSTITUTO),

    # URGENTE
    (r"substituto\s+(?:urgente|emergencia|agora|imediato)", URGENTE),
    (r"(?:urgente|emergencia)\s+(?:preciso\s+)?substituto", URGENTE),
    (r"(?:cobrir|substituir)\s+(?:urgente|agora|imediato)", URGENTE),
    (r"(?:faltou|nao\s+veio)\s+(?:e\s+)?(?:preciso|precisamos)", URGENTE),

    # CONFIRMAR
    (r"(?:confirmar|confirme|aprovar|aprove)\s+(?:a\s+)?substituicao", CONFIRMAR),
    (r"(?:aceitar|aceite)\s+(?:o\s+)?substituto", CONFIRMAR),

    # PENDENTES
    (r"substituicoes?\s+pendentes?", PENDENTES),
    (r"(?:trocas?|coberturas?)\s+pendentes?", PENDENTES),
    (r"(?:aguardando|esperando)\s+(?:aprovacao|confirmacao)", PENDENTES),

    # HISTORICO
    (r"historico\s+(?:de\s+)?substituicoes?", HISTORICO),
    (r"substituicoes?\s+(?:anteriores|passadas|recentes)", HISTORICO),
    (r"(?:ultimas?|recentes?)\s+substituicoes?", HISTORICO),

    # CUSTO
    (r"custo\s+(?:da\s+)?substituicao", CUSTO),
    (r"quanto\s+(?:custa|custou)\s+(?:a\s+)?substituicao", CUSTO),

    # DISPONIBILIDADE
    (r"(?:verificar|ver)\s+disponibilidade", DISPONIBILIDADE),
    (r"quem\s+(?:esta\s+)?disponivel\s+(?:para\s+)?(?:cobrir|substituir)", DISPONIBILIDADE),
]
```

#### AlertaAgent - INTENT_PATTERNS

```python
ALERTA_INTENT_PATTERNS = [
    # VER_ALERTAS
    (r"(?:ver|veja|mostrar|mostre|listar|liste)\s+(?:os\s+)?alertas?", VER_ALERTAS),
    (r"(?:quais?|quantos?)\s+alertas?", VER_ALERTAS),
    (r"alertas?\s+(?:do\s+)?(?:dia|sistema)", VER_ALERTAS),

    # ALERTAS_CRITICOS
    (r"alertas?\s+(?:criticos?|urgentes?|importantes?)", CRITICOS),
    (r"(?:criticos?|urgentes?)\s+(?:primeiro)?", CRITICOS),
    (r"(?:mais\s+)?(?:graves?|serios?|importantes?)", CRITICOS),

    # COBERTURA
    (r"alertas?\s+(?:de\s+)?cobertura", COBERTURA),
    (r"(?:problemas?|alertas?)\s+(?:com\s+)?postos?", COBERTURA),

    # DOCUMENTOS
    (r"(?:documentos?|docs?)\s+(?:vencendo|vencidos?|expirando)", DOCUMENTOS),
    (r"alertas?\s+(?:de\s+)?(?:documentos?|docs?)", DOCUMENTOS),
    (r"(?:vencimento|validade)\s+(?:de\s+)?(?:documentos?|docs?)", DOCUMENTOS),

    # ATRASOS
    (r"alertas?\s+(?:de\s+)?atrasos?", ATRASOS),
    (r"(?:funcionarios?|equipe)\s+atrasados?", ATRASOS),

    # RESOLVER
    (r"(?:resolver|resolva|tratar|trate)\s+(?:o\s+)?alerta", RESOLVER),
    (r"(?:fechar|encerrar)\s+(?:o\s+)?alerta", RESOLVER),
]
```

---

## 3. Testes Automatizados

### 3.1 Estrutura de Testes

```
/opt/conecta-pro/backend/tests/
└── ai/
    └── bartolo/
        ├── __init__.py
        ├── conftest.py                    # Fixtures compartilhadas
        ├── test_data_connector_patterns.py # Testes de patterns do DataConnector
        ├── test_escala_agent_patterns.py   # Testes de patterns do EscalaAgent
        ├── test_substituicao_agent.py      # Testes do SubstituicaoAgent
        ├── test_alerta_agent.py            # Testes do AlertaAgent
        ├── test_skills.py                  # Testes das skills
        ├── test_bartolo_engine_flow.py     # Testes de fluxo completo
        └── test_integration.py             # Testes de integração
```

### 3.2 Arquivo de Testes de Patterns

```python
# tests/ai/bartolo/test_data_connector_patterns.py

import pytest
from modules.ai.bartolo.services.data_connector import DataConnector, QueryType

@pytest.fixture
def data_connector():
    return DataConnector()

class TestCoberturaCriticaPatterns:
    """Testes para patterns de COBERTURA_CRITICA"""

    MENSAGENS_ESPERADAS = [
        # Variações diretas
        "cobertura critica",
        "cobertura crítica",
        "Cobertura Critica",

        # Postos
        "postos sem cobertura",
        "posto sem cobertura",
        "postos descobertos",
        "postos criticos",
        "postos com baixa cobertura",
        "postos vazios",
        "postos sem funcionarios",

        # Interrogativas
        "quais postos estão sem cobertura",
        "quantos postos estão descobertos",
        "tem algum posto sem cobertura",
        "há posto descoberto",
        "como está a cobertura",

        # Ações
        "ver cobertura",
        "mostrar cobertura",
        "listar postos sem cobertura",
        "verificar cobertura",
        "analisar cobertura",
        "cobertura de postos",
        "cobertura em tempo real",

        # Sinônimos
        "gaps de cobertura",
        "buracos na escala",
        "vagas em aberto",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_cobertura_critica(self, data_connector, mensagem):
        """Testa se todas as variações são detectadas como COBERTURA_CRITICA"""
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.COBERTURA_CRITICA, \
            f"Tipo incorreto para '{mensagem}': esperado COBERTURA_CRITICA, obtido {result.query_type}"


class TestFuncionariosTrabalhando:
    """Testes para patterns de FUNCIONARIOS_TRABALHANDO"""

    MENSAGENS_ESPERADAS = [
        "quem está trabalhando",
        "quem esta trabalhando",
        "quem ta trabalhando",
        "quem está em serviço",
        "quem está no turno",
        "funcionários em serviço",
        "funcionarios trabalhando",
        "equipe em serviço",
        "equipe no turno",
        "quantos estão trabalhando",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_funcionarios_trabalhando(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.FUNCIONARIOS_TRABALHANDO


class TestFuncionariosFolga:
    """Testes para patterns de FUNCIONARIOS_FOLGA"""

    MENSAGENS_ESPERADAS = [
        "quem está de folga",
        "funcionários de folga",
        "folgas de hoje",
        "funcionários disponíveis",
        "funcionarios disponiveis hoje",
        "quem está disponível",
        "quem pode trabalhar",
        "quem pode cobrir",
        "disponíveis para hoje",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_funcionarios_folga(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.FUNCIONARIOS_FOLGA


class TestEscalasPendentes:
    """Testes para patterns de ESCALAS_PENDENTES"""

    MENSAGENS_ESPERADAS = [
        "escalas pendentes",
        "escalas para aprovar",
        "escalas aguardando",
        "escalas em rascunho",
        "escalas não publicadas",
        "escalas atuais",
        "ver escalas",
        "verificar as escalas atuais",
        "mostrar escalas",
        "status das escalas",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_escalas_pendentes(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.ESCALAS_PENDENTES


class TestHoraExtraRanking:
    """Testes para patterns de HORA_EXTRA_RANKING"""

    MENSAGENS_ESPERADAS = [
        "horas extras",
        "hora extra",
        "ranking de horas extras",
        "quem tem mais horas extras",
        "quem fez mais hora extra",
        "banco de horas",
        "saldo de horas",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_hora_extra(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.HORA_EXTRA_RANKING


class TestSubstituicoesPendentes:
    """Testes para patterns de SUBSTITUICOES_PENDENTES"""

    MENSAGENS_ESPERADAS = [
        "substituições pendentes",
        "substituicoes pendentes",
        "trocas pendentes",
        "coberturas pendentes",
        "aguardando substituto",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_substituicoes(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.SUBSTITUICOES_PENDENTES


class TestAtrasosHoje:
    """Testes para patterns de ATRASOS_HOJE"""

    MENSAGENS_ESPERADAS = [
        "atrasos de hoje",
        "atrasados",
        "quem atrasou",
        "funcionários atrasados",
        "chegadas com atraso",
        "quem está atrasado",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_atrasos(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.ATRASOS_HOJE


class TestOperacaoGeral:
    """Testes para patterns de OPERACAO_GERAL"""

    MENSAGENS_ESPERADAS = [
        "resumo do dia",
        "resumo diário",
        "como está a operação",
        "status da operação",
        "visão geral da operação",
        "panorama da operação",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_operacao(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.OPERACAO_GERAL


class TestAlertas:
    """Testes para patterns de ALERTS"""

    MENSAGENS_ESPERADAS = [
        "alertas pendentes",
        "alertas do dia",
        "pendências",
        "problemas pendentes",
        "tem algum alerta",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_alertas(self, data_connector, mensagem):
        result = data_connector.detect_data_query(mensagem)

        assert result is not None, f"Mensagem não detectada: '{mensagem}'"
        assert result.query_type == QueryType.ALERTS
```

### 3.3 Testes do EscalaAgent

```python
# tests/ai/bartolo/test_escala_agent_patterns.py

import pytest
from modules.ai.bartolo.agents.escala_agent import EscalaAgent, EscalaIntent

@pytest.fixture
def escala_agent():
    return EscalaAgent()

class TestGerarEscalaPatterns:
    """Testes para detecção de GERAR_ESCALA"""

    MENSAGENS_ESPERADAS = [
        # Imperativo
        "gerar escala",
        "gere a escala",
        "criar escala",
        "crie a escala",
        "cria uma escala",
        "monte a escala",
        "montar escala",
        "fazer escala",
        "faça a escala",
        "faz uma escala",
        "elaborar escala",
        "elabore a escala",

        # Com contexto
        "gerar escala para janeiro",
        "criar escala para o posto 001",
        "crie a escala para agentes de portaria",
        "Crie a escala para agentes de portaria pro mes de fevereiro de 2026",

        # Outras formas
        "nova escala",
        "preciso de uma escala",
        "quero uma escala",
        "escala para fevereiro",
        "escala para o cliente X",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_gerar_escala(self, escala_agent, mensagem):
        intent = escala_agent._detect_intent(mensagem)

        assert intent == EscalaIntent.GERAR_ESCALA, \
            f"Intent incorreto para '{mensagem}': esperado GERAR_ESCALA, obtido {intent}"


class TestOtimizarEscalaPatterns:
    """Testes para detecção de OTIMIZAR_ESCALA"""

    MENSAGENS_ESPERADAS = [
        "otimizar escala",
        "otimize a escala",
        "melhorar escala",
        "melhore a escala",
        "ajustar escala",
        "ajuste a escala",
        "refinar escala",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_otimizar_escala(self, escala_agent, mensagem):
        intent = escala_agent._detect_intent(mensagem)

        assert intent == EscalaIntent.OTIMIZAR_ESCALA


class TestValidarEscalaPatterns:
    """Testes para detecção de VALIDAR_ESCALA"""

    MENSAGENS_ESPERADAS = [
        "validar escala",
        "valide a escala",
        "verificar escala",
        "verifique a escala",
        "checar escala",
        "cheque a escala",
        "conferir escala",
    ]

    @pytest.mark.parametrize("mensagem", MENSAGENS_ESPERADAS)
    def test_detecta_validar_escala(self, escala_agent, mensagem):
        intent = escala_agent._detect_intent(mensagem)

        assert intent == EscalaIntent.VALIDAR_ESCALA
```

### 3.4 Teste de Fluxo Completo

```python
# tests/ai/bartolo/test_bartolo_engine_flow.py

import pytest
from modules.ai.bartolo.services.bartolo_engine import BartoloEngine

@pytest.fixture
def engine():
    return BartoloEngine()

@pytest.mark.asyncio
class TestBartoloEngineFlow:
    """Testes de fluxo completo do BartoloEngine"""

    async def test_flow_cobertura_critica(self, engine):
        """Testa que mensagem de cobertura vai para DataConnector"""
        response = await engine.process_message(
            user_id=1,
            session_id="test",
            message="postos sem cobertura",
            module="operacional",
            db=None
        )

        # Deve retornar dados do DataConnector, não resposta genérica do LLM
        assert "posto" in response.response.lower() or "cobertura" in response.response.lower()

    async def test_flow_gerar_escala_usa_agente(self, engine):
        """Testa que mensagem de criar escala usa EscalaAgent"""
        response = await engine.process_message(
            user_id=1,
            session_id="test",
            message="crie a escala para agentes de portaria",
            module="operacional",
            db=None
        )

        assert response.model_used == "specialized_agent"
        assert response.intent == "gerar_escala"

    async def test_flow_alertas_usa_agente(self, engine):
        """Testa que mensagem de alertas usa AlertaAgent"""
        response = await engine.process_message(
            user_id=1,
            session_id="test",
            message="alertas pendentes",
            module="operacional",
            db=None
        )

        assert response.model_used == "specialized_agent"

    async def test_flow_skill_command(self, engine):
        """Testa que comando de skill é processado"""
        response = await engine.process_message(
            user_id=1,
            session_id="test",
            message="/escala help",
            module="operacional",
            db=None
        )

        assert "escala" in response.response.lower()
```

### 3.5 Script de Execução de Testes

```bash
#!/bin/bash
# scripts/test_bartolo.sh

echo "=== Executando testes do Bartolo ==="

# Vai para o diretório do backend
cd /opt/conecta-pro/backend

# Executa testes com pytest
python -m pytest tests/ai/bartolo/ -v --tb=short

# Verifica cobertura
python -m pytest tests/ai/bartolo/ --cov=modules/ai/bartolo --cov-report=term-missing

echo "=== Testes finalizados ==="
```

### 3.6 Integração com CI/CD

```yaml
# .github/workflows/test-bartolo.yml

name: Test Bartolo

on:
  push:
    paths:
      - 'backend/modules/ai/bartolo/**'
  pull_request:
    paths:
      - 'backend/modules/ai/bartolo/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio pytest-cov
          pip install -r backend/requirements.txt

      - name: Run Bartolo tests
        run: |
          cd backend
          python -m pytest tests/ai/bartolo/ -v --tb=short

      - name: Check coverage
        run: |
          cd backend
          python -m pytest tests/ai/bartolo/ --cov=modules/ai/bartolo --cov-fail-under=80
```

---

## 4. Fallback Inteligente

### 4.1 Problema Atual

Quando nenhum pattern é detectado, a mensagem vai direto para o LLM sem contexto de dados. O LLM responde de forma genérica sem acesso aos dados reais do sistema.

### 4.2 Solução: Intent Classification via LLM

```python
# modules/ai/bartolo/services/intent_classifier_llm.py

from typing import Optional, Dict, Any
from enum import Enum
import json

class LLMIntentClassifier:
    """
    Classificador de intent usando LLM como fallback.
    Usado quando os patterns regex não conseguem detectar a intenção.
    """

    INTENT_CATEGORIES = {
        "cobertura": "COBERTURA_CRITICA",
        "funcionarios_trabalhando": "FUNCIONARIOS_TRABALHANDO",
        "funcionarios_folga": "FUNCIONARIOS_FOLGA",
        "escalas": "ESCALAS_PENDENTES",
        "hora_extra": "HORA_EXTRA_RANKING",
        "substituicoes": "SUBSTITUICOES_PENDENTES",
        "atrasos": "ATRASOS_HOJE",
        "operacao": "OPERACAO_GERAL",
        "alertas": "ALERTS",
        "kpis": "KPIS",
        "gerar_escala": "GERAR_ESCALA",
        "outro": "UNKNOWN",
    }

    CLASSIFICATION_PROMPT = """Você é um classificador de intenções para um sistema de gestão operacional de segurança.

Categorias disponíveis:
- cobertura: Perguntas sobre cobertura de postos, postos descobertos, vagas
- funcionarios_trabalhando: Quem está trabalhando, em serviço, no turno
- funcionarios_folga: Quem está de folga, disponível, pode ser convocado
- escalas: Escalas pendentes, atuais, para aprovar
- hora_extra: Horas extras, banco de horas, ranking
- substituicoes: Substituições pendentes, trocas
- atrasos: Atrasos, faltas, check-in
- operacao: Resumo do dia, status geral, dashboard
- alertas: Alertas, pendências, problemas
- kpis: Indicadores, métricas, números
- gerar_escala: Criar, montar, gerar nova escala
- outro: Não se encaixa em nenhuma categoria

Mensagem do usuário: "{message}"

Responda APENAS com o nome da categoria em minúsculas, sem explicação.
"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def classify(self, message: str) -> Optional[str]:
        """
        Classifica a intenção da mensagem usando LLM.

        Returns:
            QueryType string ou None se não conseguir classificar
        """
        try:
            prompt = self.CLASSIFICATION_PROMPT.format(message=message)

            response = await self.llm_client.generate(
                prompt=prompt,
                max_tokens=20,
                temperature=0,  # Determinístico
            )

            category = response.strip().lower()

            if category in self.INTENT_CATEGORIES:
                return self.INTENT_CATEGORIES[category]

            return None

        except Exception as e:
            logger.error(f"Erro na classificação LLM: {e}")
            return None
```

### 4.3 Integração no BartoloEngine

```python
# Modificação no bartolo_engine.py

async def process_message(self, ...):
    # ... código existente ...

    # 8. Verifica se é consulta de dados
    data_results = None
    if self.config.use_data_connector:
        data_results = await self._check_data_query(message, module, data_connector)

    # 8.1 NOVO: Fallback com LLM se não detectou pattern
    if data_results is None and self.config.use_llm_fallback:
        llm_intent = await self.llm_intent_classifier.classify(message)

        if llm_intent and llm_intent != "UNKNOWN":
            logger.info(f"Fallback LLM classificou como: {llm_intent}")

            # Cria query baseada na classificação do LLM
            fallback_query = DataQuery(
                entity="sistema",
                query_type=QueryType[llm_intent],
                filters={},
                fields=[],
            )

            data_results = await data_connector.execute_query(fallback_query)

    # ... resto do código ...
```

### 4.4 Configuração

```python
# config/bartolo_config.py

class BartoloConfig:
    # ... configurações existentes ...

    # Fallback LLM
    use_llm_fallback: bool = True
    llm_fallback_model: str = "gpt-3.5-turbo"  # Modelo leve para classificação
    llm_fallback_timeout: int = 5  # segundos
```

---

## 5. Plano de Implementação

### Fase 1: Patterns (Prioridade Alta)
**Duração estimada:** 1 dia

- [ ] Atualizar `data_connector.py` com todos os patterns da seção 2.2
- [ ] Atualizar `escala_agent.py` com patterns da seção 2.3
- [ ] Atualizar `substituicao_agent.py` com patterns da seção 2.3
- [ ] Atualizar `alerta_agent.py` com patterns da seção 2.3
- [ ] Testar manualmente cada categoria

### Fase 2: Testes Automatizados (Prioridade Alta)
**Duração estimada:** 1 dia

- [ ] Criar estrutura de diretórios de teste
- [ ] Implementar `test_data_connector_patterns.py`
- [ ] Implementar `test_escala_agent_patterns.py`
- [ ] Implementar `test_bartolo_engine_flow.py`
- [ ] Criar script de execução `test_bartolo.sh`
- [ ] Executar testes e corrigir falhas

### Fase 3: Fallback Inteligente (Prioridade Média)
**Duração estimada:** 0.5 dia

- [ ] Implementar `LLMIntentClassifier`
- [ ] Integrar no `BartoloEngine`
- [ ] Testar classificação com mensagens não detectadas
- [ ] Ajustar prompt de classificação se necessário

### Fase 4: Validação Final (Prioridade Alta)
**Duração estimada:** 0.5 dia

- [ ] Executar suite completa de testes
- [ ] Testar no frontend todas as funcionalidades
- [ ] Documentar casos de uso testados
- [ ] Deploy em produção

---

## 6. Métricas de Sucesso

| Métrica | Meta | Atual |
|---------|------|-------|
| Cobertura de testes | > 80% | 0% |
| Taxa de detecção de patterns | > 95% | ~60% |
| Tempo de resposta (p95) | < 2s | N/A |
| Uso de fallback LLM | < 10% | N/A |
| Satisfação do usuário | > 8/10 | 3/10 |

---

## 7. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Patterns conflitantes | Média | Alto | Testes automatizados com casos negativos |
| Fallback LLM lento | Média | Médio | Timeout + modelo leve (gpt-3.5) |
| Novos padrões de usuário | Alta | Médio | Logs + análise periódica + testes |
| Regressões em deploy | Média | Alto | CI/CD com testes obrigatórios |

---

## 8. Checklist de Validação

Antes de considerar o Bartolo "pronto", validar:

- [ ] "Postos sem cobertura" retorna lista de postos
- [ ] "Funcionários disponíveis hoje" retorna lista de funcionários
- [ ] "Crie a escala para X" inicia fluxo de criação
- [ ] "Alertas pendentes" mostra alertas reais
- [ ] "Resumo do dia" mostra dashboard operacional
- [ ] "/escala help" mostra ajuda da skill
- [ ] Mensagem não detectada usa fallback inteligente
- [ ] Todas as variações verbais funcionam (crie/criar/gere/gerar)
- [ ] Testes automatizados passam 100%
- [ ] Tempo de resposta < 2s

---

**Documento criado por:** Claude (Sonnet)
**Revisão necessária:** Sim
**Próxima ação:** Aprovar plano e iniciar Fase 1
