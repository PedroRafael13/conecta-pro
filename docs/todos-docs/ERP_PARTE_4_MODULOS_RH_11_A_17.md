# ERP CONECTA MAIS - PARTE 4: MÓDULOS DE RH E FOLHA (11-17)

---

## CATEGORIA 2: RECURSOS HUMANOS E FOLHA DE PAGAMENTO

## 4.11 MÓDULO 11: Recrutamento e Seleção com IA

### 4.11.1 Visão Geral

**Objetivo:** Automatizar e otimizar processo de R&S, desde abertura de vaga até admissão, com IA para triagem de currículos e análise comportamental.

**Escopo:**
- Abertura de vagas
- Portal de vagas (site público)
- Triagem automática de CVs (IA)
- Testes online
- Entrevistas (agendamento e videoconferência)
- Análise comportamental (Profiler DISC)
- Feedbacks automáticos
- Banco de talentos

### 4.11.2 Funcionalidades Detalhadas

**RF-REC-001: Abertura de Vagas**
- Requisição de vaga:
  - Cargo
  - Departamento/Área
  - Tipo: CLT, PJ, Temporário, Estágio
  - Quantidade de vagas
  - Salário/Faixa salarial
  - Benefícios
  - Requisitos obrigatórios
  - Requisitos desejáveis
  - Descrição das atividades
  - Local de trabalho
  - Horário/Escala
- Aprovação por gestor/RH
- Publicação automática no portal de vagas

**RF-REC-002: Portal de Vagas Público**
- Site público: `vagas.conectamaistech.com.br`
- Listagem de vagas abertas
- Filtros: cargo, local, tipo, área
- Candidato se cadastra:
  - Dados pessoais
  - Currículo (upload PDF ou preenchimento online)
  - Foto
  - Carta de apresentação (opcional)
  - LinkedIn
- Candidato se candidata à vaga
- Confirmação por e-mail

**RF-REC-003: Triagem Automática de CVs (IA)**
- IA analisa currículo e atribui score de 0 a 100:
  - Match de palavras-chave (requisitos da vaga)
  - Experiência na área (anos)
  - Formação acadêmica
  - Certificações
  - Disponibilidade de horário
  - Proximidade ao local de trabalho (endereço)
  - Pretensão salarial vs. faixa da vaga

**Algoritmo de Triagem:**
```python
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CandidateScreener:
    def __init__(self):
        self.nlp = spacy.load('pt_core_news_lg')
        self.vectorizer = TfidfVectorizer()
    
    def score_candidate(self, candidate: Candidate, job: Job) -> int:
        score = 0
        
        # 1. Match de requisitos (40 pontos)
        job_requirements = job.requirements_text.lower()
        candidate_cv = candidate.cv_text.lower()
        
        # TF-IDF + Cosine Similarity
        texts = [job_requirements, candidate_cv]
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        score += int(similarity * 40)
        
        # 2. Experiência (25 pontos)
        years_required = job.min_experience_years
        years_candidate = candidate.experience_years
        
        if years_candidate >= years_required:
            score += 25
        elif years_candidate >= years_required * 0.7:
            score += 15
        elif years_candidate >= years_required * 0.5:
            score += 10
        
        # 3. Formação (15 pontos)
        if candidate.education_level >= job.required_education_level:
            score += 15
        elif candidate.education_level >= job.required_education_level - 1:
            score += 10
        
        # 4. Certificações (10 pontos)
        required_certs = set(job.required_certifications or [])
        candidate_certs = set(candidate.certifications or [])
        match_certs = len(required_certs & candidate_certs)
        score += min(match_certs * 5, 10)
        
        # 5. Localização (5 pontos)
        if candidate.city == job.city:
            score += 5
        elif candidate.state == job.state:
            score += 3
        
        # 6. Pretensão salarial (5 pontos)
        if candidate.salary_expectation:
            if candidate.salary_expectation <= job.salary_max:
                score += 5
            elif candidate.salary_expectation <= job.salary_max * 1.1:
                score += 3
        
        return min(score, 100)
    
    def auto_reject_reasons(self, candidate: Candidate, job: Job) -> List[str]:
        """Identifica motivos de rejeição automática"""
        reasons = []
        
        # Requisitos obrigatórios
        if job.requires_cnh and not candidate.has_cnh:
            reasons.append("CNH obrigatória não apresentada")
        
        if job.requires_vigilante_card and not candidate.has_vigilante_card:
            reasons.append("Curso de vigilante obrigatório não apresentado")
        
        # Pretensão muito acima da faixa
        if candidate.salary_expectation and candidate.salary_expectation > job.salary_max * 1.3:
            reasons.append(f"Pretensão salarial (R$ {candidate.salary_expectation}) muito acima da faixa (até R$ {job.salary_max})")
        
        # Experiência muito abaixo
        if candidate.experience_years < job.min_experience_years * 0.5:
            reasons.append(f"Experiência insuficiente ({candidate.experience_years} anos vs. {job.min_experience_years} requeridos)")
        
        return reasons
```

**RF-REC-004: Feedback Automático (IA)**
- Candidatos reprovados na triagem recebem e-mail personalizado:
  - Agradecimento pela candidatura
  - Motivo da reprovação (genérico, para não desestimular)
  - Sugestões de melhoria
  - Convite para se candidatar a outras vagas

**Exemplo de Feedback Gerado por IA:**
```
Olá [Nome do Candidato],

Agradecemos seu interesse em fazer parte da equipe Conecta Mais e pelo tempo dedicado ao processo seletivo para a vaga de [Cargo].

Após análise criteriosa dos currículos recebidos, informamos que optamos por seguir com outros candidatos cujos perfis apresentaram maior aderência aos requisitos específicos desta posição, especialmente no que se refere a [experiência prévia em vigilância / certificações necessárias / disponibilidade de horário].

Isso não significa que seu perfil não é valioso! Encorajamos você a:
- Continuar desenvolvendo suas habilidades em [área identificada]
- Acompanhar novas oportunidades em nosso portal: vagas.conectamaistech.com.br
- Manter seu currículo atualizado em nossa base de talentos

Seu currículo permanecerá em nosso banco de talentos por 12 meses e você poderá ser considerado para futuras oportunidades.

Desejamos sucesso em sua jornada profissional!

Atenciosamente,
Equipe de Recrutamento
Conecta Mais
```

**RF-REC-005: Testes Online**
- Testes técnicos por cargo:
  - Vigilante: legislação, procedimentos, segurança
  - Porteiro: atendimento, informática básica
  - Técnico de eletrônica: elétrica, redes, CFTV
- Testes comportamentais
- Tempo limite
- Correção automática
- Resultado imediato (aprovado/reprovado)

**RF-REC-006: Análise Comportamental (Profiler DISC)**
- Questionário DISC (15-20 perguntas, 7 minutos)
- Identifica perfil comportamental:
  - **D (Dominância):** Determinado, direto, orientado a resultados
  - **I (Influência):** Comunicativo, entusiasta, otimista
  - **S (Estabilidade):** Paciente, leal, consistente
  - **C (Conformidade):** Analítico, preciso, sistemático
- Gera relatório com:
  - Perfil principal e secundário
  - Pontos fortes
  - Pontos de atenção
  - Fit com a vaga (match com perfil desejado para o cargo)
  - Sugestões para liderança

**Exemplo de Match:**
```
Vaga: Vigilante Noturno
Perfil Desejado: S (Estabilidade) + C (Conformidade) - pessoa calma, atenta a detalhes, que segue procedimentos

Candidato: João Silva
Perfil Identificado: S (alto) + C (médio) + D (baixo)
Fit: 85% - Excelente match!

Análise:
✓ Perfil estável e confiável, ideal para turnos noturnos
✓ Atenção a detalhes e seguimento de procedimentos
✓ Baixa impulsividade (D baixo) é positivo para segurança
⚠ Pode ter dificuldade em situações de confronto (D baixo)

Recomendação: APROVAR para entrevista. Na entrevista, avaliar capacidade de agir sob pressão.
```

**RF-REC-007: Agendamento de Entrevistas**
- Sistema sugere horários disponíveis
- Candidato escolhe horário via link
- Confirmação automática por e-mail e SMS
- Integração com Google Calendar
- Lembrete 24h antes

**RF-REC-008: Videoconferência Integrada**
- Integração com Google Meet / Zoom
- Link gerado automaticamente
- Gravação da entrevista (com consentimento)
- Notas do entrevistador
- Avaliação por competências

**RF-REC-009: Banco de Talentos**
- Todos os candidatos ficam no banco
- Perfil completo, CV, testes, DISC
- Busca por: cargo, habilidades, localização, disponibilidade
- Reativar candidato para nova vaga
- Válido por 12 meses

**RF-REC-010: Métricas de R&S**
- Tempo médio de preenchimento de vaga
- Custo por contratação
- Taxa de aprovação em teste
- Taxa de aprovação em entrevista
- Taxa de aprovação em exame médico
- Taxa de retenção (90 dias, 180 dias, 1 ano)
- Canais de recrutamento mais efetivos
- NPS de candidatos

---

## 4.12 MÓDULO 12: Ponto Eletrônico e Jornada

### 4.12.1 Visão Geral

**Objetivo:** Controlar jornada de trabalho dos funcionários com ponto eletrônico digital, reconhecimento facial, geolocalização e tratamento automático de horas.

**Escopo:**
- Ponto eletrônico (app, totem, web)
- Reconhecimento facial
- Geolocalização (GPS)
- Modo offline
- Banco de horas
- Horas extras
- Tratamento de ponto
- Fechamento de folha ponto
- Espelho de ponto
- Integração com folha de pagamento

**Referência:** Sólides - **50% de redução no tempo de fechamento**

### 4.12.2 Funcionalidades Detalhadas

**RF-PONTO-001: Registro de Ponto**

**Formas de Registro:**
A. **App Mobile** (principal):
- Botão "Bater Ponto"
- Selfie obrigatória (reconhecimento facial)
- Captura automática de GPS
- Modo offline (sincroniza quando voltar online)
- Confirmação visual

B. **Totem (local de trabalho):**
- QR Code ou NFC
- Reconhecimento facial
- Teclado numérico (matrícula + senha)

C. **Web (exceção):**
- Para trabalho remoto/administrativo
- Geolocalização via IP
- Justificativa obrigatória se não for de local autorizado

**RF-PONTO-002: Reconhecimento Facial**
- Captura de selfie
- Comparação com foto cadastral
- Precisão > 95%
- Detecção de fraude:
  - Foto impressa
  - Vídeo
  - Pessoa errada
  - Baixa qualidade (iluminação, ângulo)
- Se não reconhecer: solicita nova foto ou permite ponto manual (com justificativa e aprovação)

```python
import face_recognition
import numpy as np

class FacialRecognition:
    def __init__(self):
        self.tolerance = 0.6  # Quanto menor, mais rigoroso
    
    def verify_face(self, employee_photo_path: str, selfie_path: str) -> dict:
        """
        Verifica se selfie corresponde à foto cadastral
        """
        # Carregar imagens
        known_image = face_recognition.load_image_file(employee_photo_path)
        unknown_image = face_recognition.load_image_file(selfie_path)
        
        # Detectar faces
        known_encodings = face_recognition.face_encodings(known_image)
        unknown_encodings = face_recognition.face_encodings(unknown_image)
        
        if len(known_encodings) == 0:
            return {"success": False, "error": "Foto cadastral sem face detectável"}
        
        if len(unknown_encodings) == 0:
            return {"success": False, "error": "Selfie sem face detectável"}
        
        if len(unknown_encodings) > 1:
            return {"success": False, "error": "Múltiplas faces detectadas na selfie"}
        
        # Comparar
        known_encoding = known_encodings[0]
        unknown_encoding = unknown_encodings[0]
        
        matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=self.tolerance)
        face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
        
        confidence = (1 - face_distance) * 100
        
        if matches[0]:
            return {
                "success": True,
                "confidence": confidence,
                "message": f"Face reconhecida com {confidence:.1f}% de confiança"
            }
        else:
            return {
                "success": False,
                "confidence": confidence,
                "error": f"Face não reconhecida (confiança: {confidence:.1f}%)"
            }
```

**RF-PONTO-003: Geolocalização**
- Captura GPS no momento do registro
- Validação de local autorizado:
  - Sede da empresa
  - Posto de trabalho
  - Raio de tolerância (ex: 100m)
- Se fora do local: marca como "ponto remoto" (requer aprovação)
- Registro de trajeto (para motoboys, técnicos de campo)

**RF-PONTO-004: Jornadas de Trabalho**
- Configuração por funcionário:
  - Horário de entrada
  - Horário de saída
  - Intervalo (almoço/jantar)
  - Tolerância de atraso (ex: 10 min)
  - Tolerância de saída antecipada
- Escalas especiais:
  - 12x36
  - 6x1
  - Turnos rotativos
- DSR (Descanso Semanal Remunerado)

**RF-PONTO-005: Marcações Obrigatórias**
- Entrada
- Saída para intervalo
- Retorno do intervalo
- Saída final
- Sistema alerta se faltou alguma marcação

**RF-PONTO-006: Tratamento de Ponto**
- Supervisor/RH pode:
  - Ajustar horário (com justificativa)
  - Adicionar marcação faltante
  - Justificar falta
  - Abonar atraso
- Histórico de alterações (auditoria)

**RF-PONTO-007: Banco de Horas**
- Saldo acumulado por funcionário
- Limite: 2h/dia (CLT)
- Compensação em folgas
- Relatório mensal
- Vencimento (6 meses ou 12 meses, conforme acordo)

**RF-PONTO-008: Horas Extras**
- Cálculo automático:
  - 50% (dias úteis até 22h)
  - 100% (após 22h, domingos, feriados)
- Limite: 2h/dia
- Aprovação prévia de gestor
- Integração com folha de pagamento

**RF-PONTO-009: Atestados e Faltas**
- Funcionário envia atestado via app (foto)
- RH valida e justifica falta
- Tipos de falta:
  - Justificada (atestado médico, falecimento familiar, casamento, nascimento filho, doação sangue)
  - Injustificada
  - Falta abonada (emergência, autorizada)
- DSR descontado em falta injustificada

**RF-PONTO-010: Fechamento de Folha Ponto**
- Fechamento mensal automático (dia configurável, ex: dia 25)
- Cálculo automático:
  - Dias trabalhados
  - Horas normais
  - Horas extras 50%
  - Horas extras 100%
  - Faltas
  - Atrasos
  - DSR
  - Adicional noturno (22h-05h = +20%)
  - Banco de horas
- Geração de espelho de ponto (PDF)
- Envio para aprovação de supervisor
- Após aprovação: envia para folha de pagamento
- **Redução de 50% no tempo** vs. processo manual

**RF-PONTO-011: Espelho de Ponto**
- Funcionário visualiza seu ponto via app
- Detalhamento diário:
  - Horários marcados
  - Horas trabalhadas
  - Horas extras
  - Saldo banco de horas
- Pode contestar (solicitar ajuste)

**RF-PONTO-012: Relatórios**
- Ponto diário (por funcionário, departamento, posto)
- Resumo mensal
- Horas extras por funcionário
- Faltas e atrasos
- Banco de horas
- Absenteísmo
- Pontualidade média

---

## 4.13 MÓDULO 13: Folha de Pagamento Digital

### 4.13.1 Visão Geral

**Objetivo:** Processar folha de pagamento completa (CLT, PJ, Diaristas), calcular encargos, gerar guias, integrar com eSocial e realizar pagamentos.

**Escopo:**
- Cálculo de folha (salários, horas extras, adicionais, descontos)
- Encargos (INSS, FGTS, IRRF)
- 13º salário
- Férias
- Rescisões
- Informe de rendimentos
- eSocial
- SEFIP/GFIP
- Geração de guias (GPS, DARF, GRRF)
- Integração bancária (pagamentos)
- Holerite digital

**Referência:** Sólides - **25x mais rápida e 30% mais econômica**

### 4.13.2 Funcionalidades Detalhadas

**RF-FOLHA-001: Estrutura de Remuneração**

**CLT:**
- Salário base
- Horas extras (50%, 100%)
- Adicional noturno (20%)
- Adicional de periculosidade (30%) - se aplicável
- Adicional de insalubridade (10%, 20%, 40%) - se aplicável
- Comissões
- Bônus/Gratificações
- Vale transporte
- Vale alimentação/refeição
- Plano de saúde
- Seguro de vida
- Outros benefícios

**Descontos:**
- INSS (7,5%, 9%, 12%, 14% conforme faixa)
- IRRF (conforme tabela)
- Vale transporte (6% do salário, se optar)
- Plano de saúde (parte do funcionário)
- Pensão alimentícia
- Adiantamento salarial
- Empréstimo consignado
- Faltas e atrasos

**RF-FOLHA-002: Cálculo de Folha**

**Processo Mensal:**
```python
from decimal import Decimal
from typing import Dict

class PayrollCalculator:
    def __init__(self, employee: Employee, month: int, year: int):
        self.employee = employee
        self.month = month
        self.year = year
        self.base_salary = employee.salary
        self.timesheet = self.get_timesheet()  # Dados do ponto
    
    def calculate(self) -> Dict:
        """Calcula folha de pagamento"""
        
        # Proventos
        base_salary = self.base_salary
        overtime_50 = self.calculate_overtime(rate=1.5)
        overtime_100 = self.calculate_overtime(rate=2.0)
        night_shift_bonus = self.calculate_night_shift_bonus()
        hazard_pay = self.calculate_hazard_pay()
        
        gross_pay = base_salary + overtime_50 + overtime_100 + night_shift_bonus + hazard_pay
        
        # Descontos
        inss = self.calculate_inss(gross_pay)
        irrf = self.calculate_irrf(gross_pay - inss)
        transport_voucher = self.calculate_transport_voucher(base_salary)
        absences = self.calculate_absences()
        
        total_discounts = inss + irrf + transport_voucher + absences
        
        net_pay = gross_pay - total_discounts
        
        return {
            "employee_id": self.employee.id,
            "month": self.month,
            "year": self.year,
            "earnings": {
                "base_salary": float(base_salary),
                "overtime_50": float(overtime_50),
                "overtime_100": float(overtime_100),
                "night_shift_bonus": float(night_shift_bonus),
                "hazard_pay": float(hazard_pay),
                "gross_pay": float(gross_pay)
            },
            "deductions": {
                "inss": float(inss),
                "irrf": float(irrf),
                "transport_voucher": float(transport_voucher),
                "absences": float(absences),
                "total_discounts": float(total_discounts)
            },
            "net_pay": float(net_pay)
        }
    
    def calculate_overtime(self, rate: float) -> Decimal:
        """Calcula horas extras"""
        hours = self.timesheet.get_overtime_hours(rate)
        hour_value = self.base_salary / Decimal('220')  # 220h = mês
        return hour_value * Decimal(str(rate)) * hours
    
    def calculate_night_shift_bonus(self) -> Decimal:
        """Adicional noturno 20% (22h-05h)"""
        night_hours = self.timesheet.get_night_hours()
        hour_value = self.base_salary / Decimal('220')
        return hour_value * Decimal('1.2') * night_hours - (hour_value * night_hours)
    
    def calculate_hazard_pay(self) -> Decimal:
        """Adicional de periculosidade 30%"""
        if self.employee.has_hazard_pay:
            return self.base_salary * Decimal('0.30')
        return Decimal('0')
    
    def calculate_inss(self, gross_pay: Decimal) -> Decimal:
        """Calcula INSS progressivo (2024)"""
        brackets = [
            (Decimal('1412.00'), Decimal('0.075')),
            (Decimal('2666.68'), Decimal('0.09')),
            (Decimal('4000.03'), Decimal('0.12')),
            (Decimal('7786.02'), Decimal('0.14'))
        ]
        
        inss = Decimal('0')
        remaining = gross_pay
        previous_bracket = Decimal('0')
        
        for limit, rate in brackets:
            if remaining <= 0:
                break
            
            taxable = min(remaining, limit - previous_bracket)
            inss += taxable * rate
            remaining -= taxable
            previous_bracket = limit
        
        return inss
    
    def calculate_irrf(self, taxable_income: Decimal) -> Decimal:
        """Calcula IRRF (2024)"""
        # Dedução por dependente
        dependents_deduction = self.employee.dependents_count * Decimal('189.59')
        
        base = taxable_income - dependents_deduction
        
        if base <= Decimal('2259.20'):
            return Decimal('0')
        elif base <= Decimal('2826.65'):
            return base * Decimal('0.075') - Decimal('169.44')
        elif base <= Decimal('3751.05'):
            return base * Decimal('0.15') - Decimal('381.44')
        elif base <= Decimal('4664.68'):
            return base * Decimal('0.225') - Decimal('662.77')
        else:
            return base * Decimal('0.275') - Decimal('896.00')
    
    def calculate_transport_voucher(self, base_salary: Decimal) -> Decimal:
        """Vale transporte: 6% do salário base"""
        if self.employee.opts_for_transport_voucher:
            return base_salary * Decimal('0.06')
        return Decimal('0')
    
    def calculate_absences(self) -> Decimal:
        """Desconto por faltas injustificadas"""
        unjustified_absences = self.timesheet.get_unjustified_absences()
        day_value = self.base_salary / Decimal('30')
        return day_value * unjustified_absences
```

**RF-FOLHA-003: 13º Salário**
- 1ª parcela: até 30/11 (50% do salário)
- 2ª parcela: até 20/12 (50% + proporção de horas extras + descontos)
- Cálculo proporcional para admitidos no ano
- Integração com eSocial (evento S-1210)

**RF-FOLHA-004: Férias**
- Direito após 12 meses (período aquisitivo)
- Concessão: 12 meses seguintes (período concessivo)
- Tipos:
  - 30 dias corridos
  - 20 dias + 10 dias (fracionado)
  - Abono pecuniário (venda de 10 dias)
- Cálculo:
  - Salário + 1/3 constitucional
  - Média de horas extras (se houver)
- Pagamento: até 2 dias antes do início
- Integração com eSocial (evento S-1200)

**RF-FOLHA-005: Rescisão**
- Tipos:
  - Sem justa causa (empregador)
  - Com justa causa (empregador)
  - Pedido de demissão (empregado)
  - Acordo mútuo
- Cálculos:
  - Saldo de salário
  - Aviso prévio (trabalhado ou indenizado)
  - 13º proporcional
  - Férias vencidas + 1/3
  - Férias proporcionais + 1/3
  - Multa FGTS 40% (se sem justa causa)
  - Seguro-desemprego (se aplicável)
- TRCT (Termo de Rescisão de Contrato de Trabalho)
- Homologação (se > 1 ano de empresa: sindicato ou MTE)
- Prazo de pagamento: até 10 dias

**RF-FOLHA-006: eSocial**
**Eventos Enviados:**
- S-1200: Remuneração mensal
- S-1210: 13º salário
- S-1260: Comercialização de produção rural (não aplicável)
- S-2190: Admissão
- S-2200: Cadastro inicial ou atualização
- S-2205: Alteração de dados cadastrais
- S-2206: Alteração de contrato
- S-2230: Afastamento temporário
- S-2298: Reintegração
- S-2299: Desligamento
- S-2300: Trabalhador sem vínculo - início
- S-2399: Trabalhador sem vínculo - término
- S-3000: Exclusão de eventos

**RF-FOLHA-007: SEFIP/GFIP**
- Geração mensal
- FGTS
- Contribuições previdenciárias
- Transmissão via Conectividade Social

**RF-FOLHA-008: Guias de Pagamento**
- GPS (Guia da Previdência Social) - INSS empregador + empregado
- DARF (IRRF retido)
- GRRF (FGTS)
- Geração automática
- Código de barras
- Pagamento via integração bancária

**RF-FOLHA-009: Holerite Digital**
- Disponível no app do funcionário
- PDF protegido por senha (CPF)
- Envio por e-mail
- Confirmação de visualização
- Histórico de holerites

**RF-FOLHA-010: Adiantamento Salarial**
- Configurável (ex: até 40% do salário)
- Solicitação via app
- Aprovação de gestor
- Pagamento via Pix
- Desconto automático na folha

**RF-FOLHA-011: Empréstimo Consignado**
- Convênio com bancos
- Margem consignável (35% do salário)
- Desconto automático em folha
- Portabilidade

**RF-FOLHA-012: Integração Bancária**
- Arquivo CNAB 240/400
- Pagamento de salários via TED/DOC/Pix
- Integração Banco Cora
- Integração Banco Inter
- Confirmação de pagamento
- Conciliação automática

**RF-FOLHA-013: Relatórios**
- Folha analítica
- Folha sintética
- Resumo de encargos
- Provisão de férias e 13º
- Custo por departamento/posto
- Custo por cliente/contrato
- Comparativo mensal
- Projeção anual

---

## 4.14 MÓDULO 14: Admissão Digital 100%

### 4.14.1 Visão Geral

**Objetivo:** Digitalizar completamente o processo de admissão, desde a coleta de documentos até o registro no eSocial, com assinatura digital e onboarding automatizado.

**Escopo:**
- Coleta digital de documentos
- Validação de documentos
- Contrato de trabalho digital
- Assinatura eletrônica
- Exame admissional (ASO)
- Registro em carteira (eSocial)
- Onboarding

### 4.14.2 Funcionalidades Detalhadas

**RF-ADM-001: Fluxo de Admissão**
1. Candidato aprovado → RH inicia processo de admissão
2. Sistema envia link/QR Code para candidato
3. Candidato acessa portal de admissão (mobile-friendly)
4. Preenche dados pessoais
5. Faz upload de documentos (foto pelo celular)
6. Assina contrato digitalmente
7. Agenda exame admissional
8. RH valida tudo
9. Sistema envia evento S-2190 (admissão) para eSocial
10. Funcionário recebe login no app
11. Inicia onboarding

**RF-ADM-002: Documentos Necessários**
- Foto 3x4
- RG e CPF
- Título de eleitor
- Reservista (homens)
- Comprovante de residência
- CTPS (física ou digital - número)
- PIS/PASEP
- Certidão de nascimento ou casamento
- Certidão de nascimento dos filhos (se houver)
- Caderneta de vacinação dos filhos < 7 anos
- Comprovante de escolaridade
- Certificados de cursos (vigilante, etc)
- Atestado de antecedentes criminais
- Carteira de habilitação (se aplicável)
- Número da conta bancária (salário)

**RF-ADM-003: Validação de Documentos**
- CPF: validação via API Receita Federal
- Título de eleitor: validação via TSE
- CNH: validação via DETRAN (se disponível)
- PIS: validação via CNIS
- OCR: extração automática de dados dos documentos
- Detecção de fraude: documentos adulterados, fotos antigas

**RF-ADM-004: Contrato de Trabalho**
- Template por cargo/função
- Preenchimento automático com dados do funcionário
- Cláusulas obrigatórias
- Assinatura digital (ICP-Brasil)
- Testemunhas (se necessário)

**RF-ADM-005: Exame Admissional (ASO)**
- Clínica conveniada ou médico do trabalho
- Agendamento online
- Funcionário escolhe data/horário
- Lembrete automático
- Upload de ASO assinado pelo médico
- Validação: CRM do médico, data, assinatura

**RF-ADM-006: Registro no eSocial**
- Evento S-2190 (Admissão)
- Evento S-2200 (Cadastro inicial)
- Dados enviados:
  - Informações pessoais
  - Endereço
  - Dependentes
  - Cargo/função
  - Salário
  - Data de admissão
  - Tipo de contrato
  - Jornada de trabalho
- Recibo de entrega
- Matrícula CEI (se aplicável)

**RF-ADM-007: Onboarding Digital**
- Boas-vindas via app
- Vídeo de apresentação da empresa
- Missão, visão, valores
- Organograma
- Políticas internas
- Código de conduta
- Segurança do trabalho (básico)
- Como usar o app
- Quiz de verificação (aprovado = concluiu onboarding)

**RF-ADM-008: Kit do Funcionário**
- Crachá
- Uniforme
- EPI (se aplicável)
- Celular corporativo (se aplicável)
- Laptop (se aplicável)
- Termo de responsabilidade (assinatura digital)

---

## 4.15 MÓDULO 15: Avaliação de Desempenho e PDI

### 4.15.1 Visão Geral

**Objetivo:** Avaliar performance dos funcionários periodicamente, identificar gaps, criar planos de desenvolvimento e acompanhar evolução.

**Escopo:**
- Avaliação 360°
- Avaliação por competências
- PDI (Plano de Desenvolvimento Individual)
- Feedbacks contínuos
- One-on-One
- Metas e OKRs
- 9-Box (potencial x performance)

### 4.15.2 Funcionalidades Detalhadas

**RF-AVAL-001: Tipos de Avaliação**
- **Auto-avaliação:** Funcionário avalia a si mesmo
- **Avaliação de gestor:** Gestor avalia subordinado
- **Avaliação 360°:** Gestor + pares + subordinados + cliente interno
- **Avaliação por competências:** Avalia competências técnicas e comportamentais

**RF-AVAL-002: Ciclo de Avaliação**
- Periodicidade: Semestral ou Anual
- Fases:
  1. Planejamento (definir avaliadores, competências, peso)
  2. Lançamento (notificação a todos)
  3. Avaliação (cada avaliador preenche)
  4. Calibração (RH + gestores ajustam notas)
  5. Feedback (gestor dá feedback ao avaliado)
  6. PDI (criação de plano de desenvolvimento)

**RF-AVAL-003: Avaliação por Competências**
**Competências Técnicas (exemplos):**
- Conhecimento em segurança patrimonial
- Operação de CFTV
- Primeiros socorros
- Informática

**Competências Comportamentais:**
- Comunicação
- Trabalho em equipe
- Proatividade
- Atenção a detalhes
- Resiliência
- Liderança (para supervisores)

**Escala:**
- 1: Abaixo do esperado
- 2: Atende parcialmente
- 3: Atende plenamente
- 4: Supera expectativas
- 5: Excepcional

**RF-AVAL-004: PDI (Plano de Desenvolvimento Individual)**
- Identificar gaps (competências com nota baixa)
- Definir ações de desenvolvimento:
  - Treinamentos
  - Cursos online
  - Mentoria
  - Job rotation
  - Leitura de livros/artigos
  - Shadowing (observar outro profissional)
- Responsável e prazo
- Acompanhamento mensal
- Atualização de status

**RF-AVAL-005: Feedbacks Contínuos**
- Gestor pode dar feedback a qualquer momento (não só na avaliação formal)
- Tipos: Positivo, Construtivo, Corretivo
- Funcionário pode pedir feedback
- Peer feedback (entre colegas)

**RF-AVAL-006: One-on-One**
- Reunião periódica (semanal, quinzenal) entre gestor e liderado
- Pauta livre: desafios, dúvidas, carreira, bem-estar
- Registro de notas
- Follow-up de ações

**RF-AVAL-007: Metas e OKRs**
- Definição de metas individuais e de equipe
- OKRs (Objectives and Key Results)
- Acompanhamento trimestral
- Check-ins
- Avaliação de atingimento

**RF-AVAL-008: 9-Box**
- Matriz 3x3: Performance (baixa, média, alta) x Potencial (baixo, médio, alto)
- Classificação dos funcionários
- Planos de sucessão
- Identificação de talentos

---

## 4.16 MÓDULO 16: Treinamento e Desenvolvimento

### 4.16.1 Visão Geral

**Objetivo:** Gerenciar todo o ciclo de treinamentos: levantamento de necessidades, planejamento, execução, avaliação e certificação.

**Escopo:**
- Levantamento de Necessidades de Treinamento (LNT)
- Catálogo de treinamentos
- Trilhas de aprendizagem
- Agendamento e convocação
- Registro de presença
- Avaliação de reação
- Certificados
- Matriz de competências
- LMS integrado

### 4.16.2 Funcionalidades Detalhadas

**RF-TREI-001: Levantamento de Necessidades (LNT)**
- A partir de avaliação de desempenho (gaps de competências)
- Solicitação de gestor
- Obrigatoriedade legal (NRs, reciclagem de vigilante)
- Planejamento estratégico da empresa

**RF-TREI-002: Catálogo de Treinamentos**
**Obrigatórios (Segurança do Trabalho):**
- NR-1: Disposições Gerais e Gerenciamento de Riscos Ocupacionais
- NR-6: EPI
- NR-10: Segurança em Instalações e Serviços em Eletricidade
- NR-35: Trabalho em Altura
- Reciclagem de Vigilante (a cada 2 anos)

**Técnicos:**
- Operação de CFTV
- Centrais de alarme
- Controle de acesso
- Combate a incêndio
- Primeiros socorros

**Comportamentais:**
- Atendimento ao cliente
- Comunicação
- Trabalho em equipe
- Liderança

**RF-TREI-003: Trilhas de Aprendizagem**
- Sequência de treinamentos por cargo
- Exemplo: Trilha do Vigilante
  1. Integração (obrigatório)
  2. Legislação e ética (obrigatório)
  3. Procedimentos operacionais (obrigatório)
  4. NR-1, NR-6 (obrigatório)
  5. Primeiros socorros (desejável)
  6. Defesa pessoal (desejável)

**RF-TREI-004: Agendamento**
- Treinamento interno (presencial ou EAD)
- Treinamento externo (fornecedor/escola)
- Turmas
- Instrutor
- Local
- Data/horário
- Material didático

**RF-TREI-005: Convocação**
- Notificação automática aos participantes
- Confirmação de presença
- Lembrete 1 dia antes

**RF-TREI-006: Registro de Presença**
- Lista de presença digital (assinatura no tablet)
- Controle de horas
- Frequência mínima para aprovação (ex: 75%)

**RF-TREI-007: Avaliação de Reação**
- Formulário pós-treinamento
- Avaliação do instrutor
- Avaliação do conteúdo
- Avaliação da infraestrutura
- Sugestões de melhoria

**RF-TREI-008: Avaliação de Aprendizagem**
- Prova/teste (múltipla escolha, dissertativa)
- Nota mínima para aprovação (ex: 7,0)
- Reaplicação se reprovado

**RF-TREI-009: Certificados**
- Geração automática de certificado digital
- Carga horária
- Conteúdo programático
- Data
- Assinatura digital (instrutor + RH)
- Download pelo app

**RF-TREI-010: Matriz de Competências**
- Visualização de competências x funcionários
- Identificação de gaps na equipe
- Planejamento de treinamentos

**RF-TREI-011: LMS Integrado**
- Cursos online (vídeos, textos, quizzes)
- Gamificação (pontos, badges)
- Ranking
- Certificação automática

---

## 4.17 MÓDULO 17: Segurança e Saúde do Trabalho (SST) COMPLETO

### 4.17.1 Visão Geral

**Objetivo:** Módulo COMPLETO de SST, gerenciando EPI, PGR, PCMSO, ASO, CIPA, CAT, exames médicos, treinamentos de NR e integração com eSocial S-2220, S-2240, S-2210.

**Escopo:**
- EPI (controle completo)
- PGR (Programa de Gerenciamento de Riscos)
- PCMSO (Programa de Controle Médico de Saúde Ocupacional)
- ASO (Atestado de Saúde Ocupacional)
- CIPA
- CAT (Comunicação de Acidente de Trabalho)
- LTCAT, PPP
- Exames médicos
- Treinamentos NR
- Insalubridade e Periculosidade
- Integração eSocial

### 4.17.2 Funcionalidades Detalhadas

**RF-SST-001: Gestão de EPI**

**Cadastro de EPI:**
- Tipos (conforme atividade):
  - Capacete
  - Óculos de proteção
  - Protetor auricular
  - Máscara/respirador
  - Luvas
  - Botas de segurança
  - Colete refletivo
  - Cinto de segurança (trabalho em altura)
- CA (Certificado de Aprovação) do MTE
- Validade do CA
- Fornecedor
- Custo
- Estoque

**Entrega de EPI:**
- Funcionário assina termo de entrega digitalmente (app + selfie)
- Foto do EPI entregue
- Data de entrega
- Prazo de validade/vida útil
- Alerta de vencimento
- Obrigatoriedade: funcionário só pode trabalhar com EPI entregue

**Devolução/Troca:**
- Motivo: fim de vida útil, danificado, perdido
- Termo de devolução
- Descarte adequado (se necessário)
- Nova entrega

**Ficha de EPI:**
- Histórico completo por funcionário
- Todos os EPIs já entregues
- EPIs em uso
- Comprovante de entrega (assinatura + foto)

**RF-SST-002: PGR (Programa de Gerenciamento de Riscos)**
- Substitui PPRA e PCMAT (NR-1 atualizada)
- Identificação de perigos e riscos por função/local:
  - Riscos físicos (ruído, calor, radiação)
  - Riscos químicos (poeiras, gases, vapores)
  - Riscos biológicos (vírus, bactérias)
  - Riscos ergonômicos (postura, repetitividade)
  - Riscos de acidentes (queda, choque, incêndio)
- Avaliação qualitativa e quantitativa
- Medidas de controle:
  - Eliminação
  - Substituição
  - Controle de engenharia
  - Controle administrativo
  - EPI
- Plano de ação
- Revisão anual
- Documentação completa

**RF-SST-003: PCMSO (Programa de Controle Médico de Saúde Ocupacional)**
- Objetivo: monitorar saúde dos trabalhadores
- Médico coordenador (responsável técnico)
- Exames obrigatórios por função:
  - Admissional
  - Periódico (anual)
  - Retorno ao trabalho (após afastamento > 30 dias)
  - Mudança de função
  - Demissional
- Exames complementares conforme riscos:
  - Audiometria (exposição a ruído)
  - Espirometria (exposição a poeiras)
  - Acuidade visual
  - Exames laboratoriais (sangue, urina)
- Agendamento
- Clínica conveniada
- Upload de ASO
- Controle de vencimento

**RF-SST-004: ASO (Atestado de Saúde Ocupacional)**
- Tipos:
  - Admissional
  - Periódico
  - Retorno ao trabalho
  - Mudança de função
  - Demissional
- Informações:
  - Dados do trabalhador
  - Função
  - Riscos ocupacionais
  - Exames realizados
  - Conclusão: **Apto** ou **Inapto**
  - Data
  - CRM do médico
  - Assinatura digital
- Integração eSocial (S-2220)
- Funcionário inapto: não pode trabalhar (bloqueio no ponto)

**RF-SST-005: CIPA (Comissão Interna de Prevenção de Acidentes)**
- Dimensionamento conforme CNAE e número de funcionários
- Eleição de membros
- Mandato (1 ano)
- Reuniões mensais:
  - Ata digital
  - Pauta
  - Deliberações
- Treinamento de cipeiros (20h)
- Mapa de riscos
- Investigação de acidentes

**RF-SST-006: CAT (Comunicação de Acidente de Trabalho)**
- Registro obrigatório em até 24h após acidente
- Informações:
  - Dados do acidentado
  - Data/hora/local do acidente
  - Descrição do acidente
  - Parte do corpo atingida
  - Agente causador
  - Testemunhas
  - Atendimento médico
  - Afastamento (sim/não, quantos dias)
- Envio para INSS
- Investigação de causas
- Plano de ação preventiva
- Integração eSocial (S-2210)

**RF-SST-007: LTCAT (Laudo Técnico das Condições Ambientais do Trabalho)**
- Elaborado por engenheiro ou médico do trabalho
- Identifica agentes nocivos (insalubres, periculosos)
- Medições (ruído, calor, etc)
- Conclusão: se há direito a adicional
- Base para PPP e aposentadoria especial

**RF-SST-008: PPP (Perfil Profissiográfico Previdenciário)**
- Documento obrigatório para todos os funcionários
- Histórico de exposição a agentes nocivos
- Base para aposentadoria especial
- Entregue na demissão
- Integração eSocial (S-2240)

**RF-SST-009: Exames Médicos**
- Agendamento online
- Clínicas conveniadas por região
- Lembretes automáticos
- Resultado: Apto/Inapto
- Restrições (se houver)
- Controle de vencimento (exames periódicos)

**RF-SST-010: Insalubridade e Periculosidade**
- Identificação via LTCAT
- Adicional de insalubridade:
  - Grau mínimo: 10% do salário mínimo
  - Grau médio: 20%
  - Grau máximo: 40%
- Adicional de periculosidade: 30% do salário base
- Não cumulativos (funcionário escolhe o maior)
- Integração com folha de pagamento

**RF-SST-011: Treinamentos de NR**
- Obrigatórios conforme atividade:
  - NR-1: todos
  - NR-6 (EPI): todos que usam EPI
  - NR-10 (Eletricidade): eletricistas, técnicos
  - NR-35 (Trabalho em Altura): quem trabalha > 2m de altura
  - NR-33 (Espaços Confinados): se aplicável
- Carga horária mínima
- Reciclagem periódica (a cada 2 anos)
- Certificado
- Controle de vencimento

**RF-SST-012: Integração com eSocial**
- S-2220: Monitoramento da Saúde do Trabalhador (ASO)
- S-2240: Condições Ambientais do Trabalho (LTCAT, fatores de risco)
- S-2210: Comunicação de Acidente de Trabalho (CAT)
- Envio automático
- Recibo de entrega
- Tratamento de erros

**RF-SST-013: Dashboard SST**
- Funcionários com exame vencido/próximo do vencimento
- EPIs a vencer
- Acidentes de trabalho (mês, ano, taxa de frequência)
- Taxa de absenteísmo por doença
- Treinamentos de NR vencidos
- Funcionários aptos vs. inaptos
- CATs emitidas

---

**CONTINUA NA PARTE 5...**

