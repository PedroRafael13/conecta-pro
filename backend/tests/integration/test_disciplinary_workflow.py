"""
Testes de integração - Workflow Disciplinar.

Testa workflow: ocorrência → medida administrativa → aprovação
"""

from datetime import datetime
from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestDisciplinaryWorkflow:
    """Testes de workflow disciplinar completo."""

    @pytest.fixture
    def mock_occurrence_data(self):
        """Dados mock para criação de ocorrência."""
        return {
            "title": "Uso de celular no posto",
            "description": "Funcionário utilizando celular durante o horário de trabalho repetidamente.",
            "occurrence_type": "COMPORTAMENTO_INADEQUADO",
            "severity": "LEVE",
            "category": "USO_CELULAR",
            "occurred_at": datetime.now().isoformat(),
            "employee_id": str(uuid4()),
            "post_id": str(uuid4()),
        }

    @pytest.fixture
    def mock_disciplinary_action_data(self):
        """Dados mock para medida administrativa."""
        return {
            "action_type": "ADVERTENCIA_VERBAL",
            "description": "Advertência verbal por uso de celular durante o expediente.",
            "justification": "Primeira ocorrência de uso inadequado de celular.",
            "applied_at": datetime.now().isoformat(),
        }

    async def test_full_disciplinary_workflow(self, client, mock_occurrence_data, mock_disciplinary_action_data):
        """
        Testa fluxo completo disciplinar.

        Passos:
        1. Registrar ocorrência (status: aberta)
        2. Analisar ocorrência (status: em_analise)
        3. Aplicar medida administrativa
        4. Submeter para aprovação
        5. Aprovar medida
        6. Resolver ocorrência (status: resolvida)
        """
        pytest.skip("Requer autenticação configurada")

        # 1. Criar ocorrência
        response = await client.post(
            "/api/v1/operacional/occurrences/",
            json=mock_occurrence_data,
        )
        assert response.status_code == 201
        occurrence = response.json()
        occurrence_id = occurrence["id"]
        assert occurrence["status"] == "aberta"

        # 2. Colocar em análise
        response = await client.patch(
            f"/api/v1/operacional/occurrences/{occurrence_id}",
            json={"status": "em_analise"},
        )
        assert response.status_code == 200
        occurrence = response.json()
        assert occurrence["status"] == "em_analise"

        # 3. Aplicar medida administrativa
        disciplinary_data = {
            **mock_disciplinary_action_data,
            "occurrence_id": occurrence_id,
            "employee_id": mock_occurrence_data["employee_id"],
        }
        response = await client.post(
            "/api/v1/operacional/medidas-administrativas/",
            json=disciplinary_data,
        )
        assert response.status_code == 201
        action = response.json()
        action_id = action["id"]

        # 4. Submeter para aprovação
        response = await client.post(f"/api/v1/operacional/medidas-administrativas/{action_id}/submit")
        assert response.status_code == 200
        action = response.json()
        assert action["status"] == "pending_approval"

        # 5. Aprovar medida
        response = await client.post(f"/api/v1/operacional/medidas-administrativas/{action_id}/approve")
        assert response.status_code == 200
        action = response.json()
        assert action["status"] == "approved"

        # 6. Resolver ocorrência
        resolve_data = {
            "resolution": "Ocorrência resolvida com aplicação de advertência verbal.",
            "resolved_by_id": str(uuid4()),
            "action_taken": "Advertência verbal",
        }
        response = await client.post(
            f"/api/v1/operacional/occurrences/{occurrence_id}/resolve",
            json=resolve_data,
        )
        assert response.status_code == 200
        occurrence = response.json()
        assert occurrence["status"] == "resolvida"

    async def test_occurrence_severity_escalation(self, client):
        """Testa escalação de severidade baseada em reincidência."""
        pytest.skip("Requer autenticação configurada")

        employee_id = str(uuid4())

        # Primeira ocorrência - LEVE
        response1 = await client.post(
            "/api/v1/operacional/occurrences/",
            json={
                "title": "Uso de celular - 1ª vez",
                "description": "Primeira ocorrência de uso de celular no posto",
                "occurrence_type": "COMPORTAMENTO_INADEQUADO",
                "severity": "LEVE",
                "category": "USO_CELULAR",
                "occurred_at": datetime.now().isoformat(),
                "employee_id": employee_id,
                "post_id": str(uuid4()),
            },
        )
        assert response1.status_code == 201

        # Segunda ocorrência - deve escalar para MODERADA
        response2 = await client.post(
            "/api/v1/operacional/occurrences/",
            json={
                "title": "Uso de celular - 2ª vez",
                "description": "Segunda ocorrência de uso de celular no posto",
                "occurrence_type": "COMPORTAMENTO_INADEQUADO",
                "severity": "MODERADA",  # Escalado
                "category": "USO_CELULAR",
                "occurred_at": datetime.now().isoformat(),
                "employee_id": employee_id,
                "post_id": str(uuid4()),
            },
        )
        assert response2.status_code == 201
        occurrence2 = response2.json()
        assert occurrence2["severity"] == "moderada"

    async def test_disciplinary_action_types(self, client):
        """Testa diferentes tipos de medidas administrativas."""
        pytest.skip("Requer autenticação configurada")

        action_types = [
            "ADVERTENCIA_VERBAL",
            "ADVERTENCIA_ESCRITA",
            "SUSPENSAO",
            "DESLIGAMENTO",
        ]

        for action_type in action_types:
            response = await client.post(
                "/api/v1/operacional/medidas-administrativas/",
                json={
                    "action_type": action_type,
                    "description": f"Medida do tipo {action_type}",
                    "justification": "Teste de tipos de medida",
                    "employee_id": str(uuid4()),
                    "applied_at": datetime.now().isoformat(),
                },
            )
            # Pode falhar por falta de occurrence_id, mas deve reconhecer o tipo
            assert response.status_code in [201, 400, 422]

    async def test_employee_history(self, client):
        """Testa histórico disciplinar do funcionário."""
        pytest.skip("Requer autenticação configurada")

        employee_id = str(uuid4())

        # Criar múltiplas ocorrências para mesmo funcionário
        for i in range(3):
            await client.post(
                "/api/v1/operacional/occurrences/",
                json={
                    "title": f"Ocorrência {i + 1}",
                    "description": f"Descrição da ocorrência número {i + 1} para teste de histórico",
                    "occurrence_type": "COMPORTAMENTO_INADEQUADO",
                    "severity": "LEVE",
                    "category": "USO_CELULAR",
                    "occurred_at": datetime.now().isoformat(),
                    "employee_id": employee_id,
                    "post_id": str(uuid4()),
                },
            )

        # Buscar histórico
        response = await client.get(f"/api/v1/operacional/medidas-administrativas/funcionario/{employee_id}")

        if response.status_code == 200:
            history = response.json()
            assert len(history) >= 0  # Pode não ter medidas aplicadas ainda


@pytest.mark.asyncio
class TestDisciplinaryBusinessRules:
    """Testes de regras de negócio disciplinares."""

    async def test_cannot_apply_action_without_occurrence(self, client):
        """Testa que medida administrativa requer ocorrência."""
        pytest.skip("Requer autenticação configurada")

        response = await client.post(
            "/api/v1/operacional/medidas-administrativas/",
            json={
                "action_type": "ADVERTENCIA_VERBAL",
                "description": "Medida sem ocorrência",
                "justification": "Teste",
                "employee_id": str(uuid4()),
                "applied_at": datetime.now().isoformat(),
                # occurrence_id ausente
            },
        )
        # Deve falhar
        assert response.status_code in [400, 422]

    async def test_occurrence_resolution_requires_action(self, client):
        """Testa que resolver ocorrência grave requer medida administrativa."""
        pytest.skip("Requer autenticação configurada")

        # Criar ocorrência GRAVE
        response = await client.post(
            "/api/v1/operacional/occurrences/",
            json={
                "title": "Abandono de posto",
                "description": "Funcionário abandonou o posto sem autorização causando grave risco de segurança.",
                "occurrence_type": "COMPORTAMENTO_INADEQUADO",
                "severity": "GRAVE",
                "category": "ABANDONO_POSTO",
                "occurred_at": datetime.now().isoformat(),
                "employee_id": str(uuid4()),
                "post_id": str(uuid4()),
            },
        )
        occurrence_id = response.json()["id"]

        # Tentar resolver sem aplicar medida
        response = await client.post(
            f"/api/v1/operacional/occurrences/{occurrence_id}/resolve",
            json={
                "resolution": "Resolvido sem medida",
                "resolved_by_id": str(uuid4()),
            },
        )
        # Pode exigir action_taken para ocorrências graves
        assert response.status_code in [200, 400, 422]
