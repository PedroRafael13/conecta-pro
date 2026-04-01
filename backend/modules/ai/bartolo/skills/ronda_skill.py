"""
Skill /ronda - Gerenciamento de rondas de inspecao via comando.

Comandos disponiveis:
    /ronda hoje                          - Rondas agendadas para hoje
    /ronda andamento                     - Rondas em andamento
    /ronda stats                         - Estatisticas por status
    /ronda inspetor <nome>               - Rondas por inspetor
    /ronda resultado <codigo>            - Resultado de uma ronda
    /ronda checkpoint <ronda_id> <posto>  - Registrar checkpoint em posto
    /ronda checkpoints <ronda_id>         - Listar checkpoints da ronda
    /ronda pausar <ronda_id>              - Pausar ronda em andamento
    /ronda retomar <ronda_id>             - Retomar ronda pausada
    /ronda help                          - Ajuda

Author: Conecta PRO Team
Date: 2026-01-29
"""

import logging
from typing import TYPE_CHECKING, Any, Optional

from .base_skill import BaseSkill

if TYPE_CHECKING:
    from modules.ai.bartolo.services.data_connector import DataConnector

logger = logging.getLogger(__name__)


class RondaSkill(BaseSkill):
    """
    Skill para gerenciamento de rondas de inspecao.

    Comandos:
        /ronda hoje                           - Rondas agendadas para hoje
        /ronda andamento                      - Rondas em andamento
        /ronda stats                          - Estatisticas por status
        /ronda inspetor <nome>                - Rondas por inspetor
        /ronda resultado <codigo>             - Resultado de ronda concluida
        /ronda checkpoint <ronda_id> <posto>  - Registrar checkpoint em posto
        /ronda checkpoints <ronda_id>         - Listar checkpoints da ronda
        /ronda pausar <ronda_id>              - Pausar ronda em andamento
        /ronda retomar <ronda_id>             - Retomar ronda pausada
        /ronda help                           - Mostra ajuda
    """

    name = "ronda"
    description = "Gerenciamento de rondas de inspecao"
    commands = [
        "hoje",
        "andamento",
        "stats",
        "inspetor",
        "resultado",
        "checkpoint",
        "checkpoints",
        "pausar",
        "retomar",
        "help",
    ]

    def __init__(self, data_connector: Optional["DataConnector"] = None):
        super().__init__(data_connector=data_connector)

    async def execute(self, command: str, args: list[str], context: dict[str, Any]) -> dict[str, Any]:
        """Executa comando de ronda."""
        try:
            if not command or command == "help":
                return {"response": self.get_help(), "suggestions": self.commands[:6]}

            handlers = {
                "hoje": self._hoje,
                "andamento": self._andamento,
                "stats": self._stats,
                "inspetor": self._inspetor,
                "resultado": self._resultado,
                "checkpoint": self._checkpoint,
                "checkpoints": self._checkpoints,
                "pausar": self._pausar,
                "retomar": self._retomar,
            }

            handler = handlers.get(command)
            if handler:
                return await handler(args, context)

            return {
                "response": f"Comando '{command}' nao reconhecido. Use /ronda help para ver os comandos.",
                "suggestions": self.commands[:6],
            }
        except Exception as e:
            logger.error(f"Erro ao executar /ronda {command}: {e}")
            return {
                "response": f"Erro ao executar comando /ronda {command}. Tente novamente.",
                "suggestions": ["/ronda help"],
            }

    async def _hoje(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista rondas agendadas para hoje."""
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_rondas_hoje()
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": {
                            "rondas": result.data,
                            "total": result.total_count,
                        },
                    }
                    if result.data:
                        suggestions = []
                        for r in result.data[:3]:
                            code = r.get("codigo", "")
                            if code and code != "N/A":
                                suggestions.append(f"/ronda resultado {code}")
                        response_data["suggestions"] = suggestions or ["/ronda help"]
                    else:
                        response_data["suggestions"] = ["/ronda stats", "/ronda andamento"]
                    return response_data
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas de hoje: {e}")

        # Fallback estatico
        from datetime import datetime

        hoje = datetime.utcnow().strftime("%d/%m/%Y")
        return {
            "response": f"""**Rondas Agendadas para Hoje ({hoje})**

Nenhuma ronda agendada para hoje.

Use `/ronda stats` para ver as estatisticas gerais.""",
            "suggestions": ["/ronda stats", "/ronda andamento"],
        }

    async def _andamento(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista rondas em andamento."""
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_rondas_andamento()
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": {
                            "rondas": result.data,
                            "total": result.total_count,
                        },
                    }
                    if result.data:
                        suggestions = []
                        for r in result.data[:3]:
                            code = r.get("codigo", "")
                            if code and code != "N/A":
                                suggestions.append(f"/ronda resultado {code}")
                        response_data["suggestions"] = suggestions or ["/ronda help"]
                    else:
                        response_data["suggestions"] = ["/ronda hoje", "/ronda stats"]
                    return response_data
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas em andamento: {e}")

        # Fallback estatico
        return {
            "response": """**Rondas em Andamento**

Nenhuma ronda em andamento no momento.

Use `/ronda hoje` para ver as rondas agendadas para hoje.""",
            "suggestions": ["/ronda hoje", "/ronda stats"],
        }

    async def _stats(self, args: list[str], context: dict) -> dict[str, Any]:
        """Exibe estatisticas de rondas por status."""
        if self.has_data_connector:
            try:
                result = await self.data_connector._get_estatisticas_rondas()
                if result.success:
                    return {
                        "response": result.message,
                        "data": result.data,
                        "suggestions": ["/ronda hoje", "/ronda andamento"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas de rondas: {e}")

        # Fallback estatico
        return {
            "response": """**Estatisticas de Rondas**

| Status | Quantidade |
|--------|-----------|
| Agendadas | 0 |
| Em Andamento | 0 |
| Concluidas | 0 |
| Pausadas | 0 |
| Canceladas | 0 |
| **Total** | **0** |

*Dados indisponiveis. Conecte ao banco de dados para dados reais.*""",
            "data": {"stats": {}},
            "suggestions": ["/ronda hoje", "/ronda andamento"],
        }

    async def _inspetor(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista rondas de um inspetor especifico."""
        if not args:
            return {
                "response": "**Uso:** `/ronda inspetor <nome>`\n\nExemplo: `/ronda inspetor Carlos Silva`",
                "suggestions": ["/ronda stats", "/ronda help"],
            }

        inspector_name = " ".join(args).title()

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_rondas_inspetor(inspector_name)
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": {
                            "rondas": result.data,
                            "inspetor": inspector_name,
                            "total": result.total_count,
                        },
                    }
                    if result.data:
                        suggestions = []
                        for r in result.data[:3]:
                            code = r.get("codigo", "")
                            if code and code != "N/A":
                                suggestions.append(f"/ronda resultado {code}")
                        response_data["suggestions"] = suggestions or ["/ronda stats"]
                    else:
                        response_data["suggestions"] = ["/ronda stats", "/ronda hoje"]
                    return response_data
            except Exception as e:
                logger.warning(f"Erro ao buscar rondas do inspetor: {e}")

        # Fallback estatico
        return {
            "response": f"""**Rondas do Inspetor {inspector_name}**

Nao foi possivel carregar as rondas do inspetor {inspector_name}.

Verifique se o nome esta correto e tente novamente.""",
            "data": {"inspetor": inspector_name},
            "suggestions": ["/ronda stats", "/ronda hoje"],
        }

    async def _resultado(self, args: list[str], context: dict) -> dict[str, Any]:
        """Exibe resultado/relatorio de uma ronda."""
        if not args:
            return {
                "response": "**Uso:** `/ronda resultado <codigo>`\n\nExemplo: `/ronda resultado RON-2026-00001`",
                "suggestions": ["/ronda hoje", "/ronda help"],
            }

        round_code = args[0].upper()

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_resultado_ronda(round_code)
                if result.success:
                    return {
                        "response": result.message,
                        "data": result.data,
                        "suggestions": ["/ronda stats", "/ronda hoje"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar resultado da ronda: {e}")

        # Fallback estatico
        return {
            "response": f"""**Resultado da Ronda {round_code}**

Nao foi possivel carregar o resultado da ronda {round_code}.

Verifique se o codigo esta correto e se a ronda foi concluida.""",
            "data": {"code": round_code},
            "suggestions": ["/ronda hoje", "/ronda stats"],
        }

    async def _checkpoint(self, args: list[str], context: dict) -> dict[str, Any]:
        """Registra checkpoint em posto durante ronda."""
        if len(args) < 2:
            return {
                "response": (
                    "**Uso:** `/ronda checkpoint <ronda_id> <posto_id> [observacoes...]`\n\n"
                    "Registra visita a um posto durante a ronda.\n\n"
                    "**Parametros:**\n"
                    "- `ronda_id` - ID ou codigo da ronda (ex: RON-2026-00001)\n"
                    "- `posto_id` - ID do posto a registrar\n"
                    "- `observacoes` - Observacoes opcionais\n\n"
                    "**Exemplo:** `/ronda checkpoint RON-2026-00001 PST-001 Tudo conforme`"
                ),
                "suggestions": ["/ronda andamento", "/ronda help"],
            }

        round_identifier = args[0].upper()
        post_identifier = args[1]
        observations = " ".join(args[2:]) if len(args) > 2 else None

        if self.has_data_connector:
            try:
                result = await self.data_connector._register_checkpoint(
                    round_identifier=round_identifier,
                    post_identifier=post_identifier,
                    observations=observations,
                    context=context,
                )
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": result.data,
                    }
                    response_data["suggestions"] = [
                        f"/ronda checkpoints {round_identifier}",
                        f"/ronda resultado {round_identifier}",
                    ]
                    return response_data
                else:
                    return {
                        "response": result.message,
                        "suggestions": ["/ronda andamento", "/ronda help"],
                    }
            except AttributeError:
                logger.warning("DataConnector nao possui metodo _register_checkpoint")
            except Exception as e:
                logger.warning(f"Erro ao registrar checkpoint: {e}")

        # Fallback - informar que precisa do data connector
        return {
            "response": (
                f"**Registrar Checkpoint**\n\n"
                f"Ronda: {round_identifier}\n"
                f"Posto: {post_identifier}\n"
                f"Observacoes: {observations or 'Nenhuma'}\n\n"
                f"Nao foi possivel registrar o checkpoint. "
                f"Conexao com banco de dados necessaria."
            ),
            "data": {
                "round_identifier": round_identifier,
                "post_identifier": post_identifier,
                "observations": observations,
            },
            "suggestions": ["/ronda andamento", "/ronda help"],
        }

    async def _checkpoints(self, args: list[str], context: dict) -> dict[str, Any]:
        """Lista checkpoints de uma ronda."""
        if not args:
            return {
                "response": (
                    "**Uso:** `/ronda checkpoints <ronda_id>`\n\n"
                    "Lista todos os checkpoints realizados na ronda.\n\n"
                    "**Exemplo:** `/ronda checkpoints RON-2026-00001`"
                ),
                "suggestions": ["/ronda andamento", "/ronda help"],
            }

        round_identifier = args[0].upper()

        if self.has_data_connector:
            try:
                result = await self.data_connector._get_checkpoints_ronda(round_identifier)
                if result.success:
                    response_data = {
                        "response": result.message,
                        "data": {
                            "checkpoints": result.data,
                            "total": result.total_count,
                            "round_code": round_identifier,
                        },
                    }
                    suggestions = [f"/ronda resultado {round_identifier}"]
                    if result.data:
                        suggestions.insert(0, f"/ronda checkpoint {round_identifier} <posto>")
                    response_data["suggestions"] = suggestions
                    return response_data
            except AttributeError:
                logger.warning("DataConnector nao possui metodo _get_checkpoints_ronda")
            except Exception as e:
                logger.warning(f"Erro ao listar checkpoints: {e}")

        # Fallback
        return {
            "response": (
                f"**Checkpoints da Ronda {round_identifier}**\n\n"
                f"Nao foi possivel carregar os checkpoints.\n"
                f"Conexao com banco de dados necessaria."
            ),
            "data": {"round_code": round_identifier},
            "suggestions": ["/ronda andamento", "/ronda help"],
        }

    async def _pausar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Pausa uma ronda em andamento."""
        if not args:
            return {
                "response": (
                    "**Uso:** `/ronda pausar <ronda_id>`\n\n"
                    "Pausa uma ronda que esta em andamento.\n\n"
                    "**Exemplo:** `/ronda pausar RON-2026-00001`"
                ),
                "suggestions": ["/ronda andamento", "/ronda help"],
            }

        round_identifier = args[0].upper()

        if self.has_data_connector:
            try:
                result = await self.data_connector._pausar_ronda(round_identifier)
                if result.success:
                    return {
                        "response": result.message,
                        "data": result.data,
                        "suggestions": [
                            f"/ronda retomar {round_identifier}",
                            f"/ronda resultado {round_identifier}",
                        ],
                    }
                else:
                    return {
                        "response": result.message,
                        "suggestions": ["/ronda andamento", "/ronda help"],
                    }
            except AttributeError:
                logger.warning("DataConnector nao possui metodo _pausar_ronda")
            except Exception as e:
                logger.warning(f"Erro ao pausar ronda: {e}")

        # Fallback
        return {
            "response": (
                f"**Pausar Ronda {round_identifier}**\n\n"
                f"Nao foi possivel pausar a ronda.\n"
                f"Conexao com banco de dados necessaria."
            ),
            "data": {"round_code": round_identifier},
            "suggestions": ["/ronda andamento", "/ronda help"],
        }

    async def _retomar(self, args: list[str], context: dict) -> dict[str, Any]:
        """Retoma uma ronda pausada."""
        if not args:
            return {
                "response": (
                    "**Uso:** `/ronda retomar <ronda_id>`\n\n"
                    "Retoma uma ronda que esta pausada.\n\n"
                    "**Exemplo:** `/ronda retomar RON-2026-00001`"
                ),
                "suggestions": ["/ronda stats", "/ronda help"],
            }

        round_identifier = args[0].upper()

        if self.has_data_connector:
            try:
                result = await self.data_connector._retomar_ronda(round_identifier)
                if result.success:
                    return {
                        "response": result.message,
                        "data": result.data,
                        "suggestions": [
                            f"/ronda checkpoint {round_identifier} <posto>",
                            f"/ronda checkpoints {round_identifier}",
                        ],
                    }
                else:
                    return {
                        "response": result.message,
                        "suggestions": ["/ronda stats", "/ronda help"],
                    }
            except AttributeError:
                logger.warning("DataConnector nao possui metodo _retomar_ronda")
            except Exception as e:
                logger.warning(f"Erro ao retomar ronda: {e}")

        # Fallback
        return {
            "response": (
                f"**Retomar Ronda {round_identifier}**\n\n"
                f"Nao foi possivel retomar a ronda.\n"
                f"Conexao com banco de dados necessaria."
            ),
            "data": {"round_code": round_identifier},
            "suggestions": ["/ronda stats", "/ronda help"],
        }

    def get_help(self) -> str:
        """Retorna texto de ajuda da skill."""
        return """**Skill /ronda**

**Comandos disponiveis:**
```
/ronda hoje                             - Rondas agendadas para hoje
/ronda andamento                        - Rondas em andamento
/ronda stats                            - Estatisticas por status
/ronda inspetor <nome>                  - Rondas por inspetor
/ronda resultado <codigo>               - Resultado de ronda concluida
/ronda checkpoint <ronda> <posto>       - Registrar checkpoint em posto
/ronda checkpoints <ronda>              - Listar checkpoints da ronda
/ronda pausar <ronda>                   - Pausar ronda em andamento
/ronda retomar <ronda>                  - Retomar ronda pausada
```

**Exemplos:**
- `/ronda hoje`
- `/ronda andamento`
- `/ronda stats`
- `/ronda inspetor Carlos Silva`
- `/ronda resultado RON-2026-00001`
- `/ronda checkpoint RON-2026-00001 PST-001 Tudo conforme`
- `/ronda checkpoints RON-2026-00001`
- `/ronda pausar RON-2026-00001`
- `/ronda retomar RON-2026-00001`"""
