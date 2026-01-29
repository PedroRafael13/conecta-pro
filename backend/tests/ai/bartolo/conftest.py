"""
Fixtures compartilhadas para testes do Bartolo
"""

import pytest
import sys
sys.path.insert(0, '/app')


@pytest.fixture
def data_connector():
    """Fixture para DataConnector"""
    from modules.ai.bartolo.services.data_connector import DataConnector
    return DataConnector()


@pytest.fixture
def escala_agent():
    """Fixture para EscalaAgent"""
    from modules.ai.bartolo.agents.escala_agent import EscalaAgent
    return EscalaAgent()


@pytest.fixture
def substituicao_agent():
    """Fixture para SubstituicaoAgent"""
    from modules.ai.bartolo.agents.substituicao_agent import SubstituicaoAgent
    return SubstituicaoAgent()


@pytest.fixture
def alerta_agent():
    """Fixture para AlertaAgent"""
    from modules.ai.bartolo.agents.alerta_agent import AlertaAgent
    return AlertaAgent()


@pytest.fixture
def bartolo_engine():
    """Fixture para BartoloEngine"""
    from modules.ai.bartolo.services.bartolo_engine import BartoloEngine
    return BartoloEngine()
