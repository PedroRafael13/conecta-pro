"""
Service CCT — lógica de negócio com fallback para constantes hardcoded.

Hierarquia de dados:
1. Cache Redis (miss → banco)
2. Banco de dados (cct_convencoes/cargos/feriados/beneficios)
3. Fallback: constantes Python dos modules/cct/models/
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from core.logging import logger
from modules.people_management.cct.repositories.cct_repository import CCTRepository


class CCTService:
    """Serviço CCT com cache Redis e fallback para constantes."""

    CACHE_TTL = 86400  # 24h

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._repo = CCTRepository(db)

    # =========================================================================
    # CONVENÇÃO VIGENTE
    # =========================================================================

    async def get_convencao_vigente(self) -> dict:
        """Retorna metadados da convenção vigente."""
        data = await self._repo.get_convencao_vigente_cached()
        if data:
            return data

        # Fallback para constantes
        logger.warning("CCT: banco vazio — usando fallback de constantes")
        return self._fallback_convencao()

    # =========================================================================
    # DIREITOS POR CARGO
    # =========================================================================

    async def get_direitos_cargo(self, cargo: str) -> dict:
        """
        Retorna piso salarial e adicionais para um cargo.

        Fluxo:
        1. Buscar convenção vigente
        2. Buscar cargo no banco com cache
        3. Se não encontrar, fallback para salary_table.py
        """
        conv = await self._repo.get_convencao_vigente_cached()
        if conv:
            convencao_id = uuid.UUID(conv["id"])
            cargo_data = await self._repo.get_cargo_by_nome_cached(convencao_id, cargo)
            if cargo_data:
                return {
                    "fonte": "banco",
                    "cargo_nome": cargo_data["cargo_nome"],
                    "piso_salarial": cargo_data["piso_salarial"],
                    "adicional_tipo": cargo_data["adicional_tipo"],
                    "adicional_noturno_percentual": cargo_data["adicional_noturno_percentual"],
                    "adicional_periculosidade_percentual": cargo_data["adicional_periculosidade_percentual"],
                    "adicional_insalubridade_percentual": cargo_data["adicional_insalubridade_percentual"],
                    "horas_extras_percentual": cargo_data["horas_extras_percentual"],
                    "horas_extras_noturnas_percentual": cargo_data["horas_extras_noturnas_percentual"],
                    "jornada_semanal_horas": cargo_data["jornada_semanal_horas"],
                }

        # Fallback: constantes Python
        return self._fallback_direitos_cargo(cargo)

    # =========================================================================
    # FERIADOS
    # =========================================================================

    async def get_feriados(self, ano: int, mes: int | None = None) -> list[dict]:
        """Retorna feriados do ano/mês com cache."""
        conv = await self._repo.get_convencao_vigente_cached()
        if conv:
            convencao_id = uuid.UUID(conv["id"])
            if mes:
                feriados = await self._repo.get_feriados_by_mes(convencao_id, ano, mes)
            else:
                feriados = await self._repo.get_feriados_by_ano(convencao_id, ano)

            if feriados:
                return feriados

        # Fallback: constantes Python
        return self._fallback_feriados(ano, mes)

    # =========================================================================
    # ADICIONAIS
    # =========================================================================

    async def get_adicional_noturno(self) -> dict:
        """Retorna configuração de adicional noturno CCT."""
        conv = await self._repo.get_convencao_vigente_cached()
        if conv:
            # Usar valores padrão CCT (fixos para todos os cargos)
            return {
                "fonte": "banco",
                "adicional_noturno_percentual": 20.0,
                "hora_noturna_minutos": 52.5,
                "periodo_noturno_inicio": "22:00",
                "periodo_noturno_fim": "05:00",
                "base_calculo": "hora_normal",
                "observacao": (
                    "Adicional noturno 20% sobre hora normal. "
                    "Hora noturna reduzida para 52min30s (periodo 22h-05h), conforme CCT 2026."
                ),
            }

        return self._fallback_adicional_noturno()

    # =========================================================================
    # BENEFÍCIOS
    # =========================================================================

    async def get_beneficios_cct(self, cargo: str, salario: float) -> list[dict]:
        """
        Retorna benefícios CCT com descontos calculados para o salário dado.
        """
        conv = await self._repo.get_convencao_vigente_cached()
        if conv:
            convencao_id = uuid.UUID(conv["id"])
            beneficios = await self._repo.get_beneficios_obrigatorios(convencao_id)
            if beneficios:
                resultado = []
                for b in beneficios:
                    desconto_calc = None
                    pct = b.get("desconto_percentual_sobre_salario")
                    if pct and salario > 0:
                        desconto_calc = round(salario * float(pct) / 100, 2)

                    resultado.append(
                        {
                            "tipo_beneficio": b["tipo_beneficio"],
                            "obrigatorio": b["obrigatorio"],
                            "valor_minimo_cct": b["valor_minimo"],
                            "valor_empresa_cct": b["valor_empresa"],
                            "desconto_maximo_cct": b["desconto_maximo_percentual"],
                            "desconto_percentual_cct": b["desconto_percentual_sobre_salario"],
                            "desconto_calculado": desconto_calc,
                            "observacao": b["observacao"],
                        }
                    )
                return resultado

        # Fallback
        return self._fallback_beneficios(salario)

    # =========================================================================
    # CÁLCULO DE RESCISÃO (delega para TerminationValidator existente)
    # =========================================================================

    async def calcular_rescisao(
        self,
        cargo: str,
        salario: float,
        data_admissao: str,
        data_demissao: str,
        motivo: str,
    ) -> dict:
        """Calcula verbas rescisórias usando dados CCT do banco."""
        try:
            from modules.cct.validators.termination_validator import TerminationValidator

            return TerminationValidator.validar_rescisao(
                employee_id=None,
                data_admissao=data_admissao,
                data_demissao=data_demissao,
                salario_base=salario,
                motivo=motivo,
            )
        except Exception as exc:
            logger.warning("Erro ao calcular rescisao via validator: %s", exc)
            return {"erro": str(exc), "salario_base": salario, "motivo": motivo}

    # =========================================================================
    # FALLBACKS — CONSTANTES PYTHON (quando banco vazio)
    # =========================================================================

    @staticmethod
    def _fallback_convencao() -> dict:
        try:
            from modules.cct.models.cct_metadata import CCT_METADATA

            return {
                "id": None,
                "sindicato_trabalhadores": CCT_METADATA.sindicato_laboral,
                "sindicato_patronal": CCT_METADATA.sindicato_patronal,
                "registro_mte": CCT_METADATA.registro_mte,
                "data_inicio": CCT_METADATA.vigencia_inicio,
                "data_fim": CCT_METADATA.vigencia_fim,
                "data_base": CCT_METADATA.data_base,
                "municipio": CCT_METADATA.municipio,
                "uf": CCT_METADATA.uf,
                "is_vigente": True,
            }
        except ImportError:
            return {
                "id": None,
                "sindicato_trabalhadores": "SINDECOMPRESTS",
                "sindicato_patronal": "SINDICOND-AM",
                "registro_mte": "AM000613/2025",
                "data_inicio": "2026-01-01",
                "data_fim": "2026-12-31",
                "data_base": "01/01",
                "municipio": "Manaus",
                "uf": "AM",
                "is_vigente": True,
            }

    @staticmethod
    def _fallback_direitos_cargo(cargo: str) -> dict:
        try:
            from modules.cct.models.salary_table import get_piso_by_cargo
            from modules.cct.models.schedule import ADICIONAIS

            entry = get_piso_by_cargo(cargo)
            piso = float(entry.piso) if entry else 1670.00
            adicional_tipo = entry.adicional.value if entry and entry.adicional else None

            return {
                "fonte": "fallback_constante",
                "cargo_nome": cargo,
                "piso_salarial": piso,
                "adicional_tipo": adicional_tipo,
                "adicional_noturno_percentual": float(ADICIONAIS.adicional_noturno_percentual),
                "adicional_periculosidade_percentual": float(ADICIONAIS.periculosidade_percentual),
                "adicional_insalubridade_percentual": float(ADICIONAIS.insalubridade_minimo_percentual),
                "horas_extras_percentual": float(ADICIONAIS.hora_extra_normal_percentual),
                "horas_extras_noturnas_percentual": float(ADICIONAIS.hora_extra_feriado_percentual),
                "jornada_semanal_horas": 44,
            }
        except ImportError:
            return {
                "fonte": "fallback_hardcoded",
                "cargo_nome": cargo,
                "piso_salarial": 1670.00,
                "adicional_tipo": None,
                "adicional_noturno_percentual": 20.0,
                "adicional_periculosidade_percentual": 30.0,
                "adicional_insalubridade_percentual": 10.0,
                "horas_extras_percentual": 50.0,
                "horas_extras_noturnas_percentual": 100.0,
                "jornada_semanal_horas": 44,
            }

    @staticmethod
    def _fallback_feriados(ano: int, mes: int | None) -> list[dict]:
        try:
            from modules.cct.models.holidays import FERIADOS_MANAUS_2026

            result = []
            for f in FERIADOS_MANAUS_2026:
                if f.data.year != ano:
                    continue
                if mes and f.data.month != mes:
                    continue
                result.append(
                    {
                        "id": None,
                        "data_feriado": f.data.isoformat(),
                        "nome": f.nome,
                        "tipo": f.tipo,
                        "ano": ano,
                    }
                )
            return result
        except ImportError:
            return []

    @staticmethod
    def _fallback_adicional_noturno() -> dict:
        return {
            "fonte": "fallback_constante",
            "adicional_noturno_percentual": 20.0,
            "hora_noturna_minutos": 52.5,
            "periodo_noturno_inicio": "22:00",
            "periodo_noturno_fim": "05:00",
            "base_calculo": "hora_normal",
            "observacao": (
                "Adicional noturno 20% sobre hora normal. "
                "Hora noturna reduzida para 52min30s (periodo 22h-05h), conforme CCT 2026."
            ),
        }

    @staticmethod
    def _fallback_beneficios(salario: float) -> list[dict]:
        try:
            from modules.cct.models.benefits import BENEFICIOS_OBRIGATORIOS_CCT

            resultado = []
            for b in BENEFICIOS_OBRIGATORIOS_CCT:
                desconto_calc = None
                if b.desconto_percentual and salario > 0:
                    desconto_calc = round(salario * float(b.desconto_percentual) / 100, 2)

                resultado.append(
                    {
                        "tipo_beneficio": b.tipo.value,
                        "obrigatorio": b.obrigatorio,
                        "valor_minimo_cct": float(b.valor_total) if b.valor_total else None,
                        "valor_empresa_cct": float(b.valor_empresa) if b.valor_empresa else None,
                        "desconto_maximo_cct": (
                            float(b.desconto_maximo_empregado) if b.desconto_maximo_empregado else None
                        ),
                        "desconto_percentual_cct": (float(b.desconto_percentual) if b.desconto_percentual else None),
                        "desconto_calculado": desconto_calc,
                        "observacao": b.observacao,
                    }
                )
            return resultado
        except ImportError:
            return []

    async def invalidar_cache(self) -> None:
        """Invalida todo o cache CCT no Redis."""
        try:
            from core.cache.redis import cache_clear_pattern

            await cache_clear_pattern("cct:*")
        except Exception:
            pass
