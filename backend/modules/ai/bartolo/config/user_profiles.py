"""
Perfis de Usuario do Bartolo.

Define como o Bartolo adapta suas respostas baseado no cargo,
departamento e nivel de acesso do usuario.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """Cargos/funcoes dos usuarios."""
    # Diretoria
    DIRETOR = "diretor"
    SOCIO = "socio"

    # Gerencia
    GERENTE_GERAL = "gerente_geral"
    GERENTE_OPERACOES = "gerente_operacoes"
    GERENTE_RH = "gerente_rh"
    GERENTE_FINANCEIRO = "gerente_financeiro"
    GERENTE_COMERCIAL = "gerente_comercial"

    # Coordenacao
    COORDENADOR_OPERACOES = "coordenador_operacoes"
    COORDENADOR_RH = "coordenador_rh"
    COORDENADOR_FINANCEIRO = "coordenador_financeiro"
    ENCARREGADO = "encarregado"  # Coordena grupo de postos

    # Supervisao
    SUPERVISOR_OPERACOES = "supervisor_operacoes"
    SUPERVISOR_SEGURANCA = "supervisor_seguranca"
    INSPETOR = "inspetor"  # Fiscaliza qualidade em campo

    # Analistas
    ANALISTA_RH = "analista_rh"
    ANALISTA_FINANCEIRO = "analista_financeiro"
    ANALISTA_COMERCIAL = "analista_comercial"
    ANALISTA_LICITACOES = "analista_licitacoes"
    ANALISTA_DP = "analista_dp"  # Departamento Pessoal

    # Assistentes
    ASSISTENTE_ADMINISTRATIVO = "assistente_administrativo"
    ASSISTENTE_RH = "assistente_rh"
    ASSISTENTE_FINANCEIRO = "assistente_financeiro"

    # Operacional de Campo
    LIDER_POSTO = "lider_posto"  # Lidera equipe no posto
    PORTEIRO = "porteiro"
    VIGILANTE = "vigilante"
    ZELADOR = "zelador"
    RECEPCIONISTA = "recepcionista"
    AUXILIAR_LIMPEZA = "auxiliar_limpeza"

    # Sistema
    ADMIN = "admin"
    SUPORTE = "suporte"


class Department(str, Enum):
    """Departamentos."""
    DIRETORIA = "diretoria"
    COMERCIAL = "comercial"
    OPERACOES = "operacoes"
    RH = "rh"
    FINANCEIRO = "financeiro"
    ADMINISTRATIVO = "administrativo"
    LICITACOES = "licitacoes"
    TI = "ti"


@dataclass
class UserProfile:
    """Perfil de usuario para contextualizacao."""
    user_id: int
    name: str
    role: UserRole
    department: Department
    is_manager: bool = False
    direct_reports: int = 0
    experience_level: str = "intermediate"  # beginner, intermediate, advanced
    preferences: dict = field(default_factory=dict)
    permissions: list = field(default_factory=list)


# Configuracao de perfis por cargo
USER_PROFILES = {
    # ==========================================
    # DIRETORIA
    # ==========================================
    UserRole.DIRETOR: {
        "department": Department.DIRETORIA,
        "is_manager": True,
        "level": "executive",
        "focus": ["visao_geral", "indicadores", "decisoes_estrategicas"],
        "modules_priority": ["relatorios", "financial", "crm", "licitacoes"],
        "communication_style": "executive_summary",
        "prompt_context": """
Este usuario e um diretor da empresa.
- Preferencia por visao macro e indicadores
- Foco em resultados e tomada de decisao
- Respostas objetivas e executivas
- Destaque impactos financeiros e estrategicos
- Oferecer insights e recomendacoes
""",
    },

    UserRole.SOCIO: {
        "department": Department.DIRETORIA,
        "is_manager": True,
        "level": "executive",
        "focus": ["rentabilidade", "crescimento", "riscos"],
        "modules_priority": ["financial", "relatorios", "licitacoes", "crm"],
        "communication_style": "executive_summary",
        "prompt_context": """
Este usuario e socio da empresa.
- Interesse em rentabilidade e ROI
- Visao de longo prazo
- Analise de riscos e oportunidades
- Comparativos e benchmarks
""",
    },

    # ==========================================
    # GERENCIA
    # ==========================================
    UserRole.GERENTE_GERAL: {
        "department": Department.DIRETORIA,
        "is_manager": True,
        "level": "management",
        "focus": ["operacoes", "pessoas", "resultados", "clientes"],
        "modules_priority": ["operacoes", "hr", "crm", "financial", "relatorios"],
        "communication_style": "detailed_summary",
        "prompt_context": """
Este usuario e gerente geral.
- Visao integrada de todas as areas
- Foco em performance e metas
- Gestao de equipes e processos
- Acompanhamento de indicadores
""",
    },

    UserRole.GERENTE_OPERACOES: {
        "department": Department.OPERACOES,
        "is_manager": True,
        "level": "management",
        "focus": ["escalas", "alocacoes", "ocorrencias", "qualidade"],
        "modules_priority": ["operacoes", "escalas", "ponto", "hr"],
        "communication_style": "operational",
        "prompt_context": """
Este usuario e gerente de operacoes.
- Foco em escalas e alocacoes
- Gestao de equipes de campo
- Resolucao de problemas operacionais
- Qualidade do servico ao cliente
""",
    },

    UserRole.GERENTE_RH: {
        "department": Department.RH,
        "is_manager": True,
        "level": "management",
        "focus": ["pessoas", "folha", "compliance", "desenvolvimento"],
        "modules_priority": ["hr", "folha_pagamento", "ponto", "recrutamento", "saude_ocupacional"],
        "communication_style": "detailed",
        "prompt_context": """
Este usuario e gerente de RH.
- Gestao de pessoas e desenvolvimento
- Folha de pagamento e encargos
- Compliance trabalhista (CLT, eSocial)
- Recrutamento e retencao
""",
    },

    UserRole.GERENTE_FINANCEIRO: {
        "department": Department.FINANCEIRO,
        "is_manager": True,
        "level": "management",
        "focus": ["fluxo_caixa", "custos", "faturamento", "contabilidade"],
        "modules_priority": ["financial", "faturamento", "contabilidade", "relatorios"],
        "communication_style": "analytical",
        "prompt_context": """
Este usuario e gerente financeiro.
- Controle de fluxo de caixa
- Analise de custos e rentabilidade
- Faturamento e cobranca
- Contabilidade e fiscal
""",
    },

    UserRole.GERENTE_COMERCIAL: {
        "department": Department.COMERCIAL,
        "is_manager": True,
        "level": "management",
        "focus": ["vendas", "propostas", "licitacoes", "relacionamento"],
        "modules_priority": ["crm", "propostas", "licitacoes", "contratos"],
        "communication_style": "commercial",
        "prompt_context": """
Este usuario e gerente comercial.
- Gestao de vendas e metas
- Elaboracao de propostas
- Participacao em licitacoes
- Relacionamento com clientes
""",
    },

    # ==========================================
    # ANALISTAS
    # ==========================================
    UserRole.ANALISTA_RH: {
        "department": Department.RH,
        "is_manager": False,
        "level": "analyst",
        "focus": ["admissoes", "folha", "beneficios", "ponto"],
        "modules_priority": ["hr", "folha_pagamento", "ponto", "recrutamento"],
        "communication_style": "detailed",
        "prompt_context": """
Este usuario e analista de RH.
- Processos de admissao e demissao
- Calculo de folha e encargos
- Gestao de beneficios
- Controle de ponto
Pode precisar de orientacao em calculos complexos.
""",
    },

    UserRole.ANALISTA_FINANCEIRO: {
        "department": Department.FINANCEIRO,
        "is_manager": False,
        "level": "analyst",
        "focus": ["contas_pagar", "contas_receber", "conciliacao"],
        "modules_priority": ["financial", "faturamento", "contabilidade"],
        "communication_style": "analytical",
        "prompt_context": """
Este usuario e analista financeiro.
- Contas a pagar e receber
- Conciliacao bancaria
- Lancamentos contabeis
- Relatorios financeiros
""",
    },

    UserRole.ANALISTA_COMERCIAL: {
        "department": Department.COMERCIAL,
        "is_manager": False,
        "level": "analyst",
        "focus": ["leads", "propostas", "orcamentos"],
        "modules_priority": ["crm", "propostas", "clientes"],
        "communication_style": "commercial",
        "prompt_context": """
Este usuario e analista comercial.
- Gestao de leads e oportunidades
- Elaboracao de propostas
- Calculo de orcamentos
- Acompanhamento de clientes
Pode precisar de ajuda para montar propostas e calcular custos.
""",
    },

    UserRole.ANALISTA_LICITACOES: {
        "department": Department.LICITACOES,
        "is_manager": False,
        "level": "analyst",
        "focus": ["editais", "propostas", "certidoes", "prazos"],
        "modules_priority": ["licitacoes", "certidoes", "propostas"],
        "communication_style": "detailed",
        "prompt_context": """
Este usuario e analista de licitacoes.
- Analise de editais
- Elaboracao de propostas para licitacoes
- Controle de certidoes e documentos
- Acompanhamento de prazos
Conhece bem a Lei 14.133/2021 e processos licitatorios.
""",
    },

    # ==========================================
    # ASSISTENTES
    # ==========================================
    UserRole.ASSISTENTE_ADMINISTRATIVO: {
        "department": Department.ADMINISTRATIVO,
        "is_manager": False,
        "level": "assistant",
        "focus": ["cadastros", "documentos", "rotinas"],
        "modules_priority": ["clientes", "contratos", "inventario"],
        "communication_style": "step_by_step",
        "prompt_context": """
Este usuario e assistente administrativo.
- Cadastros e atualizacoes
- Organizacao de documentos
- Rotinas administrativas
Pode precisar de orientacao passo a passo.
""",
    },

    UserRole.ASSISTENTE_RH: {
        "department": Department.RH,
        "is_manager": False,
        "level": "assistant",
        "focus": ["cadastros", "documentos", "ponto"],
        "modules_priority": ["hr", "ponto", "recrutamento"],
        "communication_style": "step_by_step",
        "prompt_context": """
Este usuario e assistente de RH.
- Cadastro de funcionarios
- Controle de documentos
- Apoio em processos de RH
Pode precisar de orientacao detalhada.
""",
    },

    # ==========================================
    # OPERACIONAL - GESTAO
    # ==========================================
    UserRole.SUPERVISOR_OPERACOES: {
        "department": Department.OPERACOES,
        "is_manager": True,
        "level": "supervisor",
        "focus": ["equipe", "ocorrencias", "escalas", "substituicoes", "qualidade"],
        "modules_priority": ["operacoes", "escalas", "ponto", "ocorrencias", "medidas"],
        "communication_style": "operational",
        "prompt_context": """
Este usuario e SUPERVISOR DE OPERACOES.

RESPONSABILIDADES:
- Gerenciar equipes de campo em varios postos
- Montar e ajustar escalas mensais
- Resolver substituicoes e faltas
- Analisar e resolver ocorrencias
- Aplicar medidas administrativas (advertencias)
- Acompanhar banco de horas da equipe
- Garantir qualidade do servico ao cliente

PODE FAZER:
- Consultar e editar escalas dos seus postos
- Registrar e resolver ocorrencias
- Criar advertencias (verbais e escritas)
- Aprovar banco de horas
- Solicitar substituicoes
- Ver relatorios operacionais

PRECISA APROVACAO PARA:
- Suspensoes (aprovacao do gerente)
- Horas extras acima do limite mensal
- Contratacao de diaristas

COMUNICACAO:
- Use linguagem operacional objetiva
- Foque em solucoes praticas
- Destaque pendencias urgentes
- Oriente sobre processos e CLT
""",
    },

    UserRole.ENCARREGADO: {
        "department": Department.OPERACOES,
        "is_manager": True,
        "level": "coordinator",
        "focus": ["grupo_postos", "escalas", "funcionarios", "clientes", "medidas"],
        "modules_priority": ["operacoes", "escalas", "ocorrencias", "ponto", "medidas", "diaristas"],
        "communication_style": "operational_detailed",
        "prompt_context": """
Este usuario e ENCARREGADO de operacoes.

RESPONSABILIDADES:
- Coordenar grupo de postos (regiao ou cliente especifico)
- Montar e ajustar escalas mensais
- Gerenciar substituicoes e cobertura
- Aplicar medidas administrativas
- Resolver problemas operacionais complexos
- Interface entre campo e escritorio
- Acompanhar indicadores de performance

PODE FAZER:
- Gerenciar todas as escalas dos seus postos
- Criar e submeter advertencias e suspensoes
- Alocar e desalocar funcionarios
- Aprovar banco de horas
- Contratar diaristas para cobertura
- Ver relatorios completos da sua area
- Resolver ocorrencias

PRECISA APROVACAO PARA:
- Suspensoes acima de 3 dias (gerente)
- Demissoes por justa causa
- Horas extras acima do orcamento

COMUNICACAO:
- Linguagem operacional com detalhes tecnicos
- Foque em gestao de equipe e processos
- Oriente sobre legislacao trabalhista
- Destaque impactos no cliente
""",
    },

    UserRole.INSPETOR: {
        "department": Department.OPERACOES,
        "is_manager": False,
        "level": "field_supervisor",
        "focus": ["qualidade", "fiscalizacao", "ocorrencias", "clientes"],
        "modules_priority": ["operacoes", "ocorrencias", "escalas", "clientes"],
        "communication_style": "operational",
        "prompt_context": """
Este usuario e INSPETOR de operacoes.

RESPONSABILIDADES:
- Fiscalizar postos de trabalho in loco
- Verificar qualidade do servico prestado
- Registrar ocorrencias durante visitas
- Avaliar funcionarios em campo
- Resolver problemas pontuais com clientes
- Acompanhar substituicoes e cobertura
- Reportar irregularidades

PODE FAZER:
- Registrar ocorrencias em qualquer posto que visitar
- Ver escala de todos os postos da sua regiao
- Consultar historico de funcionarios
- Solicitar substituicoes urgentes
- Registrar advertencias verbais
- Ver relatorios de cobertura

NAO PODE FAZER:
- Aprovar medidas administrativas escritas
- Alterar escalas ja publicadas
- Acessar dados financeiros ou salariais

COMUNICACAO:
- Linguagem operacional e objetiva
- Foque em acoes praticas e corretivas
- Alerte sobre problemas urgentes
- Sugira solucoes rapidas
""",
    },

    # ==========================================
    # OPERACIONAL - CAMPO
    # ==========================================
    UserRole.LIDER_POSTO: {
        "department": Department.OPERACOES,
        "is_manager": False,
        "level": "team_lead",
        "focus": ["equipe_posto", "escala_posto", "ocorrencias_locais", "ponto"],
        "modules_priority": ["operacoes", "ponto", "ocorrencias"],
        "communication_style": "simple_operational",
        "prompt_context": """
Este usuario e LIDER DE POSTO.

RESPONSABILIDADES:
- Coordenar a equipe no seu posto de trabalho
- Distribuir tarefas diarias
- Registrar ocorrencias do posto
- Controlar presenca da equipe (check-in/out)
- Ser ponto de contato com o cliente
- Reportar problemas ao supervisor

PODE FAZER:
- Ver a escala do seu posto
- Registrar check-in e check-out da equipe
- Criar ocorrencias do seu posto
- Consultar banco de horas da sua equipe
- Solicitar substituicao quando alguem falta

NAO PODE FAZER:
- Ver outros postos ou clientes
- Aplicar medidas administrativas
- Aprovar horas extras
- Alterar escalas

COMUNICACAO:
- Use linguagem simples e direta
- Foque nas tarefas do dia a dia do posto
- Oriente sobre procedimentos basicos
- Escale problemas complexos para o supervisor
""",
    },

    UserRole.PORTEIRO: {
        "department": Department.OPERACOES,
        "is_manager": False,
        "level": "operational",
        "focus": ["meu_ponto", "minha_escala", "ocorrencias_simples"],
        "modules_priority": ["ponto", "operacoes"],
        "communication_style": "simple",
        "prompt_context": """
Este usuario e PORTEIRO.

PODE FAZER:
- Registrar seu ponto (check-in e check-out)
- Consultar sua escala de trabalho
- Ver seu saldo de banco de horas
- Registrar ocorrencias simples
- Ver seus holerites

COMUNICACAO:
- Use linguagem SIMPLES e DIRETA
- Evite termos tecnicos
- Seja objetivo nas respostas
- Oriente passo a passo quando necessario
""",
    },

    UserRole.VIGILANTE: {
        "department": Department.OPERACOES,
        "is_manager": False,
        "level": "operational",
        "focus": ["meu_ponto", "minha_escala", "ocorrencias_seguranca"],
        "modules_priority": ["ponto", "operacoes"],
        "communication_style": "simple",
        "prompt_context": """
Este usuario e VIGILANTE.

PODE FAZER:
- Registrar seu ponto (check-in e check-out)
- Consultar sua escala de trabalho
- Ver seu saldo de banco de horas
- Registrar ocorrencias de seguranca
- Ver seus holerites

COMUNICACAO:
- Use linguagem SIMPLES e DIRETA
- Foque em seguranca e procedimentos
- Seja objetivo
""",
    },

    UserRole.AUXILIAR_LIMPEZA: {
        "department": Department.OPERACOES,
        "is_manager": False,
        "level": "operational",
        "focus": ["meu_ponto", "minha_escala"],
        "modules_priority": ["ponto"],
        "communication_style": "simple",
        "prompt_context": """
Este usuario e AUXILIAR DE LIMPEZA.

PODE FAZER:
- Registrar seu ponto (check-in e check-out)
- Consultar sua escala de trabalho
- Ver seu saldo de banco de horas
- Ver seus holerites

COMUNICACAO:
- Use linguagem MUITO SIMPLES
- Seja direto e claro
- Oriente passo a passo
""",
    },

    # ==========================================
    # DEPARTAMENTO PESSOAL
    # ==========================================
    UserRole.ANALISTA_DP: {
        "department": Department.RH,
        "is_manager": False,
        "level": "analyst",
        "focus": ["folha", "ponto", "afastamentos", "medidas", "esocial"],
        "modules_priority": ["hr", "folha_pagamento", "ponto", "operacoes", "medidas"],
        "communication_style": "detailed",
        "prompt_context": """
Este usuario e ANALISTA DE DEPARTAMENTO PESSOAL.

RESPONSABILIDADES:
- Processar folha de pagamento
- Controlar ponto e banco de horas
- Gerenciar afastamentos (atestados, licencas)
- Aprovar medidas administrativas
- Calcular rescisoes
- Enviar eventos ao eSocial
- Manter prontuarios atualizados

PODE FAZER:
- Aprovar ou rejeitar medidas administrativas
- Ajustar banco de horas
- Registrar afastamentos
- Calcular descontos de faltas e suspensoes
- Consultar historico de qualquer funcionario

INTEGRACAO COM OPERACIONAL:
- Recebe medidas administrativas para aprovacao
- Processa suspensoes (gera afastamento + desconto)
- Valida atestados medicos
- Informa ferias e afastamentos ao operacional

COMUNICACAO:
- Linguagem tecnica de RH/DP
- Foque em legislacao trabalhista
- Oriente sobre processos e prazos
- Destaque implicacoes legais
""",
    },

    # ==========================================
    # SISTEMA
    # ==========================================
    UserRole.ADMIN: {
        "department": Department.TI,
        "is_manager": True,
        "level": "admin",
        "focus": ["configuracoes", "usuarios", "integracoes"],
        "modules_priority": ["all"],
        "communication_style": "technical",
        "prompt_context": """
Este usuario e administrador do sistema.
- Acesso total a todas as funcionalidades
- Configuracoes avancadas
- Gestao de usuarios e permissoes
Pode usar linguagem tecnica.
""",
    },
}


def get_profile_context(role: UserRole) -> str:
    """Retorna contexto de prompt para o perfil."""
    profile = USER_PROFILES.get(role)
    if profile:
        return profile.get("prompt_context", "")
    return ""


def get_profile_modules(role: UserRole) -> list:
    """Retorna modulos prioritarios para o perfil."""
    profile = USER_PROFILES.get(role)
    if profile:
        return profile.get("modules_priority", [])
    return []


def get_communication_style(role: UserRole) -> str:
    """Retorna estilo de comunicacao para o perfil."""
    profile = USER_PROFILES.get(role)
    if profile:
        return profile.get("communication_style", "detailed")
    return "detailed"


def adapt_response_for_profile(response: str, role: UserRole) -> str:
    """Adapta resposta para o perfil do usuario."""
    style = get_communication_style(role)

    # Por enquanto retorna como esta, mas pode ser expandido
    # para formatar a resposta de acordo com o estilo
    return response
