"""
CostByTypeService — Custeio detalhado por tipo de serviço.

Fornece cálculo de custos estimados para cada tipo de serviço de segurança
(Portaria, Limpeza, Jardinagem, Segurança Eletrônica, Portaria Remota),
lendo dados reais das tabelas de custo ou caindo back para benchmarks.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.financial.models.custo_posto_portaria import CustoPostoPortaria
from modules.financial.models.custo_posto_limpeza import CustoPostoLimpeza
from modules.financial.models.custo_posto_jardinagem import CustoPostoJardinagem
from modules.financial.models.custo_contrato_seg_eletronica import CustoContratoSegEletronica
from modules.financial.models.custo_contrato_portaria_remota import CustoContratoPortariaRemota

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Benchmarks de custo por tipo (mesmos dados do PricingOptimizerAgent)
# ───────────────────────────────────────────────────────────────────────────────
_BENCHMARKS: dict[str, dict] = {
    "portaria": {
        "label": "Portaria",
        "cor": "#3B82F6",
        "unidade": "posto/mês",
        "custo_base": 8500.0,
        "breakdown": {
            "Salários": 0.45,
            "Encargos": 0.30,
            "Benefícios": 0.10,
            "Uniformes/EPI": 0.05,
            "Equipamentos": 0.04,
            "Supervisão": 0.03,
            "Overhead": 0.03,
        },
        "margem_benchmark_pct": 22.0,
    },
    "limpeza": {
        "label": "Limpeza",
        "cor": "#10B981",
        "unidade": "R$/m²/mês",
        "custo_base": 4.5,
        "breakdown": {
            "Mão de Obra": 0.48,
            "Encargos": 0.28,
            "Benefícios": 0.09,
            "Materiais": 0.08,
            "Equipamentos": 0.04,
            "Supervisão": 0.02,
            "Overhead": 0.01,
        },
        "margem_benchmark_pct": 18.0,
    },
    "jardinagem": {
        "label": "Jardinagem",
        "cor": "#84CC16",
        "unidade": "R$/m²/mês",
        "custo_base": 3.0,
        "breakdown": {
            "Mão de Obra": 0.40,
            "Encargos": 0.25,
            "Benefícios": 0.08,
            "Insumos": 0.12,
            "Equipamentos": 0.08,
            "Combustível": 0.04,
            "Supervisão": 0.02,
            "Overhead": 0.01,
        },
        "margem_benchmark_pct": 25.0,
    },
    "seguranca_eletronica": {
        "label": "Segurança Eletrônica",
        "cor": "#F59E0B",
        "unidade": "R$/câmera/mês",
        "custo_base": 350.0,
        "breakdown": {
            "Monitoramento": 0.30,
            "Operadores": 0.20,
            "Manutenção": 0.15,
            "Conectividade": 0.15,
            "Software": 0.10,
            "Depreciação": 0.07,
            "Overhead": 0.03,
        },
        "margem_benchmark_pct": 35.0,
    },
    "portaria_remota": {
        "label": "Portaria Remota",
        "cor": "#8B5CF6",
        "unidade": "R$/unidade/mês",
        "custo_base": 1200.0,
        "breakdown": {
            "Central Operações": 0.25,
            "Operadores": 0.22,
            "Equipamentos": 0.18,
            "Conectividade": 0.15,
            "Manutenção": 0.10,
            "Backup Presencial": 0.05,
            "Overhead": 0.05,
        },
        "margem_benchmark_pct": 40.0,
    },
}


class CostByTypeService:
    """Serviço de custeio detalhado por tipo de serviço."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ───────────────────────────────────────────────────────────────────────────
    # Calcular custo estimado para um tipo/mês
    # ───────────────────────────────────────────────────────────────────────────

    async def calcular_custo_estimado(
        self,
        tipo: str,
        contrato_id: int | None,
        mes: date,
    ) -> dict[str, Any]:
        """
        Retorna breakdown de custos para um tipo de serviço.
        1. Tenta ler dados reais das tabelas específicas do tipo.
        2. Se não houver dados, usa benchmarks como estimativa.
        """
        tipo = tipo.lower().replace(" ", "_")
        benchmark = _BENCHMARKS.get(tipo)
        if not benchmark:
            return {"erro": f"Tipo de serviço desconhecido: {tipo}"}

        # Tentar dados reais
        real_data = await self._get_real_data(tipo, contrato_id, mes)

        if real_data and real_data.get("custo_total", 0) > 0:
            return {
                "tipo": tipo,
                "label": benchmark["label"],
                "cor": benchmark["cor"],
                "mes": mes.isoformat(),
                "fonte": "real",
                "custo_total": real_data["custo_total"],
                "margem_contratual": real_data.get("margem_contratual", 0),
                "breakdown": real_data.get("breakdown", {}),
                "unidade": benchmark["unidade"],
                "margem_pct": (
                    real_data["margem_contratual"] / (real_data["custo_total"] + real_data["margem_contratual"]) * 100
                    if real_data.get("margem_contratual", 0) > 0 and real_data["custo_total"] > 0
                    else benchmark["margem_benchmark_pct"]
                ),
            }

        # Fallback: benchmark
        custo_base = benchmark["custo_base"]
        breakdown_values = {
            k: round(v * custo_base, 2)
            for k, v in benchmark["breakdown"].items()
        }

        return {
            "tipo": tipo,
            "label": benchmark["label"],
            "cor": benchmark["cor"],
            "mes": mes.isoformat(),
            "fonte": "benchmark",
            "custo_total": custo_base,
            "margem_pct": benchmark["margem_benchmark_pct"],
            "breakdown": breakdown_values,
            "unidade": benchmark["unidade"],
            "aviso": "Baseado em benchmarks de mercado. Registre custos reais para análise precisa.",
        }

    async def _get_real_data(
        self,
        tipo: str,
        contrato_id: int | None,
        mes: date,
    ) -> dict[str, Any] | None:
        """Lê dados reais de custo da tabela correspondente ao tipo."""
        try:
            if tipo == "portaria":
                return await self._get_portaria_data(contrato_id, mes)
            elif tipo == "limpeza":
                return await self._get_limpeza_data(contrato_id, mes)
            elif tipo == "jardinagem":
                return await self._get_jardinagem_data(contrato_id, mes)
            elif tipo == "seguranca_eletronica":
                return await self._get_seg_eletronica_data(contrato_id, mes)
            elif tipo == "portaria_remota":
                return await self._get_portaria_remota_data(contrato_id, mes)
        except Exception as exc:
            logger.warning("Erro ao ler dados reais de custo (%s): %s", tipo, exc)
        return None

    async def _get_portaria_data(self, contrato_id: int | None, mes: date) -> dict | None:
        q = select(CustoPostoPortaria).where(CustoPostoPortaria.mes_referencia == mes)
        if contrato_id:
            q = q.where(CustoPostoPortaria.contrato_id == contrato_id)
        result = (await self.session.execute(q)).scalars().first()
        if not result:
            return None
        return {
            "custo_total": float(result.custo_total or 0),
            "margem_contratual": float(result.margem_contratual or 0),
            "breakdown": {
                "Salários": float(result.custo_salarios or 0),
                "Encargos": float(result.custo_encargos or 0),
                "Benefícios": float(result.custo_beneficios or 0),
                "Adicional Noturno": float(result.custo_adicional_noturno or 0),
                "Horas Extras": float(result.custo_horas_extras or 0),
                "Uniformes/EPI": float(result.custo_uniformes or 0),
                "Equipamentos": float(result.custo_equipamentos or 0),
                "Supervisão": float(result.custo_supervisao or 0),
                "Overhead": float(result.custo_overhead or 0),
            },
        }

    async def _get_limpeza_data(self, contrato_id: int | None, mes: date) -> dict | None:
        q = select(CustoPostoLimpeza).where(CustoPostoLimpeza.mes_referencia == mes)
        if contrato_id:
            q = q.where(CustoPostoLimpeza.contrato_id == contrato_id)
        result = (await self.session.execute(q)).scalars().first()
        if not result:
            return None
        return {
            "custo_total": float(result.custo_total or 0),
            "margem_contratual": float(result.margem_contratual or 0),
            "breakdown": {
                "Mão de Obra": float(result.custo_mao_obra or 0),
                "Encargos": float(result.custo_encargos or 0),
                "Benefícios": float(result.custo_beneficios or 0),
                "Materiais": float(result.custo_materiais or 0),
                "Equipamentos": float(result.custo_equipamentos or 0),
                "Supervisão": float(result.custo_supervisao or 0),
                "Overhead": float(result.custo_overhead or 0),
            },
        }

    async def _get_jardinagem_data(self, contrato_id: int | None, mes: date) -> dict | None:
        q = select(CustoPostoJardinagem).where(CustoPostoJardinagem.mes_referencia == mes)
        if contrato_id:
            q = q.where(CustoPostoJardinagem.contrato_id == contrato_id)
        result = (await self.session.execute(q)).scalars().first()
        if not result:
            return None
        return {
            "custo_total": float(result.custo_total or 0),
            "margem_contratual": float(result.margem_contratual or 0),
            "breakdown": {
                "Mão de Obra": float(result.custo_mao_obra or 0),
                "Encargos": float(result.custo_encargos or 0),
                "Benefícios": float(result.custo_beneficios or 0),
                "Insumos": float(result.custo_insumos or 0),
                "Equipamentos": float(result.custo_equipamentos or 0),
                "Combustível": float(result.custo_combustivel or 0),
                "Supervisão": float(result.custo_supervisao or 0),
                "Overhead": float(result.custo_overhead or 0),
            },
        }

    async def _get_seg_eletronica_data(self, contrato_id: int | None, mes: date) -> dict | None:
        q = select(CustoContratoSegEletronica).where(CustoContratoSegEletronica.mes_referencia == mes)
        if contrato_id:
            q = q.where(CustoContratoSegEletronica.contrato_id == contrato_id)
        result = (await self.session.execute(q)).scalars().first()
        if not result:
            return None
        return {
            "custo_total": float(result.custo_total or 0),
            "margem_contratual": float(result.margem_contratual or 0),
            "breakdown": {
                "Monitoramento": float(result.custo_monitoramento or 0),
                "Operadores": float(result.custo_operadores or 0),
                "Manutenção": float(result.custo_manutencao or 0),
                "Conectividade": float(result.custo_conectividade or 0),
                "Software": float(result.custo_software or 0),
                "Depreciação": float(result.custo_depreciacao or 0),
                "Overhead": float(result.custo_overhead or 0),
            },
        }

    async def _get_portaria_remota_data(self, contrato_id: int | None, mes: date) -> dict | None:
        q = select(CustoContratoPortariaRemota).where(CustoContratoPortariaRemota.mes_referencia == mes)
        if contrato_id:
            q = q.where(CustoContratoPortariaRemota.contrato_id == contrato_id)
        result = (await self.session.execute(q)).scalars().first()
        if not result:
            return None
        return {
            "custo_total": float(result.custo_total or 0),
            "margem_contratual": float(result.margem_contratual or 0),
            "breakdown": {
                "Central Operações": float(result.custo_central or 0),
                "Operadores": float(result.custo_operadores or 0),
                "Equipamentos": float(result.custo_equipamentos or 0),
                "Conectividade": float(result.custo_conectividade or 0),
                "Manutenção": float(result.custo_manutencao or 0),
                "Backup Presencial": float(result.custo_backup_presencial or 0),
                "Overhead": float(result.custo_overhead or 0),
            },
        }

    # ───────────────────────────────────────────────────────────────────────────
    # Listar todos os registros de custo por tipo em um mês
    # ───────────────────────────────────────────────────────────────────────────

    async def listar_custos_por_tipo(
        self,
        tipo: str,
        mes: date,
    ) -> list[dict[str, Any]]:
        """Retorna todos os registros de custo para um tipo em um mês."""
        tipo = tipo.lower().replace(" ", "_")
        try:
            if tipo == "portaria":
                q = select(CustoPostoPortaria).where(CustoPostoPortaria.mes_referencia == mes)
                rows = (await self.session.execute(q)).scalars().all()
                return [r.to_dict() for r in rows]

            elif tipo == "limpeza":
                q = select(CustoPostoLimpeza).where(CustoPostoLimpeza.mes_referencia == mes)
                rows = (await self.session.execute(q)).scalars().all()
                return [r.to_dict() for r in rows]

            elif tipo == "jardinagem":
                q = select(CustoPostoJardinagem).where(CustoPostoJardinagem.mes_referencia == mes)
                rows = (await self.session.execute(q)).scalars().all()
                return [r.to_dict() for r in rows]

            elif tipo == "seguranca_eletronica":
                q = select(CustoContratoSegEletronica).where(CustoContratoSegEletronica.mes_referencia == mes)
                rows = (await self.session.execute(q)).scalars().all()
                return [r.to_dict() for r in rows]

            elif tipo == "portaria_remota":
                q = select(CustoContratoPortariaRemota).where(CustoContratoPortariaRemota.mes_referencia == mes)
                rows = (await self.session.execute(q)).scalars().all()
                return [r.to_dict() for r in rows]

        except Exception as exc:
            logger.warning("Erro ao listar custos por tipo (%s): %s", tipo, exc)

        return []

    # ───────────────────────────────────────────────────────────────────────────
    # Resumo de margem por tipo para o mês
    # ───────────────────────────────────────────────────────────────────────────

    async def get_resumo_margem_por_tipo(self, mes: date) -> list[dict[str, Any]]:
        """
        Retorna resumo de margem por tipo de serviço para o mês informado.
        Usa dados reais quando disponíveis; caso contrário usa benchmarks.
        """
        resumo = []
        for tipo, benchmark in _BENCHMARKS.items():
            custo_real = 0.0
            margem_real = 0.0
            tem_dados = False

            try:
                if tipo == "portaria":
                    q = select(
                        func.coalesce(func.sum(CustoPostoPortaria.custo_total), 0),
                        func.coalesce(func.sum(CustoPostoPortaria.margem_contratual), 0),
                    ).where(CustoPostoPortaria.mes_referencia == mes)
                    row = (await self.session.execute(q)).one()
                    custo_real, margem_real = float(row[0]), float(row[1])
                    tem_dados = custo_real > 0

                elif tipo == "limpeza":
                    q = select(
                        func.coalesce(func.sum(CustoPostoLimpeza.custo_total), 0),
                        func.coalesce(func.sum(CustoPostoLimpeza.margem_contratual), 0),
                    ).where(CustoPostoLimpeza.mes_referencia == mes)
                    row = (await self.session.execute(q)).one()
                    custo_real, margem_real = float(row[0]), float(row[1])
                    tem_dados = custo_real > 0

                elif tipo == "jardinagem":
                    q = select(
                        func.coalesce(func.sum(CustoPostoJardinagem.custo_total), 0),
                        func.coalesce(func.sum(CustoPostoJardinagem.margem_contratual), 0),
                    ).where(CustoPostoJardinagem.mes_referencia == mes)
                    row = (await self.session.execute(q)).one()
                    custo_real, margem_real = float(row[0]), float(row[1])
                    tem_dados = custo_real > 0

                elif tipo == "seguranca_eletronica":
                    q = select(
                        func.coalesce(func.sum(CustoContratoSegEletronica.custo_total), 0),
                        func.coalesce(func.sum(CustoContratoSegEletronica.margem_contratual), 0),
                    ).where(CustoContratoSegEletronica.mes_referencia == mes)
                    row = (await self.session.execute(q)).one()
                    custo_real, margem_real = float(row[0]), float(row[1])
                    tem_dados = custo_real > 0

                elif tipo == "portaria_remota":
                    q = select(
                        func.coalesce(func.sum(CustoContratoPortariaRemota.custo_total), 0),
                        func.coalesce(func.sum(CustoContratoPortariaRemota.margem_contratual), 0),
                    ).where(CustoContratoPortariaRemota.mes_referencia == mes)
                    row = (await self.session.execute(q)).one()
                    custo_real, margem_real = float(row[0]), float(row[1])
                    tem_dados = custo_real > 0

            except Exception as exc:
                logger.warning("Erro ao calcular resumo margem (%s): %s", tipo, exc)

            if tem_dados:
                receita_total = custo_real + margem_real
                margem_pct = (margem_real / receita_total * 100) if receita_total > 0 else 0.0
                resumo.append({
                    "tipo": tipo,
                    "label": benchmark["label"],
                    "cor": benchmark["cor"],
                    "custo_total": custo_real,
                    "margem_contratual": margem_real,
                    "margem_pct": round(margem_pct, 1),
                    "fonte": "real",
                })
            else:
                resumo.append({
                    "tipo": tipo,
                    "label": benchmark["label"],
                    "cor": benchmark["cor"],
                    "custo_total": 0.0,
                    "margem_contratual": 0.0,
                    "margem_pct": benchmark["margem_benchmark_pct"],
                    "fonte": "benchmark",
                })

        return resumo

    # ───────────────────────────────────────────────────────────────────────────
    # Registrar custo
    # ───────────────────────────────────────────────────────────────────────────

    async def registrar_custo(
        self,
        tipo: str,
        contrato_id: int | None,
        mes: date,
        custo_total: float,
        margem_contratual: float,
        breakdown: dict[str, float],
    ) -> dict[str, Any]:
        """Cria um registro de custo na tabela correspondente ao tipo."""
        tipo = tipo.lower().replace(" ", "_")

        try:
            if tipo == "portaria":
                record = CustoPostoPortaria(
                    contrato_id=contrato_id,
                    mes_referencia=mes,
                    custo_total=Decimal(str(custo_total)),
                    margem_contratual=Decimal(str(margem_contratual)),
                    custo_salarios=Decimal(str(breakdown.get("Salários", 0))),
                    custo_encargos=Decimal(str(breakdown.get("Encargos", 0))),
                    custo_beneficios=Decimal(str(breakdown.get("Benefícios", 0))),
                    custo_adicional_noturno=Decimal(str(breakdown.get("Adicional Noturno", 0))),
                    custo_horas_extras=Decimal(str(breakdown.get("Horas Extras", 0))),
                    custo_uniformes=Decimal(str(breakdown.get("Uniformes/EPI", 0))),
                    custo_equipamentos=Decimal(str(breakdown.get("Equipamentos", 0))),
                    custo_supervisao=Decimal(str(breakdown.get("Supervisão", 0))),
                    custo_overhead=Decimal(str(breakdown.get("Overhead", 0))),
                )

            elif tipo == "limpeza":
                record = CustoPostoLimpeza(
                    contrato_id=contrato_id,
                    mes_referencia=mes,
                    custo_total=Decimal(str(custo_total)),
                    margem_contratual=Decimal(str(margem_contratual)),
                    custo_mao_obra=Decimal(str(breakdown.get("Mão de Obra", 0))),
                    custo_encargos=Decimal(str(breakdown.get("Encargos", 0))),
                    custo_beneficios=Decimal(str(breakdown.get("Benefícios", 0))),
                    custo_materiais=Decimal(str(breakdown.get("Materiais", 0))),
                    custo_equipamentos=Decimal(str(breakdown.get("Equipamentos", 0))),
                    custo_supervisao=Decimal(str(breakdown.get("Supervisão", 0))),
                    custo_overhead=Decimal(str(breakdown.get("Overhead", 0))),
                )

            elif tipo == "jardinagem":
                record = CustoPostoJardinagem(
                    contrato_id=contrato_id,
                    mes_referencia=mes,
                    custo_total=Decimal(str(custo_total)),
                    margem_contratual=Decimal(str(margem_contratual)),
                    custo_mao_obra=Decimal(str(breakdown.get("Mão de Obra", 0))),
                    custo_encargos=Decimal(str(breakdown.get("Encargos", 0))),
                    custo_beneficios=Decimal(str(breakdown.get("Benefícios", 0))),
                    custo_insumos=Decimal(str(breakdown.get("Insumos", 0))),
                    custo_equipamentos=Decimal(str(breakdown.get("Equipamentos", 0))),
                    custo_combustivel=Decimal(str(breakdown.get("Combustível", 0))),
                    custo_supervisao=Decimal(str(breakdown.get("Supervisão", 0))),
                    custo_overhead=Decimal(str(breakdown.get("Overhead", 0))),
                )

            elif tipo == "seguranca_eletronica":
                record = CustoContratoSegEletronica(
                    contrato_id=contrato_id,
                    mes_referencia=mes,
                    custo_total=Decimal(str(custo_total)),
                    margem_contratual=Decimal(str(margem_contratual)),
                    custo_monitoramento=Decimal(str(breakdown.get("Monitoramento", 0))),
                    custo_operadores=Decimal(str(breakdown.get("Operadores", 0))),
                    custo_manutencao=Decimal(str(breakdown.get("Manutenção", 0))),
                    custo_conectividade=Decimal(str(breakdown.get("Conectividade", 0))),
                    custo_software=Decimal(str(breakdown.get("Software", 0))),
                    custo_depreciacao=Decimal(str(breakdown.get("Depreciação", 0))),
                    custo_overhead=Decimal(str(breakdown.get("Overhead", 0))),
                )

            elif tipo == "portaria_remota":
                record = CustoContratoPortariaRemota(
                    contrato_id=contrato_id,
                    mes_referencia=mes,
                    custo_total=Decimal(str(custo_total)),
                    margem_contratual=Decimal(str(margem_contratual)),
                    custo_central=Decimal(str(breakdown.get("Central Operações", 0))),
                    custo_operadores=Decimal(str(breakdown.get("Operadores", 0))),
                    custo_equipamentos=Decimal(str(breakdown.get("Equipamentos", 0))),
                    custo_conectividade=Decimal(str(breakdown.get("Conectividade", 0))),
                    custo_manutencao=Decimal(str(breakdown.get("Manutenção", 0))),
                    custo_backup_presencial=Decimal(str(breakdown.get("Backup Presencial", 0))),
                    custo_overhead=Decimal(str(breakdown.get("Overhead", 0))),
                )

            else:
                return {"erro": f"Tipo desconhecido: {tipo}"}

            self.session.add(record)
            await self.session.commit()
            await self.session.refresh(record)
            return {"ok": True, "id": str(record.id), "tipo": tipo}

        except Exception as exc:
            await self.session.rollback()
            logger.error("Erro ao registrar custo (%s): %s", tipo, exc)
            return {"erro": str(exc)}
