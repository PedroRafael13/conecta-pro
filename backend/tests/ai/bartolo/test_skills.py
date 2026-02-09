"""
Testes automatizados para Skills do Bartolo.

Testa:
- EscalaSkill: comandos gerar, otimizar, validar, publicar, custo, comparar
- CoberturaSkill: visao geral, critica, hoje, semana, posto especifico
- SubstitutoSkill: buscar, urgente, confirmar, pendentes, historico
- AlertaSkill: todos, cobertura, documentos, atrasos, urgente
- BaseSkill: parse_command
- Skills Registry: get_skill, list_skills
"""

import sys

import pytest

sys.path.insert(0, "/app")

from modules.ai.bartolo.skills import SKILL_REGISTRY, get_skill, list_skills
from modules.ai.bartolo.skills.alerta_skill import AlertaSkill
from modules.ai.bartolo.skills.base_skill import BaseSkill
from modules.ai.bartolo.skills.cobertura_skill import CoberturaSkill
from modules.ai.bartolo.skills.escala_skill import EscalaSkill
from modules.ai.bartolo.skills.substituto_skill import SubstitutoSkill

# ==========================================================================
# Testes de BaseSkill
# ==========================================================================


class TestBaseSkillParseCommand:
    """Testes para parse_command da BaseSkill."""

    @pytest.fixture
    def skill(self):
        """Usa EscalaSkill como instancia concreta."""
        return EscalaSkill()

    def test_parse_command_with_slash(self, skill):
        """Testa parse de comando com /."""
        cmd, args = skill.parse_command("/escala gerar POST-001")
        assert cmd == "escala"
        assert args == ["gerar", "POST-001"]

    def test_parse_command_without_slash(self, skill):
        """Testa parse de comando sem /."""
        cmd, args = skill.parse_command("gerar POST-001")
        assert cmd == "gerar"
        assert args == ["POST-001"]

    def test_parse_command_empty(self, skill):
        """Testa parse de comando vazio."""
        cmd, args = skill.parse_command("")
        assert cmd == ""
        assert args == []

    def test_parse_command_single_word(self, skill):
        """Testa parse com palavra unica."""
        cmd, args = skill.parse_command("/help")
        assert cmd == "help"
        assert args == []

    def test_parse_command_multiple_args(self, skill):
        """Testa parse com multiplos argumentos."""
        cmd, args = skill.parse_command("/escala comparar SCALE-1 SCALE-2")
        assert cmd == "escala"
        assert args == ["comparar", "SCALE-1", "SCALE-2"]


# ==========================================================================
# Testes de EscalaSkill
# ==========================================================================


class TestEscalaSkill:
    """Testes para EscalaSkill."""

    @pytest.fixture
    def skill(self):
        return EscalaSkill()

    def test_skill_name(self, skill):
        """Testa nome da skill."""
        assert skill.name == "escala"

    def test_skill_description(self, skill):
        """Testa descricao da skill."""
        assert skill.description == "Gerenciamento de escalas de trabalho"

    def test_skill_commands(self, skill):
        """Testa lista de comandos."""
        assert "gerar" in skill.commands
        assert "otimizar" in skill.commands
        assert "validar" in skill.commands
        assert "publicar" in skill.commands
        assert "custo" in skill.commands
        assert "comparar" in skill.commands
        assert "help" in skill.commands

    @pytest.mark.asyncio
    async def test_execute_help(self, skill):
        """Testa comando help."""
        result = await skill.execute("help", [], {})
        assert "response" in result
        assert "/escala" in result["response"]
        assert "suggestions" in result

    @pytest.mark.asyncio
    async def test_execute_empty_command(self, skill):
        """Testa comando vazio retorna help."""
        result = await skill.execute("", [], {})
        assert "response" in result
        assert "/escala" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_gerar_with_args(self, skill):
        """Testa comando gerar com argumentos."""
        result = await skill.execute("gerar", ["POST-001", "mar/2026"], {})
        assert "response" in result
        assert "POST-001" in result["response"]
        assert result.get("intent") == "escala_gerar"
        assert result["data"]["posto"] == "POST-001"
        assert result["data"]["periodo"] == "mar/2026"

    @pytest.mark.asyncio
    async def test_execute_gerar_without_args(self, skill):
        """Testa comando gerar sem argumentos retorna instrucoes."""
        result = await skill.execute("gerar", [], {})
        assert "response" in result
        assert "Uso" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_otimizar_with_args(self, skill):
        """Testa comando otimizar com ID."""
        result = await skill.execute("otimizar", ["SCALE-123"], {})
        assert "response" in result
        assert "SCALE-123" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_otimizar_without_args(self, skill):
        """Testa comando otimizar sem argumentos."""
        result = await skill.execute("otimizar", [], {})
        assert "Uso" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_validar(self, skill):
        """Testa comando validar."""
        result = await skill.execute("validar", ["SCALE-123"], {})
        assert "response" in result
        assert "SCALE-123" in result["response"]
        assert result["data"]["scale_id"] == "SCALE-123"
        assert result["data"]["valid"] is True

    @pytest.mark.asyncio
    async def test_execute_publicar(self, skill):
        """Testa comando publicar."""
        result = await skill.execute("publicar", ["SCALE-123"], {})
        assert "response" in result
        assert "SCALE-123" in result["response"]
        assert "actions" in result

    @pytest.mark.asyncio
    async def test_execute_custo(self, skill):
        """Testa comando custo."""
        result = await skill.execute("custo", ["POST-001"], {})
        assert "response" in result
        assert "POST-001" in result["response"]
        assert result["data"]["custo_total"] == 7806.40

    @pytest.mark.asyncio
    async def test_execute_comparar(self, skill):
        """Testa comando comparar."""
        result = await skill.execute("comparar", ["SCALE-1", "SCALE-2"], {})
        assert "response" in result
        assert "SCALE-1" in result["response"]
        assert "SCALE-2" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_comparar_without_args(self, skill):
        """Testa comando comparar sem argumentos suficientes."""
        result = await skill.execute("comparar", ["SCALE-1"], {})
        assert "Uso" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_unknown_command(self, skill):
        """Testa comando desconhecido."""
        result = await skill.execute("inexistente", [], {})
        assert "nao reconhecido" in result["response"]

    def test_get_help(self, skill):
        """Testa texto de help."""
        help_text = skill.get_help()
        assert "/escala gerar" in help_text
        assert "/escala otimizar" in help_text
        assert "/escala validar" in help_text
        assert "/escala publicar" in help_text
        assert "/escala custo" in help_text


# ==========================================================================
# Testes de CoberturaSkill
# ==========================================================================


class TestCoberturaSkill:
    """Testes para CoberturaSkill."""

    @pytest.fixture
    def skill(self):
        return CoberturaSkill()

    def test_skill_name(self, skill):
        """Testa nome da skill."""
        assert skill.name == "cobertura"

    def test_skill_commands(self, skill):
        """Testa lista de comandos."""
        assert "critica" in skill.commands
        assert "hoje" in skill.commands
        assert "semana" in skill.commands

    @pytest.mark.asyncio
    async def test_execute_visao_geral(self, skill):
        """Testa comando vazio retorna visao geral."""
        result = await skill.execute("", [], {})
        assert "response" in result
        assert "Cobertura Geral" in result["response"]
        assert result["data"]["media"] == 87.5
        assert result["data"]["criticos"] == 2

    @pytest.mark.asyncio
    async def test_execute_help(self, skill):
        """Testa comando help."""
        result = await skill.execute("help", [], {})
        assert "response" in result
        assert "Cobertura Geral" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_critica(self, skill):
        """Testa comando critica."""
        result = await skill.execute("critica", [], {})
        assert "response" in result
        assert "Critica" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_hoje(self, skill):
        """Testa comando hoje."""
        result = await skill.execute("hoje", [], {})
        assert "response" in result
        assert "Hoje" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_semana(self, skill):
        """Testa comando semana."""
        result = await skill.execute("semana", [], {})
        assert "response" in result
        assert "Semana" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_posto_especifico(self, skill):
        """Testa comando com nome de posto especifico."""
        result = await skill.execute("Centro-001", [], {})
        assert "response" in result
        assert "Centro-001" in result["response"]

    def test_get_help(self, skill):
        """Testa texto de help."""
        help_text = skill.get_help()
        assert "/cobertura" in help_text
        assert "critica" in help_text


# ==========================================================================
# Testes de SubstitutoSkill
# ==========================================================================


class TestSubstitutoSkill:
    """Testes para SubstitutoSkill."""

    @pytest.fixture
    def skill(self):
        return SubstitutoSkill()

    def test_skill_name(self, skill):
        """Testa nome da skill."""
        assert skill.name == "substituto"

    def test_skill_commands(self, skill):
        """Testa lista de comandos."""
        assert "buscar" in skill.commands
        assert "urgente" in skill.commands
        assert "confirmar" in skill.commands
        assert "pendentes" in skill.commands
        assert "historico" in skill.commands

    @pytest.mark.asyncio
    async def test_execute_help(self, skill):
        """Testa comando help."""
        result = await skill.execute("help", [], {})
        assert "response" in result
        assert "/substituto" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_empty_command(self, skill):
        """Testa comando vazio retorna help."""
        result = await skill.execute("", [], {})
        assert "response" in result

    @pytest.mark.asyncio
    async def test_execute_buscar_with_args(self, skill):
        """Testa comando buscar com ID de turno."""
        result = await skill.execute("buscar", ["TURNO-001"], {})
        assert "response" in result
        assert "TURNO-001" in result["response"]
        assert "Candidatos" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_buscar_without_args(self, skill):
        """Testa comando buscar sem argumentos."""
        result = await skill.execute("buscar", [], {})
        assert "Uso" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_urgente(self, skill):
        """Testa comando urgente."""
        result = await skill.execute("urgente", ["Centro-001"], {})
        assert "response" in result
        assert "URGENTE" in result["response"]
        assert result.get("priority") == "critical"

    @pytest.mark.asyncio
    async def test_execute_confirmar(self, skill):
        """Testa comando confirmar."""
        result = await skill.execute("confirmar", ["SUB-001"], {})
        assert "response" in result
        assert result["data"]["confirmed"] is True
        assert result["data"]["id"] == "SUB-001"

    @pytest.mark.asyncio
    async def test_execute_confirmar_without_args(self, skill):
        """Testa comando confirmar sem ID."""
        result = await skill.execute("confirmar", [], {})
        assert "Uso" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_pendentes(self, skill):
        """Testa comando pendentes."""
        result = await skill.execute("pendentes", [], {})
        assert "response" in result
        assert "Pendentes" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_historico(self, skill):
        """Testa comando historico."""
        result = await skill.execute("historico", [], {})
        assert "response" in result
        assert "Historico" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_unknown_command(self, skill):
        """Testa comando desconhecido."""
        result = await skill.execute("xyz", [], {})
        assert "nao reconhecido" in result["response"]

    def test_get_help(self, skill):
        """Testa texto de help."""
        help_text = skill.get_help()
        assert "/substituto buscar" in help_text
        assert "/substituto urgente" in help_text


# ==========================================================================
# Testes de AlertaSkill
# ==========================================================================


class TestAlertaSkill:
    """Testes para AlertaSkill."""

    @pytest.fixture
    def skill(self):
        return AlertaSkill()

    def test_skill_name(self, skill):
        """Testa nome da skill."""
        assert skill.name == "alerta"

    def test_skill_commands(self, skill):
        """Testa lista de comandos."""
        assert "cobertura" in skill.commands
        assert "documentos" in skill.commands
        assert "atrasos" in skill.commands
        assert "urgente" in skill.commands

    @pytest.mark.asyncio
    async def test_execute_todos(self, skill):
        """Testa comando vazio retorna todos os alertas."""
        result = await skill.execute("", [], {})
        assert "response" in result
        assert "Central de Alertas" in result["response"]
        assert result["data"]["total"] == 10
        assert result["data"]["criticos"] == 2

    @pytest.mark.asyncio
    async def test_execute_help(self, skill):
        """Testa comando help."""
        result = await skill.execute("help", [], {})
        assert "response" in result
        assert "Central de Alertas" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_cobertura(self, skill):
        """Testa comando cobertura."""
        result = await skill.execute("cobertura", [], {})
        assert "response" in result
        assert "Cobertura" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_documentos(self, skill):
        """Testa comando documentos."""
        result = await skill.execute("documentos", [], {})
        assert "response" in result
        assert "Documentos" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_atrasos(self, skill):
        """Testa comando atrasos."""
        result = await skill.execute("atrasos", [], {})
        assert "response" in result
        assert "Atrasos" in result["response"]

    @pytest.mark.asyncio
    async def test_execute_urgente(self, skill):
        """Testa comando urgente."""
        result = await skill.execute("urgente", [], {})
        assert "response" in result
        assert "URGENTE" in result["response"]
        assert result.get("priority") == "critical"

    def test_get_help(self, skill):
        """Testa texto de help."""
        help_text = skill.get_help()
        assert "/alerta" in help_text
        assert "cobertura" in help_text
        assert "documentos" in help_text


# ==========================================================================
# Testes do Skills Registry
# ==========================================================================


class TestSkillsRegistry:
    """Testes para o registry de skills."""

    def test_registry_has_all_skills(self):
        """Testa que o registry tem todas as skills."""
        assert "escala" in SKILL_REGISTRY
        assert "cobertura" in SKILL_REGISTRY
        assert "substituto" in SKILL_REGISTRY
        assert "alerta" in SKILL_REGISTRY

    def test_get_skill_existing(self):
        """Testa get_skill para skill existente."""
        skill = get_skill("escala")
        assert skill is not None
        assert isinstance(skill, EscalaSkill)

    def test_get_skill_nonexistent(self):
        """Testa get_skill para skill inexistente."""
        skill = get_skill("inexistente")
        assert skill is None

    def test_list_skills(self):
        """Testa listagem de skills."""
        skills = list_skills()
        assert "escala" in skills
        assert "cobertura" in skills
        assert "substituto" in skills
        assert "alerta" in skills
        assert len(skills) == 12

    @pytest.mark.parametrize(
        "skill_name,expected_class",
        [
            ("escala", EscalaSkill),
            ("cobertura", CoberturaSkill),
            ("substituto", SubstitutoSkill),
            ("alerta", AlertaSkill),
        ],
    )
    def test_get_skill_returns_correct_class(self, skill_name, expected_class):
        """Testa que get_skill retorna a classe correta."""
        skill = get_skill(skill_name)
        assert isinstance(skill, expected_class)

    @pytest.mark.parametrize("skill_name", ["escala", "cobertura", "substituto", "alerta"])
    def test_all_skills_have_name(self, skill_name):
        """Testa que todas as skills tem nome definido."""
        skill = get_skill(skill_name)
        assert skill.name, f"Skill '{skill_name}' sem nome"

    @pytest.mark.parametrize("skill_name", ["escala", "cobertura", "substituto", "alerta"])
    def test_all_skills_have_description(self, skill_name):
        """Testa que todas as skills tem descricao."""
        skill = get_skill(skill_name)
        assert skill.description, f"Skill '{skill_name}' sem descricao"

    @pytest.mark.parametrize("skill_name", ["escala", "cobertura", "substituto", "alerta"])
    def test_all_skills_have_commands(self, skill_name):
        """Testa que todas as skills tem comandos definidos."""
        skill = get_skill(skill_name)
        assert len(skill.commands) > 0, f"Skill '{skill_name}' sem comandos"

    @pytest.mark.parametrize("skill_name", ["escala", "cobertura", "substituto", "alerta"])
    def test_all_skills_have_get_help(self, skill_name):
        """Testa que todas as skills retornam texto de help."""
        skill = get_skill(skill_name)
        help_text = skill.get_help()
        assert help_text, f"Skill '{skill_name}' sem help"
        assert isinstance(help_text, str)
