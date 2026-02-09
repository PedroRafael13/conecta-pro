"""
Model DisciplinaryTemplate - Template de Documento Disciplinar.

Este modelo armazena templates de documentos para medidas disciplinares,
permitindo geracao automatica de documentos com placeholders.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score Target: 99+/100
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class DisciplinaryTemplate(Base):
    """
    Modelo de Template de Documento Disciplinar.

    Armazena templates de documentos que serao utilizados para gerar
    advertencias, suspensoes e demissoes. Suporta placeholders que
    serao substituidos no momento da geracao.

    Placeholders disponiveis:
        {{employee_name}} - Nome do funcionario
        {{employee_cpf}} - CPF do funcionario
        {{employee_position}} - Cargo do funcionario
        {{employee_admission_date}} - Data de admissao
        {{incident_date}} - Data do incidente
        {{application_date}} - Data de aplicacao
        {{reason_description}} - Descricao do motivo
        {{reason_category}} - Categoria do motivo
        {{company_name}} - Nome da empresa
        {{company_cnpj}} - CNPJ da empresa
        {{suspension_days}} - Dias de suspensao
        {{suspension_start_date}} - Inicio suspensao
        {{suspension_end_date}} - Fim suspensao
        {{witness_1_name}} - Nome testemunha 1
        {{witness_1_cpf}} - CPF testemunha 1
        {{witness_2_name}} - Nome testemunha 2
        {{witness_2_cpf}} - CPF testemunha 2
        {{current_date}} - Data atual
        {{previous_warnings}} - Advertencias anteriores
        {{previous_suspensions}} - Suspensoes anteriores

    Attributes:
        id: Identificador unico UUID
        tenant_id: ID do tenant (multi-tenancy)
        action_type: Tipo de medida que este template atende
        name: Nome do template
        description: Descricao do template
        content: Conteudo do template com placeholders
        is_default: Se e o template padrao para o tipo
        is_active: Se template esta ativo
        created_at: Data criacao
        updated_at: Data ultima atualizacao
        created_by: Usuario que criou
    """

    __tablename__ = "disciplinary_templates"

    # === Identificacao ===
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    tenant_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        nullable=False,
        index=True,
        comment="ID do tenant para multi-tenancy",
    )

    # === Dados do Template ===
    action_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
        comment="Tipo de medida: advertencia_verbal, advertencia_escrita, suspensao, demissao_justa_causa",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Nome do template",
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="Descricao do template",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Conteudo do template com placeholders {{...}}",
    )

    # === Configuracoes ===
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Se e o template padrao para este tipo de medida",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Se template esta ativo",
    )

    # === Controle ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="Data de criacao",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Data ultima atualizacao",
    )
    created_by: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        nullable=True,
        comment="ID do usuario que criou",
    )

    def __repr__(self) -> str:
        """Representacao string do objeto."""
        return f"<DisciplinaryTemplate {self.name} ({self.action_type})>"

    @property
    def placeholder_list(self) -> list[str]:
        """Retorna lista de placeholders encontrados no template."""
        import re

        pattern = r"\{\{(\w+)\}\}"
        matches = re.findall(pattern, self.content)
        return list(set(matches))

    def render(self, context: dict[str, str]) -> str:
        """
        Renderiza o template substituindo placeholders.

        Args:
            context: Dicionario com valores para substituicao
                     Ex: {"employee_name": "Joao Silva", "incident_date": "01/01/2026"}

        Returns:
            Texto do documento com placeholders substituidos
        """
        result = self.content

        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value) if value else "")

        return result

    @classmethod
    def get_available_placeholders(cls) -> dict[str, str]:
        """
        Retorna dicionario com todos os placeholders disponiveis e suas descricoes.

        Returns:
            Dict com placeholder como chave e descricao como valor
        """
        return {
            "employee_name": "Nome completo do funcionario",
            "employee_cpf": "CPF do funcionario (formatado)",
            "employee_position": "Cargo do funcionario",
            "employee_admission_date": "Data de admissao (DD/MM/AAAA)",
            "incident_date": "Data do incidente (DD/MM/AAAA)",
            "application_date": "Data de aplicacao da medida (DD/MM/AAAA)",
            "reason_description": "Descricao detalhada do motivo",
            "reason_category": "Categoria do motivo",
            "reason_category_display": "Nome de exibicao da categoria",
            "company_name": "Razao social da empresa",
            "company_cnpj": "CNPJ da empresa (formatado)",
            "suspension_days": "Numero de dias de suspensao",
            "suspension_start_date": "Data inicio da suspensao (DD/MM/AAAA)",
            "suspension_end_date": "Data fim da suspensao (DD/MM/AAAA)",
            "witness_1_name": "Nome da primeira testemunha",
            "witness_1_cpf": "CPF da primeira testemunha",
            "witness_2_name": "Nome da segunda testemunha",
            "witness_2_cpf": "CPF da segunda testemunha",
            "current_date": "Data atual (DD/MM/AAAA)",
            "current_datetime": "Data e hora atual",
            "previous_warnings": "Numero de advertencias anteriores",
            "previous_suspensions": "Numero de suspensoes anteriores",
            "post_name": "Nome do posto de trabalho",
            "client_name": "Nome do cliente",
            "city": "Cidade",
            "state": "Estado (UF)",
        }


# Templates padrao que serao criados na migracao inicial
DEFAULT_TEMPLATES = {
    "advertencia_verbal": {
        "name": "Advertencia Verbal - Padrao",
        "description": "Template padrao para advertencias verbais",
        "content": """ADVERTENCIA VERBAL

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento registrar ADVERTENCIA VERBAL ao(a) funcionario(a):

FUNCIONARIO: {{employee_name}}
CPF: {{employee_cpf}}
CARGO: {{employee_position}}
DATA DE ADMISSAO: {{employee_admission_date}}

MOTIVO DA ADVERTENCIA:
{{reason_description}}

DATA DO INCIDENTE: {{incident_date}}

O(A) funcionario(a) acima identificado(a) esta sendo advertido(a) verbalmente em razao do fato descrito acima, ficando ciente de que a reincidencia podera acarretar em penalidades mais severas, conforme legislacao trabalhista vigente.

Esta advertencia verbal fica registrada para fins de historico disciplinar.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
{{employee_name}}
Funcionario(a)
""",
    },
    "advertencia_escrita": {
        "name": "Advertencia Escrita - Padrao",
        "description": "Template padrao para advertencias escritas",
        "content": """ADVERTENCIA ESCRITA

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento aplicar ADVERTENCIA ESCRITA ao(a) funcionario(a) abaixo identificado(a):

DADOS DO FUNCIONARIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissao: {{employee_admission_date}}
Local de Trabalho: {{post_name}}

HISTORICO DISCIPLINAR:
Advertencias anteriores: {{previous_warnings}}
Suspensoes anteriores: {{previous_suspensions}}

DESCRICAO DA OCORRENCIA:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTACAO LEGAL:
Esta advertencia esta fundamentada no Art. 482 da CLT e no regulamento interno da empresa, servindo como registro formal de conduta inadequada.

CIENCIA:
O(A) funcionario(a) declara estar ciente de que:
1. A reincidencia podera resultar em suspensao disciplinar;
2. Novas infrações poderão ensejar rescisão por justa causa;
3. Esta advertencia ficara arquivada em seu prontuario.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
{{employee_name}}
Funcionario(a)

TESTEMUNHAS (em caso de recusa de assinatura):

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
    },
    "suspensao": {
        "name": "Suspensao Disciplinar - Padrao",
        "description": "Template padrao para suspensoes disciplinares",
        "content": """TERMO DE SUSPENSAO DISCIPLINAR

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, vem por meio deste documento aplicar SUSPENSAO DISCIPLINAR ao(a) funcionario(a) abaixo identificado(a):

DADOS DO FUNCIONARIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissao: {{employee_admission_date}}
Local de Trabalho: {{post_name}}

HISTORICO DISCIPLINAR:
Advertencias anteriores: {{previous_warnings}}
Suspensoes anteriores: {{previous_suspensions}}

PERIODO DA SUSPENSAO:
Data de Inicio: {{suspension_start_date}}
Data de Termino: {{suspension_end_date}}
Total de Dias: {{suspension_days}} dias

DESCRICAO DA OCORRENCIA:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTACAO LEGAL:
Esta suspensão disciplinar está fundamentada no Art. 474 da CLT, limitada ao máximo de 30 dias consecutivos, e decorre das seguintes justificativas:
- Reincidencia em condutas inadequadas apesar de advertencias anteriores;
- Gravidade da falta cometida que justifica medida mais severa.

CONSEQUENCIAS:
1. Durante o periodo de suspensao, o contrato de trabalho fica suspenso;
2. Nao havera remuneracao correspondente aos dias de suspensao;
3. O periodo de suspensao nao sera computado para ferias e 13o salario;
4. O(A) funcionario(a) devera retornar ao trabalho no primeiro dia util apos o termino da suspensao.

CIENCIA:
O(A) funcionario(a) declara estar ciente de que nova infraçao podera resultar em demissao por justa causa.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
Departamento de Recursos Humanos

_________________________________
{{employee_name}}
Funcionario(a)

TESTEMUNHAS (em caso de recusa de assinatura):

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
    },
    "demissao_justa_causa": {
        "name": "Demissao por Justa Causa - Padrao",
        "description": "Template padrao para demissoes por justa causa",
        "content": """TERMO DE RESCISAO DO CONTRATO DE TRABALHO POR JUSTA CAUSA

A empresa {{company_name}}, inscrita no CNPJ {{company_cnpj}}, comunica a RESCISAO DO CONTRATO DE TRABALHO POR JUSTA CAUSA do(a) funcionario(a) abaixo identificado(a):

DADOS DO FUNCIONARIO:
Nome: {{employee_name}}
CPF: {{employee_cpf}}
Cargo: {{employee_position}}
Data de Admissao: {{employee_admission_date}}
Data da Rescisao: {{application_date}}
Local de Trabalho: {{post_name}}

HISTORICO DISCIPLINAR:
Advertencias anteriores: {{previous_warnings}}
Suspensoes anteriores: {{previous_suspensions}}

DESCRICAO DA FALTA GRAVE:
Data do Incidente: {{incident_date}}
Categoria: {{reason_category_display}}

{{reason_description}}

FUNDAMENTACAO LEGAL:
A presente rescisão por justa causa está fundamentada no Art. 482 da Consolidação das Leis do Trabalho (CLT), especificamente na(s) alinea(s) aplicavel(is) ao caso:

a) Ato de improbidade;
b) Incontinencia de conduta ou mau procedimento;
c) Negociacao habitual por conta propria;
d) Condenacao criminal do empregado;
e) Desidia no desempenho das funcoes;
f) Embriaguez habitual ou em servico;
g) Violacao de segredo da empresa;
h) Ato de indisciplina ou de insubordinacao;
i) Abandono de emprego;
j) Ato lesivo da honra ou da boa fama;
k) Ofensas fisicas;
l) Pratica constante de jogos de azar;
m) Perda da habilitacao profissional.

VERBAS RESCISORIAS:
Conforme Art. 477 da CLT, o(a) funcionario(a) tera direito apenas as seguintes verbas:
- Saldo de salario
- Ferias vencidas + 1/3 (se houver)

NAO tera direito a:
- Aviso previo
- Ferias proporcionais + 1/3
- 13o salario proporcional
- Multa de 40% do FGTS
- Seguro-desemprego

CIENCIA:
O(A) funcionario(a) declara ciencia da presente rescisao e de seus motivos, reservando-se o direito de questiona-la perante a Justica do Trabalho.

{{city}}, {{current_date}}

_________________________________
Empregador/Representante Legal

_________________________________
Departamento de Recursos Humanos

_________________________________
{{employee_name}}
Funcionario(a)

TESTEMUNHAS:

1. _________________________________
   Nome: {{witness_1_name}}
   CPF: {{witness_1_cpf}}

2. _________________________________
   Nome: {{witness_2_name}}
   CPF: {{witness_2_cpf}}
""",
    },
}
