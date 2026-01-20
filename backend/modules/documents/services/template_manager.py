"""
Template Manager Service.

Gerencia templates de extracao de documentos,
incluindo CRUD, versionamento e templates builtin.
"""

import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..models.extraction_template import (
    ExtractionTemplate,
    PostProcessor,
    RuleType,
    TemplateCategory,
    TemplateField,
    TemplateRule,
    TemplateStatus,
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Gerenciador de templates de extracao.

    Gerencia templates builtin e customizados para
    extracao estruturada de documentos.
    """

    def __init__(self, templates_path: Optional[str] = None):
        """
        Inicializa gerenciador.

        Args:
            templates_path: Diretorio para templates customizados
        """
        self.templates_path = templates_path or "/opt/conecta-pro/data/templates"
        os.makedirs(self.templates_path, exist_ok=True)

        self._templates: Dict[str, ExtractionTemplate] = {}
        self._load_builtin_templates()

    def _load_builtin_templates(self) -> None:
        """Carrega templates builtin."""
        # Template: Boleto Bancario
        boleto = ExtractionTemplate(
            id="builtin_boleto",
            name="Boleto Bancario",
            description="Template para extracao de boletos bancarios",
            document_type="boleto",
            category=TemplateCategory.FINANCIAL,
            status=TemplateStatus.ACTIVE,
            is_official=True,
            detection_keywords=[
                "boleto",
                "codigo de barras",
                "linha digitavel",
                "pagavel em qualquer banco",
                "ficha de compensacao",
            ],
            detection_patterns=[
                r"\d{5}\.\d{5}\s+\d{5}\.\d{6}\s+\d{5}\.\d{6}\s+\d\s+\d{14}",
            ],
            fields=[
                TemplateField(
                    name="linha_digitavel",
                    label="Linha Digitavel",
                    field_type="boleto_line",
                    required=True,
                    is_key_field=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{5}[.\s]?\d{5}[.\s]+\d{5}[.\s]?\d{6}[.\s]+\d{5}[.\s]?\d{6}[.\s]+\d[.\s]+\d{14}",
                            post_processors=[PostProcessor.DIGITS_ONLY],
                        ),
                    ],
                ),
                TemplateField(
                    name="valor",
                    label="Valor do Documento",
                    field_type="currency",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="valor do documento",
                            pattern=r"[\d.,]+",
                        ),
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"R\$\s*[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="vencimento",
                    label="Data de Vencimento",
                    field_type="date",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="vencimento",
                            pattern=r"\d{2}/\d{2}/\d{4}",
                        ),
                    ],
                ),
                TemplateField(
                    name="cedente",
                    label="Cedente",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="cedente",
                        ),
                    ],
                ),
                TemplateField(
                    name="sacado",
                    label="Sacado/Pagador",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="sacado",
                        ),
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="pagador",
                        ),
                    ],
                ),
                TemplateField(
                    name="cpf_cnpj_sacado",
                    label="CPF/CNPJ Sacado",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}",
                        ),
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{2}[.\s]?\d{3}[.\s]?\d{3}[/.\s]?\d{4}[-.\s]?\d{2}",
                        ),
                    ],
                ),
                TemplateField(
                    name="nosso_numero",
                    label="Nosso Numero",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="nosso numero",
                            pattern=r"[\d./-]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="banco",
                    label="Banco",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"banco\s+(\d{3})",
                            group=1,
                        ),
                    ],
                ),
            ],
        )
        self._templates[boleto.id] = boleto

        # Template: NFe
        nfe = ExtractionTemplate(
            id="builtin_nfe",
            name="Nota Fiscal Eletronica",
            description="Template para extracao de NFe/DANFE",
            document_type="nfe",
            category=TemplateCategory.FINANCIAL,
            status=TemplateStatus.ACTIVE,
            is_official=True,
            detection_keywords=[
                "nota fiscal",
                "danfe",
                "chave de acesso",
                "icms",
                "natureza da operacao",
            ],
            fields=[
                TemplateField(
                    name="chave_acesso",
                    label="Chave de Acesso",
                    field_type="nfe_key",
                    required=True,
                    is_key_field=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{44}",
                            post_processors=[PostProcessor.DIGITS_ONLY],
                        ),
                    ],
                ),
                TemplateField(
                    name="numero_nf",
                    label="Numero da NF",
                    field_type="text",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"n[°o]?\s*(\d+)",
                            group=1,
                        ),
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="numero",
                            pattern=r"\d+",
                        ),
                    ],
                ),
                TemplateField(
                    name="serie",
                    label="Serie",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="serie",
                            pattern=r"\d+",
                        ),
                    ],
                ),
                TemplateField(
                    name="data_emissao",
                    label="Data de Emissao",
                    field_type="date",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="emissao",
                            pattern=r"\d{2}/\d{2}/\d{4}",
                        ),
                    ],
                ),
                TemplateField(
                    name="valor_total",
                    label="Valor Total",
                    field_type="currency",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="valor total da nota",
                            pattern=r"[\d.,]+",
                        ),
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="total",
                            pattern=r"[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="emitente_nome",
                    label="Nome Emitente",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="emitente",
                        ),
                    ],
                ),
                TemplateField(
                    name="emitente_cnpj",
                    label="CNPJ Emitente",
                    field_type="cnpj",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{2}[.\s]?\d{3}[.\s]?\d{3}[/.\s]?\d{4}[-.\s]?\d{2}",
                        ),
                    ],
                ),
                TemplateField(
                    name="destinatario_nome",
                    label="Nome Destinatario",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="destinatario",
                        ),
                    ],
                ),
                TemplateField(
                    name="destinatario_cpf_cnpj",
                    label="CPF/CNPJ Destinatario",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}",
                        ),
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{2}[.\s]?\d{3}[.\s]?\d{3}[/.\s]?\d{4}[-.\s]?\d{2}",
                        ),
                    ],
                ),
                TemplateField(
                    name="natureza_operacao",
                    label="Natureza da Operacao",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="natureza da operacao",
                        ),
                    ],
                ),
            ],
        )
        self._templates[nfe.id] = nfe

        # Template: CNH
        cnh = ExtractionTemplate(
            id="builtin_cnh",
            name="Carteira Nacional de Habilitacao",
            description="Template para extracao de CNH",
            document_type="cnh",
            category=TemplateCategory.PERSONAL,
            status=TemplateStatus.ACTIVE,
            is_official=True,
            detection_keywords=[
                "carteira nacional de habilitacao",
                "cnh",
                "detran",
                "habilitacao",
                "categoria",
            ],
            fields=[
                TemplateField(
                    name="nome",
                    label="Nome",
                    field_type="name",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="nome",
                        ),
                    ],
                ),
                TemplateField(
                    name="cpf",
                    label="CPF",
                    field_type="cpf",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}",
                            post_processors=[PostProcessor.DIGITS_ONLY],
                        ),
                    ],
                ),
                TemplateField(
                    name="registro",
                    label="Numero de Registro",
                    field_type="text",
                    required=True,
                    is_key_field=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="registro",
                            pattern=r"\d{9,11}",
                        ),
                    ],
                ),
                TemplateField(
                    name="data_nascimento",
                    label="Data de Nascimento",
                    field_type="date",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="nascimento",
                            pattern=r"\d{2}/\d{2}/\d{4}",
                        ),
                    ],
                ),
                TemplateField(
                    name="validade",
                    label="Validade",
                    field_type="date",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="validade",
                            pattern=r"\d{2}/\d{2}/\d{4}",
                        ),
                    ],
                ),
                TemplateField(
                    name="categoria",
                    label="Categoria",
                    field_type="text",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"cat[.\s]*([abcde]{1,5})",
                            group=1,
                        ),
                    ],
                ),
                TemplateField(
                    name="primeira_habilitacao",
                    label="Primeira Habilitacao",
                    field_type="date",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="1 habilitacao",
                            pattern=r"\d{2}/\d{2}/\d{4}",
                        ),
                    ],
                ),
            ],
        )
        self._templates[cnh.id] = cnh

        # Template: Holerite
        holerite = ExtractionTemplate(
            id="builtin_holerite",
            name="Holerite/Contracheque",
            description="Template para extracao de holerites",
            document_type="holerite",
            category=TemplateCategory.BUSINESS,
            status=TemplateStatus.ACTIVE,
            is_official=True,
            detection_keywords=[
                "holerite",
                "contracheque",
                "demonstrativo de pagamento",
                "proventos",
                "descontos",
            ],
            fields=[
                TemplateField(
                    name="funcionario_nome",
                    label="Nome do Funcionario",
                    field_type="name",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="funcionario",
                        ),
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="nome",
                        ),
                    ],
                ),
                TemplateField(
                    name="cpf",
                    label="CPF",
                    field_type="cpf",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"\d{3}[.\s]?\d{3}[.\s]?\d{3}[-.\s]?\d{2}",
                        ),
                    ],
                ),
                TemplateField(
                    name="competencia",
                    label="Competencia",
                    field_type="text",
                    required=True,
                    is_key_field=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.REGEX,
                            pattern=r"(?:competencia|referencia)[:\s]*(\d{2}/\d{4})",
                            group=1,
                        ),
                    ],
                ),
                TemplateField(
                    name="salario_base",
                    label="Salario Base",
                    field_type="currency",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="salario base",
                            pattern=r"[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="total_proventos",
                    label="Total Proventos",
                    field_type="currency",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="total proventos",
                            pattern=r"[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="total_descontos",
                    label="Total Descontos",
                    field_type="currency",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="total descontos",
                            pattern=r"[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="liquido",
                    label="Liquido a Receber",
                    field_type="currency",
                    required=True,
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="liquido",
                            pattern=r"[\d.,]+",
                        ),
                    ],
                ),
                TemplateField(
                    name="empresa",
                    label="Empresa",
                    field_type="text",
                    rules=[
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="empregador",
                        ),
                        TemplateRule(
                            rule_type=RuleType.AFTER_LABEL,
                            anchor="empresa",
                        ),
                    ],
                ),
            ],
        )
        self._templates[holerite.id] = holerite

        logger.info(f"Carregados {len(self._templates)} templates builtin")

    def get_template(self, template_id: str) -> Optional[ExtractionTemplate]:
        """
        Obtem template por ID.

        Args:
            template_id: ID do template

        Returns:
            Template ou None
        """
        # Tentar memoria primeiro
        if template_id in self._templates:
            return self._templates[template_id]

        # Tentar carregar do disco
        return self._load_from_file(template_id)

    def get_templates_by_type(
        self, document_type: str
    ) -> List[ExtractionTemplate]:
        """
        Obtem templates por tipo de documento.

        Args:
            document_type: Tipo do documento

        Returns:
            Lista de templates
        """
        return [
            t
            for t in self._templates.values()
            if t.document_type == document_type and t.status == TemplateStatus.ACTIVE
        ]

    def get_templates_by_category(
        self, category: TemplateCategory
    ) -> List[ExtractionTemplate]:
        """
        Obtem templates por categoria.

        Args:
            category: Categoria

        Returns:
            Lista de templates
        """
        return [t for t in self._templates.values() if t.category == category]

    def list_templates(
        self,
        tenant_id: Optional[str] = None,
        category: Optional[TemplateCategory] = None,
        status: Optional[TemplateStatus] = None,
        include_builtin: bool = True,
    ) -> List[ExtractionTemplate]:
        """
        Lista templates com filtros.

        Args:
            tenant_id: Filtrar por tenant
            category: Filtrar por categoria
            status: Filtrar por status
            include_builtin: Incluir templates builtin

        Returns:
            Lista de templates
        """
        templates = []

        for template in self._templates.values():
            # Filtros
            if tenant_id and template.tenant_id and template.tenant_id != tenant_id:
                continue
            if category and template.category != category:
                continue
            if status and template.status != status:
                continue
            if not include_builtin and template.is_official:
                continue

            templates.append(template)

        return sorted(templates, key=lambda t: t.name)

    def create_template(
        self, template: ExtractionTemplate
    ) -> ExtractionTemplate:
        """
        Cria novo template.

        Args:
            template: Template a criar

        Returns:
            Template criado
        """
        # Validar
        errors = template.validate()
        if errors:
            raise ValueError(f"Template invalido: {errors}")

        # Definir status inicial
        template.status = TemplateStatus.DRAFT
        template.created_at = datetime.utcnow()
        template.updated_at = datetime.utcnow()

        # Salvar
        self._templates[template.id] = template
        self._save_to_file(template)

        logger.info(f"Template criado: {template.id}")

        return template

    def update_template(
        self,
        template_id: str,
        updates: Dict[str, Any],
    ) -> Optional[ExtractionTemplate]:
        """
        Atualiza template existente.

        Args:
            template_id: ID do template
            updates: Campos a atualizar

        Returns:
            Template atualizado ou None
        """
        template = self.get_template(template_id)
        if not template:
            return None

        # Nao permitir alterar templates oficiais
        if template.is_official:
            raise ValueError("Nao e possivel alterar templates oficiais")

        # Atualizar campos
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.utcnow()
        template.increment_version()

        # Salvar
        self._templates[template.id] = template
        self._save_to_file(template)

        return template

    def delete_template(self, template_id: str) -> bool:
        """
        Remove template.

        Args:
            template_id: ID do template

        Returns:
            True se removido
        """
        template = self.get_template(template_id)
        if not template:
            return False

        # Nao permitir deletar templates oficiais
        if template.is_official:
            raise ValueError("Nao e possivel deletar templates oficiais")

        # Remover
        if template_id in self._templates:
            del self._templates[template_id]

        # Remover arquivo
        file_path = os.path.join(self.templates_path, f"{template_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)

        logger.info(f"Template removido: {template_id}")

        return True

    def clone_template(
        self,
        template_id: str,
        new_name: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[ExtractionTemplate]:
        """
        Clona um template.

        Args:
            template_id: ID do template original
            new_name: Nome do clone
            tenant_id: Tenant do novo template

        Returns:
            Template clonado ou None
        """
        original = self.get_template(template_id)
        if not original:
            return None

        cloned = original.clone(new_name)
        cloned.tenant_id = tenant_id
        cloned.is_official = False
        cloned.is_public = False

        return self.create_template(cloned)

    def activate_template(self, template_id: str) -> bool:
        """Ativa um template."""
        template = self.get_template(template_id)
        if not template:
            return False

        # Validar antes de ativar
        errors = template.validate()
        if errors:
            raise ValueError(f"Template invalido: {errors}")

        template.activate()
        self._templates[template.id] = template
        self._save_to_file(template)

        return True

    def deprecate_template(self, template_id: str) -> bool:
        """Deprecia um template."""
        template = self.get_template(template_id)
        if not template:
            return False

        template.deprecate()
        self._templates[template.id] = template
        self._save_to_file(template)

        return True

    def _save_to_file(self, template: ExtractionTemplate) -> None:
        """Salva template em arquivo."""
        if template.is_official:
            return  # Nao salvar templates builtin

        file_path = os.path.join(self.templates_path, f"{template.id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)

    def _load_from_file(self, template_id: str) -> Optional[ExtractionTemplate]:
        """Carrega template de arquivo."""
        file_path = os.path.join(self.templates_path, f"{template_id}.json")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            template = self._dict_to_template(data)
            self._templates[template.id] = template

            return template

        except Exception as e:
            logger.error(f"Erro ao carregar template {template_id}: {e}")
            return None

    def _dict_to_template(self, data: Dict[str, Any]) -> ExtractionTemplate:
        """Converte dicionario para template."""
        # Converter campos
        fields = []
        for field_data in data.get("fields", []):
            rules = [
                TemplateRule(
                    rule_type=RuleType(r.get("rule_type", "regex")),
                    pattern=r.get("pattern"),
                    anchor=r.get("anchor"),
                    anchor_position=r.get("anchor_position", "after"),
                    group=r.get("group", 0),
                    post_processors=[
                        PostProcessor(p) for p in r.get("post_processors", [])
                    ],
                )
                for r in field_data.get("rules", [])
            ]

            fields.append(
                TemplateField(
                    name=field_data.get("name", ""),
                    label=field_data.get("label"),
                    field_type=field_data.get("field_type", "text"),
                    group=field_data.get("group"),
                    rules=rules,
                    required=field_data.get("required", False),
                    default_value=field_data.get("default_value"),
                    description=field_data.get("description"),
                    min_confidence=field_data.get("min_confidence", 0.5),
                    order=field_data.get("order", 0),
                    is_key_field=field_data.get("is_key_field", False),
                )
            )

        return ExtractionTemplate(
            id=data.get("id", ""),
            tenant_id=data.get("tenant_id"),
            name=data.get("name", ""),
            description=data.get("description"),
            document_type=data.get("document_type", ""),
            category=TemplateCategory(data.get("category", "other")),
            status=TemplateStatus(data.get("status", "draft")),
            fields=fields,
            detection_keywords=data.get("detection_keywords", []),
            detection_patterns=data.get("detection_patterns", []),
            min_detection_score=data.get("min_detection_score", 0.7),
            version=data.get("version", 1),
            tags=data.get("tags", []),
            is_official=data.get("is_official", False),
            is_public=data.get("is_public", False),
        )

    def get_builtin_templates(self) -> List[ExtractionTemplate]:
        """Retorna templates builtin."""
        return [t for t in self._templates.values() if t.is_official]

    def export_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Exporta template como dicionario."""
        template = self.get_template(template_id)
        if template:
            return template.to_dict()
        return None

    def import_template(
        self,
        data: Dict[str, Any],
        tenant_id: Optional[str] = None,
    ) -> ExtractionTemplate:
        """Importa template de dicionario."""
        template = self._dict_to_template(data)
        template.tenant_id = tenant_id
        template.is_official = False
        return self.create_template(template)
