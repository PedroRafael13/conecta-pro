"""
Repository CCT — acesso a dados com cache Redis.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.cache.redis import cache_delete, cache_get, cache_set
from core.logging import logger
from modules.people_management.cct.models.cct_models import (
    CCTBeneficio,
    CCTCargo,
    CCTConvencao,
    CCTFeriado,
)

# TTL padrão para dados CCT (dados quase estáticos — 24h)
CACHE_TTL_CCT = 86400


class CCTRepository:
    """Repositório de dados CCT com cache Redis transparente."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # =========================================================================
    # CONSULTAS DE LEITURA
    # =========================================================================

    async def get_convencao_vigente(self) -> CCTConvencao | None:
        """Retorna a convenção coletiva vigente (is_vigente=True)."""
        cache_key = "cct:convencao_vigente"
        cached = await cache_get(cache_key)
        if cached:
            logger.debug("Cache HIT: %s", cache_key)
            return None  # caller usa cached dict diretamente quando serializado

        result = await self.db.execute(
            select(CCTConvencao).where(
                CCTConvencao.is_vigente.is_(True),
                CCTConvencao.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def get_convencao_vigente_cached(self) -> dict | None:
        """Retorna convenção vigente como dict, com cache Redis."""
        cache_key = "cct:convencao_vigente"
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: %s", cache_key)
            return cached

        result = await self.db.execute(
            select(CCTConvencao).where(
                CCTConvencao.is_vigente.is_(True),
                CCTConvencao.is_active.is_(True),
            )
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return None

        data = {
            "id": str(conv.id),
            "sindicato_trabalhadores": conv.sindicato_trabalhadores,
            "sindicato_patronal": conv.sindicato_patronal,
            "registro_mte": conv.registro_mte,
            "data_inicio": str(conv.data_inicio),
            "data_fim": str(conv.data_fim),
            "data_base": conv.data_base,
            "municipio": conv.municipio,
            "uf": conv.uf,
            "descricao": conv.descricao,
            "is_vigente": conv.is_vigente,
        }
        await cache_set(cache_key, data, CACHE_TTL_CCT)
        return data

    async def get_convencao_by_id(self, convencao_id: uuid.UUID) -> CCTConvencao | None:
        """Retorna convenção por ID."""
        result = await self.db.execute(select(CCTConvencao).where(CCTConvencao.id == convencao_id))
        return result.scalar_one_or_none()

    async def list_convencoes(self) -> list[CCTConvencao]:
        """Lista todas as convenções."""
        result = await self.db.execute(select(CCTConvencao).order_by(CCTConvencao.data_inicio.desc()))
        return list(result.scalars().all())

    async def get_cargos_by_convencao(self, convencao_id: uuid.UUID) -> list[CCTCargo]:
        """Retorna todos os cargos de uma convenção, com cache."""
        cache_key = f"cct:cargos:{convencao_id}"
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: %s", cache_key)
            # cached é lista de dicts — retornamos como-está para uso direto
            return cached  # type: ignore[return-value]

        result = await self.db.execute(
            select(CCTCargo)
            .where(
                CCTCargo.convencao_id == convencao_id,
                CCTCargo.is_active.is_(True),
            )
            .order_by(CCTCargo.cargo_nome)
        )
        cargos = list(result.scalars().all())

        data = [
            {
                "id": str(c.id),
                "cargo_nome": c.cargo_nome,
                "piso_salarial": float(c.piso_salarial),
                "adicional_tipo": c.adicional_tipo,
                "adicional_noturno_percentual": float(c.adicional_noturno_percentual),
                "adicional_periculosidade_percentual": float(c.adicional_periculosidade_percentual),
                "adicional_insalubridade_percentual": float(c.adicional_insalubridade_percentual),
                "horas_extras_percentual": float(c.horas_extras_percentual),
                "horas_extras_noturnas_percentual": float(c.horas_extras_noturnas_percentual),
                "jornada_semanal_horas": c.jornada_semanal_horas,
            }
            for c in cargos
        ]
        await cache_set(cache_key, data, CACHE_TTL_CCT)
        return data  # type: ignore[return-value]

    async def get_cargo_by_nome(self, convencao_id: uuid.UUID, cargo_nome: str) -> CCTCargo | None:
        """Busca cargo por nome (case-insensitive)."""
        result = await self.db.execute(
            select(CCTCargo).where(
                CCTCargo.convencao_id == convencao_id,
                CCTCargo.is_active.is_(True),
            )
        )
        cargo_upper = cargo_nome.strip().upper()
        for cargo in result.scalars().all():
            if cargo.cargo_nome.upper() == cargo_upper:
                return cargo
        return None

    async def get_cargo_by_nome_cached(self, convencao_id: uuid.UUID, cargo_nome: str) -> dict | None:
        """Busca cargo por nome com cache."""
        cache_key = f"cct:cargo:{convencao_id}:{cargo_nome.strip().upper()}"
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: %s", cache_key)
            return cached

        cargo = await self.get_cargo_by_nome(convencao_id, cargo_nome)
        if not cargo:
            return None

        data = {
            "id": str(cargo.id),
            "cargo_nome": cargo.cargo_nome,
            "piso_salarial": float(cargo.piso_salarial),
            "adicional_tipo": cargo.adicional_tipo,
            "adicional_noturno_percentual": float(cargo.adicional_noturno_percentual),
            "adicional_periculosidade_percentual": float(cargo.adicional_periculosidade_percentual),
            "adicional_insalubridade_percentual": float(cargo.adicional_insalubridade_percentual),
            "horas_extras_percentual": float(cargo.horas_extras_percentual),
            "horas_extras_noturnas_percentual": float(cargo.horas_extras_noturnas_percentual),
            "jornada_semanal_horas": cargo.jornada_semanal_horas,
        }
        await cache_set(cache_key, data, CACHE_TTL_CCT)
        return data

    async def get_feriados_by_ano(self, convencao_id: uuid.UUID, ano: int) -> list[CCTFeriado]:
        """Retorna feriados de um ano com cache."""
        cache_key = f"cct:feriados:{convencao_id}:{ano}"
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: %s", cache_key)
            return cached  # type: ignore[return-value]

        result = await self.db.execute(
            select(CCTFeriado)
            .where(
                CCTFeriado.convencao_id == convencao_id,
                CCTFeriado.ano == ano,
                CCTFeriado.is_active.is_(True),
            )
            .order_by(CCTFeriado.data_feriado)
        )
        feriados = list(result.scalars().all())

        data = [
            {
                "id": str(f.id),
                "data_feriado": str(f.data_feriado),
                "nome": f.nome,
                "tipo": f.tipo,
                "ano": f.ano,
            }
            for f in feriados
        ]
        await cache_set(cache_key, data, CACHE_TTL_CCT)
        return data  # type: ignore[return-value]

    async def get_feriados_by_mes(self, convencao_id: uuid.UUID, ano: int, mes: int) -> list[dict]:
        """Retorna feriados filtrados por mês."""
        todos = await self.get_feriados_by_ano(convencao_id, ano)
        return [f for f in todos if isinstance(f, dict) and int(f["data_feriado"][5:7]) == mes]

    async def get_beneficios_obrigatorios(self, convencao_id: uuid.UUID) -> list[CCTBeneficio]:
        """Retorna benefícios obrigatórios com cache."""
        cache_key = f"cct:beneficios:{convencao_id}"
        cached = await cache_get(cache_key)
        if cached is not None:
            logger.debug("Cache HIT: %s", cache_key)
            return cached  # type: ignore[return-value]

        result = await self.db.execute(
            select(CCTBeneficio)
            .where(
                CCTBeneficio.convencao_id == convencao_id,
                CCTBeneficio.is_active.is_(True),
            )
            .order_by(CCTBeneficio.obrigatorio.desc(), CCTBeneficio.tipo_beneficio)
        )
        beneficios = list(result.scalars().all())

        data = [
            {
                "id": str(b.id),
                "tipo_beneficio": b.tipo_beneficio,
                "valor_minimo": float(b.valor_minimo) if b.valor_minimo else None,
                "valor_empresa": float(b.valor_empresa) if b.valor_empresa else None,
                "desconto_maximo_percentual": (
                    float(b.desconto_maximo_percentual) if b.desconto_maximo_percentual else None
                ),
                "desconto_percentual_sobre_salario": (
                    float(b.desconto_percentual_sobre_salario) if b.desconto_percentual_sobre_salario else None
                ),
                "obrigatorio": b.obrigatorio,
                "observacao": b.observacao,
            }
            for b in beneficios
        ]
        await cache_set(cache_key, data, CACHE_TTL_CCT)
        return data  # type: ignore[return-value]

    # =========================================================================
    # CRUD ADMIN — CONVENÇÕES
    # =========================================================================

    async def create_convencao(self, data: dict) -> CCTConvencao:
        """Cria nova convenção coletiva."""
        # Desativar is_vigente das anteriores se nova é vigente
        if data.get("is_vigente"):
            await self.db.execute(CCTConvencao.__table__.update().values(is_vigente=False))

        conv = CCTConvencao(**data)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        await self._invalidate_convencao_cache()
        return conv

    async def update_convencao(self, convencao_id: uuid.UUID, data: dict) -> CCTConvencao | None:
        """Atualiza convenção coletiva."""
        conv = await self.get_convencao_by_id(convencao_id)
        if not conv:
            return None

        if data.get("is_vigente") and not conv.is_vigente:
            await self.db.execute(CCTConvencao.__table__.update().values(is_vigente=False))

        for field, value in data.items():
            setattr(conv, field, value)

        await self.db.commit()
        await self.db.refresh(conv)
        await self._invalidate_convencao_cache()
        return conv

    # =========================================================================
    # CRUD ADMIN — CARGOS
    # =========================================================================

    async def create_cargo(self, data: dict) -> CCTCargo:
        """Adiciona cargo a uma convenção."""
        cargo = CCTCargo(**data)
        self.db.add(cargo)
        await self.db.commit()
        await self.db.refresh(cargo)
        await cache_delete(f"cct:cargos:{data['convencao_id']}")
        return cargo

    async def update_cargo(self, cargo_id: uuid.UUID, data: dict) -> CCTCargo | None:
        """Atualiza cargo."""
        result = await self.db.execute(select(CCTCargo).where(CCTCargo.id == cargo_id))
        cargo = result.scalar_one_or_none()
        if not cargo:
            return None

        for field, value in data.items():
            setattr(cargo, field, value)

        await self.db.commit()
        await self.db.refresh(cargo)
        await cache_delete(f"cct:cargos:{cargo.convencao_id}")
        await cache_delete(f"cct:cargo:{cargo.convencao_id}:{cargo.cargo_nome.upper()}")
        return cargo

    async def get_cargo_by_id(self, cargo_id: uuid.UUID) -> CCTCargo | None:
        """Retorna cargo por ID."""
        result = await self.db.execute(select(CCTCargo).where(CCTCargo.id == cargo_id))
        return result.scalar_one_or_none()

    # =========================================================================
    # CRUD ADMIN — FERIADOS
    # =========================================================================

    async def create_feriado(self, data: dict) -> CCTFeriado:
        """Adiciona feriado a uma convenção."""
        feriado = CCTFeriado(**data)
        self.db.add(feriado)
        await self.db.commit()
        await self.db.refresh(feriado)
        await cache_delete(f"cct:feriados:{data['convencao_id']}:{data.get('ano', '')}")
        return feriado

    async def delete_feriado(self, feriado_id: uuid.UUID) -> bool:
        """Remove feriado (soft delete via is_active=False)."""
        result = await self.db.execute(select(CCTFeriado).where(CCTFeriado.id == feriado_id))
        feriado = result.scalar_one_or_none()
        if not feriado:
            return False

        feriado.is_active = False
        await self.db.commit()
        await cache_delete(f"cct:feriados:{feriado.convencao_id}:{feriado.ano}")
        return True

    async def get_feriado_by_id(self, feriado_id: uuid.UUID) -> CCTFeriado | None:
        """Retorna feriado por ID."""
        result = await self.db.execute(select(CCTFeriado).where(CCTFeriado.id == feriado_id))
        return result.scalar_one_or_none()

    # =========================================================================
    # CRUD ADMIN — BENEFÍCIOS
    # =========================================================================

    async def create_beneficio(self, data: dict) -> CCTBeneficio:
        """Adiciona benefício a uma convenção."""
        beneficio = CCTBeneficio(**data)
        self.db.add(beneficio)
        await self.db.commit()
        await self.db.refresh(beneficio)
        await cache_delete(f"cct:beneficios:{data['convencao_id']}")
        return beneficio

    async def get_beneficio_by_id(self, beneficio_id: uuid.UUID) -> CCTBeneficio | None:
        """Retorna benefício por ID."""
        result = await self.db.execute(select(CCTBeneficio).where(CCTBeneficio.id == beneficio_id))
        return result.scalar_one_or_none()

    # =========================================================================
    # HELPERS DE CACHE
    # =========================================================================

    async def _invalidate_convencao_cache(self) -> None:
        """Invalida caches relacionados à convenção vigente."""
        await cache_delete("cct:convencao_vigente")
