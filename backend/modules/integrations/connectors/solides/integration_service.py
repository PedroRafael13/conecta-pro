"""
SolidesIntegrationService - Sincroniza Solides DP com Funcionarios Conecta PRO.
Sprint 33: Integration Framework

Este servico implementa a sincronizacao de funcionarios entre o Solides DP
e a base de dados do Conecta PRO, incluindo:
- Mapeamento de campos entre sistemas
- Upsert baseado em CPF ou solides_id
- Tratamento de conflitos
- Auditoria de sincronizacao
"""

import logging
from datetime import date, datetime
from enum import StrEnum
from typing import Any, TypedDict
from uuid import UUID, uuid4

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from modules.integrations.connectors.solides.mappers import (
    compute_solides_entity_hash,
    detect_changes,
    solides_colaborador_to_employee,
)
from modules.integrations.connectors.solides.models import (
    SolidesEntityMapping,
    SyncSource,
    create_or_update_mapping,
    get_entity_mapping,
)

logger = logging.getLogger(__name__)


class SyncAction(StrEnum):
    """Acoes possiveis durante sincronizacao."""

    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncEmployeeResult(TypedDict):
    """Resultado da sincronizacao de um funcionario."""

    action: str
    funcionario_id: str | None
    solides_id: str
    cpf: str | None
    name: str
    changes: dict[str, Any] | None
    error: str | None


class SyncSummary(TypedDict):
    """Resumo da sincronizacao."""

    total_processed: int
    created: int
    updated: int
    skipped: int
    conflicts: int
    errors: int
    duration_seconds: float
    details: list[SyncEmployeeResult]


class SolidesIntegrationService:
    """
    Servico de integracao Solides <-> Conecta PRO.

    Responsavel por sincronizar dados de funcionarios do Solides DP
    para a tabela de funcionarios do Conecta PRO.

    Attributes:
        db: Sessao async do banco de dados
        condominio_id: ID do condominio para sincronizacao

    Example:
        >>> async with AsyncSession(engine) as db:
        ...     service = SolidesIntegrationService(db, condominio_id)
        ...     result = await service.sync_all_employees(employees_data)
        ...     print(f"Sincronizados: {result['created'] + result['updated']}")
    """

    # Mapeamento de campos Solides -> Funcionario Conecta PRO
    FIELD_MAPPING = {
        # Dados pessoais
        "nome": "nome_completo",
        "email": "email",
        "cpf": "cpf",
        "rg": "rg",
        "data_nascimento": "data_nascimento",
        "sexo": "genero",
        "estado_civil": "estado_civil",
        "telefone": "telefone",
        "celular": "celular",
        # Endereco
        "endereco.logradouro": "endereco_logradouro",
        "endereco.numero": "endereco_numero",
        "endereco.complemento": "endereco_complemento",
        "endereco.bairro": "endereco_bairro",
        "endereco.cidade": "endereco_cidade",
        "endereco.estado": "endereco_uf",
        "endereco.cep": "endereco_cep",
        # Dados profissionais
        "matricula": "matricula",
        "cargo.nome": "cargo_nome",
        "departamento.nome": "departamento_nome",
        "gestor_nome": "gestor_nome",
        "data_admissao": "data_admissao",
        "data_demissao": "data_demissao",
        "tipo_contrato": "tipo_contrato",
        "regime_trabalho": "regime_trabalho",
        "jornada_trabalho": "jornada_trabalho",
        "salario": "salario_base",
        # Documentos
        "ctps_numero": "ctps_numero",
        "ctps_serie": "ctps_serie",
        "ctps_uf": "ctps_uf",
        "pis": "pis",
        "titulo_eleitor": "titulo_eleitor",
        "certificado_reservista": "certificado_reservista",
        # Metadados
        "foto_url": "foto_url",
        "situacao": "status",
    }

    # Campos obrigatorios para criar funcionario
    REQUIRED_FIELDS = ["nome", "cpf"]

    def __init__(self, db: AsyncSession, condominio_id: UUID) -> None:
        """
        Inicializa o servico de integracao.

        Args:
            db: Sessao async do SQLAlchemy
            condominio_id: UUID do condominio para sincronizacao
        """
        self.db = db
        self.condominio_id = condominio_id
        self._stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "conflicts": 0,
            "errors": 0,
        }

    async def sync_employee(self, solides_data: dict[str, Any], force_update: bool = False) -> SyncEmployeeResult:
        """
        Sincroniza um funcionario do Solides para Conecta PRO.

        Realiza upsert baseado em:
        1. solides_id (se existir mapeamento)
        2. CPF (identificador unico)

        Args:
            solides_data: Dados do colaborador do Solides
            force_update: Se True, atualiza mesmo sem mudancas detectadas

        Returns:
            SyncEmployeeResult com detalhes da sincronizacao

        Raises:
            ValueError: Se dados obrigatorios estiverem ausentes
        """
        solides_id = str(solides_data.get("id", ""))
        cpf = self._clean_cpf(solides_data.get("cpf"))
        nome = solides_data.get("nome", "Desconhecido")

        logger.debug(f"[SolidesIntegration] Sincronizando funcionario: solides_id={solides_id}, cpf={cpf}, nome={nome}")

        # Validar dados obrigatorios
        if not solides_data.get("nome"):
            logger.warning(f"[SolidesIntegration] Funcionario sem nome: {solides_id}")
            return SyncEmployeeResult(
                action=SyncAction.ERROR.value,
                funcionario_id=None,
                solides_id=solides_id,
                cpf=cpf,
                name=nome,
                changes=None,
                error="Campo obrigatorio 'nome' ausente",
            )

        if not cpf:
            logger.warning(f"[SolidesIntegration] Funcionario sem CPF: {nome}")
            return SyncEmployeeResult(
                action=SyncAction.ERROR.value,
                funcionario_id=None,
                solides_id=solides_id,
                cpf=None,
                name=nome,
                changes=None,
                error="Campo obrigatorio 'cpf' ausente",
            )

        try:
            # Buscar funcionario existente
            funcionario = await self._find_existing_employee(solides_id, cpf)

            if funcionario:
                # Atualizar existente
                return await self._update_employee(funcionario, solides_data, force_update)
            else:
                # Criar novo
                return await self._create_employee(solides_data)

        except Exception as e:
            logger.error(f"[SolidesIntegration] Erro sincronizando {nome}: {e}", exc_info=True)
            return SyncEmployeeResult(
                action=SyncAction.ERROR.value,
                funcionario_id=None,
                solides_id=solides_id,
                cpf=cpf,
                name=nome,
                changes=None,
                error=str(e),
            )

    async def sync_all_employees(self, employees: list[dict[str, Any]], batch_size: int = 50) -> SyncSummary:
        """
        Sincroniza todos os funcionarios em lote.

        Processa funcionarios em batches para melhor performance
        e controle de transacoes.

        Args:
            employees: Lista de dados de colaboradores do Solides
            batch_size: Tamanho do lote para commit

        Returns:
            SyncSummary com estatisticas da sincronizacao
        """
        start_time = datetime.utcnow()
        results: list[SyncEmployeeResult] = []

        total = len(employees)
        logger.info(
            f"[SolidesIntegration] Iniciando sincronizacao de {total} funcionarios para condominio {self.condominio_id}"
        )

        # Reset stats
        self._stats = {
            "created": 0,
            "updated": 0,
            "skipped": 0,
            "conflicts": 0,
            "errors": 0,
        }

        for i, employee_data in enumerate(employees, 1):
            result = await self.sync_employee(employee_data)
            results.append(result)

            # Atualizar estatisticas
            action = result["action"]
            if action in self._stats:
                self._stats[action] += 1

            # Commit em batches
            if i % batch_size == 0:
                await self.db.commit()
                logger.debug(f"[SolidesIntegration] Processados {i}/{total} funcionarios")

        # Commit final
        await self.db.commit()

        duration = (datetime.utcnow() - start_time).total_seconds()

        logger.info(
            f"[SolidesIntegration] Sincronizacao concluida em {duration:.2f}s: "
            f"criados={self._stats['created']}, "
            f"atualizados={self._stats['updated']}, "
            f"pulados={self._stats['skipped']}, "
            f"erros={self._stats['errors']}"
        )

        return SyncSummary(
            total_processed=total,
            created=self._stats["created"],
            updated=self._stats["updated"],
            skipped=self._stats["skipped"],
            conflicts=self._stats["conflicts"],
            errors=self._stats["errors"],
            duration_seconds=duration,
            details=results,
        )

    async def get_sync_status(self) -> dict[str, Any]:
        """
        Retorna status da sincronizacao de funcionarios.

        Consulta informacoes sobre:
        - Total de funcionarios sincronizados
        - Ultima sincronizacao
        - Funcionarios com pendencias

        Returns:
            Dict com informacoes de status
        """
        # Contar mapeamentos ativos
        stmt = select(SolidesEntityMapping).where(
            and_(
                SolidesEntityMapping.condominio_id == self.condominio_id,
                SolidesEntityMapping.entity_type == "colaboradores",
                SolidesEntityMapping.is_active,
            )
        )
        result = await self.db.execute(stmt)
        mappings = result.scalars().all()

        total_synced = len(mappings)
        last_sync = None

        if mappings:
            last_sync = max((m.last_synced_at for m in mappings if m.last_synced_at), default=None)

        # Contar funcionarios locais sem mapeamento
        # (implementar conforme modelo Funcionario existir)
        orphan_count = 0

        return {
            "condominio_id": str(self.condominio_id),
            "entity_type": "funcionarios",
            "total_synced": total_synced,
            "last_sync_at": last_sync.isoformat() if last_sync else None,
            "orphan_records": orphan_count,
            "sync_source": "solides",
            "mapping_stats": {
                "active": sum(1 for m in mappings if m.is_active),
                "inactive": sum(1 for m in mappings if not m.is_active),
            },
        }

    async def _find_existing_employee(self, solides_id: str, cpf: str) -> dict[str, Any] | None:
        """
        Busca funcionario existente por solides_id ou CPF.

        Primeiro tenta pelo mapeamento solides_id, depois por CPF.

        Args:
            solides_id: ID do funcionario no Solides
            cpf: CPF do funcionario (limpo)

        Returns:
            Dict com dados do funcionario ou None
        """
        # 1. Buscar por mapeamento Solides
        if solides_id:
            mapping = get_entity_mapping(self.db, self.condominio_id, "colaboradores", solides_id=solides_id)
            if mapping and mapping.conecta_id:
                funcionario = await self._load_employee_by_id(mapping.conecta_id)
                if funcionario:
                    return funcionario

        # 2. Buscar por CPF na tabela de funcionarios
        if cpf:
            funcionario = await self._load_employee_by_cpf(cpf)
            if funcionario:
                return funcionario

        return None

    async def _load_employee_by_id(self, employee_id: UUID) -> dict[str, Any] | None:
        """
        Carrega funcionario pelo ID.

        Args:
            employee_id: UUID do funcionario

        Returns:
            Dict com dados ou None
        """
        # Implementacao depende do modelo Funcionario existente
        # Exemplo usando query direta:
        try:
            from modules.hr.models import Funcionario  # type: ignore

            stmt = select(Funcionario).where(
                and_(Funcionario.id == employee_id, Funcionario.condominio_id == self.condominio_id)
            )
            result = await self.db.execute(stmt)
            func = result.scalar_one_or_none()

            if func:
                return self._employee_to_dict(func)
        except ImportError:
            logger.warning("[SolidesIntegration] Modelo Funcionario nao encontrado, usando tabela generica")
            # Fallback para query direta na tabela
            pass

        return None

    async def _load_employee_by_cpf(self, cpf: str) -> dict[str, Any] | None:
        """
        Carrega funcionario pelo CPF.

        Args:
            cpf: CPF limpo (somente digitos)

        Returns:
            Dict com dados ou None
        """
        try:
            from modules.hr.models import Funcionario  # type: ignore

            stmt = select(Funcionario).where(
                and_(Funcionario.cpf == cpf, Funcionario.condominio_id == self.condominio_id)
            )
            result = await self.db.execute(stmt)
            func = result.scalar_one_or_none()

            if func:
                return self._employee_to_dict(func)
        except ImportError:
            pass

        return None

    async def _create_employee(self, solides_data: dict[str, Any]) -> SyncEmployeeResult:
        """
        Cria novo funcionario a partir dos dados do Solides.

        Args:
            solides_data: Dados do colaborador do Solides

        Returns:
            SyncEmployeeResult com detalhes da criacao
        """
        solides_id = str(solides_data.get("id", ""))
        cpf = self._clean_cpf(solides_data.get("cpf"))
        nome = solides_data.get("nome", "")

        # Mapear dados do Solides para formato interno
        employee_data = solides_colaborador_to_employee(solides_data, self.condominio_id)

        # Adicionar campos de controle
        employee_id = uuid4()
        employee_data.update(
            {
                "id": employee_id,
                "solides_id": solides_id,
                "sync_source": SyncSource.SOLIDES.value,
                "last_synced_at": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
            }
        )

        try:
            # Criar funcionario
            # Implementacao depende do modelo existente
            created = await self._insert_employee(employee_data)

            if created:
                # Criar mapeamento
                create_or_update_mapping(
                    self.db,
                    self.condominio_id,
                    "colaboradores",
                    solides_id,
                    employee_id,
                    sync_source=SyncSource.SOLIDES,
                    data_hash=compute_solides_entity_hash("colaboradores", solides_data),
                )

                logger.info(f"[SolidesIntegration] Funcionario criado: {nome} (ID: {employee_id})")

                return SyncEmployeeResult(
                    action=SyncAction.CREATED.value,
                    funcionario_id=str(employee_id),
                    solides_id=solides_id,
                    cpf=cpf,
                    name=nome,
                    changes=None,
                    error=None,
                )

        except Exception as e:
            logger.error(f"[SolidesIntegration] Erro criando funcionario: {e}")
            raise

        return SyncEmployeeResult(
            action=SyncAction.ERROR.value,
            funcionario_id=None,
            solides_id=solides_id,
            cpf=cpf,
            name=nome,
            changes=None,
            error="Falha ao inserir funcionario",
        )

    async def _update_employee(
        self, existing: dict[str, Any], solides_data: dict[str, Any], force_update: bool = False
    ) -> SyncEmployeeResult:
        """
        Atualiza funcionario existente com dados do Solides.

        Detecta mudancas e atualiza apenas campos alterados.

        Args:
            existing: Dados atuais do funcionario
            solides_data: Novos dados do Solides
            force_update: Forcar atualizacao mesmo sem mudancas

        Returns:
            SyncEmployeeResult com detalhes da atualizacao
        """
        solides_id = str(solides_data.get("id", ""))
        cpf = self._clean_cpf(solides_data.get("cpf"))
        nome = solides_data.get("nome", "")
        employee_id = existing.get("id")

        # Verificar hash para detectar mudancas
        current_hash = existing.get("data_hash", "")
        new_hash = compute_solides_entity_hash("colaboradores", solides_data)

        if not force_update and current_hash == new_hash:
            logger.debug(f"[SolidesIntegration] Sem mudancas para {nome}")
            return SyncEmployeeResult(
                action=SyncAction.SKIPPED.value,
                funcionario_id=str(employee_id) if employee_id else None,
                solides_id=solides_id,
                cpf=cpf,
                name=nome,
                changes=None,
                error=None,
            )

        # Mapear dados novos
        new_data = solides_colaborador_to_employee(solides_data, self.condominio_id)

        # Detectar campos alterados
        changes = detect_changes(existing, new_data, "colaboradores")

        if not changes and not force_update:
            return SyncEmployeeResult(
                action=SyncAction.SKIPPED.value,
                funcionario_id=str(employee_id) if employee_id else None,
                solides_id=solides_id,
                cpf=cpf,
                name=nome,
                changes=None,
                error=None,
            )

        # Atualizar dados
        new_data.update(
            {
                "updated_at": datetime.utcnow(),
                "sync_source": SyncSource.SOLIDES.value,
                "last_synced_at": datetime.utcnow(),
            }
        )

        try:
            await self._update_employee_record(employee_id, new_data)

            # Atualizar mapeamento
            create_or_update_mapping(
                self.db,
                self.condominio_id,
                "colaboradores",
                solides_id,
                employee_id,
                sync_source=SyncSource.SOLIDES,
                data_hash=new_hash,
            )

            logger.info(f"[SolidesIntegration] Funcionario atualizado: {nome} (campos: {list(changes.keys())})")

            return SyncEmployeeResult(
                action=SyncAction.UPDATED.value,
                funcionario_id=str(employee_id) if employee_id else None,
                solides_id=solides_id,
                cpf=cpf,
                name=nome,
                changes=changes,
                error=None,
            )

        except Exception as e:
            logger.error(f"[SolidesIntegration] Erro atualizando funcionario: {e}")
            raise

    async def _insert_employee(self, data: dict[str, Any]) -> bool:
        """
        Insere funcionario no banco de dados.

        Implementacao generica que pode ser adaptada para o modelo
        especifico do projeto.

        Args:
            data: Dados do funcionario a inserir

        Returns:
            True se inserido com sucesso
        """
        try:
            from modules.hr.models import Funcionario  # type: ignore

            funcionario = Funcionario(**self._prepare_insert_data(data))
            self.db.add(funcionario)
            await self.db.flush()
            return True

        except ImportError:
            # Se modelo nao existe, tenta insert direto
            logger.warning("[SolidesIntegration] Modelo Funcionario nao disponivel, pulando insercao")
            # Aqui poderia fazer insert direto na tabela se necessario
            return False

    async def _update_employee_record(self, employee_id: UUID, data: dict[str, Any]) -> bool:
        """
        Atualiza registro de funcionario no banco.

        Args:
            employee_id: UUID do funcionario
            data: Dados a atualizar

        Returns:
            True se atualizado com sucesso
        """
        try:
            from modules.hr.models import Funcionario  # type: ignore

            stmt = update(Funcionario).where(Funcionario.id == employee_id).values(**self._prepare_update_data(data))
            await self.db.execute(stmt)
            return True

        except ImportError:
            logger.warning("[SolidesIntegration] Modelo Funcionario nao disponivel, pulando atualizacao")
            return False

    def _prepare_insert_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Prepara dados para insercao, removendo campos nao mapeados.

        Args:
            data: Dados brutos

        Returns:
            Dados filtrados para insercao
        """
        # Campos validos para o modelo Funcionario
        valid_fields = {
            "id",
            "condominio_id",
            "nome_completo",
            "email",
            "cpf",
            "rg",
            "data_nascimento",
            "genero",
            "estado_civil",
            "telefone",
            "celular",
            "endereco_logradouro",
            "endereco_numero",
            "endereco_complemento",
            "endereco_bairro",
            "endereco_cidade",
            "endereco_uf",
            "endereco_cep",
            "matricula",
            "cargo_nome",
            "cargo_id",
            "departamento_nome",
            "departamento_id",
            "gestor_nome",
            "gestor_id",
            "data_admissao",
            "data_demissao",
            "tipo_contrato",
            "regime_trabalho",
            "jornada_trabalho",
            "salario_base",
            "ctps_numero",
            "ctps_serie",
            "ctps_uf",
            "pis",
            "titulo_eleitor",
            "certificado_reservista",
            "foto_url",
            "status",
            "solides_id",
            "sync_source",
            "last_synced_at",
            "created_at",
            "updated_at",
            "is_active",
            "extra_data",
        }

        return {k: v for k, v in data.items() if k in valid_fields and v is not None}

    def _prepare_update_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Prepara dados para atualizacao.

        Args:
            data: Dados brutos

        Returns:
            Dados filtrados para atualizacao
        """
        # Campos que nao devem ser atualizados
        readonly_fields = {"id", "condominio_id", "cpf", "created_at"}

        prepared = self._prepare_insert_data(data)
        return {k: v for k, v in prepared.items() if k not in readonly_fields}

    def _employee_to_dict(self, employee: Any) -> dict[str, Any]:
        """
        Converte objeto Funcionario para dicionario.

        Args:
            employee: Objeto do modelo Funcionario

        Returns:
            Dict com atributos do funcionario
        """
        return {
            "id": employee.id,
            "condominio_id": employee.condominio_id,
            "nome_completo": getattr(employee, "nome_completo", None),
            "email": getattr(employee, "email", None),
            "cpf": getattr(employee, "cpf", None),
            "data_nascimento": getattr(employee, "data_nascimento", None),
            "data_admissao": getattr(employee, "data_admissao", None),
            "data_demissao": getattr(employee, "data_demissao", None),
            "status": getattr(employee, "status", None),
            "solides_id": getattr(employee, "solides_id", None),
            "data_hash": getattr(employee, "data_hash", None),
            "created_at": getattr(employee, "created_at", None),
            "updated_at": getattr(employee, "updated_at", None),
        }

    @staticmethod
    def _clean_cpf(cpf: str | None) -> str | None:
        """
        Remove formatacao do CPF, mantendo apenas digitos.

        Args:
            cpf: CPF com ou sem formatacao

        Returns:
            CPF somente com digitos ou None
        """
        if not cpf:
            return None
        return "".join(filter(str.isdigit, cpf))

    @staticmethod
    def _parse_date(date_val: Any) -> date | None:
        """
        Faz parse de data em varios formatos.

        Args:
            date_val: Valor de data (str, date, datetime)

        Returns:
            date object ou None
        """
        if not date_val:
            return None

        if isinstance(date_val, date):
            return date_val

        if isinstance(date_val, datetime):
            return date_val.date()

        if isinstance(date_val, str):
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(date_val[:10], fmt[:10]).date()
                except (ValueError, TypeError):
                    continue

        return None


# ==================== FACTORY FUNCTIONS ====================


def get_integration_service(db: AsyncSession, condominio_id: UUID) -> SolidesIntegrationService:
    """
    Factory para criar servico de integracao.

    Args:
        db: Sessao async do banco de dados
        condominio_id: UUID do condominio

    Returns:
        SolidesIntegrationService configurado

    Example:
        >>> service = get_integration_service(db, condominio_id)
        >>> result = await service.sync_employee(solides_data)
    """
    return SolidesIntegrationService(db=db, condominio_id=condominio_id)


async def sync_employees_from_solides(
    db: AsyncSession, condominio_id: UUID, employees_data: list[dict[str, Any]]
) -> SyncSummary:
    """
    Funcao de conveniencia para sincronizar funcionarios.

    Args:
        db: Sessao async do banco
        condominio_id: UUID do condominio
        employees_data: Lista de colaboradores do Solides

    Returns:
        SyncSummary com resultado da sincronizacao

    Example:
        >>> async with AsyncSession(engine) as db:
        ...     result = await sync_employees_from_solides(
        ...         db, condominio_id, employees
        ...     )
        ...     print(f"Total: {result['total_processed']}")
    """
    service = get_integration_service(db, condominio_id)
    return await service.sync_all_employees(employees_data)
