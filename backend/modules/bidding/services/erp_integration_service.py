"""
Service de Integracao ERP - Licitacoes
======================================
Bridge: Licitacao -> Contrato Operacional -> Financeiro

Converte contratos publicos (bidding) em entidades operacionais
(postos, alocacoes) e gera medicoes/faturas para o financeiro.
"""

import logging
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from modules.bidding.models.measurement import Measurement, MeasurementStatus, MeasurementType
from modules.bidding.models.public_contract import ContractStatus, PublicContract
from modules.operacional.models.allocation import Allocation, AllocationStatus
from modules.operacional.models.post import Post, PostStatus, PostType, ShiftType

logger = logging.getLogger(__name__)


class ERPIntegrationService:
    """
    Service de integracao ERP para o modulo de licitacoes.

    Responsavel por:
    - Converter contratos publicos em entidades operacionais (postos/alocacoes)
    - Gerar medicoes baseadas em alocacoes e horas trabalhadas
    - Gerar faturas a partir de medicoes aprovadas
    - Consultar status de integracao entre modulos
    """

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------ #
    #  1. Converter contrato publico -> entidades operacionais           #
    # ------------------------------------------------------------------ #

    async def converter_para_contrato_operacional(
        self,
        contract_id: UUID,
        postos_config: list[dict] | None = None,
        user_id: UUID | None = None,
    ) -> dict:
        """
        Converte um contrato publico (bidding) em entidades operacionais.

        Cria postos de trabalho e (opcionalmente) alocacoes iniciais
        vinculados ao contrato de licitacao.

        Args:
            contract_id: ID do contrato publico (bidding_public_contracts)
            postos_config: Lista de configuracoes de postos a criar.
                Cada item: {
                    "name": str,
                    "post_type": str (PostType value),
                    "shift_type": str (ShiftType value),
                    "headcount": int,
                    "address": str | None,
                    "city": str | None,
                    "state": str | None,
                    "hourly_rate": float | None,
                    "monthly_cost": float | None,
                    "requires_armed": bool,
                }
                Se None, cria um posto generico baseado no objeto do contrato.
            user_id: ID do usuario que esta realizando a conversao.

        Returns:
            dict com contrato, postos criados e resumo.

        Raises:
            ValueError: Se contrato nao encontrado, inativo ou ja convertido.
        """
        # Busca contrato
        result = await self.db.execute(
            select(PublicContract)
            .options(selectinload(PublicContract.medicoes))
            .where(PublicContract.id == contract_id, PublicContract.ativo)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            raise ValueError(f"Contrato {contract_id} nao encontrado ou inativo")

        if contract.status not in (ContractStatus.ACTIVE.value, ContractStatus.DRAFT.value):
            raise ValueError(
                f"Contrato {contract.numero_contrato}/{contract.ano_contrato} "
                f"com status '{contract.status}' nao pode ser convertido. "
                f"Status permitidos: active, draft"
            )

        # Verifica se ja existem postos vinculados
        existing_posts = await self._get_postos_por_contrato(contract_id)
        if existing_posts:
            raise ValueError(
                f"Contrato {contract.numero_contrato}/{contract.ano_contrato} "
                f"ja possui {len(existing_posts)} posto(s) operacional(is) vinculado(s). "
                f"Use status_integracao() para consultar."
            )

        # Gera codigo sequencial para postos
        code_base = await self._next_post_code()

        # Cria postos
        created_posts = []
        if postos_config:
            for i, cfg in enumerate(postos_config):
                post = await self._criar_posto(
                    contract=contract,
                    code=f"POST-{code_base + i:04d}",
                    config=cfg,
                    user_id=user_id,
                )
                created_posts.append(post)
        else:
            # Posto generico baseado no objeto do contrato
            post = await self._criar_posto(
                contract=contract,
                code=f"POST-{code_base:04d}",
                config={
                    "name": f"Posto - {contract.objeto_resumido or contract.objeto[:80]}",
                    "post_type": PostType.VIGILANTE.value,
                    "shift_type": ShiftType.DIURNO.value,
                    "headcount": 1,
                    "address": None,
                    "city": None,
                    "state": contract.orgao_uf,
                },
                user_id=user_id,
            )
            created_posts.append(post)

        await self.db.commit()

        # Refresh para obter IDs gerados
        for post in created_posts:
            await self.db.refresh(post)

        logger.info(
            "Contrato %s/%s convertido: %d posto(s) criado(s)",
            contract.numero_contrato,
            contract.ano_contrato,
            len(created_posts),
        )

        return {
            "contrato_id": str(contract.id),
            "numero_contrato": contract.numero_contrato,
            "ano_contrato": contract.ano_contrato,
            "orgao_nome": contract.orgao_nome,
            "valor_contrato": float(contract.valor_contrato),
            "vigencia_inicio": contract.data_vigencia_inicio.isoformat(),
            "vigencia_fim": contract.data_vigencia_fim.isoformat(),
            "postos_criados": [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "post_type": p.post_type,
                    "shift_type": p.shift_type,
                    "required_headcount": p.required_headcount,
                    "monthly_cost": p.monthly_cost,
                }
                for p in created_posts
            ],
            "total_postos": len(created_posts),
            "total_headcount": sum(p.required_headcount for p in created_posts),
            "custo_mensal_estimado": sum(p.monthly_cost for p in created_posts),
            "proximos_passos": [
                "Alocar funcionarios nos postos criados",
                "Configurar escalas de trabalho",
                "Gerar primeira medicao apos inicio da vigencia",
            ],
        }

    # ------------------------------------------------------------------ #
    #  2. Gerar medicao para um periodo                                  #
    # ------------------------------------------------------------------ #

    async def gerar_medicao(
        self,
        contract_id: UUID,
        competencia: str,
        periodo_inicio: date,
        periodo_fim: date,
        user_id: UUID | None = None,
    ) -> dict:
        """
        Gera uma medicao para um contrato em um periodo especifico.

        Calcula o valor bruto baseado nos postos/alocacoes ativas e
        horas trabalhadas no periodo.

        Args:
            contract_id: ID do contrato publico.
            competencia: Competencia no formato YYYY-MM.
            periodo_inicio: Data inicio do periodo de medicao.
            periodo_fim: Data fim do periodo de medicao.
            user_id: ID do usuario.

        Returns:
            dict com dados da medicao criada.

        Raises:
            ValueError: Se contrato nao encontrado ou periodo invalido.
        """
        # Busca contrato
        result = await self.db.execute(
            select(PublicContract)
            .options(selectinload(PublicContract.medicoes))
            .where(PublicContract.id == contract_id, PublicContract.ativo)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            raise ValueError(f"Contrato {contract_id} nao encontrado")

        if contract.status != ContractStatus.ACTIVE.value:
            raise ValueError(
                f"Contrato {contract.numero_contrato}/{contract.ano_contrato} "
                f"nao esta ativo (status: {contract.status})"
            )

        if periodo_inicio > periodo_fim:
            raise ValueError("periodo_inicio deve ser anterior a periodo_fim")

        # Verifica se ja existe medicao para esta competencia
        existing = await self.db.execute(
            select(Measurement).where(
                Measurement.contrato_id == contract_id,
                Measurement.competencia == competencia,
                Measurement.ativo,
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(
                f"Ja existe medicao para competencia {competencia} "
                f"no contrato {contract.numero_contrato}/{contract.ano_contrato}"
            )

        # Calcula valor baseado nos postos e alocacoes
        postos = await self._get_postos_por_contrato(contract_id)
        alocacoes = await self._get_alocacoes_ativas_por_contrato(contract_id)

        # Calcula dias uteis no periodo (simplificado: todos os dias)
        dias_periodo = (periodo_fim - periodo_inicio).days + 1

        # Valor bruto: soma do custo mensal dos postos proporcional ao periodo
        valor_bruto = Decimal("0")
        itens_medidos = []

        if postos:
            for post in postos:
                # Proporcional: monthly_cost * (dias_periodo / 30)
                custo_proporcional = Decimal(str(post.monthly_cost)) * Decimal(str(dias_periodo)) / Decimal("30")
                valor_bruto += custo_proporcional

                # Conta alocacoes ativas neste posto
                alocacoes_posto = [a for a in alocacoes if a.post_id == post.id]

                itens_medidos.append(
                    {
                        "descricao": f"{post.name} ({post.code})",
                        "unidade": "mes",
                        "quantidade": str(Decimal(str(dias_periodo)) / Decimal("30")),
                        "valor_unitario": str(Decimal(str(post.monthly_cost))),
                        "valor_total": str(custo_proporcional),
                        "headcount_previsto": post.required_headcount,
                        "headcount_alocado": len(alocacoes_posto),
                    }
                )
        else:
            # Sem postos: usa valor mensal do contrato
            valor_mensal = contract.valor_contrato / Decimal(str(contract.prazo_meses or 12))
            valor_bruto = valor_mensal * Decimal(str(dias_periodo)) / Decimal("30")
            itens_medidos.append(
                {
                    "descricao": f"Servicos - {contract.objeto_resumido or contract.objeto[:80]}",
                    "unidade": "mes",
                    "quantidade": str(Decimal(str(dias_periodo)) / Decimal("30")),
                    "valor_unitario": str(valor_mensal),
                    "valor_total": str(valor_bruto),
                }
            )

        # Proxima numeracao
        numero = len(contract.medicoes or []) + 1

        # Cria medicao
        measurement = Measurement(
            id=uuid4(),
            contrato_id=contract_id,
            numero_medicao=numero,
            competencia=competencia,
            tipo=MeasurementType.MENSAL.value,
            periodo_inicio=periodo_inicio,
            periodo_fim=periodo_fim,
            valor_bruto=valor_bruto,
            valor_retencoes=Decimal("0"),
            valor_glosas=Decimal("0"),
            valor_liquido=valor_bruto,
            status=MeasurementStatus.DRAFT.value,
            itens_medidos=itens_medidos,
            descricao_servicos=(
                f"Medicao #{numero} - {competencia} - {contract.numero_contrato}/{contract.ano_contrato}"
            ),
            created_by=user_id,
        )

        # Calcula retencoes padrao
        measurement.calcular_retencoes()

        self.db.add(measurement)
        await self.db.commit()
        await self.db.refresh(measurement)

        logger.info(
            "Medicao #%d gerada para contrato %s/%s - Competencia %s - Valor bruto: R$ %s",
            numero,
            contract.numero_contrato,
            contract.ano_contrato,
            competencia,
            valor_bruto,
        )

        return {
            "id": str(measurement.id),
            "contrato_id": str(contract_id),
            "numero_contrato": contract.numero_contrato,
            "numero_medicao": measurement.numero_medicao,
            "competencia": measurement.competencia,
            "periodo_inicio": measurement.periodo_inicio.isoformat(),
            "periodo_fim": measurement.periodo_fim.isoformat(),
            "valor_bruto": float(measurement.valor_bruto),
            "valor_retencoes": float(measurement.valor_retencoes),
            "valor_glosas": float(measurement.valor_glosas),
            "valor_liquido": float(measurement.valor_liquido),
            "status": measurement.status,
            "itens_medidos": measurement.itens_medidos,
            "postos_vinculados": len(postos),
            "alocacoes_ativas": len(alocacoes),
        }

    # ------------------------------------------------------------------ #
    #  3. Gerar fatura a partir de medicao                               #
    # ------------------------------------------------------------------ #

    async def gerar_fatura(
        self,
        medicao_id: UUID,
        user_id: UUID | None = None,
    ) -> dict:
        """
        Gera fatura (conta a receber) a partir de uma medicao aprovada.

        TODO: Integrar com modulo financeiro (contas_a_receber).
        TODO: Integrar com NFS-e via government_integrations.

        Args:
            medicao_id: ID da medicao aprovada.
            user_id: ID do usuario.

        Returns:
            dict com dados da fatura gerada (stub).

        Raises:
            ValueError: Se medicao nao encontrada ou nao aprovada.
        """
        # Busca medicao
        result = await self.db.execute(
            select(Measurement).where(
                Measurement.id == medicao_id,
                Measurement.ativo,
            )
        )
        measurement = result.scalar_one_or_none()

        if not measurement:
            raise ValueError(f"Medicao {medicao_id} nao encontrada")

        if not measurement.esta_aprovada:
            raise ValueError(
                f"Medicao #{measurement.numero_medicao} ({measurement.competencia}) "
                f"nao esta aprovada (status: {measurement.status}). "
                f"Aprove a medicao antes de gerar a fatura."
            )

        # Busca contrato para dados complementares
        result = await self.db.execute(select(PublicContract).where(PublicContract.id == measurement.contrato_id))
        contract = result.scalar_one_or_none()

        # TODO: Criar registro em contas_a_receber (modulo financeiro)
        # from modules.financial.services.receivable_service import ReceivableService
        # receivable = await ReceivableService(self.db).create(...)

        # TODO: Disparar geracao de NFS-e via government_integrations
        # from modules.government_integrations.services.nfse_service import NFSeService
        # nfse = await NFSeService(self.db).emitir(...)

        fatura_stub = {
            "id": str(uuid4()),  # ID provisorio
            "status": "pendente_integracao",
            "medicao_id": str(measurement.id),
            "contrato_id": str(measurement.contrato_id),
            "numero_contrato": contract.numero_contrato if contract else None,
            "competencia": measurement.competencia,
            "valor_bruto": float(measurement.valor_bruto),
            "valor_retencoes": float(measurement.valor_retencoes or 0),
            "valor_liquido": float(measurement.valor_liquido),
            "cliente_cnpj": contract.orgao_cnpj if contract else None,
            "cliente_nome": contract.orgao_nome if contract else None,
            "descricao": (
                f"Medicao #{measurement.numero_medicao} - {measurement.competencia} - "
                f"Contrato {contract.numero_contrato}/{contract.ano_contrato}"
                if contract
                else f"Medicao #{measurement.numero_medicao} - {measurement.competencia}"
            ),
            "data_emissao": date.today().isoformat(),
            "data_vencimento": None,  # TODO: calcular baseado em prazo do contrato
            "nota_fiscal": {
                "status": "pendente",
                "numero": None,
                "mensagem": "NFS-e sera gerada apos integracao com modulo fiscal",
            },
            "conta_a_receber": {
                "status": "pendente",
                "id": None,
                "mensagem": "Conta a receber sera criada apos integracao com modulo financeiro",
            },
            "integracao_pendente": True,
            "mensagem": (
                "Fatura gerada em modo stub. Integracao com modulos financeiro e fiscal pendente de implementacao."
            ),
        }

        logger.info(
            "Fatura stub gerada para medicao #%d do contrato %s - Valor: R$ %s",
            measurement.numero_medicao,
            contract.numero_contrato if contract else "N/A",
            measurement.valor_liquido,
        )

        return fatura_stub

    # ------------------------------------------------------------------ #
    #  4. Status de integracao                                           #
    # ------------------------------------------------------------------ #

    async def status_integracao(self, contract_id: UUID) -> dict:
        """
        Retorna o status completo de integracao de um contrato publico.

        Mostra o que ja foi criado em cada modulo (operacional, medicoes,
        faturas) e quais passos estao pendentes.

        Args:
            contract_id: ID do contrato publico.

        Returns:
            dict com status detalhado da integracao.

        Raises:
            ValueError: Se contrato nao encontrado.
        """
        # Busca contrato
        result = await self.db.execute(
            select(PublicContract)
            .options(selectinload(PublicContract.medicoes))
            .where(PublicContract.id == contract_id)
        )
        contract = result.scalar_one_or_none()

        if not contract:
            raise ValueError(f"Contrato {contract_id} nao encontrado")

        # Busca postos operacionais vinculados
        postos = await self._get_postos_por_contrato(contract_id)

        # Busca alocacoes ativas
        alocacoes = await self._get_alocacoes_ativas_por_contrato(contract_id)

        # Medicoes
        medicoes = contract.medicoes or []
        medicoes_por_status = {}
        for m in medicoes:
            medicoes_por_status.setdefault(m.status, []).append(
                {
                    "id": str(m.id),
                    "numero": m.numero_medicao,
                    "competencia": m.competencia,
                    "valor_bruto": float(m.valor_bruto),
                    "valor_liquido": float(m.valor_liquido),
                }
            )

        # Determina etapas concluidas e pendentes
        tem_postos = len(postos) > 0
        tem_alocacoes = len(alocacoes) > 0
        tem_medicoes = len(medicoes) > 0
        tem_medicoes_aprovadas = any(m.esta_aprovada for m in medicoes)

        # Monta headcount info por posto
        postos_info = []
        for post in postos:
            aloc_posto = [a for a in alocacoes if a.post_id == post.id]
            postos_info.append(
                {
                    "id": post.id,
                    "code": post.code,
                    "name": post.name,
                    "post_type": post.post_type,
                    "shift_type": post.shift_type,
                    "status": post.status,
                    "required_headcount": post.required_headcount,
                    "current_headcount": len(aloc_posto),
                    "monthly_cost": post.monthly_cost,
                    "preenchido": len(aloc_posto) >= post.required_headcount,
                }
            )

        total_headcount_necessario = sum(p.required_headcount for p in postos)
        total_headcount_alocado = len(alocacoes)

        etapas = {
            "contrato_licitacao": {
                "concluido": True,
                "detalhes": {
                    "id": str(contract.id),
                    "numero": f"{contract.numero_contrato}/{contract.ano_contrato}",
                    "orgao": contract.orgao_nome,
                    "status": contract.status,
                    "valor": float(contract.valor_contrato),
                    "vigencia_inicio": (
                        contract.data_vigencia_inicio.isoformat() if contract.data_vigencia_inicio else None
                    ),
                    "vigencia_fim": (contract.data_vigencia_fim.isoformat() if contract.data_vigencia_fim else None),
                },
            },
            "postos_operacionais": {
                "concluido": tem_postos,
                "quantidade": len(postos),
                "detalhes": postos_info,
            },
            "alocacoes": {
                "concluido": tem_alocacoes,
                "total_necessario": total_headcount_necessario,
                "total_alocado": total_headcount_alocado,
                "percentual_preenchimento": (
                    round(total_headcount_alocado / total_headcount_necessario * 100, 1)
                    if total_headcount_necessario > 0
                    else 0
                ),
            },
            "medicoes": {
                "concluido": tem_medicoes,
                "total": len(medicoes),
                "por_status": medicoes_por_status,
                "valor_total_bruto": sum(float(m.valor_bruto) for m in medicoes),
                "valor_total_liquido": sum(float(m.valor_liquido) for m in medicoes),
            },
            "faturas": {
                "concluido": False,
                "mensagem": "Integracao com modulo financeiro pendente de implementacao",
                "medicoes_aptas": sum(1 for m in medicoes if m.esta_aprovada),
            },
            "nfse": {
                "concluido": False,
                "mensagem": "Integracao com NFS-e pendente de implementacao",
            },
        }

        # Calcula progresso geral
        etapas_total = 6
        etapas_concluidas = sum(1 for e in etapas.values() if e.get("concluido", False))

        # Pendencias
        pendencias = []
        if not tem_postos:
            pendencias.append("Criar postos operacionais (converter contrato)")
        if tem_postos and not tem_alocacoes:
            pendencias.append("Alocar funcionarios nos postos")
        if tem_postos and total_headcount_alocado < total_headcount_necessario:
            vagas = total_headcount_necessario - total_headcount_alocado
            pendencias.append(f"Preencher {vagas} vaga(s) nos postos")
        if not tem_medicoes:
            pendencias.append("Gerar primeira medicao")
        if tem_medicoes and not tem_medicoes_aprovadas:
            pendencias.append("Aprovar medicoes pendentes")
        if tem_medicoes_aprovadas:
            pendencias.append("Gerar faturas para medicoes aprovadas (integracao financeira)")
        pendencias.append("Configurar emissao de NFS-e (integracao fiscal)")

        return {
            "contrato_id": str(contract.id),
            "numero_contrato": f"{contract.numero_contrato}/{contract.ano_contrato}",
            "orgao": contract.orgao_nome,
            "progresso": {
                "etapas_concluidas": etapas_concluidas,
                "etapas_total": etapas_total,
                "percentual": round(etapas_concluidas / etapas_total * 100, 1),
            },
            "etapas": etapas,
            "pendencias": pendencias,
        }

    # ------------------------------------------------------------------ #
    #  Metodos auxiliares (privados)                                      #
    # ------------------------------------------------------------------ #

    async def _get_postos_por_contrato(self, contract_id: UUID) -> list[Post]:
        """Busca postos operacionais vinculados a um contrato."""
        result = await self.db.execute(
            select(Post).where(
                Post.contract_id == str(contract_id),
                Post.is_active,
            )
        )
        return list(result.scalars().all())

    async def _get_alocacoes_ativas_por_contrato(self, contract_id: UUID) -> list[Allocation]:
        """Busca alocacoes ativas nos postos de um contrato."""
        result = await self.db.execute(
            select(Allocation)
            .join(Post, Allocation.post_id == Post.id)
            .where(
                Post.contract_id == str(contract_id),
                Post.is_active,
                Allocation.status == AllocationStatus.ACTIVE.value,
                Allocation.is_active,
            )
        )
        return list(result.scalars().all())

    async def _next_post_code(self) -> int:
        """Retorna proximo numero sequencial para codigo de posto."""
        result = await self.db.execute(select(func.count(Post.id)))
        count = result.scalar() or 0
        return count + 1

    async def _criar_posto(
        self,
        contract: PublicContract,
        code: str,
        config: dict,
        user_id: UUID | None = None,
    ) -> Post:
        """Cria um posto de trabalho vinculado ao contrato."""
        post = Post(
            id=str(uuid4()),
            code=code,
            name=config.get("name", f"Posto {code}"),
            description=(
                f"Posto criado a partir do contrato "
                f"{contract.numero_contrato}/{contract.ano_contrato} - "
                f"{contract.orgao_nome}"
            ),
            post_type=config.get("post_type", PostType.VIGILANTE.value),
            status=PostStatus.ACTIVE.value,
            shift_type=config.get("shift_type", ShiftType.DIURNO.value),
            contract_id=str(contract.id),
            client_id=None,
            address=config.get("address"),
            city=config.get("city"),
            state=config.get("state", contract.orgao_uf),
            required_headcount=config.get("headcount", 1),
            current_headcount=0,
            hourly_rate=config.get("hourly_rate", 0.0),
            monthly_cost=config.get("monthly_cost", 0.0),
            requires_armed=config.get("requires_armed", False),
            requires_vehicle=config.get("requires_vehicle", False),
            notes=(
                f"Origem: Licitacao - Contrato {contract.numero_contrato}/{contract.ano_contrato} | "
                f"Orgao: {contract.orgao_nome} | "
                f"Vigencia: {contract.data_vigencia_inicio} a {contract.data_vigencia_fim}"
            ),
            created_by=str(user_id) if user_id else None,
        )

        self.db.add(post)
        return post
