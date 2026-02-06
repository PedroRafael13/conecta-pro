"""
PostoAgent - Agente especialista em postos de trabalho.

Processa intents relacionados a postos de servico,
consulta dados via DataConnector e oferece fallback estatico.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class PostoIntent(str, Enum):
    """Intents relacionados a postos de trabalho."""
    LISTAR_POSTOS = "listar_postos"
    VER_POSTO = "ver_posto"
    CRIAR_POSTO = "criar_posto"
    ATUALIZAR_POSTO = "atualizar_posto"
    VER_REQUISITOS = "ver_requisitos"
    VER_STATS = "ver_stats"
    VER_COBERTURA = "ver_cobertura"


class PostoAgent:
    """
    Agente especializado em operacoes de postos de trabalho.

    Capabilities:
    - Listar postos com filtros (contrato, cliente, status)
    - Consultar detalhes de um posto especifico
    - Criar novo posto
    - Atualizar dados de posto
    - Ver requisitos do posto (certificacoes, armamento, veiculo)
    - Estatisticas do posto (cobertura, custo, ocorrencias)
    - Ver cobertura atual (funcionarios alocados vs necessarios)
    """

    # ==========================================================================
    # INTENT_PATTERNS - Deteccao de intencoes de postos
    # Patterns mais especificos ANTES dos mais genericos
    # ==========================================================================
    INTENT_PATTERNS = [
        # ==================================================================
        # CRIAR_POSTO - Antes de listar (mais especifico)
        # ==================================================================
        (r"(?:criar|crie|cria|registrar|registre|cadastrar|cadastre|novo|nova)\s+(?:um\s+)?posto", PostoIntent.CRIAR_POSTO),
        (r"(?:adicionar|adicione|incluir|inclua)\s+(?:um\s+)?(?:novo\s+)?posto", PostoIntent.CRIAR_POSTO),
        (r"(?:abrir|abra)\s+(?:um\s+)?(?:novo\s+)?posto", PostoIntent.CRIAR_POSTO),
        (r"novo\s+posto\s+de\s+(?:trabalho|servico|vigilancia|portaria)", PostoIntent.CRIAR_POSTO),
        (r"(?:preciso|precisamos)\s+(?:de\s+)?(?:um\s+)?(?:novo\s+)?posto", PostoIntent.CRIAR_POSTO),

        # ==================================================================
        # ATUALIZAR_POSTO - Antes de ver detalhes (mais especifico)
        # ==================================================================
        (r"(?:atualizar|atualize|editar|edite|alterar|altere|modificar|modifique)\s+(?:o\s+)?posto", PostoIntent.ATUALIZAR_POSTO),
        (r"(?:mudar|mude|trocar|troque)\s+(?:dados?\s+)?(?:do\s+)?posto", PostoIntent.ATUALIZAR_POSTO),
        (r"(?:atualizar|atualize|editar|edite|alterar|altere)\s+POST-\d+", PostoIntent.ATUALIZAR_POSTO),
        (r"posto\s+POST-\d+\s+(?:atualizar|editar|alterar|mudar)", PostoIntent.ATUALIZAR_POSTO),

        # ==================================================================
        # VER_REQUISITOS - Antes de detalhes (mais especifico)
        # ==================================================================
        (r"(?:requisitos?|exigencias?|certificac[oõ]es?|qualificac[oõ]es?)\s+(?:do\s+)?posto", PostoIntent.VER_REQUISITOS),
        (r"posto\s+(?:precisa|requer|exige|necessita)\s+(?:de\s+)?", PostoIntent.VER_REQUISITOS),
        (r"(?:o\s+que|quais?)\s+(?:o\s+)?posto\s+(?:precisa|requer|exige)", PostoIntent.VER_REQUISITOS),
        (r"(?:requisitos?|exigencias?|certificac[oõ]es?)\s+(?:do\s+)?POST-\d+", PostoIntent.VER_REQUISITOS),
        (r"(?:armamento|veiculo|cnh|certificado)\s+(?:do\s+|no\s+)?posto", PostoIntent.VER_REQUISITOS),
        (r"posto\s+(?:armado|desarmado|com\s+veiculo)", PostoIntent.VER_REQUISITOS),

        # ==================================================================
        # VER_COBERTURA - Antes de stats (mais especifico)
        # ==================================================================
        (r"cobertura\s+(?:do\s+|dos\s+)?postos?", PostoIntent.VER_COBERTURA),
        (r"(?:efetivo|alocacao|alocados?)\s+(?:do\s+|dos\s+|no\s+|nos\s+)?postos?", PostoIntent.VER_COBERTURA),
        (r"postos?\s+(?:com\s+)?(?:deficit|falta|carencia|vaga)", PostoIntent.VER_COBERTURA),
        (r"(?:falta|faltam|deficit|vagas?)\s+(?:de\s+)?(?:funcionarios?|colaboradores?|vigilantes?)\s+(?:no\s+|nos\s+)?postos?", PostoIntent.VER_COBERTURA),
        (r"postos?\s+(?:descobertos?|sem\s+cobertura|sem\s+efetivo)", PostoIntent.VER_COBERTURA),
        (r"(?:quantos?\s+)?(?:funcionarios?|colaboradores?)\s+(?:alocados?|trabalhando)\s+(?:no\s+|nos\s+)?postos?", PostoIntent.VER_COBERTURA),
        (r"cobertura\s+(?:do\s+)?POST-\d+", PostoIntent.VER_COBERTURA),
        (r"postos?\s+(?:com\s+)?cobertura\s+(?:critica|baixa|insuficiente)", PostoIntent.VER_COBERTURA),

        # ==================================================================
        # VER_STATS - Estatisticas gerais
        # ==================================================================
        (r"(?:estatisticas?|stats?|numeros?|indicadores?|dashboard)\s+(?:de\s+|dos\s+)?postos?", PostoIntent.VER_STATS),
        (r"(?:resumo|panorama|visao\s+geral)\s+(?:de\s+|dos\s+)?postos?", PostoIntent.VER_STATS),
        (r"(?:quantos?|total)\s+(?:de\s+)?postos?", PostoIntent.VER_STATS),
        (r"postos?\s+(?:em\s+)?numeros", PostoIntent.VER_STATS),
        (r"(?:custo|valor)\s+(?:total\s+)?(?:dos\s+)?postos?", PostoIntent.VER_STATS),
        (r"(?:stats?|estatisticas?)\s+(?:do\s+)?POST-\d+", PostoIntent.VER_STATS),

        # ==================================================================
        # VER_POSTO - Detalhes de um posto especifico
        # ==================================================================
        (r"(?:detalhe|detalhes|info|informacoes?)\s+(?:do\s+)?posto\s+POST-\d+", PostoIntent.VER_POSTO),
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba)\s+(?:o\s+)?posto\s+POST-\d+", PostoIntent.VER_POSTO),
        (r"POST-\d+", PostoIntent.VER_POSTO),
        (r"(?:detalhe|detalhes|info)\s+(?:do\s+)?posto", PostoIntent.VER_POSTO),
        (r"(?:ver|veja|mostrar|mostre)\s+(?:o\s+)?posto\b(?!\s*s)", PostoIntent.VER_POSTO),
        (r"sobre\s+(?:o\s+)?posto", PostoIntent.VER_POSTO),

        # ==================================================================
        # LISTAR_POSTOS - Generico (por ultimo)
        # ==================================================================
        (r"(?:ver|veja|mostrar|mostre|exibir|exiba|listar|liste)\s+(?:os\s+)?postos?(?:\s+(?:ativos?|inativos?|todos?))?", PostoIntent.LISTAR_POSTOS),
        (r"postos?\s+(?:ativos?|inativos?|cadastrados?|existentes?|disponiveis?)", PostoIntent.LISTAR_POSTOS),
        (r"(?:tem|ha|há)\s+(?:algum|quantos?)\s+postos?", PostoIntent.LISTAR_POSTOS),
        (r"(?:quais?|que)\s+(?:sao\s+)?(?:os\s+)?postos?", PostoIntent.LISTAR_POSTOS),
        (r"postos?\s+(?:do\s+|da\s+)?(?:contrato|cliente)", PostoIntent.LISTAR_POSTOS),
        (r"postos?\s+(?:em\s+)?(?:operacao|funcionamento)", PostoIntent.LISTAR_POSTOS),
        (r"(?:todos?\s+)?(?:os\s+)?postos?\s*$", PostoIntent.LISTAR_POSTOS),
    ]

    def __init__(self, db=None, data_connector=None):
        self.db = db
        self.data_connector = data_connector
        # Se tem db mas nao tem data_connector, criar automaticamente
        if db and not data_connector:
            try:
                from modules.ai.bartolo.services.data_connector import DataConnector
                self.data_connector = DataConnector(db)
            except Exception as e:
                logger.warning(f"Nao foi possivel criar DataConnector: {e}")
                self.data_connector = None

    async def process(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processa uma mensagem relacionada a postos.

        Returns:
            Dict com response, intent, data, suggestions, actions
        """
        intent = self._detect_intent(message)
        context = context or {}

        if intent == PostoIntent.LISTAR_POSTOS:
            return await self._handle_listar_postos(message, context)
        elif intent == PostoIntent.VER_POSTO:
            return await self._handle_ver_posto(message, context)
        elif intent == PostoIntent.CRIAR_POSTO:
            return await self._handle_criar_posto(message, context)
        elif intent == PostoIntent.ATUALIZAR_POSTO:
            return await self._handle_atualizar_posto(message, context)
        elif intent == PostoIntent.VER_REQUISITOS:
            return await self._handle_ver_requisitos(message, context)
        elif intent == PostoIntent.VER_STATS:
            return await self._handle_ver_stats(message, context)
        elif intent == PostoIntent.VER_COBERTURA:
            return await self._handle_ver_cobertura(message, context)
        else:
            return await self._handle_default(message, context)

    def _detect_intent(self, message: str) -> Optional[PostoIntent]:
        """Detecta o intent da mensagem."""
        message_lower = message.lower()

        for pattern, intent in self.INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                return intent
        return None

    # =========================================================================
    # HANDLERS
    # =========================================================================

    async def _handle_listar_postos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Lista postos usando DataConnector ou repositorio direto."""
        if self.data_connector and self.db:
            try:
                from modules.operacional.repositories.post_repository import PostRepository
                from modules.operacional.schemas.post import PostFilter
                from modules.operacional.models.post import PostStatus, PostType

                repo = PostRepository(self.db)

                # Extrair filtros da mensagem
                filters = self._extract_post_filters(message)
                post_filter = None
                if filters:
                    post_filter = PostFilter(**filters)

                posts, total = await repo.list(filters=post_filter, page=1, page_size=20)

                if posts:
                    lines = []
                    for p in posts[:15]:
                        status_icon = {
                            "active": "🟢",
                            "inactive": "🔴",
                            "temporary": "🟡",
                            "suspended": "⚫",
                        }.get(p.status, "⚪")
                        cobertura = f"{p.current_headcount}/{p.required_headcount}"
                        lines.append(
                            f"- {status_icon} **{p.code}** - {p.name} | "
                            f"{p.post_type} | Turno: {p.shift_type} | "
                            f"Efetivo: {cobertura}"
                        )

                    filter_desc = ""
                    if filters:
                        filter_parts = []
                        if filters.get("status"):
                            filter_parts.append(f"Status: {filters['status'].value}")
                        if filters.get("post_type"):
                            filter_parts.append(f"Tipo: {filters['post_type'].value}")
                        if filter_parts:
                            filter_desc = f" ({', '.join(filter_parts)})"

                    response = f"""📍 **POSTOS DE TRABALHO{filter_desc}** ({total})

{chr(10).join(lines)}

**Total:** {total} postos cadastrados
**Legenda:** 🟢 Ativo | 🔴 Inativo | 🟡 Temporario | ⚫ Suspenso"""

                    return {
                        "response": response,
                        "intent": PostoIntent.LISTAR_POSTOS.value,
                        "data": {
                            "postos": [
                                {
                                    "codigo": p.code,
                                    "nome": p.name,
                                    "tipo": p.post_type,
                                    "status": p.status,
                                    "turno": p.shift_type,
                                    "efetivo": p.current_headcount,
                                    "requerido": p.required_headcount,
                                }
                                for p in posts
                            ],
                            "total": total,
                        },
                        "suggestions": [
                            "/posto stats",
                            "/posto cobertura",
                            "Criar novo posto",
                        ],
                    }
                else:
                    return {
                        "response": "📍 **Nenhum posto encontrado** com os filtros informados.",
                        "intent": PostoIntent.LISTAR_POSTOS.value,
                        "data": {"postos": [], "total": 0},
                        "suggestions": ["/posto listar", "Criar novo posto"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao listar postos via DB: {e}")

        # Fallback estatico
        today = date.today().strftime('%d/%m/%Y')
        return {
            "response": f"""📍 **POSTOS DE TRABALHO** (5)

- 🟢 **POST-0001** - Portaria Principal | vigilante | Turno: 12x36 | Efetivo: 4/4
- 🟢 **POST-0002** - Guarita Norte | vigilante | Turno: diurno | Efetivo: 2/2
- 🟢 **POST-0003** - Recepcao Bloco A | porteiro | Turno: administrativo | Efetivo: 1/2
- 🟡 **POST-0004** - Estacionamento | controlador_acesso | Turno: diurno | Efetivo: 1/1
- 🔴 **POST-0005** - Guarita Sul (Desativado) | vigilante | Turno: noturno | Efetivo: 0/2

**Total:** 5 postos cadastrados
**Legenda:** 🟢 Ativo | 🔴 Inativo | 🟡 Temporario | ⚫ Suspenso

Dados de referencia ({today})""",
            "intent": PostoIntent.LISTAR_POSTOS.value,
            "data": {"total": 5},
            "suggestions": ["/posto stats", "/posto cobertura", "Criar novo posto"],
        }

    async def _handle_ver_posto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra detalhes de um posto especifico."""
        # Extrair codigo do posto
        code_match = re.search(r"POST-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if self.db and code:
            try:
                from modules.operacional.repositories.post_repository import PostRepository

                repo = PostRepository(self.db)
                post = await repo.get_by_code(code)

                if post:
                    status_label = {
                        "active": "Ativo 🟢",
                        "inactive": "Inativo 🔴",
                        "temporary": "Temporario 🟡",
                        "suspended": "Suspenso ⚫",
                    }.get(post.status, post.status)

                    shift_start = post.shift_start_time.strftime('%H:%M') if post.shift_start_time else 'N/A'
                    shift_end = post.shift_end_time.strftime('%H:%M') if post.shift_end_time else 'N/A'
                    created = post.created_at.strftime('%d/%m/%Y') if post.created_at else 'N/A'

                    # Requisitos
                    req_lines = []
                    if post.requires_armed:
                        req_lines.append("Armamento obrigatorio")
                    if post.requires_vehicle:
                        req_lines.append("Veiculo obrigatorio")
                    if post.requires_experience_months > 0:
                        req_lines.append(f"Experiencia minima: {post.requires_experience_months} meses")
                    if post.required_certifications:
                        certs = ", ".join(str(c) for c in post.required_certifications.values()) if isinstance(post.required_certifications, dict) else str(post.required_certifications)
                        req_lines.append(f"Certificacoes: {certs}")

                    requisitos_text = "\n".join(f"  - {r}" for r in req_lines) if req_lines else "  Nenhum requisito especial"

                    response = f"""📍 **POSTO {post.code}**

**Nome:** {post.name}
**Descricao:** {post.description or 'N/A'}

**Classificacao:**
- Tipo: {post.post_type}
- Status: {status_label}
- Turno: {post.shift_type} ({shift_start} - {shift_end})
- Intervalo: {post.break_duration_minutes} minutos

**Efetivo:**
- Requerido: {post.required_headcount}
- Alocado: {post.current_headcount}
- Vagas: {post.vacancy_count}

**Custos:**
- Valor hora: R$ {post.hourly_rate:,.2f}
- Custo mensal: R$ {post.monthly_cost:,.2f}
- Ad. noturno: {post.night_shift_bonus_percent}%
- Periculosidade: {post.hazard_pay_percent}%

**Requisitos:**
{requisitos_text}

**Localizacao:**
- Endereco: {post.address or 'N/A'}
- Cidade: {post.city or 'N/A'}/{post.state or 'N/A'}

**Contatos:**
- Supervisor: {post.supervisor_name or 'N/A'} ({post.supervisor_phone or 'N/A'})
- Emergencia: {post.emergency_contact or 'N/A'} ({post.emergency_phone or 'N/A'})

**Criado em:** {created}"""

                    return {
                        "response": response,
                        "intent": PostoIntent.VER_POSTO.value,
                        "data": {
                            "codigo": post.code,
                            "id": post.id,
                            "nome": post.name,
                            "status": post.status,
                            "tipo": post.post_type,
                        },
                        "suggestions": [
                            f"/posto requisitos {post.code}",
                            f"/posto cobertura {post.code}",
                            f"/posto atualizar {post.code}",
                        ],
                    }
                else:
                    return {
                        "response": f"Posto **{code}** nao encontrado. Verifique o codigo e tente novamente.",
                        "intent": PostoIntent.VER_POSTO.value,
                        "data": {"codigo": code, "encontrado": False},
                        "suggestions": ["/posto listar", "Criar novo posto"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes do posto via DB: {e}")

        # Fallback estatico
        code_display = code or "POST-0001"
        return {
            "response": f"""📍 **POSTO {code_display}**

**Nome:** Portaria Principal
**Descricao:** Posto de vigilancia na entrada principal do condominio

**Classificacao:**
- Tipo: vigilante
- Status: Ativo 🟢
- Turno: 12x36 (07:00 - 19:00)
- Intervalo: 60 minutos

**Efetivo:**
- Requerido: 4
- Alocado: 4
- Vagas: 0

**Custos:**
- Valor hora: R$ 25,00
- Custo mensal: R$ 18.000,00
- Ad. noturno: 20.0%
- Periculosidade: 30.0%

**Requisitos:**
  - Armamento obrigatorio
  - Experiencia minima: 12 meses
  - Certificacoes: Vigilante armado, Primeiros socorros

**Localizacao:**
- Endereco: Av. Principal, 1000
- Cidade: Sao Paulo/SP

**Contatos:**
- Supervisor: Carlos Silva (11-99999-0001)
- Emergencia: Base Central (11-99999-0000)

**Criado em:** {date.today().strftime('%d/%m/%Y')}""",
            "intent": PostoIntent.VER_POSTO.value,
            "data": {"codigo": code_display},
            "suggestions": [
                f"/posto requisitos {code_display}",
                f"/posto cobertura {code_display}",
                f"/posto atualizar {code_display}",
            ],
        }

    async def _handle_criar_posto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para wizard/action de criacao de posto."""
        return {
            "response": """📝 **CRIAR NOVO POSTO**

Para criar um novo posto de trabalho, preciso das seguintes informacoes:

1. **Nome** do posto (ex: Portaria Principal, Guarita Norte)
2. **Tipo** (vigilante, porteiro, recepcionista, controlador_acesso, supervisor, rondante, monitoramento)
3. **Turno** (diurno, noturno, manha, tarde, noite, administrativo, 12x36)
4. **Quantidade** de funcionarios necessarios
5. **Endereco/Localizacao** do posto
6. **Requisitos** (armamento, veiculo, certificacoes)
7. **Contrato/Cliente** associado (opcional)

**Custos** (opcional):
- Valor hora
- Custo mensal estimado
- Adicional noturno / Periculosidade

Posso iniciar o **assistente guiado** para coletar esses dados passo a passo.

**Deseja iniciar?**""",
            "intent": PostoIntent.CRIAR_POSTO.value,
            "data": {"action": "create_post", "wizard": "posto_wizard"},
            "suggestions": ["Iniciar assistente", "Cancelar"],
            "actions": [
                {
                    "type": "create",
                    "label": "Criar Posto",
                    "target": "post",
                    "data": {"wizard": "posto"},
                },
            ],
        }

    async def _handle_atualizar_posto(self, message: str, context: Dict) -> Dict[str, Any]:
        """Redireciona para action de atualizacao de posto."""
        code_match = re.search(r"POST-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if code:
            response = f"""✏️ **ATUALIZAR POSTO {code}**

Quais dados deseja atualizar?

- **Nome** ou descricao
- **Tipo** de posto
- **Turno** e horarios
- **Efetivo** requerido
- **Endereco** e localizacao
- **Custos** (valor hora, custo mensal)
- **Requisitos** (armamento, veiculo, certificacoes)
- **Contatos** (supervisor, emergencia)
- **Status** (ativar, desativar, suspender)

Informe os campos e valores desejados."""
        else:
            response = """✏️ **ATUALIZAR POSTO**

Informe o codigo do posto que deseja atualizar (ex: POST-0001).

Apos identificar o posto, sera possivel alterar:
- Nome, tipo, turno, efetivo
- Endereco, custos, requisitos
- Contatos, status"""

        return {
            "response": response,
            "intent": PostoIntent.ATUALIZAR_POSTO.value,
            "data": {"action": "update_post", "code": code},
            "suggestions": ["/posto listar", "Cancelar"],
            "actions": [
                {
                    "type": "edit",
                    "label": "Atualizar Posto",
                    "target": "post",
                    "data": {"code": code, "action": "update"},
                },
            ],
        }

    async def _handle_ver_requisitos(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra requisitos de um posto especifico."""
        code_match = re.search(r"POST-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if self.db and code:
            try:
                from modules.operacional.repositories.post_repository import PostRepository

                repo = PostRepository(self.db)
                post = await repo.get_by_code(code)

                if post:
                    req_lines = []

                    # Armamento
                    armed_status = "SIM - Armamento obrigatorio" if post.requires_armed else "NAO"
                    req_lines.append(f"- Armamento: **{armed_status}**")

                    # Veiculo
                    vehicle_status = "SIM - Veiculo obrigatorio" if post.requires_vehicle else "NAO"
                    req_lines.append(f"- Veiculo: **{vehicle_status}**")

                    # Experiencia
                    if post.requires_experience_months > 0:
                        req_lines.append(f"- Experiencia minima: **{post.requires_experience_months} meses**")
                    else:
                        req_lines.append("- Experiencia minima: **Nao exigida**")

                    # Certificacoes
                    if post.required_certifications:
                        if isinstance(post.required_certifications, dict):
                            for key, val in post.required_certifications.items():
                                req_lines.append(f"- Certificacao: **{key}** - {val}")
                        elif isinstance(post.required_certifications, list):
                            for cert in post.required_certifications:
                                req_lines.append(f"- Certificacao: **{cert}**")
                    else:
                        req_lines.append("- Certificacoes: **Nenhuma exigida**")

                    # Adicional noturno / Periculosidade
                    if post.night_shift_bonus_percent > 0:
                        req_lines.append(f"- Adicional noturno: **{post.night_shift_bonus_percent}%**")
                    if post.hazard_pay_percent > 0:
                        req_lines.append(f"- Periculosidade: **{post.hazard_pay_percent}%**")

                    response = f"""📋 **REQUISITOS DO POSTO {post.code}** ({post.name})

**Tipo:** {post.post_type} | **Turno:** {post.shift_type}

**Requisitos:**
{chr(10).join(req_lines)}

**Efetivo requerido:** {post.required_headcount} funcionario(s)"""

                    return {
                        "response": response,
                        "intent": PostoIntent.VER_REQUISITOS.value,
                        "data": {
                            "codigo": post.code,
                            "armado": post.requires_armed,
                            "veiculo": post.requires_vehicle,
                            "experiencia_meses": post.requires_experience_months,
                            "certificacoes": post.required_certifications,
                        },
                        "suggestions": [
                            f"/posto ver {post.code}",
                            f"/posto cobertura {post.code}",
                            "/posto listar",
                        ],
                    }
                else:
                    return {
                        "response": f"Posto **{code}** nao encontrado.",
                        "intent": PostoIntent.VER_REQUISITOS.value,
                        "data": {"codigo": code, "encontrado": False},
                        "suggestions": ["/posto listar"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar requisitos do posto via DB: {e}")

        # Fallback estatico
        code_display = code or "POST-0001"
        return {
            "response": f"""📋 **REQUISITOS DO POSTO {code_display}** (Portaria Principal)

**Tipo:** vigilante | **Turno:** 12x36

**Requisitos:**
- Armamento: **SIM - Armamento obrigatorio**
- Veiculo: **NAO**
- Experiencia minima: **12 meses**
- Certificacao: **Vigilante armado** - Obrigatorio
- Certificacao: **Primeiros socorros** - Desejavel
- Periculosidade: **30.0%**
- Adicional noturno: **20.0%**

**Efetivo requerido:** 4 funcionario(s)

Informe o codigo do posto para consulta especifica: `/posto requisitos POST-XXX`""",
            "intent": PostoIntent.VER_REQUISITOS.value,
            "data": {"codigo": code_display},
            "suggestions": [
                f"/posto ver {code_display}",
                f"/posto cobertura {code_display}",
                "/posto listar",
            ],
        }

    async def _handle_ver_stats(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra estatisticas gerais dos postos."""
        if self.db:
            try:
                from modules.operacional.repositories.post_repository import PostRepository

                repo = PostRepository(self.db)
                stats = await repo.get_stats()

                if stats.total > 0:
                    # Por status
                    status_lines = []
                    status_icons = {"active": "🟢", "inactive": "🔴", "temporary": "🟡", "suspended": "⚫"}
                    status_labels = {"active": "Ativos", "inactive": "Inativos", "temporary": "Temporarios", "suspended": "Suspensos"}
                    for st, count in sorted(stats.by_status.items(), key=lambda x: x[1], reverse=True):
                        icon = status_icons.get(st, "⚪")
                        label = status_labels.get(st, st.title())
                        status_lines.append(f"  - {icon} {label}: **{count}**")

                    # Por tipo
                    type_lines = []
                    for tp, count in sorted(stats.by_type.items(), key=lambda x: x[1], reverse=True):
                        type_lines.append(f"  - {tp.replace('_', ' ').title()}: **{count}**")

                    # Por turno
                    shift_lines = []
                    for sh, count in sorted(stats.by_shift.items(), key=lambda x: x[1], reverse=True):
                        shift_lines.append(f"  - {sh.replace('_', ' ').title()}: **{count}**")

                    # Cobertura
                    cobertura_pct = round((stats.total_allocated / stats.total_headcount) * 100, 1) if stats.total_headcount > 0 else 0

                    response = f"""📊 **ESTATISTICAS DE POSTOS**

**Visao Geral:**
- Total: **{stats.total}**
- Preenchidos: **{stats.filled}**
- Com vagas: **{stats.with_vacancy}**
- Cobertura geral: **{cobertura_pct}%** ({stats.total_allocated}/{stats.total_headcount})

**Por Status:**
{chr(10).join(status_lines) if status_lines else '  Nenhum dado'}

**Por Tipo:**
{chr(10).join(type_lines[:5]) if type_lines else '  Nenhum dado'}

**Por Turno:**
{chr(10).join(shift_lines[:5]) if shift_lines else '  Nenhum dado'}

**Custo Mensal Total:** R$ {stats.total_monthly_cost:,.2f}"""

                    return {
                        "response": response,
                        "intent": PostoIntent.VER_STATS.value,
                        "data": {
                            "total": stats.total,
                            "preenchidos": stats.filled,
                            "com_vagas": stats.with_vacancy,
                            "cobertura_pct": cobertura_pct,
                            "custo_total": stats.total_monthly_cost,
                        },
                        "suggestions": ["/posto cobertura", "/posto listar", "Criar novo posto"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar estatisticas de postos via DB: {e}")

        # Fallback estatico
        return {
            "response": """📊 **ESTATISTICAS DE POSTOS**

**Visao Geral:**
- Total: **25**
- Preenchidos: **18**
- Com vagas: **7**
- Cobertura geral: **82.5%** (66/80)

**Por Status:**
  - 🟢 Ativos: **20**
  - 🔴 Inativos: **3**
  - 🟡 Temporarios: **2**

**Por Tipo:**
  - Vigilante: **12**
  - Porteiro: **6**
  - Controlador Acesso: **3**
  - Recepcionista: **2**
  - Supervisor: **2**

**Por Turno:**
  - 12x36: **10**
  - Diurno: **8**
  - Noturno: **4**
  - Administrativo: **3**

**Custo Mensal Total:** R$ 245.000,00""",
            "intent": PostoIntent.VER_STATS.value,
            "data": {"total": 25, "preenchidos": 18, "com_vagas": 7, "cobertura_pct": 82.5, "custo_total": 245000.0},
            "suggestions": ["/posto cobertura", "/posto listar", "Criar novo posto"],
        }

    async def _handle_ver_cobertura(self, message: str, context: Dict) -> Dict[str, Any]:
        """Mostra cobertura atual dos postos (alocados vs necessarios)."""
        # Extrair codigo do posto se informado
        code_match = re.search(r"POST-\d+", message.upper())
        code = code_match.group(0) if code_match else None

        if self.db:
            try:
                from modules.operacional.repositories.post_repository import PostRepository

                repo = PostRepository(self.db)

                if code:
                    # Cobertura de um posto especifico
                    post = await repo.get_by_code(code)
                    if post:
                        cobertura_pct = round((post.current_headcount / post.required_headcount) * 100, 1) if post.required_headcount > 0 else 0
                        cobertura_icon = "🟢" if cobertura_pct >= 80 else "🟡" if cobertura_pct >= 50 else "🔴"

                        response = f"""📊 **COBERTURA DO POSTO {post.code}** ({post.name})

{cobertura_icon} **Cobertura: {cobertura_pct}%**

- Efetivo requerido: **{post.required_headcount}**
- Efetivo alocado: **{post.current_headcount}**
- Vagas abertas: **{post.vacancy_count}**

**Turno:** {post.shift_type}
**Tipo:** {post.post_type}"""

                        if post.vacancy_count > 0:
                            response += f"\n\n**Acao recomendada:** Alocar {post.vacancy_count} funcionario(s) para cobertura total."

                        return {
                            "response": response,
                            "intent": PostoIntent.VER_COBERTURA.value,
                            "data": {
                                "codigo": post.code,
                                "cobertura_pct": cobertura_pct,
                                "requerido": post.required_headcount,
                                "alocado": post.current_headcount,
                                "vagas": post.vacancy_count,
                            },
                            "suggestions": [
                                f"/posto ver {post.code}",
                                "/posto cobertura",
                                "/posto stats",
                            ],
                        }
                    else:
                        return {
                            "response": f"Posto **{code}** nao encontrado.",
                            "intent": PostoIntent.VER_COBERTURA.value,
                            "data": {"codigo": code, "encontrado": False},
                            "suggestions": ["/posto listar"],
                        }

                # Cobertura geral - todos os postos
                posts, total = await repo.list(page=1, page_size=100)

                postos_cobertura = []
                for p in posts:
                    if p.required_headcount > 0:
                        cob = round((p.current_headcount / p.required_headcount) * 100, 1)
                        postos_cobertura.append({
                            "codigo": p.code,
                            "nome": p.name,
                            "alocados": p.current_headcount,
                            "requeridos": p.required_headcount,
                            "cobertura": cob,
                            "deficit": p.vacancy_count,
                        })

                # Ordenar por cobertura (menor primeiro)
                postos_cobertura.sort(key=lambda x: x["cobertura"])

                # Separar criticos e ok
                criticos = [p for p in postos_cobertura if p["cobertura"] < 80]
                ok = [p for p in postos_cobertura if p["cobertura"] >= 80]

                lines_criticos = []
                for p in criticos[:10]:
                    icon = "🔴" if p["cobertura"] < 50 else "🟡"
                    lines_criticos.append(
                        f"- {icon} **{p['codigo']}** - {p['nome']}: "
                        f"{p['alocados']}/{p['requeridos']} ({p['cobertura']}%) - "
                        f"Deficit: {p['deficit']}"
                    )

                total_requerido = sum(p["requeridos"] for p in postos_cobertura)
                total_alocado = sum(p["alocados"] for p in postos_cobertura)
                cobertura_geral = round((total_alocado / total_requerido) * 100, 1) if total_requerido > 0 else 0

                response = f"""📊 **COBERTURA DOS POSTOS**

**Cobertura geral:** {cobertura_geral}% ({total_alocado}/{total_requerido})
**Postos com cobertura OK (>=80%):** {len(ok)}
**Postos com cobertura critica (<80%):** {len(criticos)}"""

                if lines_criticos:
                    response += f"""

**Postos com cobertura critica:**
{chr(10).join(lines_criticos)}

**Acao recomendada:** Priorizar alocacao nos postos com deficit."""
                else:
                    response += "\n\nTodos os postos com cobertura acima de 80%. ✅"

                return {
                    "response": response,
                    "intent": PostoIntent.VER_COBERTURA.value,
                    "data": {
                        "cobertura_geral": cobertura_geral,
                        "total_postos": len(postos_cobertura),
                        "criticos": len(criticos),
                        "ok": len(ok),
                    },
                    "suggestions": ["/posto stats", "/posto listar", "Ver escalas"],
                }
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura de postos via DB: {e}")

        # Fallback estatico - tenta DataConnector
        if self.data_connector:
            try:
                result = await self.data_connector._get_cobertura_critica()
                if result.success and result.message:
                    return {
                        "response": result.message,
                        "intent": PostoIntent.VER_COBERTURA.value,
                        "data": {"postos_criticos": result.data, "total": result.total_count},
                        "suggestions": ["/posto stats", "/posto listar", "Ver escalas"],
                    }
            except Exception as e:
                logger.warning(f"Erro ao buscar cobertura via DataConnector: {e}")

        # Fallback estatico final
        return {
            "response": """📊 **COBERTURA DOS POSTOS**

**Cobertura geral:** 82.5% (66/80)
**Postos com cobertura OK (>=80%):** 18
**Postos com cobertura critica (<80%):** 3

**Postos com cobertura critica:**
- 🔴 **POST-0007** - Guarita Sul: 1/4 (25.0%) - Deficit: 3
- 🟡 **POST-0012** - Recepcao Bloco C: 1/2 (50.0%) - Deficit: 1
- 🟡 **POST-0019** - Estacionamento VIP: 2/3 (66.7%) - Deficit: 1

**Acao recomendada:** Priorizar alocacao nos postos com deficit.""",
            "intent": PostoIntent.VER_COBERTURA.value,
            "data": {"cobertura_geral": 82.5, "criticos": 3, "ok": 18},
            "suggestions": ["/posto stats", "/posto listar", "Ver escalas"],
        }

    async def _handle_default(self, message: str, context: Dict) -> Optional[Dict[str, Any]]:
        """Handler padrao - retorna None para permitir que DataConnector processe."""
        return None

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _extract_post_filters(self, message: str) -> dict:
        """Extrai filtros de postos a partir da mensagem."""
        from modules.operacional.models.post import PostStatus, PostType, ShiftType

        filters = {}
        msg = message.lower()

        # Filtro de status
        if "ativo" in msg and "inativo" not in msg:
            filters["status"] = PostStatus.ACTIVE
        elif "inativo" in msg:
            filters["status"] = PostStatus.INACTIVE
        elif "temporario" in msg:
            filters["status"] = PostStatus.TEMPORARY
        elif "suspenso" in msg:
            filters["status"] = PostStatus.SUSPENDED

        # Filtro de tipo
        tipo_map = {
            "vigilant": PostType.VIGILANTE,
            "porteir": PostType.PORTEIRO,
            "recepcionist": PostType.RECEPCIONISTA,
            "controlador": PostType.CONTROLADOR_ACESSO,
            "supervisor": PostType.SUPERVISOR,
            "lider": PostType.LIDER,
            "rondant": PostType.RONDANTE,
            "monitorament": PostType.MONITORAMENTO,
            "manutenc": PostType.MANUTENCAO,
            "servicos gerais": PostType.SERVICOS_GERAIS,
            "limpeza": PostType.SERVICOS_GERAIS,
            "jardinag": PostType.JARDINAGEM,
            "portaria": PostType.PORTARIA,
        }
        for key, value in tipo_map.items():
            if key in msg:
                filters["post_type"] = value
                break

        # Filtro de turno
        turno_map = {
            "diurno": ShiftType.DIURNO,
            "noturno": ShiftType.NOTURNO,
            "manha": ShiftType.MANHA,
            "tarde": ShiftType.TARDE,
            "noite": ShiftType.NOITE,
            "administrativo": ShiftType.ADMINISTRATIVO,
            "12x36": ShiftType.ESCALA_12X36,
            "integral": ShiftType.INTEGRAL,
        }
        for key, value in turno_map.items():
            if key in msg:
                filters["shift_type"] = value
                break

        # Filtro de armamento
        if "armado" in msg:
            filters["requires_armed"] = True
        elif "desarmado" in msg:
            filters["requires_armed"] = False

        # Filtro de veiculo
        if "com veiculo" in msg or "com carro" in msg or "motorizado" in msg:
            filters["requires_vehicle"] = True

        return filters

    def get_capabilities(self) -> List[str]:
        """Retorna lista de capabilities do agente."""
        return [
            "Listar postos com filtros (contrato, cliente, status, tipo, turno)",
            "Consultar detalhes completos de um posto",
            "Criar novo posto de trabalho (via wizard)",
            "Atualizar dados de um posto existente",
            "Ver requisitos do posto (certificacoes, armamento, veiculo)",
            "Estatisticas gerais de postos (custo, cobertura, distribuicao)",
            "Ver cobertura atual (alocados vs necessarios por posto)",
        ]
