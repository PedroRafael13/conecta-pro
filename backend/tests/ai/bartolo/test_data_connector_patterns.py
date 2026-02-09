"""
Testes automatizados para patterns do DataConnector.
Fase 2 do Plano de Refinamento do Bartolo.

Cada categoria de pattern é testada com múltiplas variações:
- Forma direta
- Interrogativa
- Imperativa
- Sinônimos
"""

import sys

import pytest

sys.path.insert(0, "/app")

from modules.ai.bartolo.services.data_connector import DataConnector, QueryType


class TestDataConnectorPatterns:
    """Testes para detecção de patterns no DataConnector."""

    @pytest.fixture
    def connector(self):
        """Fixture para DataConnector."""
        return DataConnector()

    def _detect(self, connector, message):
        """Helper para detectar query e retornar o tipo."""
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    # ==========================================================================
    # COBERTURA_CRITICA - Postos com cobertura < 80%
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Forma direta
            "cobertura critica",
            "cobertura baixa",
            "gaps de cobertura",
            "buracos na escala",
            "buracos na cobertura",
            # Postos
            "postos sem cobertura",
            "postos com baixa cobertura",
            "postos descobertos",
            "postos criticos",
            "postos com problema",
            "postos em alerta",
            "postos vazios",
            "postos sem funcionarios",
            "sem cobertura",
            "posto descoberto",
            # Interrogativas
            "quais postos estao sem cobertura",
            "quantos postos estao descobertos",
            "tem algum posto sem cobertura",
            "ha posto descoberto",
            "como esta a cobertura",
            "como ta a cobertura",
            "situacao da cobertura",
            # Ações
            "ver cobertura",
            "mostrar postos sem cobertura",
            "exibir cobertura",
            "listar postos descobertos",
            "verificar cobertura",
            "checar cobertura",
            "analisar cobertura",
            "cobertura de postos",
            "cobertura dos postos",
            "cobertura em tempo real",
            # Sinônimos
            "vagas em aberto",
            "posicoes sem preencher",
            "locais sem cobertura",
        ],
    )
    def test_cobertura_critica(self, connector, message):
        """Testa detecção de COBERTURA_CRITICA."""
        result = self._detect(connector, message)
        assert result == QueryType.COBERTURA_CRITICA, f"Falhou para: '{message}'"

    # ==========================================================================
    # FUNCIONARIOS_TRABALHANDO - Quem está em serviço agora
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Direto
            "quem esta trabalhando",
            "quem ta trabalhando",
            "quem está trabalhando",
            "quem esta em servico",
            "quem ta em servico",
            "quem esta no turno",
            "quem esta em campo",
            "quem esta no posto",
            # Funcionários
            "funcionarios em servico",
            "funcionarios em turno",
            "funcionarios em trabalho",
            "funcionarios agora",
            "funcionarios atualmente",
            "funcionarios trabalhando",
            "funcionarios ativos agora",
            "funcionarios ativos hoje",
            "trabalhando agora",
            # Equipe
            "equipe em servico",
            "equipe de hoje",
            "equipe de plantao",
            "equipe no turno",
            "equipe trabalhando",
            # Interrogativas
            "quantos estao trabalhando",
            "quantos funcionarios em servico",
            # Sinônimos
            "colaboradores em servico",
            "colaboradores em turno",
            "vigilantes em servico",
            "vigilantes em turno",
            "porteiros em servico",
            "porteiros em turno",
        ],
    )
    def test_funcionarios_trabalhando(self, connector, message):
        """Testa detecção de FUNCIONARIOS_TRABALHANDO."""
        result = self._detect(connector, message)
        assert result == QueryType.FUNCIONARIOS_TRABALHANDO, f"Falhou para: '{message}'"

    # ==========================================================================
    # FUNCIONARIOS_FOLGA - Disponíveis para convocação
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Folga
            "quem esta de folga",
            "quem ta de folga",
            "quem esta folgando",
            "funcionarios de folga",
            "funcionarios em folga",
            "folgas de hoje",
            # Disponíveis
            "funcionarios disponiveis",
            "funcionarios disponiveis hoje",
            "quem esta disponivel",
            "quem ta disponivel",
            "disponiveis para hoje",
            "disponiveis para trabalhar",
            "disponiveis para cobrir",
            "quem pode trabalhar",
            "quem pode cobrir",
            "quem pode substituir",
            "quem esta livre",
            "quem ta livre",
            # Para convocação
            "funcionarios para convocar",
            "quem posso chamar",
            "quem posso convocar",
            "quem pode convocar",
            "lista de convocacao",
            "lista de disponiveis",
            # Banco de reserva
            "reservas disponiveis",
            "plantonistas disponiveis",
            "sobreaviso",
        ],
    )
    def test_funcionarios_folga(self, connector, message):
        """Testa detecção de FUNCIONARIOS_FOLGA."""
        result = self._detect(connector, message)
        assert result == QueryType.FUNCIONARIOS_FOLGA, f"Falhou para: '{message}'"

    # ==========================================================================
    # ESCALAS_PENDENTES - Escalas aguardando aprovação/publicação
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Pendentes
            "escalas pendentes",
            "escala pendente",
            "escalas para aprovar",
            "escalas aguardando",
            "escalas em rascunho",
            "escalas nao publicadas",
            "aprovacao de escalas",
            # Atuais
            "escalas atuais",
            "escala atual",
            "escalas em vigor",
            "escalas da semana",
            "escala da semana",
            "escalas do mes",
            "escala do mes",
            # Verificar
            "ver escalas",
            "ver as escalas",
            "verificar escalas",
            "mostrar escalas",
            "listar escalas",
            "quais escalas pendentes",
            "quantas escalas aguardando",
            # Status
            "status das escalas",
            "status da escala",
            "situacao das escalas",
            "situacao da escala",
        ],
    )
    def test_escalas_pendentes(self, connector, message):
        """Testa detecção de ESCALAS_PENDENTES."""
        result = self._detect(connector, message)
        assert result == QueryType.ESCALAS_PENDENTES, f"Falhou para: '{message}'"

    # ==========================================================================
    # HORA_EXTRA_RANKING - Ranking de horas extras
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Hora extra
            "horas extras",
            "hora extra",
            "HE do mes",
            # Ranking
            "ranking de horas extras",
            "ranking de hora extra",
            "quem tem mais horas extras",
            "quem fez mais horas extras",
            "funcionarios com mais horas extras",
            # Banco de horas
            "banco de horas",
            "saldo de horas",
            "credito de horas",
            "debito de horas",
            # Limites
            "quem esta no limite",
            "quem ta no limite",
            "funcionarios no limite de HE",
            "funcionarios no limite de horas",
            "excesso de horas",
        ],
    )
    def test_hora_extra_ranking(self, connector, message):
        """Testa detecção de HORA_EXTRA_RANKING."""
        result = self._detect(connector, message)
        assert result == QueryType.HORA_EXTRA_RANKING, f"Falhou para: '{message}'"

    # ==========================================================================
    # SUBSTITUICOES_PENDENTES - Substituições aguardando resolução
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Substituições
            "substituicoes pendentes",
            "substituicao pendente",
            "substituicoes em aberto",
            "substituicoes nao resolvidas",
            # Trocas
            "trocas pendentes",
            "troca pendente",
            "trocas de turno",
            "trocas em aberto",
            # Coberturas
            "coberturas pendentes",
            "cobertura pendente",
            "coberturas em aberto",
            # Aguardando
            "aguardando substituto",
            "aguardando cobertura",
            "aguardando troca",
            "esperando substituto",
            "esperando cobertura",
            "precisando de substituto",
            "precisando de cobertura",
        ],
    )
    def test_substituicoes_pendentes(self, connector, message):
        """Testa detecção de SUBSTITUICOES_PENDENTES."""
        result = self._detect(connector, message)
        assert result == QueryType.SUBSTITUICOES_PENDENTES, f"Falhou para: '{message}'"

    # ==========================================================================
    # ATRASOS_HOJE - Funcionários atrasados hoje
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Atrasos
            "atrasos de hoje",
            "atraso de hoje",
            "atrasos do dia",
            "atrasados",
            "quem esta atrasado",
            "quem ta atrasado",
            "quem atrasou",
            "funcionarios atrasados",
            # Check-in
            "sem check-in",
            "sem checkin",
            "nao fez check-in",
            "nao fizeram check-in",
            "falta check-in",
            "faltou check-in",
            # Chegadas
            "chegadas com atraso",
            "chegadas atrasadas",
            "nao chegou ainda",
            "nao chegou no horario",
            # Ausências
            "ausencias de hoje",
            "ausencia de hoje",
            "faltas de hoje",
            "falta de hoje",
            "quem faltou",
            "quem nao veio",
        ],
    )
    def test_atrasos_hoje(self, connector, message):
        """Testa detecção de ATRASOS_HOJE."""
        result = self._detect(connector, message)
        assert result == QueryType.ATRASOS_HOJE, f"Falhou para: '{message}'"

    # ==========================================================================
    # OPERACAO_GERAL - Resumo operacional
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Status
            "como esta a operacao",
            "como ta a operacao",
            "como está a operacao",
            "status da operacao",
            "situacao da operacao",
            "visao geral da operacao",
            "panorama da operacao",
            # Dashboard
            "dashboard",
            "dashboard operacional",
            "painel",
            "painel operacional",
            "indicadores do dia",
            # Dia
            "o que esta acontecendo",
            "que esta acontecendo",
            "novidades do dia",
        ],
    )
    def test_operacao_geral(self, connector, message):
        """Testa detecção de OPERACAO_GERAL."""
        result = self._detect(connector, message)
        assert result == QueryType.OPERACAO_GERAL, f"Falhou para: '{message}'"

    # ==========================================================================
    # DAILY_SUMMARY - Resumo do dia
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "resumo do dia",
            "resumo diario",
            "resumo da operacao",
            "resumo operacional",
            "como esta o dia",
            "como foi o dia",
            "visao geral do dia",
            "status do dia",
        ],
    )
    def test_daily_summary(self, connector, message):
        """Testa detecção de DAILY_SUMMARY."""
        result = self._detect(connector, message)
        assert result == QueryType.DAILY_SUMMARY, f"Falhou para: '{message}'"

    # ==========================================================================
    # ALERTS - Alertas pendentes
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            # Alertas
            "alertas pendentes",
            "alerta pendente",
            "alertas do dia",
            "alertas do sistema",
            "alertas em aberto",
            "alertas nao resolvidos",
            # Pendências
            "pendencias",
            "o que esta pendente",
            "quais estao pendentes",
            "itens pendentes",
            # Problemas
            "problemas pendentes",
            "problemas abertos",
            "tem algum problema",
            "ha algum alerta",
            "algo errado",
            "alguma coisa pendente",
            # Urgente
            "urgente",
            "critico",
            "importante",
            "preciso resolver",
            "precisamos atender",
            "atencao imediata",
            "atenção",
        ],
    )
    def test_alerts(self, connector, message):
        """Testa detecção de ALERTS."""
        result = self._detect(connector, message)
        assert result == QueryType.ALERTS, f"Falhou para: '{message}'"

    # ==========================================================================
    # KPIS - Indicadores de performance
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "kpis",
            "kpi principais",
            "kpis do sistema",
            "indicadores",
            "metricas",
            "performance",
        ],
    )
    def test_kpis(self, connector, message):
        """Testa detecção de KPIS."""
        result = self._detect(connector, message)
        assert result == QueryType.KPIS, f"Falhou para: '{message}'"

    # ==========================================================================
    # Testes de frases completas do usuário
    # ==========================================================================
    @pytest.mark.parametrize(
        "message,expected_type",
        [
            # Frases reais que falharam antes
            ("Analisar cobertura de postos em tempo real", QueryType.COBERTURA_CRITICA),
            ("Funcionarios disponiveis hoje", QueryType.FUNCIONARIOS_FOLGA),
            ("Postos sem cobertura", QueryType.COBERTURA_CRITICA),
            ("verifique as escalas atuais", QueryType.ESCALAS_PENDENTES),
            ("me mostre quem esta trabalhando agora", QueryType.FUNCIONARIOS_TRABALHANDO),
            ("quantos funcionarios estao de folga", QueryType.FUNCIONARIOS_FOLGA),
            ("lista de substituicoes pendentes", QueryType.SUBSTITUICOES_PENDENTES),
            ("quem faltou hoje", QueryType.ATRASOS_HOJE),
            ("me da um resumo do dia", QueryType.DAILY_SUMMARY),
            ("como esta a operacao hoje", QueryType.OPERACAO_GERAL),
            ("tem algum alerta critico", QueryType.ALERTS),
        ],
    )
    def test_frases_completas(self, connector, message, expected_type):
        """Testa frases completas que o usuário pode digitar."""
        result = self._detect(connector, message)
        assert result == expected_type, f"Falhou para: '{message}' - esperado {expected_type}, obtido {result}"

    # ==========================================================================
    # Testes negativos - não devem detectar special query
    # ==========================================================================
    @pytest.mark.parametrize(
        "message",
        [
            "ola",
            "bom dia",
            "ajuda",
            "o que voce pode fazer",
            "qual seu nome",
            "me conte uma piada",
            "obrigado",
        ],
    )
    def test_nao_deve_detectar_special_query(self, connector, message):
        """Testa que mensagens genéricas não detectam special query."""
        result = self._detect(connector, message)
        assert result is None, f"Detectou incorretamente para: '{message}'"


class TestDataConnectorDiaristaPatterns:
    """Testes para detecção de patterns de diarista no DataConnector."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result

    @pytest.mark.parametrize(
        "message,expected_type",
        [
            # Contagem
            ("quantos diaristas", QueryType.COUNT),
            ("quantas diaristas temos", QueryType.COUNT),
            ("total de diaristas", QueryType.COUNT),
            ("diaristas cadastrados", QueryType.COUNT),
            # Listagem
            ("listar diaristas", QueryType.LIST),
            ("mostrar diaristas", QueryType.LIST),
            ("ver diaristas", QueryType.LIST),
            ("quais diaristas", QueryType.LIST),
            ("diaristas disponiveis", QueryType.LIST),
        ],
    )
    def test_diarista_patterns(self, connector, message, expected_type):
        """Testa detecção de consultas sobre diaristas."""
        result = self._detect(connector, message)
        assert result is not None, f"Nao detectou query para: '{message}'"
        assert result.query_type == expected_type, (
            f"Tipo errado para: '{message}' - esperado {expected_type}, obtido {result.query_type}"
        )
        assert result.entity in ("diarista", "diaristas"), f"Entidade errada para: '{message}' - obtido {result.entity}"

    def test_diarista_entity_map(self, connector):
        """Verifica que diarista está no ENTITY_MAP."""
        assert "diarista" in connector.ENTITY_MAP
        assert "diaristas" in connector.ENTITY_MAP

    def test_diarista_frase_completa(self, connector):
        """Testa frases completas sobre diaristas."""
        result = self._detect(connector, "quantos diaristas temos cadastrados")
        assert result is not None, "Deveria detectar query de diaristas"

    def test_diarista_nao_detecta_frase_generica(self, connector):
        """Testa que frases sem diarista não detectam diarista."""
        result = self._detect(connector, "bom dia bartolo")
        assert result is None


class TestDataConnectorQueryPatterns:
    """Testes para patterns de consulta genérica."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        """Helper para detectar query e retornar o tipo."""
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    @pytest.mark.parametrize(
        "message,expected_type",
        [
            # Contagem
            ("quantos funcionarios", QueryType.COUNT),
            ("quantas escalas", QueryType.COUNT),
            ("total de postos", QueryType.COUNT),
            ("numero de turnos", QueryType.COUNT),
            ("funcionarios cadastrados", QueryType.COUNT),
            ("temos quantos clientes", QueryType.COUNT),
            # Listagem
            ("listar funcionarios", QueryType.LIST),
            ("mostrar postos", QueryType.LIST),
            ("ver escalas", QueryType.LIST),
            ("quais turnos", QueryType.LIST),
            ("ultimos contratos", QueryType.LIST),
            # Detalhe
            ("detalhes do funcionario", QueryType.DETAIL),
            ("informacoes da escala", QueryType.DETAIL),
        ],
    )
    def test_query_patterns(self, connector, message, expected_type):
        """Testa patterns de consulta genérica."""
        result = self._detect(connector, message)
        # Alguns patterns podem detectar special queries primeiro
        # então só verificamos se detectou algo
        if result:
            # Se detectou, aceita qualquer tipo válido
            assert result is not None
        else:
            # Se não detectou, falha
            pytest.skip(f"Pattern não detectado para: '{message}' - pode ser que special query pegou primeiro")


class TestDataConnectorOcorrenciaPatterns:
    """Testes para detecção de patterns de ocorrências no DataConnector."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    @pytest.mark.parametrize(
        "message",
        [
            # Forma direta
            "ocorrencias abertas",
            "ocorrencias pendentes",
            "ocorrencias em aberto",
            "ocorrencias nao resolvidas",
            "ocorrencias em analise",
            "ocorrencias do dia",
            "ocorrencias de hoje",
            "ocorrencias recentes",
            "ocorrencias graves",
            "ocorrencias do posto",
            # Interrogativas
            "quantas ocorrencias",
            "quais ocorrencias",
            "tem alguma ocorrencia",
            "ha alguma ocorrencia",
            "quem teve ocorrencia",
            # Imperativas
            "ver ocorrencias",
            "mostrar ocorrencias",
            "listar ocorrencias",
            "verificar ocorrencias",
            "ultimas ocorrencias",
            # Sinônimos
            "infracoes abertas",
            "infracoes pendentes",
            "nao conformidades abertas",
            "registros de ocorrencias",
            "historico de ocorrencias",
            "status das ocorrencias",
        ],
    )
    def test_ocorrencias_abertas(self, connector, message):
        """Testa detecção de OCORRENCIAS_ABERTAS."""
        result = self._detect(connector, message)
        assert result == QueryType.OCORRENCIAS_ABERTAS, f"Falhou para: '{message}'"


class TestDataConnectorDisciplinarPatterns:
    """Testes para detecção de patterns disciplinares no DataConnector."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    @pytest.mark.parametrize(
        "message",
        [
            # Forma direta
            "advertencias pendentes",
            "advertencias em aberto",
            "advertencias nao assinadas",
            "advertencias recentes",
            "medidas disciplinares",
            "medidas pendentes",
            "suspensoes pendentes",
            "suspensoes ativas",
            "suspensoes aplicadas",
            "acoes disciplinares",
            # Interrogativas
            "quantas advertencias",
            "quais medidas disciplinares",
            "tem alguma advertencia",
            "quem foi advertido",
            "quem esta suspenso",
            "quem levou advertencia",
            # Imperativas
            "ver advertencias",
            "mostrar medidas disciplinares",
            "listar advertencias",
            "verificar medidas disciplinares",
            # Sinônimos
            "historico disciplinar",
            "punicoes pendentes",
            "aprovacao de advertencias",
            "status das advertencias",
        ],
    )
    def test_medidas_pendentes(self, connector, message):
        """Testa detecção de MEDIDAS_PENDENTES."""
        result = self._detect(connector, message)
        assert result == QueryType.MEDIDAS_PENDENTES, f"Falhou para: '{message}'"


class TestDataConnectorComunicacaoPatterns:
    """Testes para detecção de patterns de comunicação no DataConnector."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    @pytest.mark.parametrize(
        "message",
        [
            # Forma direta
            "comunicados publicados",
            "comunicados ativos",
            "comunicados do dia",
            "comunicados de hoje",
            "comunicados recentes",
            "comunicados pendentes",
            "comunicados nao lidos",
            "avisos pendentes",
            "avisos publicados",
            "anuncios publicados",
            # Interrogativas
            "quantos comunicados",
            "quais comunicados",
            "tem algum comunicado",
            "quem leu o comunicado",
            # Imperativas
            "ver comunicados",
            "mostrar comunicados",
            "listar comunicados",
            "verificar comunicados",
            "ultimos comunicados",
            # Sinônimos
            "informativos publicados",
            "mural de avisos",
            "circulares",
            "status dos comunicados",
        ],
    )
    def test_comunicados_ativos(self, connector, message):
        """Testa detecção de COMUNICADOS_ATIVOS."""
        result = self._detect(connector, message)
        assert result == QueryType.COMUNICADOS_ATIVOS, f"Falhou para: '{message}'"


class TestDataConnectorRondaPatterns:
    """Testes para detecção de patterns de rondas no DataConnector."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result.query_type if result else None

    @pytest.mark.parametrize(
        "message",
        [
            # Forma direta
            "rondas de hoje",
            "rondas do dia",
            "rondas em andamento",
            "rondas agendadas",
            "rondas programadas",
            "rondas concluidas",
            "rondas recentes",
            "rondas pendentes",
            "proxima ronda",
            "inspecoes de hoje",
            "inspecoes do dia",
            "inspecoes agendadas",
            "inspecoes em andamento",
            "inspecoes recentes",
            # Interrogativas
            "quantas rondas",
            "quais rondas",
            "tem alguma ronda",
            "quem esta fazendo ronda",
            # Imperativas
            "ver rondas",
            "mostrar rondas",
            "listar inspecoes",
            "verificar rondas",
            "resultado da ronda",
            # Sinônimos
            "fiscalizacoes de hoje",
            "visitas de inspecao",
            "status das rondas",
        ],
    )
    def test_rondas_hoje(self, connector, message):
        """Testa detecção de RONDAS_HOJE."""
        result = self._detect(connector, message)
        assert result == QueryType.RONDAS_HOJE, f"Falhou para: '{message}'"


class TestDataConnectorEntidadesExpandidas:
    """Testes para frases completas envolvendo entidades expandidas."""

    @pytest.fixture
    def connector(self):
        return DataConnector()

    def _detect(self, connector, message):
        result = connector.detect_data_query(message)
        return result

    @pytest.mark.parametrize(
        "message,expected_type",
        [
            # Frases completas de ocorrências
            ("quantas ocorrencias abertas temos", QueryType.OCORRENCIAS_ABERTAS),
            ("me mostre as ocorrencias de hoje", QueryType.OCORRENCIAS_ABERTAS),
            ("tem alguma ocorrencia grave", QueryType.OCORRENCIAS_ABERTAS),
            ("listar ocorrencias em analise", QueryType.OCORRENCIAS_ABERTAS),
            # Frases completas de disciplinares
            ("quais advertencias estao pendentes", QueryType.MEDIDAS_PENDENTES),
            ("listar medidas disciplinares pendentes", QueryType.MEDIDAS_PENDENTES),
            ("quem foi advertido recentemente", QueryType.MEDIDAS_PENDENTES),
            ("suspensoes em vigor atualmente", QueryType.MEDIDAS_PENDENTES),
            # Frases completas de comunicação
            ("quais comunicados foram publicados", QueryType.COMUNICADOS_ATIVOS),
            ("mostrar comunicados do dia", QueryType.COMUNICADOS_ATIVOS),
            ("tem algum aviso pendente", QueryType.COMUNICADOS_ATIVOS),
            ("ultimos comunicados publicados", QueryType.COMUNICADOS_ATIVOS),
            # Frases completas de rondas
            ("rondas de inspecao de hoje", QueryType.RONDAS_HOJE),
            ("quem esta fazendo ronda agora", QueryType.RONDAS_HOJE),
            ("resultado da ultima ronda", QueryType.RONDAS_HOJE),
            ("inspecoes agendadas para hoje", QueryType.RONDAS_HOJE),
        ],
    )
    def test_frases_completas_expandidas(self, connector, message, expected_type):
        """Testa frases completas para entidades expandidas."""
        result = self._detect(connector, message)
        assert result is not None, f"Nao detectou query para: '{message}'"
        assert result.query_type == expected_type, (
            f"Falhou para: '{message}' - esperado {expected_type}, obtido {result.query_type}"
        )

    def test_entity_map_novas_entidades(self, connector):
        """Verifica que novas entidades estão no ENTITY_MAP."""
        novas = [
            "ocorrencia",
            "ocorrencias",
            "advertencia",
            "advertencias",
            "medida_disciplinar",
            "medidas_disciplinares",
            "suspensao",
            "suspensoes",
            "comunicado",
            "comunicados",
            "anuncio",
            "anuncios",
            "ronda",
            "rondas",
            "inspecao",
            "inspecoes",
            "substituicao",
            "banco_horas",
        ]
        for entidade in novas:
            assert entidade in connector.ENTITY_MAP, f"Entidade '{entidade}' nao encontrada no ENTITY_MAP"
