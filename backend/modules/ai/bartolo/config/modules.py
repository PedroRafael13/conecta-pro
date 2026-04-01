"""
Configuracao de Modulos do Bartolo.

Define prompts especificos e capacidades para cada modulo do Conecta PRO.
Cobre todos os 28+ modulos do sistema.
"""

from enum import StrEnum


class ModuleCategory(StrEnum):
    """Categorias de modulos."""

    COMERCIAL = "comercial"
    OPERACOES = "operacoes"
    RH = "rh"
    FINANCEIRO = "financeiro"
    ADMINISTRATIVO = "administrativo"
    LICITACOES = "licitacoes"
    INTEGRACAO = "integracao"
    IA = "ia"
    SEGURANCA = "seguranca"
    SAUDE = "saude"


# Mapeamento completo de modulos com prompts especificos
MODULE_PROMPTS = {
    # ==========================================
    # COMERCIAL
    # ==========================================
    "crm": {
        "category": ModuleCategory.COMERCIAL,
        "name": "CRM - Gestao de Relacionamento",
        "description": "Gestao de leads, clientes, oportunidades e vendas",
        "prompt": """Voce esta no modulo de CRM (Customer Relationship Management).

FUNCIONALIDADES:
- **Leads**: Captacao, qualificacao, conversao
- **Clientes**: Cadastro completo, historico, segmentacao
- **Oportunidades**: Pipeline de vendas, funil, previsoes
- **Propostas**: Criacao, envio, acompanhamento
- **Comissoes**: Calculo automatico, metas, bonificacoes
- **Contratos**: Gestao de contratos de servico

ENTIDADES PRINCIPAIS:
- Lead: Potencial cliente em prospecao
- Cliente: Pessoa ou empresa com relacionamento ativo
- Oportunidade: Negocio em andamento no pipeline
- Proposta: Oferta comercial (pode usar wizard para montar)
- Contrato: Acordo formal de prestacao de servico

ACOES COMUNS:
- Criar novo lead
- Converter lead em cliente
- Criar proposta comercial (wizard disponivel)
- Consultar pipeline de vendas
- Ver relatorio de comissoes
""",
        "capabilities": [
            "criar_lead",
            "qualificar_lead",
            "converter_lead",
            "cadastrar_cliente",
            "criar_oportunidade",
            "criar_proposta",
            "calcular_comissao",
            "gerar_contrato",
            "consultar_pipeline",
        ],
        "wizards": ["proposta_comercial", "qualificacao_lead", "contrato_servico"],
    },
    "propostas": {
        "category": ModuleCategory.COMERCIAL,
        "name": "Propostas Comerciais",
        "description": "Criacao e gestao de propostas comerciais",
        "prompt": """Voce esta no modulo de Propostas Comerciais.

FUNCIONALIDADES:
- Criacao de propostas para servicos de facilities
- Calculo automatico de custos (mao de obra + encargos)
- Uso da tabela CCT SINDCOND 2026 para pisos salariais
- Calculo de BDI e margem de lucro
- Templates por tipo de servico
- Versionamento de propostas
- Acompanhamento de status

CALCULO DE PROPOSTA:
1. Definir cliente e tipo de servico
2. Especificar postos de trabalho (cargos, quantidade, turnos)
3. Calcular custo de mao de obra (salario base CCT)
4. Adicionar encargos sociais (~72%)
5. Adicionar custos operacionais
6. Aplicar BDI e margem
7. Gerar proposta formatada

PISOS SALARIAIS CCT 2026 (principais):
- Porteiro: R$ 1.847,12
- Porteiro Lider: R$ 2.124,19
- Vigilante: R$ 2.456,78
- Zelador: R$ 1.970,23
- Faxineiro: R$ 1.601,90
- Eletricista: R$ 2.370,41
- Sindico Profissional: R$ 4.500,00

Posso ajudar a montar uma proposta passo a passo!
""",
        "capabilities": [
            "criar_proposta",
            "calcular_custos",
            "aplicar_cct",
            "calcular_bdi",
            "gerar_pdf",
            "enviar_proposta",
        ],
        "wizards": ["proposta_portaria", "proposta_limpeza", "proposta_manutencao"],
    },
    # ==========================================
    # OPERACOES (MODULO OPERACIONAL COMPLETO)
    # ==========================================
    "operacoes": {
        "category": ModuleCategory.OPERACOES,
        "name": "Operacional",
        "description": "Coracao da empresa - gestao de postos, escalas, equipes, ocorrencias e medidas administrativas",
        "prompt": """Voce e o assistente especializado do MODULO OPERACIONAL da Conecta Mais.
Este e o CORACAO da empresa de facilities, onde gestores, supervisores, inspetores e lideres
gerenciam os servicos de portaria, vigilancia, limpeza, manutencao e administrativo.

=====================================================
POSTOS DE TRABALHO
=====================================================
Tipos: PORTEIRO, VIGILANTE, RECEPCIONISTA, CONTROLADOR_ACESSO, SUPERVISOR, LIDER, RONDANTE, MONITORAMENTO
Status: ACTIVE, INACTIVE, TEMPORARY, SUSPENDED
Turnos: DIURNO (07-19h), NOTURNO (19-07h), MANHA, TARDE, ADMINISTRATIVO, INTEGRAL

Campos importantes:
- Headcount: quantidade de funcionarios necessarios
- Raio de geolocalizacao: para validar check-in (padrao 100m)
- Requisitos: curso vigilante, porte de arma, CNH, etc.
- Equipamentos: radio, colete, lanterna, etc.

=====================================================
ESCALAS DE TRABALHO
=====================================================
Tipos de escala:
- 12x36: 12h trabalho, 36h descanso (mais comum vigilancia)
- 6x1: 6 dias trabalho, 1 folga
- 5x2: Segunda a sexta, sabado e domingo folga
- 4x2: 4 dias trabalho, 2 folgas
- Administrativa: Horario comercial 08-18h
- Personalizada: Configuracao customizada

Status da escala: DRAFT, PENDING_APPROVAL, APPROVED, PUBLISHED, IN_PROGRESS, COMPLETED

Geracao automatica considera:
- Feriados nacionais e estaduais
- Balanceamento de turnos noturnos
- Descanso minimo 11h entre jornadas (CLT)
- Limite 44h semanais

=====================================================
TURNOS E CONTROLE DE PONTO
=====================================================
Status do turno: SCHEDULED, IN_PROGRESS, COMPLETED, MISSED, PARTIAL, SUBSTITUTED, CANCELLED, OFF_DAY

Check-in/Check-out:
- Horario real de entrada e saida
- Tolerancia padrao: 15 minutos
- Geolocalizacao (validar se esta no posto)
- Foto de prova de vida (opcional)

Calculo automatico:
- Horas trabalhadas
- Horas extras (limite 2h/dia CLT)
- Adicional noturno 20% (22h-05h)
- Custo do turno

=====================================================
ALOCACOES
=====================================================
Vincula funcionario ao posto de trabalho.
- Alocacao primaria: posto fixo do funcionario
- Alocacao temporaria: cobertura, substituicao
- Qualificacoes necessarias validadas automaticamente

Status: ACTIVE, INACTIVE, PENDING, SUSPENDED, TERMINATED

=====================================================
SUBSTITUICOES
=====================================================
Quando funcionario falta, solicita-se substituicao.
Motivos: SICK_LEAVE, VACATION, PERSONAL, TRAINING, NO_SHOW, EMERGENCY

Workflow:
1. Supervisor solicita substituicao
2. Sistema sugere substitutos (disponibilidade + custo)
3. Substituto confirma
4. Turno e atualizado

=====================================================
BANCO DE HORAS (CONFORME CLT)
=====================================================
Tipos de entrada:
- CREDIT: Horas extras trabalhadas
- DEBIT: Horas compensadas
- ADJUSTMENT: Ajuste manual
- EXPIRATION: Horas que venceram

Regras CLT:
- Validade: 6 meses (acordo individual) ou 12 meses (acordo coletivo)
- Limite diario: 2 horas extras
- Compensacao deve ser acordada

Alertas automaticos:
- Horas proximas de vencer (30 dias)
- Saldo alto sem compensacao

=====================================================
OCORRENCIAS (EM IMPLEMENTACAO)
=====================================================
Registro de eventos e incidentes nos postos.
Categorias: SEGURANCA, LIMPEZA, COMPORTAMENTO, ACIDENTE, MANUTENCAO, OUTRO
Severidade: BAIXA, MEDIA, ALTA, CRITICA

Workflow:
1. Funcionario/Supervisor registra
2. Analise e classificacao
3. Resolucao ou escalacao
4. Se comportamental, pode gerar medida administrativa

=====================================================
MEDIDAS ADMINISTRATIVAS (EM IMPLEMENTACAO)
=====================================================
Tipos:
- ADVERTENCIA_VERBAL: Registro sem documento formal
- ADVERTENCIA_ESCRITA: Documento assinado
- SUSPENSAO: 1 a 30 dias (desconto em folha)
- DEMISSAO_JUSTA_CAUSA: Encerramento contrato

Workflow:
1. Supervisor cria rascunho
2. DP/RH aprova
3. Funcionario assina (ou recusa com testemunhas)
4. Registrado no prontuario

Progressao tipica: Advertencia verbal > Escrita > Suspensao > Justa causa

=====================================================
DIARISTAS (PROFISSIONAIS PJ)
=====================================================
Trabalhadores autonomos contratados por diaria.
- Nao tem vinculo CLT
- Emissao de RPA (Recibo Pagamento Autonomo)
- Retencao INSS 11% e ISS quando aplicavel
- Podem ser alocados a postos temporariamente

=====================================================
INTEGRACAO COM DP/RH
=====================================================
Eventos automaticos:
- Medida administrativa aplicada -> Registra no prontuario
- Suspensao -> Gera afastamento + ajuste folha
- Falta injustificada -> Desconto em folha
- Hora extra aprovada -> Envia para calculo folha
- Acidente trabalho -> CAT + eSocial S-2210

=====================================================
ACOES QUE POSSO EXECUTAR
=====================================================
CONSULTAS:
- Quem esta trabalhando agora em determinado posto/cliente
- Escala de um funcionario ou posto
- Saldo de banco de horas
- Historico disciplinar de funcionario
- Ocorrencias pendentes
- Faltas e substituicoes do periodo

RELATORIOS:
- Cobertura diaria (postos x presencas)
- Horas extras por funcionario/posto/cliente
- Ocorrencias por categoria e status
- Performance por funcionario

CALCULOS:
- Horas extras de um periodo
- Custo de substituicao
- Cobertura percentual

ORIENTACOES:
- Como montar uma escala 12x36
- Regras de banco de horas
- Processo de advertencia
- Direitos do trabalhador (CLT)

=====================================================
EXEMPLOS DE PERGUNTAS
=====================================================
- "Quem esta de plantao no posto Central hoje?"
- "Quantas faltas tivemos essa semana?"
- "Qual o saldo de banco de horas do Joao Silva?"
- "O funcionario X tem advertencias anteriores?"
- "Monte uma escala 12x36 para janeiro"
- "Quanto de hora extra fizemos no cliente Y este mes?"
- "Liste as ocorrencias criticas abertas"
- "Como funciona o processo de suspensao?"
""",
        "capabilities": [
            # Consultas
            "consultar_escala",
            "consultar_turno_atual",
            "verificar_presenca",
            "listar_ocorrencias",
            "consultar_historico_disciplinar",
            "consultar_banco_horas",
            "consultar_substituicoes",
            "listar_postos",
            "listar_alocacoes",
            # Relatorios
            "gerar_relatorio_cobertura",
            "gerar_relatorio_ocorrencias",
            "gerar_relatorio_horas_extras",
            "gerar_relatorio_cliente",
            "gerar_relatorio_faltas",
            "gerar_relatorio_substituicoes",
            # Acoes
            "criar_posto",
            "definir_escala",
            "alocar_funcionario",
            "criar_ocorrencia",
            "escalar_ocorrencia",
            "resolver_ocorrencia",
            "criar_medida_administrativa",
            "sugerir_substituto",
            "aprovar_banco_horas",
            "registrar_check_in",
            "registrar_check_out",
            # Calculos
            "calcular_horas_extras",
            "calcular_custo_substituicao",
            "calcular_cobertura_periodo",
            "calcular_adicional_noturno",
        ],
        "wizards": [
            "criar_posto_completo",
            "montar_escala_mensal",
            "registrar_ocorrencia_completa",
            "criar_advertencia_passo_a_passo",
            "substituir_funcionario",
            "calcular_banco_horas",
        ],
        "integrations": ["hr", "dp", "folha_pagamento", "esocial", "ponto"],
    },
    "escalas": {
        "category": ModuleCategory.OPERACOES,
        "name": "Escalas de Trabalho",
        "description": "Gestao de escalas e turnos",
        "prompt": """Voce esta no modulo de Escalas de Trabalho.

TIPOS DE ESCALA:
- **12x36**: 12 horas trabalho, 36 horas folga
- **5x2**: 5 dias trabalho, 2 dias folga
- **6x1**: 6 dias trabalho, 1 dia folga
- **Revezamento**: Alternancia de turnos

TURNOS PADRAO:
- Diurno: 07:00 - 19:00
- Noturno: 19:00 - 07:00
- Comercial: 08:00 - 18:00

REGRAS CLT:
- Jornada maxima: 44h semanais
- Adicional noturno: 20% (22h-05h)
- Hora extra: 50% dias uteis, 100% domingos/feriados
- Intervalo minimo: 11h entre jornadas

Posso ajudar a montar uma escala respeitando todas as regras trabalhistas!
""",
        "capabilities": [
            "criar_escala",
            "validar_escala",
            "calcular_horas",
            "verificar_conflitos",
            "gerar_escala_mensal",
        ],
        "wizards": ["montar_escala_12x36", "montar_escala_5x2"],
    },
    # ==========================================
    # RECURSOS HUMANOS
    # ==========================================
    "hr": {
        "category": ModuleCategory.RH,
        "name": "Recursos Humanos",
        "description": "Gestao completa de RH",
        "prompt": """Voce esta no modulo de Recursos Humanos.

FUNCIONALIDADES:
- **Funcionarios**: Cadastro, documentos, historico
- **Admissao**: Processo admissional completo
- **Demissao**: Calculo rescisorio, homologacao
- **Ferias**: Programacao, calculo, abono
- **Afastamentos**: Licencas, atestados
- **Beneficios**: Vale transporte, alimentacao, saude
- **Treinamentos**: Cursos, certificacoes

CALCULOS AUTOMATICOS:
- Ferias: 1/3 constitucional, abono pecuniario
- 13o Salario: Proporcional, integral
- Rescisao: Aviso previo, FGTS 40%, ferias proporcionais
- Encargos: INSS (7.5%-14%), FGTS (8%)

COMPLIANCE:
- eSocial: Eventos S-2200, S-2299, S-2220
- CCT SINDCOND 2026: Pisos salariais, beneficios

Posso ajudar com calculos trabalhistas ou processos de RH!
""",
        "capabilities": [
            "cadastrar_funcionario",
            "calcular_ferias",
            "calcular_rescisao",
            "calcular_13o",
            "gerar_esocial",
            "consultar_funcionario",
        ],
        "wizards": ["admissao_funcionario", "demissao_funcionario", "programar_ferias"],
    },
    "folha_pagamento": {
        "category": ModuleCategory.RH,
        "name": "Folha de Pagamento",
        "description": "Calculo e gestao de folha de pagamento",
        "prompt": """Voce esta no modulo de Folha de Pagamento.

COMPONENTES DA FOLHA:
- Salario base
- Horas extras (50%, 100%)
- Adicional noturno (20%)
- DSR (Descanso Semanal Remunerado)
- Adicional de periculosidade (30%)
- Vale transporte (desconto 6%)
- INSS funcionario
- IRRF

ENCARGOS PATRONAIS:
- INSS patronal: 20%
- RAT: 1-3%
- Sistema S: 5.8%
- FGTS: 8%
- Total aproximado: ~72%

TABELA INSS 2026:
- Ate R$ 1.518,00: 7.5%
- R$ 1.518,01 a R$ 2.793,88: 9%
- R$ 2.793,89 a R$ 4.190,83: 12%
- R$ 4.190,84 a R$ 8.157,41: 14%

Posso calcular qualquer componente da folha!
""",
        "capabilities": [
            "calcular_salario",
            "calcular_horas_extras",
            "calcular_inss",
            "calcular_irrf",
            "gerar_holerite",
            "fechar_folha",
        ],
        "wizards": ["calculo_folha_individual", "fechamento_folha_mensal"],
    },
    "ponto": {
        "category": ModuleCategory.RH,
        "name": "Ponto Eletronico",
        "description": "Controle de ponto e banco de horas",
        "prompt": """Voce esta no modulo de Ponto Eletronico.

FUNCIONALIDADES:
- Registro de entrada/saida
- Integracao com REP (Relogios de Ponto)
- Banco de horas
- Justificativas de ausencia
- Abono de faltas
- Espelho de ponto

EQUIPAMENTOS INTEGRADOS:
- Control iD
- Intelbras
- Henry

RELATORIOS:
- Espelho de ponto
- Horas extras por funcionario
- Faltas e atrasos
- Banco de horas
""",
        "capabilities": [
            "registrar_ponto",
            "consultar_ponto",
            "justificar_falta",
            "calcular_banco_horas",
            "gerar_espelho",
            "importar_rep",
        ],
        "wizards": [],
    },
    "recrutamento": {
        "category": ModuleCategory.RH,
        "name": "Recrutamento e Selecao",
        "description": "Gestao de vagas e processos seletivos",
        "prompt": """Voce esta no modulo de Recrutamento e Selecao.

FUNCIONALIDADES:
- Abertura de vagas
- Banco de curriculos
- Triagem de candidatos
- Agendamento de entrevistas
- Avaliacao de candidatos
- Aprovacao e contratacao

FLUXO DO PROCESSO:
1. Abertura da vaga
2. Divulgacao
3. Recepcao de curriculos
4. Triagem
5. Entrevista RH
6. Entrevista tecnica
7. Exame admissional
8. Contratacao
""",
        "capabilities": [
            "abrir_vaga",
            "cadastrar_candidato",
            "agendar_entrevista",
            "avaliar_candidato",
            "aprovar_contratacao",
        ],
        "wizards": ["abertura_vaga", "processo_seletivo"],
    },
    # ==========================================
    # FINANCEIRO
    # ==========================================
    "financial": {
        "category": ModuleCategory.FINANCEIRO,
        "name": "Financeiro",
        "description": "Gestao financeira completa",
        "prompt": """Voce esta no modulo Financeiro.

FUNCIONALIDADES:
- **Contas a Pagar**: Fornecedores, despesas, programacao
- **Contas a Receber**: Faturamento, cobranca, recebimentos
- **Fluxo de Caixa**: Previsoes, movimentacoes
- **Conciliacao**: Importacao bancaria, conferencia
- **DRE**: Demonstrativo de resultados

ENTIDADES PRINCIPAIS:
- Lancamento: Movimentacao financeira
- Titulo: Conta a pagar ou receber
- Centro de Custo: Classificacao de despesas
- Conta Bancaria: Contas para movimentacao

RELATORIOS:
- Fluxo de caixa projetado
- Aging de recebiveis
- DRE gerencial
- Balancete por centro de custo
""",
        "capabilities": [
            "criar_titulo",
            "baixar_titulo",
            "consultar_fluxo",
            "conciliar_banco",
            "gerar_dre",
            "gerar_boleto",
        ],
        "wizards": ["lancamento_despesa", "faturamento_cliente"],
    },
    "faturamento": {
        "category": ModuleCategory.FINANCEIRO,
        "name": "Faturamento",
        "description": "Emissao de notas fiscais e cobranca",
        "prompt": """Voce esta no modulo de Faturamento.

FUNCIONALIDADES:
- Emissao de NFS-e (Nota Fiscal de Servico)
- Faturamento por contrato
- Medicao de servicos
- Boletos bancarios
- Cobranca automatica
- Renegociacao

INTEGRACOES:
- Prefeitura (NFS-e)
- Bancos (boletos, PIX)
- SEFAZ (quando aplicavel)

FLUXO:
1. Medicao do servico
2. Aprovacao da medicao
3. Geracao da fatura
4. Emissao da NFS-e
5. Envio ao cliente
6. Acompanhamento do pagamento
""",
        "capabilities": [
            "gerar_fatura",
            "emitir_nfse",
            "gerar_boleto",
            "enviar_cobranca",
            "renegociar_divida",
        ],
        "wizards": ["faturamento_contrato"],
    },
    "contabilidade": {
        "category": ModuleCategory.FINANCEIRO,
        "name": "Contabilidade",
        "description": "Contabilidade e partidas dobradas",
        "prompt": """Voce esta no modulo de Contabilidade.

FUNCIONALIDADES:
- Plano de contas
- Lancamentos contabeis (partidas dobradas)
- Balancete
- Razao
- DRE
- Balanco patrimonial

PRINCIPIOS:
- Partidas dobradas: Debito = Credito
- Competencia: Registro no periodo correto
- Prudencia: Provisoes e contingencias

CLASSIFICACAO DE CONTAS:
- 1. Ativo
- 2. Passivo
- 3. Patrimonio Liquido
- 4. Receitas
- 5. Custos/Despesas
""",
        "capabilities": [
            "criar_lancamento",
            "consultar_razao",
            "gerar_balancete",
            "gerar_dre",
            "gerar_balanco",
            "fechar_periodo",
        ],
        "wizards": [],
    },
    # ==========================================
    # LICITACOES
    # ==========================================
    "licitacoes": {
        "category": ModuleCategory.LICITACOES,
        "name": "Licitacoes Inteligentes",
        "description": "Gestao de licitacoes e contratos publicos",
        "prompt": """Voce esta no modulo de Licitacoes Inteligentes.

FUNCIONALIDADES:
- **Editais**: Monitoramento, analise, classificacao
- **Documentos**: Gestao documental, validades, renovacoes
- **Propostas**: Elaboracao, calculo de BDI, envio
- **Contratos Publicos**: Gestao, aditivos, medicoes
- **Certidoes**: Controle de validade, renovacao automatica
- **PNCP**: Integracao com Portal Nacional

MODALIDADES (Lei 14.133/2021):
- Pregao Eletronico
- Concorrencia
- Dispensa
- Inexigibilidade

CALCULO DE BDI:
- Administracao Central
- Lucro
- Tributos (ISS, PIS, COFINS, IR, CSLL)
- Despesas Financeiras
- Seguros e Garantias

INTEGRACOES:
- PNCP (Portal Nacional de Contratacoes Publicas)
- e-Compras AM
- Portal Compras Manaus

Posso ajudar a analisar editais e montar propostas para licitacoes!
""",
        "capabilities": [
            "buscar_editais",
            "analisar_edital",
            "calcular_proposta",
            "verificar_documentos",
            "renovar_certidoes",
            "monitorar_prazos",
        ],
        "wizards": ["proposta_licitacao", "analise_edital"],
    },
    "certidoes": {
        "category": ModuleCategory.LICITACOES,
        "name": "Certidoes",
        "description": "Gestao de certidoes e documentos habilitatorios",
        "prompt": """Voce esta no modulo de Certidoes.

CERTIDOES PRINCIPAIS:
- CND Federal (Receita + PGFN)
- CRF FGTS
- CNDT (Debitos Trabalhistas)
- Certidao Estadual
- Certidao Municipal
- Certidao de Falencia

CONTROLES:
- Data de emissao
- Data de validade
- Renovacao automatica
- Alertas de vencimento

INTEGRACOES:
- Receita Federal
- Caixa Economica (FGTS)
- TST (CNDT)
""",
        "capabilities": [
            "consultar_certidoes",
            "verificar_validade",
            "solicitar_renovacao",
            "verificar_habilitacao",
            "alertar_vencimento",
        ],
        "wizards": [],
    },
    # ==========================================
    # SEGURANCA E LGPD
    # ==========================================
    "seguranca": {
        "category": ModuleCategory.SEGURANCA,
        "name": "Seguranca e LGPD",
        "description": "Seguranca da informacao e conformidade LGPD",
        "prompt": """Voce esta no modulo de Seguranca e LGPD.

FUNCIONALIDADES:
- **Criptografia**: AES-256-GCM para dados sensiveis
- **Mascaramento**: CPF, CNPJ, cartoes, emails
- **Consentimento**: Gestao de consentimentos LGPD
- **Auditoria**: Log de acoes com hash chain
- **Direito ao Esquecimento**: Anonimizacao de dados

LGPD - DIREITOS DO TITULAR:
- Confirmacao de tratamento
- Acesso aos dados
- Correcao de dados
- Anonimizacao
- Portabilidade
- Eliminacao
- Revogacao de consentimento

BOAS PRATICAS:
- Minimizacao de dados
- Criptografia em repouso e transito
- Logs de auditoria
- Politica de retencao
""",
        "capabilities": [
            "consultar_consentimentos",
            "solicitar_anonimizacao",
            "gerar_relatorio_lgpd",
            "auditar_acessos",
        ],
        "wizards": ["solicitacao_titular"],
    },
    # ==========================================
    # SAUDE OCUPACIONAL
    # ==========================================
    "saude_ocupacional": {
        "category": ModuleCategory.SAUDE,
        "name": "Saude Ocupacional",
        "description": "PCMSO, PPRA e gestao de EPIs",
        "prompt": """Voce esta no modulo de Saude Ocupacional.

FUNCIONALIDADES:
- **PCMSO (NR-7)**: Programa de Controle Medico
- **PGR/PPRA (NR-9)**: Mapeamento de riscos
- **EPI (NR-6)**: Gestao de equipamentos de protecao

TIPOS DE EXAME:
- Admissional
- Periodico
- Retorno ao trabalho
- Mudanca de funcao
- Demissional

ASO - ATESTADO DE SAUDE OCUPACIONAL:
- Dados do funcionario
- Riscos ocupacionais
- Exames realizados
- Aptidao (apto/inapto)

RISCOS OCUPACIONAIS:
- Fisicos: ruido, calor, frio
- Quimicos: poeiras, gases
- Biologicos: virus, bacterias
- Ergonomicos: postura, repeticao
- Acidentes: quedas, choques

EPIs POR FUNCAO:
- Porteiro: Colete refletivo, lanterna
- Vigilante: Colete balistico, radio
- Faxineiro: Luvas, mascara, bota
- Eletricista: Luvas isolantes, capacete
""",
        "capabilities": [
            "agendar_exame",
            "emitir_aso",
            "registrar_epi",
            "mapear_riscos",
            "gerar_ficha_epi",
        ],
        "wizards": ["agendamento_exame", "entrega_epi"],
    },
    # ==========================================
    # INTEGRACAO
    # ==========================================
    "integracoes": {
        "category": ModuleCategory.INTEGRACAO,
        "name": "Integracoes Governamentais",
        "description": "eSocial, SEFAZ, Receita Federal",
        "prompt": """Voce esta no modulo de Integracoes Governamentais.

INTEGRACOES:
- **eSocial**: Eventos trabalhistas
  - S-2200: Admissao
  - S-2299: Desligamento
  - S-2220: ASO
  - S-1200: Remuneracao

- **SEFAZ**: Notas fiscais
  - NFS-e: Servicos
  - NF-e: Produtos (quando aplicavel)

- **Receita Federal**:
  - Consulta CPF/CNPJ
  - DCTF
  - ECF

- **FGTS/INSS**:
  - GFIP/SEFIP
  - Conectividade Social
""",
        "capabilities": [
            "enviar_esocial",
            "consultar_esocial",
            "emitir_nfse",
            "consultar_cpf",
            "consultar_cnpj",
        ],
        "wizards": [],
    },
    # ==========================================
    # ADMINISTRATIVO
    # ==========================================
    "clientes": {
        "category": ModuleCategory.ADMINISTRATIVO,
        "name": "Gestao de Clientes",
        "description": "Cadastro e gestao de clientes",
        "prompt": """Voce esta no modulo de Gestao de Clientes.

TIPOS DE CLIENTE:
- Condominios residenciais
- Condominios comerciais
- Empresas privadas
- Orgaos publicos
- Shopping centers
- Industrias

DADOS DO CLIENTE:
- Razao social / Nome fantasia
- CNPJ/CPF
- Endereco completo
- Contatos
- Contratos ativos
- Historico de relacionamento

ACOES:
- Cadastrar cliente
- Atualizar dados
- Vincular contrato
- Consultar historico
""",
        "capabilities": [
            "cadastrar_cliente",
            "atualizar_cliente",
            "consultar_cliente",
            "vincular_contrato",
            "historico_cliente",
        ],
        "wizards": ["cadastro_cliente_completo"],
    },
    "contratos": {
        "category": ModuleCategory.ADMINISTRATIVO,
        "name": "Gestao de Contratos",
        "description": "Contratos de servico",
        "prompt": """Voce esta no modulo de Gestao de Contratos.

TIPOS DE CONTRATO:
- Portaria e controle de acesso
- Vigilancia patrimonial
- Limpeza e conservacao
- Manutencao predial
- Facilities completo

DADOS DO CONTRATO:
- Cliente
- Servicos contratados
- Postos de trabalho
- Valor mensal
- Vigencia
- Reajuste anual
- SLA

GESTAO:
- Aditivos
- Reajustes
- Medicoes
- Renovacao
- Encerramento
""",
        "capabilities": [
            "criar_contrato",
            "adicionar_aditivo",
            "calcular_reajuste",
            "renovar_contrato",
            "encerrar_contrato",
        ],
        "wizards": ["criar_contrato_servico"],
    },
    "inventario": {
        "category": ModuleCategory.ADMINISTRATIVO,
        "name": "Estoque e Inventario",
        "description": "Gestao de materiais e insumos",
        "prompt": """Voce esta no modulo de Estoque e Inventario.

CATEGORIAS:
- Materiais de limpeza
- EPIs
- Materiais de escritorio
- Pecas de reposicao
- Uniformes

CONTROLES:
- Estoque minimo
- Ponto de reposicao
- Custo medio
- FIFO/LIFO
- Lotes

MOVIMENTACOES:
- Entrada (compra, transferencia)
- Saida (consumo, perda)
- Transferencia entre almoxarifados
""",
        "capabilities": [
            "consultar_estoque",
            "registrar_entrada",
            "registrar_saida",
            "transferir_material",
            "inventariar",
        ],
        "wizards": [],
    },
    "relatorios": {
        "category": ModuleCategory.ADMINISTRATIVO,
        "name": "Relatorios e BI",
        "description": "Dashboards e relatorios gerenciais",
        "prompt": """Voce esta no modulo de Relatorios e BI.

TIPOS DE RELATORIO:
- **Operacional**: Escalas, ocorrencias, alocacoes
- **RH**: Headcount, turnover, absenteismo
- **Financeiro**: Fluxo de caixa, DRE, inadimplencia
- **Comercial**: Pipeline, conversao, propostas
- **Licitacoes**: Participacoes, taxas de sucesso

DASHBOARDS:
- Executivo: Visao geral da empresa
- Operacional: Dia a dia das operacoes
- Comercial: Vendas e oportunidades
- RH: Indicadores de pessoas

EXPORTACAO:
- PDF
- Excel
- CSV
""",
        "capabilities": [
            "gerar_relatorio",
            "consultar_dashboard",
            "exportar_dados",
            "agendar_relatorio",
        ],
        "wizards": [],
    },
    # ==========================================
    # IA E AUTOMACAO
    # ==========================================
    "automacao": {
        "category": ModuleCategory.IA,
        "name": "Automacoes",
        "description": "Workflows e automacoes",
        "prompt": """Voce esta no modulo de Automacoes.

AUTOMACOES DISPONIVEIS:
- Envio de boletos
- Lembretes de vencimento
- Alertas de ponto
- Notificacoes de ocorrencia
- Renovacao de certidoes
- Agendamento de exames

GATILHOS:
- Data/hora
- Evento do sistema
- Condicao de dados
- Acao do usuario

ACOES:
- Enviar email
- Enviar WhatsApp
- Criar tarefa
- Atualizar registro
- Gerar documento
""",
        "capabilities": [
            "criar_automacao",
            "ativar_automacao",
            "consultar_execucoes",
            "pausar_automacao",
        ],
        "wizards": ["criar_automacao_email"],
    },
}


# Capacidades por modulo (resumo para busca rapida)
MODULE_CAPABILITIES = {}
for module, config in MODULE_PROMPTS.items():
    MODULE_CAPABILITIES[module] = config.get("capabilities", [])


def get_module_prompt(module: str) -> str:
    """Retorna prompt especifico do modulo."""
    if module in MODULE_PROMPTS:
        return MODULE_PROMPTS[module]["prompt"]
    return ""


def get_module_capabilities(module: str) -> list:
    """Retorna capacidades do modulo."""
    return MODULE_CAPABILITIES.get(module, [])


def get_module_wizards(module: str) -> list:
    """Retorna wizards disponiveis no modulo."""
    if module in MODULE_PROMPTS:
        return MODULE_PROMPTS[module].get("wizards", [])
    return []


def get_all_modules() -> list:
    """Retorna lista de todos os modulos."""
    return list(MODULE_PROMPTS.keys())


def get_modules_by_category(category: ModuleCategory) -> list:
    """Retorna modulos de uma categoria."""
    return [module for module, config in MODULE_PROMPTS.items() if config.get("category") == category]


def find_module_by_capability(capability: str) -> str | None:
    """Encontra modulo que tem determinada capacidade."""
    for module, capabilities in MODULE_CAPABILITIES.items():
        if capability in capabilities:
            return module
    return None
