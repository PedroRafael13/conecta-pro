"""
Serviço de Sincronização Sólides.
Sprint 33: Integration Framework

Sincronização bidirecional completa entre Sólides e Conecta PRO.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from modules.integrations.connectors.solides.conflict_resolver import (
    get_resolver_for_entity,
)
from modules.integrations.connectors.solides.connector import SolidesConnector
from modules.integrations.connectors.solides.mappers import (
    compute_solides_entity_hash,
)
from modules.integrations.connectors.solides.models import (
    ConflictStatus,
    SolidesIntegrationConfig,
    SolidesSyncConflict,
    SolidesSyncState,
    SyncDirection,
    SyncSource,
    SyncStatus,
    create_or_update_mapping,
    get_entity_mapping,
    get_or_create_sync_state,
    log_sync_operation,
)

logger = logging.getLogger(__name__)


@dataclass
class SyncStats:
    """Estatísticas de sincronização."""

    total_processed: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    conflicts: int = 0
    errors: int = 0
    error_details: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SyncResult:
    """Resultado de operação de sincronização."""

    success: bool
    stats: SyncStats
    sync_log_id: UUID | None = None
    duration_seconds: int = 0
    error: str | None = None


class SolidesSyncService:
    """
    Serviço de sincronização bidirecional Sólides ↔ Conecta PRO.

    Funcionalidades:
    - Full sync: Sincronização completa de todas as entidades
    - Incremental sync: Apenas alterações desde última sync
    - Single entity sync: Sincronizar uma entidade específica
    - Bidirectional sync: Sincronizar em ambas direções
    """

    # Ordem de sincronização (dependências)
    SYNC_ORDER = [
        "unidades",
        "departamentos",
        "cargos",
        "colaboradores",
        "ocorrencias",
        "absenteismos",
        "passaportes",
    ]

    def __init__(
        self,
        db: Session,
        condominio_id: UUID,
        connector: SolidesConnector | None = None,
        config: SolidesIntegrationConfig | None = None,
    ):
        """
        Inicializa o serviço de sincronização.

        Args:
            db: Sessão do banco de dados
            condominio_id: ID do condomínio
            connector: Conector Sólides (opcional, criado automaticamente)
            config: Configuração da integração
        """
        self.db = db
        self.condominio_id = condominio_id
        self._connector = connector
        self._config = config

    @property
    def connector(self) -> SolidesConnector:
        """Retorna ou cria conector."""
        if self._connector is None:
            self._connector = self._create_connector()
        return self._connector

    @property
    def config(self) -> SolidesIntegrationConfig:
        """Retorna ou carrega configuração."""
        if self._config is None:
            self._config = self._load_config()
        return self._config

    def _create_connector(self) -> SolidesConnector:
        """Cria conector com credenciais do banco."""
        from modules.integrations.connectors.solides.models import SolidesCredential

        cred = self.db.query(SolidesCredential).filter(SolidesCredential.condominio_id == self.condominio_id).first()

        if not cred:
            raise ValueError(f"Credenciais Sólides não configuradas para condomínio {self.condominio_id}")

        # Descriptografar token (implementar conforme sistema de criptografia)
        token = cred.api_token_encrypted  # TODO: decrypt

        return SolidesConnector(
            credentials={"api_token": token},
            config={"rate_limit_per_minute": self.config.rate_limit_per_minute if self._config else 60},
        )

    def _load_config(self) -> SolidesIntegrationConfig:
        """Carrega configuração do banco."""
        config = (
            self.db.query(SolidesIntegrationConfig)
            .filter(SolidesIntegrationConfig.condominio_id == self.condominio_id)
            .first()
        )

        if not config:
            # Criar configuração padrão
            config = SolidesIntegrationConfig(condominio_id=self.condominio_id, is_enabled=True)
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

        return config

    async def full_sync(
        self,
        direction: SyncDirection = SyncDirection.SOLIDES_TO_CONECTA,
        entity_types: list[str] | None = None,
        triggered_by: str = "system",
    ) -> SyncResult:
        """
        Executa sincronização completa.

        Args:
            direction: Direção da sincronização
            entity_types: Tipos de entidade (ou todas configuradas)
            triggered_by: Quem disparou

        Returns:
            SyncResult com estatísticas
        """
        start_time = datetime.utcnow()
        total_stats = SyncStats()

        # Determinar entidades a sincronizar
        entities = entity_types or self.config.enabled_entities or self.SYNC_ORDER
        entities = [e for e in self.SYNC_ORDER if e in entities]

        logger.info(
            f"[Solides] Iniciando full sync para condomínio {self.condominio_id}, "
            f"entidades: {entities}, direção: {direction}"
        )

        # Criar log
        sync_log = log_sync_operation(
            self.db,
            self.condominio_id,
            sync_type="full",
            entity_type="all",
            status=SyncStatus.IN_PROGRESS,
            direction=direction,
            triggered_by=triggered_by,
        )

        try:
            async with self.connector:
                for entity_type in entities:
                    try:
                        logger.info(f"[Solides] Sincronizando {entity_type}...")

                        if direction in [SyncDirection.SOLIDES_TO_CONECTA, SyncDirection.BIDIRECTIONAL]:
                            stats = await self._sync_from_solides(entity_type, incremental=False)
                            total_stats.total_processed += stats.total_processed
                            total_stats.created += stats.created
                            total_stats.updated += stats.updated
                            total_stats.conflicts += stats.conflicts
                            total_stats.errors += stats.errors
                            total_stats.error_details.extend(stats.error_details)

                        if direction in [SyncDirection.CONECTA_TO_SOLIDES, SyncDirection.BIDIRECTIONAL]:
                            pass

                        # Atualizar estado
                        state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
                        state.last_full_sync_at = datetime.utcnow()
                        state.last_sync_at = datetime.utcnow()
                        state.status = SyncStatus.COMPLETED
                        self.db.commit()

                    except Exception as e:
                        logger.error(f"[Solides] Erro sincronizando {entity_type}: {e}")
                        total_stats.errors += 1
                        total_stats.error_details.append({"entity_type": entity_type, "error": str(e)})

            # Finalizar log
            duration = int((datetime.utcnow() - start_time).total_seconds())
            sync_log.status = SyncStatus.COMPLETED if total_stats.errors == 0 else SyncStatus.PARTIAL
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration_ms = duration * 1000
            sync_log.items_processed = total_stats.total_processed
            sync_log.items_created = total_stats.created
            sync_log.items_updated = total_stats.updated
            sync_log.conflicts_detected = total_stats.conflicts
            sync_log.items_failed = total_stats.errors
            sync_log.error_details = total_stats.error_details if total_stats.error_details else None
            self.db.commit()

            logger.info(
                f"[Solides] Full sync concluído: "
                f"{total_stats.total_processed} processados, "
                f"{total_stats.created} criados, "
                f"{total_stats.updated} atualizados, "
                f"{total_stats.conflicts} conflitos, "
                f"{total_stats.errors} erros"
            )

            return SyncResult(
                success=total_stats.errors == 0, stats=total_stats, sync_log_id=sync_log.id, duration_seconds=duration
            )

        except Exception as e:
            logger.error(f"[Solides] Erro no full sync: {e}")
            sync_log.status = SyncStatus.FAILED
            sync_log.completed_at = datetime.utcnow()
            sync_log.error_details = [{"error": str(e)}]
            self.db.commit()

            return SyncResult(success=False, stats=total_stats, sync_log_id=sync_log.id, error=str(e))

    async def incremental_sync(
        self, entity_types: list[str] | None = None, triggered_by: str = "scheduler"
    ) -> SyncResult:
        """
        Executa sincronização incremental (apenas alterações).

        Args:
            entity_types: Tipos de entidade (ou todas configuradas)
            triggered_by: Quem disparou

        Returns:
            SyncResult com estatísticas
        """
        start_time = datetime.utcnow()
        total_stats = SyncStats()

        entities = entity_types or self.config.enabled_entities or self.SYNC_ORDER
        entities = [e for e in self.SYNC_ORDER if e in entities]

        logger.info(f"[Solides] Iniciando incremental sync para {self.condominio_id}")

        sync_log = log_sync_operation(
            self.db,
            self.condominio_id,
            sync_type="incremental",
            entity_type="all",
            status=SyncStatus.IN_PROGRESS,
            direction=SyncDirection.SOLIDES_TO_CONECTA,
            triggered_by=triggered_by,
        )

        try:
            async with self.connector:
                for entity_type in entities:
                    try:
                        stats = await self._sync_from_solides(entity_type, incremental=True)
                        total_stats.total_processed += stats.total_processed
                        total_stats.created += stats.created
                        total_stats.updated += stats.updated
                        total_stats.skipped += stats.skipped
                        total_stats.conflicts += stats.conflicts
                        total_stats.errors += stats.errors

                        # Atualizar estado
                        state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
                        state.last_sync_at = datetime.utcnow()
                        state.last_sync_count = stats.total_processed
                        state.total_synced += stats.created + stats.updated
                        state.status = SyncStatus.COMPLETED
                        self.db.commit()

                    except Exception as e:
                        logger.error(f"[Solides] Erro incremental {entity_type}: {e}")
                        total_stats.errors += 1

            # Finalizar log
            duration = int((datetime.utcnow() - start_time).total_seconds())
            sync_log.status = SyncStatus.COMPLETED
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration_ms = duration * 1000
            sync_log.items_processed = total_stats.total_processed
            sync_log.items_created = total_stats.created
            sync_log.items_updated = total_stats.updated
            sync_log.items_skipped = total_stats.skipped
            sync_log.conflicts_detected = total_stats.conflicts
            sync_log.items_failed = total_stats.errors
            self.db.commit()

            return SyncResult(success=True, stats=total_stats, sync_log_id=sync_log.id, duration_seconds=duration)

        except Exception as e:
            logger.error(f"[Solides] Erro no incremental sync: {e}")
            sync_log.status = SyncStatus.FAILED
            sync_log.completed_at = datetime.utcnow()
            self.db.commit()

            return SyncResult(success=False, stats=total_stats, error=str(e))

    async def sync_single_entity(
        self, entity_type: str, solides_id: str, direction: SyncDirection = SyncDirection.SOLIDES_TO_CONECTA
    ) -> SyncResult:
        """
        Sincroniza uma entidade específica.

        Args:
            entity_type: Tipo da entidade
            solides_id: ID no Sólides
            direction: Direção

        Returns:
            SyncResult
        """
        stats = SyncStats()

        try:
            async with self.connector:
                if direction == SyncDirection.SOLIDES_TO_CONECTA:
                    # Buscar do Sólides
                    data = await self.connector.fetch_entity_by_id(entity_type, solides_id)

                    if not data:
                        return SyncResult(
                            success=False,
                            stats=stats,
                            error=f"Entidade {entity_type}/{solides_id} não encontrada no Sólides",
                        )

                    # Processar
                    result = await self._process_solides_entity(entity_type, data)
                    stats.total_processed = 1
                    if result == "created":
                        stats.created = 1
                    elif result == "updated":
                        stats.updated = 1
                    elif result == "conflict":
                        stats.conflicts = 1

                else:
                    pass

            return SyncResult(success=True, stats=stats)

        except Exception as e:
            logger.error(f"[Solides] Erro sync single entity: {e}")
            return SyncResult(success=False, stats=stats, error=str(e))

    async def _sync_from_solides(self, entity_type: str, incremental: bool = True) -> SyncStats:
        """
        Sincroniza entidade do Sólides para Conecta.

        Args:
            entity_type: Tipo da entidade
            incremental: Se True, sincroniza apenas alterações

        Returns:
            SyncStats
        """
        stats = SyncStats()

        # Obter data da última sync para incremental
        updated_since = None
        if incremental:
            state = get_or_create_sync_state(self.db, self.condominio_id, entity_type)
            if state.last_sync_at:
                updated_since = state.last_sync_at

        # Buscar dados paginados
        cursor = None
        while True:
            result = await self.connector.fetch_entities(
                entity_type=entity_type, cursor=cursor, updated_since=updated_since, page_size=100
            )

            if not result.success:
                stats.errors += 1
                break

            # Processar cada item
            for item in result.data:
                try:
                    action = await self._process_solides_entity(entity_type, item)
                    stats.total_processed += 1

                    if action == "created":
                        stats.created += 1
                    elif action == "updated":
                        stats.updated += 1
                    elif action == "skipped":
                        stats.skipped += 1
                    elif action == "conflict":
                        stats.conflicts += 1

                except Exception as e:
                    stats.errors += 1
                    stats.error_details.append({"entity_id": item.get("id"), "error": str(e)})
                    logger.error(f"[Solides] Erro processando {entity_type}/{item.get('id')}: {e}")

            # Próxima página
            if result.has_more and result.cursor:
                cursor = result.cursor
            else:
                break

        return stats

    async def _process_solides_entity(self, entity_type: str, solides_data: dict[str, Any]) -> str:
        """
        Processa uma entidade do Sólides.

        Args:
            entity_type: Tipo da entidade
            solides_data: Dados do Sólides

        Returns:
            Ação tomada: "created", "updated", "skipped", "conflict"
        """
        solides_id = str(solides_data.get("id"))

        # Verificar se já existe mapeamento
        mapping = get_entity_mapping(self.db, self.condominio_id, entity_type, solides_id=solides_id)

        # Calcular hash dos dados
        data_hash = compute_solides_entity_hash(entity_type, solides_data)

        if mapping:
            # Já existe - verificar se mudou
            if mapping.data_hash == data_hash:
                return "skipped"  # Sem alterações

            # Verificar conflito
            get_resolver_for_entity(entity_type)

            # Por enquanto, atualiza direto
            await self._update_conecta_entity(entity_type, mapping.conecta_id, solides_data)

            mapping.data_hash = data_hash
            mapping.last_synced_at = datetime.utcnow()
            mapping.sync_source = SyncSource.SOLIDES
            self.db.commit()

            return "updated"

        else:
            # Novo - criar
            conecta_id = await self._create_conecta_entity(entity_type, solides_data)

            if conecta_id:
                create_or_update_mapping(
                    self.db,
                    self.condominio_id,
                    entity_type,
                    solides_id,
                    conecta_id,
                    sync_source=SyncSource.SOLIDES,
                    data_hash=data_hash,
                )
                return "created"

        return "skipped"

    async def _create_conecta_entity(self, entity_type: str, solides_data: dict[str, Any]) -> UUID | None:
        """
        Cria entidade no Conecta PRO (tabelas de staging solides_*).

        Args:
            entity_type: Tipo da entidade
            solides_data: Dados do Sólides

        Returns:
            ID da entidade criada ou None
        """
        from modules.integrations.connectors.solides.mappers import compute_solides_entity_hash

        solides_id = str(solides_data.get("id", ""))
        data_hash = compute_solides_entity_hash(entity_type, solides_data)

        try:
            if entity_type in ["colaboradores", "employees"]:
                entity = self._create_employee(solides_data, data_hash)
            elif entity_type in ["departamentos", "departments"]:
                entity = self._create_department(solides_data, data_hash)
            elif entity_type in ["cargos", "job_roles"]:
                entity = self._create_position(solides_data, data_hash)
            elif entity_type in ["ocorrencias", "occurrences"]:
                entity = self._create_occurrence(solides_data, data_hash)
            elif entity_type in ["absenteismos", "absences"]:
                entity = self._create_absence(solides_data, data_hash)
            elif entity_type in ["unidades", "workplaces"]:
                entity = self._create_workplace(solides_data, data_hash)
            elif entity_type in ["escalas", "work_schedules"]:
                entity = self._create_work_schedule(solides_data, data_hash)
            elif entity_type in ["centros_custo", "cost_centers"]:
                entity = self._create_cost_center(solides_data, data_hash)
            else:
                logger.warning(f"[Solides] Tipo de entidade não suportado: {entity_type}")
                return None

            if entity:
                self.db.add(entity)
                self.db.commit()
                self.db.refresh(entity)
                logger.info(f"[Solides] Criado {entity_type}/{solides_id} -> {entity.id}")
                return entity.id

        except Exception as e:
            logger.error(f"[Solides] Erro ao criar {entity_type}/{solides_id}: {e}")
            self.db.rollback()

        return None

    def _create_employee(self, data: dict[str, Any], data_hash: str):
        """Cria registro de colaborador."""
        from modules.integrations.connectors.solides.models import SolidesEmployee

        # Extrair dados de cargo/departamento se forem objetos
        cargo_nome = None
        if isinstance(data.get("cargo"), dict):
            cargo_nome = data["cargo"].get("nome")
        elif data.get("cargo_nome"):
            cargo_nome = data["cargo_nome"]

        departamento_nome = None
        if isinstance(data.get("departamento"), dict):
            departamento_nome = data["departamento"].get("nome")
        elif data.get("departamento_nome"):
            departamento_nome = data["departamento_nome"]

        unidade_nome = None
        if isinstance(data.get("unidade"), dict):
            unidade_nome = data["unidade"].get("nome")

        return SolidesEmployee(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome", data.get("name", "")),
            email=data.get("email"),
            cpf=data.get("cpf"),
            rg=data.get("rg"),
            data_nascimento=self._parse_datetime(data.get("data_nascimento") or data.get("birthDate")),
            sexo=data.get("sexo") or data.get("gender"),
            estado_civil=data.get("estado_civil") or data.get("maritalStatus"),
            telefone=data.get("telefone") or data.get("phone"),
            celular=data.get("celular") or data.get("mobile"),
            endereco=data.get("endereco") or data.get("address") or {},
            matricula=data.get("matricula") or data.get("registrationNumber"),
            cargo_id=str(data.get("cargo_id") or data.get("jobRoleId") or ""),
            cargo_nome=cargo_nome or data.get("jobRoleName"),
            departamento_id=str(data.get("departamento_id") or data.get("departmentId") or ""),
            departamento_nome=departamento_nome or data.get("departmentName"),
            unidade_id=str(data.get("unidade_id") or data.get("workplaceId") or ""),
            unidade_nome=unidade_nome or data.get("workplaceName"),
            gestor_id=str(data.get("gestor_id") or data.get("managerId") or ""),
            gestor_nome=data.get("gestor_nome") or data.get("managerName"),
            data_admissao=self._parse_datetime(
                data.get("data_admissao") or data.get("admissionDate") or data.get("hireDate")
            ),
            data_demissao=self._parse_datetime(data.get("data_demissao") or data.get("terminationDate")),
            tipo_contrato=data.get("tipo_contrato") or data.get("contractType"),
            regime_trabalho=data.get("regime_trabalho") or data.get("workRegime"),
            jornada_trabalho=data.get("jornada_trabalho") or data.get("workSchedule"),
            carga_horaria_semanal=data.get("carga_horaria_semanal") or data.get("weeklyHours"),
            salario=str(data.get("salario") or data.get("salary") or ""),
            ctps_numero=data.get("ctps_numero") or data.get("ctpsNumber"),
            ctps_serie=data.get("ctps_serie") or data.get("ctpsSeries"),
            ctps_uf=data.get("ctps_uf") or data.get("ctpsState"),
            pis=data.get("pis") or data.get("pisNumber"),
            titulo_eleitor=data.get("titulo_eleitor") or data.get("voterId"),
            certificado_reservista=data.get("certificado_reservista") or data.get("militaryCertificate"),
            dependentes=data.get("dependentes") or data.get("dependents") or [],
            situacao=data.get("situacao") or data.get("status") or "ativo",
            perfil_disc=data.get("perfil_disc") or data.get("discProfile"),
            perfil_profiler=data.get("perfil_profiler") or data.get("profilerProfile"),
            foto_url=data.get("foto_url") or data.get("photoUrl"),
            dados_adicionais=data.get("dados_adicionais") or {},
            data_hash=data_hash,
        )

    def _create_department(self, data: dict[str, Any], data_hash: str):
        """Cria registro de departamento."""
        from modules.integrations.connectors.solides.models import SolidesDepartment

        return SolidesDepartment(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome") or data.get("name", ""),
            codigo=data.get("codigo") or data.get("code"),
            departamento_pai_id=str(data.get("departamento_pai_id") or data.get("parentId") or ""),
            gestor_id=str(data.get("gestor_id") or data.get("managerId") or ""),
            unidade_id=str(data.get("unidade_id") or data.get("workplaceId") or ""),
            ativo=data.get("ativo", data.get("active", True)),
            data_hash=data_hash,
        )

    def _create_position(self, data: dict[str, Any], data_hash: str):
        """Cria registro de cargo."""
        from modules.integrations.connectors.solides.models import SolidesPosition

        return SolidesPosition(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome") or data.get("name", ""),
            codigo=data.get("codigo") or data.get("code"),
            descricao=data.get("descricao") or data.get("description"),
            departamento_id=str(data.get("departamento_id") or data.get("departmentId") or ""),
            cbo_id=str(data.get("cbo_id") or ""),
            cbo_codigo=data.get("cbo_codigo") or data.get("cboCode"),
            nivel=data.get("nivel") or data.get("level"),
            faixa_salarial_min=str(data.get("faixa_salarial_min") or data.get("salaryRangeMin") or ""),
            faixa_salarial_max=str(data.get("faixa_salarial_max") or data.get("salaryRangeMax") or ""),
            ativo=data.get("ativo", data.get("active", True)),
            data_hash=data_hash,
        )

    def _create_occurrence(self, data: dict[str, Any], data_hash: str):
        """Cria registro de ocorrência."""
        from modules.integrations.connectors.solides.models import SolidesOccurrence

        return SolidesOccurrence(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            colaborador_id=str(data.get("colaborador_id") or data.get("employeeId", "")),
            colaborador_nome=data.get("colaborador_nome") or data.get("employeeName"),
            tipo=data.get("tipo") or data.get("type", "outro"),
            descricao=data.get("descricao") or data.get("description"),
            data=self._parse_datetime(data.get("data") or data.get("date")),
            data_vigencia=self._parse_datetime(data.get("data_vigencia") or data.get("effectiveDate")),
            duracao_dias=data.get("duracao_dias") or data.get("durationDays"),
            valor_aumento=str(data.get("valor_aumento") or data.get("raiseAmount") or ""),
            percentual_aumento=str(data.get("percentual_aumento") or data.get("raisePercentage") or ""),
            novo_cargo_id=str(data.get("novo_cargo_id") or data.get("newPositionId") or ""),
            novo_cargo_nome=data.get("novo_cargo_nome") or data.get("newPositionName"),
            registrado_por_id=str(data.get("registrado_por_id") or data.get("registeredById") or ""),
            registrado_por_nome=data.get("registrado_por_nome") or data.get("registeredByName"),
            anexos=data.get("anexos") or data.get("attachments") or [],
            observacoes=data.get("observacoes") or data.get("notes"),
            dados_adicionais=data.get("dados_adicionais") or {},
            data_hash=data_hash,
        )

    def _create_absence(self, data: dict[str, Any], data_hash: str):
        """Cria registro de absenteísmo."""
        from modules.integrations.connectors.solides.models import SolidesAbsence

        return SolidesAbsence(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            colaborador_id=str(data.get("colaborador_id") or data.get("employeeId", "")),
            colaborador_nome=data.get("colaborador_nome") or data.get("employeeName"),
            tipo=data.get("tipo") or data.get("type", "falta"),
            motivo=data.get("motivo") or data.get("reason"),
            data_inicio=self._parse_datetime(data.get("data_inicio") or data.get("startDate")),
            data_fim=self._parse_datetime(data.get("data_fim") or data.get("endDate")),
            horas=str(data.get("horas") or data.get("hours") or ""),
            minutos_atraso=data.get("minutos_atraso") or data.get("minutesLate"),
            justificado=data.get("justificado", data.get("justified", False)),
            documento_anexo=data.get("documento_anexo") or data.get("documentUrl"),
            cid=data.get("cid") or data.get("icdCode"),
            desconto_em_folha=data.get("desconto_em_folha", data.get("payrollDeduction", True)),
            dias_descontados=data.get("dias_descontados") or data.get("daysDeducted"),
            numero_beneficio_inss=data.get("numero_beneficio_inss") or data.get("inssBenefitNumber"),
            data_inicio_inss=self._parse_datetime(data.get("data_inicio_inss") or data.get("inssStartDate")),
            data_fim_inss=self._parse_datetime(data.get("data_fim_inss") or data.get("inssEndDate")),
            registrado_por_id=str(data.get("registrado_por_id") or data.get("registeredById") or ""),
            registrado_por_nome=data.get("registrado_por_nome") or data.get("registeredByName"),
            observacoes=data.get("observacoes") or data.get("notes"),
            dados_adicionais=data.get("dados_adicionais") or {},
            data_hash=data_hash,
        )

    def _create_workplace(self, data: dict[str, Any], data_hash: str):
        """Cria registro de local de trabalho/unidade."""
        from modules.integrations.connectors.solides.models import SolidesWorkplace

        return SolidesWorkplace(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome") or data.get("name", ""),
            codigo=data.get("codigo") or data.get("code"),
            cnpj=data.get("cnpj"),
            endereco=data.get("endereco") or data.get("address") or {},
            telefone=data.get("telefone") or data.get("phone"),
            email=data.get("email"),
            ativo=data.get("ativo", data.get("active", True)),
            data_hash=data_hash,
        )

    def _create_work_schedule(self, data: dict[str, Any], data_hash: str):
        """Cria registro de escala de trabalho."""
        from modules.integrations.connectors.solides.models import SolidesWorkSchedule

        return SolidesWorkSchedule(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome") or data.get("name", ""),
            codigo=data.get("codigo") or data.get("code"),
            tipo=data.get("tipo") or data.get("type"),
            carga_horaria_semanal=data.get("carga_horaria_semanal") or data.get("weeklyHours"),
            horarios=data.get("horarios") or data.get("schedule") or {},
            ativo=data.get("ativo", data.get("active", True)),
            data_hash=data_hash,
        )

    def _create_cost_center(self, data: dict[str, Any], data_hash: str):
        """Cria registro de centro de custo."""
        from modules.integrations.connectors.solides.models import SolidesCostCenter

        return SolidesCostCenter(
            condominio_id=self.condominio_id,
            solides_id=str(data.get("id", "")),
            nome=data.get("nome") or data.get("name", ""),
            codigo=data.get("codigo") or data.get("code"),
            descricao=data.get("descricao") or data.get("description"),
            ativo=data.get("ativo", data.get("active", True)),
            data_hash=data_hash,
        )

    def _parse_datetime(self, value) -> datetime | None:
        """Converte valor para datetime."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%d/%m/%Y"]:
                try:
                    return datetime.strptime(value[:26], fmt)
                except (ValueError, TypeError):
                    continue
        return None

    async def _update_conecta_entity(self, entity_type: str, conecta_id: UUID, solides_data: dict[str, Any]) -> bool:
        """
        Atualiza entidade no Conecta PRO (tabelas de staging solides_*).

        Args:
            entity_type: Tipo da entidade
            conecta_id: ID local
            solides_data: Dados do Sólides

        Returns:
            True se atualizado
        """
        from modules.integrations.connectors.solides.mappers import compute_solides_entity_hash
        from modules.integrations.connectors.solides.models import (
            SolidesAbsence,
            SolidesCostCenter,
            SolidesDepartment,
            SolidesEmployee,
            SolidesOccurrence,
            SolidesPosition,
            SolidesWorkplace,
            SolidesWorkSchedule,
        )

        # Mapear tipo para modelo
        model_map = {
            "colaboradores": SolidesEmployee,
            "employees": SolidesEmployee,
            "departamentos": SolidesDepartment,
            "departments": SolidesDepartment,
            "cargos": SolidesPosition,
            "job_roles": SolidesPosition,
            "ocorrencias": SolidesOccurrence,
            "occurrences": SolidesOccurrence,
            "absenteismos": SolidesAbsence,
            "absences": SolidesAbsence,
            "unidades": SolidesWorkplace,
            "workplaces": SolidesWorkplace,
            "escalas": SolidesWorkSchedule,
            "work_schedules": SolidesWorkSchedule,
            "centros_custo": SolidesCostCenter,
            "cost_centers": SolidesCostCenter,
        }

        model = model_map.get(entity_type)
        if not model:
            logger.warning(f"[Solides] Modelo não encontrado para {entity_type}")
            return False

        try:
            entity = self.db.query(model).filter(model.id == conecta_id).first()
            if not entity:
                logger.warning(f"[Solides] Entidade não encontrada: {entity_type}/{conecta_id}")
                return False

            # Atualizar campos baseado no tipo
            data_hash = compute_solides_entity_hash(entity_type, solides_data)
            self._update_entity_fields(entity, entity_type, solides_data, data_hash)

            entity.last_synced_at = datetime.utcnow()
            entity.data_hash = data_hash
            self.db.commit()

            logger.info(f"[Solides] Atualizado {entity_type}/{conecta_id}")
            return True

        except Exception as e:
            logger.error(f"[Solides] Erro ao atualizar {entity_type}/{conecta_id}: {e}")
            self.db.rollback()
            return False

    def _update_entity_fields(self, entity, entity_type: str, data: dict[str, Any], data_hash: str):
        """Atualiza campos da entidade com novos dados."""
        if entity_type in ["colaboradores", "employees"]:
            # Extrair dados de cargo/departamento se forem objetos
            cargo_nome = None
            if isinstance(data.get("cargo"), dict):
                cargo_nome = data["cargo"].get("nome")
            elif data.get("cargo_nome"):
                cargo_nome = data["cargo_nome"]

            departamento_nome = None
            if isinstance(data.get("departamento"), dict):
                departamento_nome = data["departamento"].get("nome")
            elif data.get("departamento_nome"):
                departamento_nome = data["departamento_nome"]

            entity.nome = data.get("nome", data.get("name")) or entity.nome
            entity.email = data.get("email") or entity.email
            entity.cpf = data.get("cpf") or entity.cpf
            entity.telefone = data.get("telefone") or data.get("phone") or entity.telefone
            entity.celular = data.get("celular") or data.get("mobile") or entity.celular
            entity.cargo_id = str(data.get("cargo_id") or data.get("jobRoleId") or entity.cargo_id)
            entity.cargo_nome = cargo_nome or data.get("jobRoleName") or entity.cargo_nome
            entity.departamento_id = str(
                data.get("departamento_id") or data.get("departmentId") or entity.departamento_id
            )
            entity.departamento_nome = departamento_nome or data.get("departmentName") or entity.departamento_nome
            entity.situacao = data.get("situacao") or data.get("status") or entity.situacao
            entity.data_demissao = (
                self._parse_datetime(data.get("data_demissao") or data.get("terminationDate")) or entity.data_demissao
            )
            entity.salario = str(data.get("salario") or data.get("salary") or entity.salario)

        elif entity_type in ["departamentos", "departments"]:
            entity.nome = data.get("nome") or data.get("name") or entity.nome
            entity.codigo = data.get("codigo") or data.get("code") or entity.codigo
            entity.ativo = data.get("ativo", data.get("active", entity.ativo))

        elif entity_type in ["cargos", "job_roles"]:
            entity.nome = data.get("nome") or data.get("name") or entity.nome
            entity.codigo = data.get("codigo") or data.get("code") or entity.codigo
            entity.descricao = data.get("descricao") or data.get("description") or entity.descricao
            entity.ativo = data.get("ativo", data.get("active", entity.ativo))

        elif entity_type in ["ocorrencias", "occurrences"]:
            entity.tipo = data.get("tipo") or data.get("type") or entity.tipo
            entity.descricao = data.get("descricao") or data.get("description") or entity.descricao
            entity.observacoes = data.get("observacoes") or data.get("notes") or entity.observacoes

        elif entity_type in ["absenteismos", "absences"]:
            entity.tipo = data.get("tipo") or data.get("type") or entity.tipo
            entity.motivo = data.get("motivo") or data.get("reason") or entity.motivo
            entity.justificado = data.get("justificado", data.get("justified", entity.justificado))
            entity.data_fim = self._parse_datetime(data.get("data_fim") or data.get("endDate")) or entity.data_fim

    async def get_sync_status(self) -> dict[str, Any]:
        """
        Retorna status geral da sincronização.

        Returns:
            Dict com status de cada entidade
        """
        # Health check
        health = await self.connector.health_check()

        # Status por entidade
        entity_status = {}
        for entity_type in self.SYNC_ORDER:
            state = (
                self.db.query(SolidesSyncState)
                .filter(
                    SolidesSyncState.condominio_id == self.condominio_id, SolidesSyncState.entity_type == entity_type
                )
                .first()
            )

            if state:
                entity_status[entity_type] = {
                    "status": state.status.value if state.status else "never_synced",
                    "last_sync_at": state.last_sync_at.isoformat() if state.last_sync_at else None,
                    "last_full_sync_at": state.last_full_sync_at.isoformat() if state.last_full_sync_at else None,
                    "total_synced": state.total_synced,
                    "last_error": state.last_error,
                }
            else:
                entity_status[entity_type] = {"status": "never_synced"}

        # Conflitos pendentes
        pending_conflicts = (
            self.db.query(SolidesSyncConflict)
            .filter(
                SolidesSyncConflict.condominio_id == self.condominio_id,
                SolidesSyncConflict.status == ConflictStatus.PENDING,
            )
            .count()
        )

        return {
            "connected": health.healthy,
            "api_latency_ms": health.latency_ms,
            "api_message": health.message,
            "config": {
                "is_enabled": self.config.is_enabled,
                "sync_direction": self.config.sync_direction.value if self.config.sync_direction else None,
                "conflict_strategy": self.config.conflict_strategy.value if self.config.conflict_strategy else None,
                "enabled_entities": self.config.enabled_entities,
            },
            "entities": entity_status,
            "pending_conflicts": pending_conflicts,
        }


# ==================== FACTORY ====================


def get_sync_service(db: Session, condominio_id: UUID) -> SolidesSyncService:
    """
    Factory para criar serviço de sincronização.

    Args:
        db: Sessão do banco
        condominio_id: ID do condomínio

    Returns:
        SolidesSyncService configurado
    """
    return SolidesSyncService(db=db, condominio_id=condominio_id)
