"""
Voice Command Processor Service - Sprint 52.

Service for processing and executing voice commands.
"""

import re
import time
from difflib import SequenceMatcher
from typing import Any
from uuid import UUID, uuid4


class VoiceCommandProcessor:
    """Service for processing voice commands."""

    # Built-in command patterns
    BUILTIN_COMMANDS = {
        "navigate": {
            "phrases": ["ir para", "abrir", "mostrar", "navegar para", "vá para"],
            "category": "navigation",
            "params": ["destination"],
        },
        "search": {
            "phrases": ["buscar", "pesquisar", "procurar", "encontrar"],
            "category": "search",
            "params": ["query"],
        },
        "create": {
            "phrases": ["criar", "novo", "adicionar", "cadastrar", "registrar"],
            "category": "create",
            "params": ["entity_type", "name"],
        },
        "list": {
            "phrases": ["listar", "mostrar todos", "ver todos", "quais são"],
            "category": "query",
            "params": ["entity_type"],
        },
        "report": {
            "phrases": ["relatório de", "gerar relatório", "exportar"],
            "category": "report",
            "params": ["report_type"],
        },
        "help": {
            "phrases": ["ajuda", "como", "o que posso fazer", "comandos"],
            "category": "help",
            "params": [],
        },
        "cancel": {
            "phrases": ["cancelar", "parar", "desistir", "voltar"],
            "category": "system",
            "params": [],
        },
    }

    # Entity mappings for parameter extraction
    ENTITY_MAPPINGS = {
        "destinations": {
            "dashboard": ["dashboard", "painel", "início", "home"],
            "clientes": ["clientes", "cliente", "cadastro de clientes"],
            "financeiro": ["financeiro", "finanças", "contas"],
            "relatórios": ["relatórios", "reports"],
            "configurações": ["configurações", "config", "ajustes"],
            "ocorrências": ["ocorrências", "ocorrência", "chamados"],
        },
        "entities": {
            "cliente": ["cliente", "clientes"],
            "contrato": ["contrato", "contratos"],
            "ocorrência": ["ocorrência", "ocorrências", "chamado"],
            "reunião": ["reunião", "reuniões", "meeting"],
            "tarefa": ["tarefa", "tarefas", "task"],
        },
    }

    def __init__(self, min_confidence: float = 0.6):
        """Initialize command processor."""
        self.min_confidence = min_confidence
        self._command_registry: dict[str, dict] = {}
        self._load_builtin_commands()

    def _load_builtin_commands(self) -> None:
        """Load built-in commands into registry."""
        for code, config in self.BUILTIN_COMMANDS.items():
            self._command_registry[code] = {
                "code": code,
                "phrases": config["phrases"],
                "category": config["category"],
                "params": config["params"],
                "is_system": True,
            }

    def register_command(
        self,
        code: str,
        phrases: list[str],
        category: str,
        params: list[str],
        action_config: dict,
    ) -> None:
        """Register a custom command."""
        self._command_registry[code] = {
            "code": code,
            "phrases": phrases,
            "category": category,
            "params": params,
            "action_config": action_config,
            "is_system": False,
        }

    def process_command(
        self,
        text: str,
        context: dict | None = None,
        user_id: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Process a voice command text.

        Args:
            text: The spoken text
            context: Current application context
            user_id: User executing the command

        Returns:
            Command processing result
        """
        start_time = time.time()
        context = context or {}

        # Normalize text
        normalized = self._normalize_text(text)

        # Find matching command
        match_result = self._find_command(normalized)

        if not match_result["found"]:
            return {
                "recognized": False,
                "command_code": None,
                "confidence": 0,
                "status": "not_recognized",
                "alternatives": match_result.get("alternatives", []),
                "response_text": "Desculpe, não entendi o comando. Diga 'ajuda' para ver os comandos disponíveis.",
                "processing_time_ms": int((time.time() - start_time) * 1000),
            }

        command = match_result["command"]
        confidence = match_result["confidence"]

        # Extract parameters
        params = self._extract_parameters(normalized, command)

        # Check for missing required params
        missing_params = self._get_missing_params(command, params)

        # Determine status
        if confidence < self.min_confidence:
            status = "low_confidence"
        elif missing_params:
            status = "missing_params"
        else:
            status = "ready"

        return {
            "recognized": True,
            "command_code": command["code"],
            "command_category": command["category"],
            "confidence": confidence,
            "status": status,
            "parameters": params,
            "missing_params": missing_params,
            "alternatives": match_result.get("alternatives", []),
            "requires_confirmation": command.get("requires_confirmation", False),
            "is_dangerous": command.get("is_dangerous", False),
            "response_text": self._generate_response(command, params, status),
            "processing_time_ms": int((time.time() - start_time) * 1000),
        }

    def execute_command(
        self,
        command_code: str,
        parameters: dict[str, Any],
        context: dict | None = None,
    ) -> dict[str, Any]:
        """
        Execute a recognized command.

        Args:
            command_code: The command code to execute
            parameters: Extracted parameters
            context: Execution context

        Returns:
            Execution result
        """
        start_time = time.time()

        command = self._command_registry.get(command_code)
        if not command:
            return {
                "success": False,
                "error": f"Command not found: {command_code}",
                "execution_time_ms": int((time.time() - start_time) * 1000),
            }

        # Simulate command execution
        result = self._simulate_execution(command, parameters, context)

        return {
            "success": result["success"],
            "command_code": command_code,
            "result": result.get("data"),
            "response_text": result.get("response"),
            "action_taken": result.get("action"),
            "execution_time_ms": int((time.time() - start_time) * 1000),
        }

    def _normalize_text(self, text: str) -> str:
        """Normalize text for command matching."""
        # Lowercase
        text = text.lower().strip()
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)
        # Remove punctuation except hyphens
        text = re.sub(r"[^\w\s-]", "", text)
        return text

    def _find_command(self, text: str) -> dict[str, Any]:
        """Find matching command from text."""
        best_match = None
        best_confidence = 0
        alternatives = []

        for code, command in self._command_registry.items():
            for phrase in command["phrases"]:
                # Check direct match
                if phrase in text or text.startswith(phrase):
                    confidence = 0.95
                else:
                    # Calculate similarity
                    confidence = SequenceMatcher(None, phrase, text[: len(phrase) + 5]).ratio()

                if confidence > best_confidence:
                    if best_match:
                        alternatives.append(
                            {
                                "code": best_match["code"],
                                "confidence": best_confidence,
                            }
                        )
                    best_match = command
                    best_confidence = confidence
                elif confidence > 0.5:
                    alternatives.append(
                        {
                            "code": code,
                            "confidence": confidence,
                        }
                    )

        if best_match and best_confidence >= self.min_confidence:
            return {
                "found": True,
                "command": best_match,
                "confidence": round(best_confidence, 2),
                "alternatives": sorted(alternatives, key=lambda x: x["confidence"], reverse=True)[:3],
            }

        return {
            "found": False,
            "alternatives": sorted(alternatives, key=lambda x: x["confidence"], reverse=True)[:3],
        }

    def _extract_parameters(self, text: str, command: dict) -> dict[str, Any]:
        """Extract parameters from command text."""
        params = {}
        required_params = command.get("params", [])

        # Extract destination
        if "destination" in required_params:
            for dest, keywords in self.ENTITY_MAPPINGS["destinations"].items():
                for keyword in keywords:
                    if keyword in text:
                        params["destination"] = dest
                        break

        # Extract entity type
        if "entity_type" in required_params:
            for entity, keywords in self.ENTITY_MAPPINGS["entities"].items():
                for keyword in keywords:
                    if keyword in text:
                        params["entity_type"] = entity
                        break

        # Extract query (everything after command phrase)
        if "query" in required_params:
            for phrase in command["phrases"]:
                if phrase in text:
                    query = text.split(phrase, 1)[-1].strip()
                    if query:
                        params["query"] = query
                    break

        # Extract name (quoted or after "chamado/chamada")
        if "name" in required_params:
            # Look for quoted text
            quoted = re.findall(r'"([^"]+)"', text)
            if quoted:
                params["name"] = quoted[0]
            else:
                # Look for "chamado X" pattern
                match = re.search(r"chamad[oa]\s+(.+)", text)
                if match:
                    params["name"] = match.group(1).strip()

        return params

    def _get_missing_params(self, command: dict, params: dict) -> list[str]:
        """Get list of missing required parameters."""
        required = command.get("params", [])
        return [p for p in required if p not in params]

    def _generate_response(self, command: dict, params: dict, status: str) -> str:
        """Generate response text for command."""
        code = command["code"]

        if status == "missing_params":
            missing = self._get_missing_params(command, params)
            if "destination" in missing:
                return "Para onde você quer ir?"
            if "query" in missing:
                return "O que você quer buscar?"
            if "entity_type" in missing:
                return "Qual tipo de item você quer criar?"
            return f"Faltam informações: {', '.join(missing)}"

        if status == "low_confidence":
            return f"Você quis dizer '{code}'? Confirme ou reformule o comando."

        # Success responses
        responses = {
            "navigate": f"Abrindo {params.get('destination', 'página')}...",
            "search": f"Buscando por '{params.get('query', '')}'...",
            "create": f"Criando novo {params.get('entity_type', 'item')}...",
            "list": f"Listando {params.get('entity_type', 'itens')}...",
            "report": "Gerando relatório...",
            "help": "Comandos disponíveis: navegar, buscar, criar, listar, relatório, ajuda.",
            "cancel": "Operação cancelada.",
        }

        return responses.get(code, "Comando reconhecido.")

    def _simulate_execution(
        self,
        command: dict,
        params: dict,
        context: dict | None,
    ) -> dict[str, Any]:
        """Simulate command execution."""
        code = command["code"]

        # Simulate different command executions
        if code == "navigate":
            return {
                "success": True,
                "action": "navigation",
                "data": {"destination": params.get("destination")},
                "response": f"Navegando para {params.get('destination')}.",
            }

        if code == "search":
            return {
                "success": True,
                "action": "search",
                "data": {"query": params.get("query"), "results_count": 5},
                "response": f"Encontrados 5 resultados para '{params.get('query')}'.",
            }

        if code == "create":
            return {
                "success": True,
                "action": "create",
                "data": {"entity_type": params.get("entity_type"), "id": str(uuid4())},
                "response": f"Criado novo {params.get('entity_type')}.",
            }

        if code == "help":
            return {
                "success": True,
                "action": "help",
                "data": {"commands": list(self._command_registry.keys())},
                "response": "Comandos: navegar, buscar, criar, listar, relatório.",
            }

        return {
            "success": True,
            "action": code,
            "data": params,
            "response": "Comando executado.",
        }

    def get_suggestions(self, partial_text: str, max_suggestions: int = 5) -> list[dict]:
        """Get command suggestions for partial input."""
        normalized = self._normalize_text(partial_text)
        suggestions = []

        for code, command in self._command_registry.items():
            for phrase in command["phrases"]:
                if phrase.startswith(normalized) or normalized in phrase:
                    suggestions.append(
                        {
                            "code": code,
                            "phrase": phrase,
                            "category": command["category"],
                        }
                    )

        # Sort by relevance
        suggestions.sort(
            key=lambda x: (
                not x["phrase"].startswith(normalized),
                len(x["phrase"]),
            )
        )

        return suggestions[:max_suggestions]

    def list_commands(self, category: str | None = None) -> list[dict]:
        """List available commands."""
        commands = []
        for code, command in self._command_registry.items():
            if category and command["category"] != category:
                continue
            commands.append(
                {
                    "code": code,
                    "phrases": command["phrases"],
                    "category": command["category"],
                    "params": command["params"],
                    "is_system": command.get("is_system", False),
                }
            )
        return commands
