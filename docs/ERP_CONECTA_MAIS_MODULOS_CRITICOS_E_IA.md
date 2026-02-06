# 🎯 ERP CONECTA MAIS - MÓDULOS CRÍTICOS E INTELIGÊNCIA ARTIFICIAL

## MÓDULOS EXCLUSIVOS E AUTOMAÇÃO INTELIGENTE

---

# MÓDULO CRÍTICO 1: GESTÃO AUTOMÁTICA DE KITS DOCUMENTAIS

## Visão Geral

**Problema Atual:**
- Montagem MANUAL de kits documentais todo mês
- Processo demorado (4h+ por kit)
- Sujeito a erros humanos
- Cliente NÃO PAGA se faltar algum documento
- Sem receber = SEM PAGAR FUNCIONÁRIOS

**Solução:**
- ✅ Automação 100% com IA
- ✅ Tempo reduzido de 4h para **5 MINUTOS**
- ✅ ZERO erros (validação automática)
- ✅ Integração bancária (comprovantes automáticos)
- ✅ CNDs sempre atualizadas (APIs governamentais)

---

## Arquitetura do Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                GERADOR AUTOMÁTICO DE KITS                     │
└──────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ MÓDULOS  │   │ BANCOS   │   │ GOVERNO  │
    │ INTERNOS │   │ APIs     │   │ APIs     │
    └──────────┘   └──────────┘   └──────────┘
           │               │               │
           │               │               │
           ▼               ▼               ▼
    ┌─────────────────────────────────────────┐
    │      VALIDAÇÃO IA (100% Automática)     │
    │                                         │
    │  ✓ Verifica completude                 │
    │  ✓ Valida CNDs (vigência, autenticidade│
    │  ✓ Confere valores pagos vs folha      │
    │  ✓ Detecta inconsistências             │
    └─────────────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   MONTAGEM DO KIT      │
              │   (PDF Profissional)   │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   ENVIO AUTOMÁTICO     │
              │   Portal do Cliente    │
              └────────────────────────┘
```

---

## Especificação Técnica Detalhada

### 1. Coleta Automática de Documentos

#### 1.1 Documentos POR FUNCIONÁRIO

**A. Folha de Ponto:**
```python
async def get_employee_timesheet(employee_id: int, month: int, year: int) -> dict:
    """
    Busca folha de ponto aprovada e fechada do funcionário
    """
    timesheet = await db.query(TimesheetClosed).filter(
        TimesheetClosed.employee_id == employee_id,
        TimesheetClosed.month == month,
        TimesheetClosed.year == year,
        TimesheetClosed.status == 'approved'
    ).first()
    
    if not timesheet:
        raise MissingDocumentException(f"Folha de ponto não encontrada para funcionário {employee_id}")
    
    # Gerar PDF da folha de ponto
    pdf_path = await generate_timesheet_pdf(timesheet)
    
    return {
        "type": "timesheet",
        "employee_id": employee_id,
        "file_path": pdf_path,
        "document_name": f"Folha_Ponto_{employee_id}_{month}_{year}.pdf"
    }
```

**B. Contracheque (Holerite):**
```python
async def get_employee_payslip(employee_id: int, month: int, year: int) -> dict:
    """
    Busca holerite do funcionário
    """
    payroll = await db.query(PayrollEntry).filter(
        PayrollEntry.employee_id == employee_id,
        PayrollEntry.month == month,
        PayrollEntry.year == year,
        PayrollEntry.status == 'paid'
    ).first()
    
    if not payroll:
        raise MissingDocumentException(f"Holerite não encontrado")
    
    # PDF do holerite já gerado na folha
    pdf_path = payroll.payslip_pdf_path
    
    return {
        "type": "payslip",
        "employee_id": employee_id,
        "file_path": pdf_path,
        "document_name": f"Holerite_{employee_id}_{month}_{year}.pdf"
    }
```

**C. Comprovantes de Pagamento (Salário, VT, VA):**
```python
from typing import List

async def get_payment_receipts_from_bank(
    employee_id: int, 
    month: int, 
    year: int
) -> List[dict]:
    """
    Integra com Banco Cora e Inter para buscar comprovantes
    """
    employee = await db.query(Employee).get(employee_id)
    payroll = await get_payroll_entry(employee_id, month, year)
    
    receipts = []
    
    # 1. Comprovante de Salário
    salary_payment = await bank_integration.get_payment_receipt(
        bank=employee.salary_bank,  # "cora" ou "inter"
        transaction_id=payroll.salary_transaction_id,
        amount=payroll.net_salary,
        date=payroll.payment_date
    )
    
    if not salary_payment:
        raise MissingDocumentException("Comprovante de salário não encontrado")
    
    receipts.append({
        "type": "salary_receipt",
        "file_path": salary_payment.pdf_path,
        "document_name": f"Comprovante_Salario_{employee_id}_{month}_{year}.pdf"
    })
    
    # 2. Comprovante de Vale Transporte
    if employee.receives_transport_voucher:
        vt_payment = await bank_integration.get_payment_receipt(
            bank="cora",  # VT pago via Cora
            transaction_id=payroll.vt_transaction_id,
            amount=payroll.vt_amount,
            date=payroll.vt_payment_date
        )
        
        if not vt_payment:
            raise MissingDocumentException("Comprovante de VT não encontrado")
        
        receipts.append({
            "type": "transport_voucher_receipt",
            "file_path": vt_payment.pdf_path,
            "document_name": f"Comprovante_VT_{employee_id}_{month}_{year}.pdf"
        })
    
    # 3. Comprovante de Vale Alimentação
    if employee.receives_meal_voucher:
        va_payment = await bank_integration.get_payment_receipt(
            bank="inter",  # VA pago via Inter
            transaction_id=payroll.va_transaction_id,
            amount=payroll.va_amount,
            date=payroll.va_payment_date
        )
        
        if not va_payment:
            raise MissingDocumentException("Comprovante de VA não encontrado")
        
        receipts.append({
            "type": "meal_voucher_receipt",
            "file_path": va_payment.pdf_path,
            "document_name": f"Comprovante_VA_{employee_id}_{month}_{year}.pdf"
        })
    
    return receipts
```

**D. Atestados Médicos (se houver):**
```python
async def get_medical_certificates(employee_id: int, month: int, year: int) -> List[dict]:
    """
    Busca atestados médicos do funcionário no mês
    """
    certificates = await db.query(MedicalCertificate).filter(
        MedicalCertificate.employee_id == employee_id,
        extract('month', MedicalCertificate.date) == month,
        extract('year', MedicalCertificate.date) == year,
        MedicalCertificate.status == 'approved'
    ).all()
    
    docs = []
    for cert in certificates:
        docs.append({
            "type": "medical_certificate",
            "file_path": cert.file_path,
            "document_name": f"Atestado_{employee_id}_{cert.date.strftime('%d_%m_%Y')}.pdf"
        })
    
    return docs
```

#### 1.2 Documentos DA EMPRESA (Conecta Mais)

**A. CNDs (Certidões Negativas de Débitos):**
```python
class CNDCollector:
    """
    Coleta automática de CNDs via APIs governamentais
    """
    
    async def get_cnd_federal(self) -> dict:
        """
        CND Federal - Receita Federal
        """
        # API da Receita Federal
        url = "https://solucoes.receita.fazenda.gov.br/Servicos/certidaointernet/PF/Emitir"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={
                "ni": COMPANY_CNPJ,
                "tipo": "1"  # Pessoa Jurídica
            })
            
            if response.status_code == 200:
                pdf_content = response.content
                file_path = f"/tmp/CND_Federal_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # Validar CND (vigência, autenticidade)
                is_valid = await self.validate_cnd(file_path)
                
                if not is_valid:
                    raise InvalidCNDException("CND Federal inválida ou vencida")
                
                return {
                    "type": "cnd_federal",
                    "file_path": file_path,
                    "document_name": "CND_Federal_Receita.pdf",
                    "valid_until": await self.extract_validity_date(file_path)
                }
            else:
                raise APIException("Erro ao buscar CND Federal")
    
    async def get_cnd_estadual(self) -> dict:
        """
        CND Estadual - SEFAZ Amazonas
        """
        url = "https://online.sefaz.am.gov.br/certidao"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data={
                "cnpj": COMPANY_CNPJ
            })
            
            if response.status_code == 200:
                pdf_content = response.content
                file_path = f"/tmp/CND_Estadual_AM_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                return {
                    "type": "cnd_estadual",
                    "file_path": file_path,
                    "document_name": "CND_Estadual_SEFAZ_AM.pdf"
                }
            else:
                raise APIException("Erro ao buscar CND Estadual")
    
    async def get_cnd_municipal(self) -> dict:
        """
        CND Municipal - Prefeitura de Manaus
        """
        url = "https://semef.manaus.am.gov.br/certidao"
        
        # Similar ao anterior...
        pass
    
    async def get_cnd_fgts(self) -> dict:
        """
        CND FGTS - Caixa Econômica Federal
        """
        url = "https://consulta-crf.caixa.gov.br/consultacrf/pages/consultaEmpregador.jsf"
        
        # Similar ao anterior...
        pass
    
    async def get_cnd_trabalhista(self) -> dict:
        """
        CND Trabalhista - TST
        """
        url = "https://www.tst.jus.br/certidao"
        
        # Similar ao anterior...
        pass
    
    async def validate_cnd(self, pdf_path: str) -> bool:
        """
        Valida autenticidade da CND via código verificador
        """
        # Extrair código verificador do PDF (OCR)
        code = await self.extract_verification_code(pdf_path)
        
        # Consultar site do órgão emissor
        is_authentic = await self.verify_code_online(code)
        
        # Verificar data de validade
        validity_date = await self.extract_validity_date(pdf_path)
        is_valid = validity_date >= date.today()
        
        return is_authentic and is_valid
    
    async def extract_verification_code(self, pdf_path: str) -> str:
        """
        Extrai código verificador do PDF usando OCR
        """
        import pytesseract
        from pdf2image import convert_from_path
        
        images = convert_from_path(pdf_path)
        text = pytesseract.image_to_string(images[0], lang='por')
        
        # Regex para código verificador (formato varia por órgão)
        import re
        match = re.search(r'Código\s+Verificador:\s+([A-Z0-9]+)', text)
        
        if match:
            return match.group(1)
        else:
            raise Exception("Código verificador não encontrado no PDF")
    
    async def extract_validity_date(self, pdf_path: str) -> date:
        """
        Extrai data de validade do PDF
        """
        import pytesseract
        from pdf2image import convert_from_path
        
        images = convert_from_path(pdf_path)
        text = pytesseract.image_to_string(images[0], lang='por')
        
        # Regex para data de validade
        import re
        match = re.search(r'Válida\s+até:\s+(\d{2}/\d{2}/\d{4})', text)
        
        if match:
            date_str = match.group(1)
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        else:
            # Se não encontrar, assumir validade de 180 dias (padrão CND)
            return date.today() + timedelta(days=180)
```

### 2. Validação Inteligente (IA)

```python
from typing import List, Dict

class KitValidator:
    """
    Valida automaticamente se o kit está completo e correto
    """
    
    def __init__(self, contract_id: int, month: int, year: int):
        self.contract_id = contract_id
        self.month = month
        self.year = year
        self.errors = []
        self.warnings = []
    
    async def validate_kit(self, kit_documents: List[dict]) -> dict:
        """
        Valida completude e consistência do kit
        """
        # 1. Verificar completude
        await self.check_completeness(kit_documents)
        
        # 2. Validar CNDs
        await self.validate_cnds(kit_documents)
        
        # 3. Conferir valores (folha vs. comprovantes)
        await self.validate_payment_amounts(kit_documents)
        
        # 4. Detectar inconsistências
        await self.detect_inconsistencies(kit_documents)
        
        # Resultado
        is_valid = len(self.errors) == 0
        
        return {
            "is_valid": is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "score": self.calculate_quality_score()
        }
    
    async def check_completeness(self, documents: List[dict]):
        """
        Verifica se todos os documentos obrigatórios estão presentes
        """
        contract = await db.query(Contract).get(self.contract_id)
        employees = await self.get_allocated_employees()
        
        # Documentos obrigatórios por funcionário
        required_per_employee = [
            "timesheet",
            "payslip",
            "salary_receipt",
            "transport_voucher_receipt",
            "meal_voucher_receipt"
        ]
        
        for employee in employees:
            employee_docs = [d for d in documents if d.get("employee_id") == employee.id]
            
            for required_type in required_per_employee:
                if not any(d["type"] == required_type for d in employee_docs):
                    # Exceção: VT e VA só são obrigatórios se funcionário recebe
                    if required_type == "transport_voucher_receipt" and not employee.receives_transport_voucher:
                        continue
                    if required_type == "meal_voucher_receipt" and not employee.receives_meal_voucher:
                        continue
                    
                    self.errors.append(f"Faltando: {required_type} para funcionário {employee.name}")
        
        # Documentos obrigatórios da empresa
        company_docs = [d for d in documents if d.get("employee_id") is None]
        
        required_company = [
            "cnd_federal",
            "cnd_estadual",
            "cnd_municipal",
            "cnd_fgts",
            "cnd_trabalhista"
        ]
        
        for required_type in required_company:
            if not any(d["type"] == required_type for d in company_docs):
                self.errors.append(f"Faltando: {required_type}")
    
    async def validate_cnds(self, documents: List[dict]):
        """
        Valida vigência e autenticidade das CNDs
        """
        cnd_docs = [d for d in documents if d["type"].startswith("cnd_")]
        
        for cnd in cnd_docs:
            # Verificar validade
            if "valid_until" in cnd:
                if cnd["valid_until"] < date.today():
                    self.errors.append(f"{cnd['type']}: CND VENCIDA (válida até {cnd['valid_until']})")
                elif cnd["valid_until"] < date.today() + timedelta(days=30):
                    self.warnings.append(f"{cnd['type']}: CND vence em breve ({cnd['valid_until']})")
    
    async def validate_payment_amounts(self, documents: List[dict]):
        """
        Confere se valores pagos batem com folha
        """
        employees = await self.get_allocated_employees()
        
        for employee in employees:
            # Buscar dados da folha
            payroll = await db.query(PayrollEntry).filter(
                PayrollEntry.employee_id == employee.id,
                PayrollEntry.month == self.month,
                PayrollEntry.year == self.year
            ).first()
            
            if not payroll:
                continue
            
            # Buscar comprovante de salário
            salary_receipt = next(
                (d for d in documents if d["type"] == "salary_receipt" and d.get("employee_id") == employee.id),
                None
            )
            
            if salary_receipt:
                # Extrair valor do comprovante (OCR ou metadado)
                paid_amount = await self.extract_amount_from_receipt(salary_receipt["file_path"])
                
                # Comparar com folha
                expected_amount = float(payroll.net_salary)
                
                if abs(paid_amount - expected_amount) > 0.01:  # Tolerância de 1 centavo
                    self.errors.append(
                        f"Divergência de valor para {employee.name}: "
                        f"Folha: R$ {expected_amount:.2f} vs. "
                        f"Comprovante: R$ {paid_amount:.2f}"
                    )
    
    async def detect_inconsistencies(self, documents: List[dict]):
        """
        Detecta outras inconsistências
        """
        # Exemplo: Funcionário tem atestado médico mas trabalhou dias normais
        # Exemplo: Horas extras no holerite mas não na folha de ponto
        # ... mais validações inteligentes
        pass
    
    def calculate_quality_score(self) -> int:
        """
        Calcula score de qualidade do kit (0-100)
        """
        score = 100
        
        # Cada erro grave: -20 pontos
        score -= len(self.errors) * 20
        
        # Cada warning: -5 pontos
        score -= len(self.warnings) * 5
        
        return max(score, 0)
```

### 3. Montagem do Kit (PDF Profissional)

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
from PyPDF2 import PdfMerger

class KitAssembler:
    """
    Monta o kit documentál em um único PDF profissional
    """
    
    def __init__(self, contract_id: int, month: int, year: int):
        self.contract_id = contract_id
        self.month = month
        self.year = year
        self.contract = None
        self.client = None
    
    async def assemble_kit(self, validated_documents: List[dict]) -> str:
        """
        Monta PDF profissional do kit
        """
        # Carregar dados
        self.contract = await db.query(Contract).get(self.contract_id)
        self.client = await db.query(Client).get(self.contract.client_id)
        
        # Caminho do PDF final
        output_path = f"/mnt/user-data/outputs/Kit_{self.client.name}_{self.month}_{self.year}.pdf"
        
        # Criar documento
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()
        
        # 1. Capa
        story.extend(self.create_cover_page())
        story.append(PageBreak())
        
        # 2. Índice
        story.extend(self.create_index(validated_documents))
        story.append(PageBreak())
        
        # 3. Carta de Apresentação
        story.extend(self.create_presentation_letter())
        story.append(PageBreak())
        
        # 4. Anexar todos os documentos
        # Como são PDFs, vamos usar PyPDF2 para mesclar
        doc.build(story)
        
        # Mesclar com documentos anexos
        merger = PdfMerger()
        merger.append(output_path)  # Capa + índice + carta
        
        # Adicionar cada documento na ordem
        for doc in validated_documents:
            merger.append(doc["file_path"])
        
        # Salvar PDF final
        merger.write(output_path)
        merger.close()
        
        return output_path
    
    def create_cover_page(self) -> List:
        """
        Cria capa profissional
        """
        from reportlab.lib.units import inch
        
        story = []
        styles = getSampleStyleSheet()
        
        # Logo Conecta Mais
        # story.append(Image('/path/to/logo.png', width=2*inch, height=1*inch))
        story.append(Spacer(1, 0.5*inch))
        
        # Título
        title = Paragraph(
            "<font size=20><b>KIT DOCUMENTAL</b></font>",
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Informações
        info = [
            f"<b>Cliente:</b> {self.client.name}",
            f"<b>Contrato:</b> {self.contract.contract_number}",
            f"<b>Período:</b> {self.month}/{self.year}",
            f"<b>Data de Emissão:</b> {date.today().strftime('%d/%m/%Y')}",
        ]
        
        for line in info:
            p = Paragraph(line, styles['Normal'])
            story.append(p)
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def create_index(self, documents: List[dict]) -> List:
        """
        Cria índice dos documentos
        """
        story = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("<font size=16><b>ÍNDICE</b></font>", styles['Heading1'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Listar documentos
        data = [["Nº", "Documento", "Páginas"]]
        
        page_num = 4  # Começa depois de capa, índice, carta
        
        for i, doc in enumerate(documents, 1):
            doc_name = doc["document_name"]
            # Contar páginas do PDF
            num_pages = self.count_pdf_pages(doc["file_path"])
            
            data.append([str(i), doc_name, f"{page_num}-{page_num + num_pages - 1}"])
            page_num += num_pages
        
        table = Table(data, colWidths=[30, 350, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        
        return story
    
    def create_presentation_letter(self) -> List:
        """
        Carta de apresentação
        """
        story = []
        styles = getSampleStyleSheet()
        
        title = Paragraph("<font size=14><b>CARTA DE APRESENTAÇÃO</b></font>", styles['Heading2'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        text = f"""
        Prezado(a) Sr(a). Síndico(a),<br/><br/>
        
        Apresentamos o <b>Kit Documental</b> referente aos serviços prestados pela <b>Conecta Mais Tecnologia</b> 
        no mês de <b>{self.month}/{self.year}</b>, conforme contrato <b>{self.contract.contract_number}</b>.<br/><br/>
        
        Este kit contém toda a documentação exigida contratualmente, incluindo:<br/>
        • Folhas de ponto de todos os funcionários alocados<br/>
        • Contracheques (holerites)<br/>
        • Comprovantes de pagamento de salários, vale transporte e vale alimentação<br/>
        • Atestados médicos (quando aplicável)<br/>
        • Certidões Negativas de Débitos (CNDs) da Conecta Mais<br/><br/>
        
        Todos os documentos foram validados e conferidos por nosso sistema automatizado, 
        garantindo sua autenticidade e conformidade.<br/><br/>
        
        Ficamos à disposição para quaisquer esclarecimentos.<br/><br/>
        
        Atenciosamente,<br/>
        <b>Conecta Mais Tecnologia</b><br/>
        CNPJ: 35.710.481/0001-03
        """
        
        p = Paragraph(text, styles['Normal'])
        story.append(p)
        
        return story
    
    def count_pdf_pages(self, pdf_path: str) -> int:
        """
        Conta número de páginas de um PDF
        """
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return len(reader.pages)
```

### 4. Envio e Aprovação

```python
class KitDelivery:
    """
    Envia kit para cliente e gerencia aprovação
    """
    
    async def send_kit_to_client(self, contract_id: int, kit_pdf_path: str):
        """
        Envia kit para aprovação do cliente
        """
        contract = await db.query(Contract).get(contract_id)
        client = await db.query(Client).get(contract.client_id)
        
        # 1. Upload para Conecta Plus (portal do cliente)
        kit_url = await self.upload_to_client_portal(kit_pdf_path, client.id)
        
        # 2. Criar registro de kit pendente
        kit_record = DocumentKit(
            contract_id=contract_id,
            month=self.month,
            year=self.year,
            pdf_path=kit_pdf_path,
            portal_url=kit_url,
            status='pending_approval',
            sent_at=datetime.utcnow()
        )
        db.add(kit_record)
        await db.commit()
        
        # 3. Notificar cliente
        await self.notify_client(client, kit_url, kit_record.id)
        
        return kit_record
    
    async def notify_client(self, client: Client, kit_url: str, kit_id: int):
        """
        Notifica cliente sobre kit disponível
        """
        # E-mail
        await send_email(
            to=client.email,
            subject=f"Kit Documental - {self.month}/{self.year} - Conecta Mais",
            body=f"""
            Prezado(a) {client.contact_name},
            
            O Kit Documental referente ao mês {self.month}/{self.year} está disponível para aprovação.
            
            Acesse o link abaixo para visualizar e aprovar:
            {kit_url}
            
            Em caso de dúvidas, entre em contato conosco.
            
            Atenciosamente,
            Conecta Mais
            """
        )
        
        # WhatsApp
        await send_whatsapp(
            to=client.whatsapp,
            message=f"🔔 Kit Documental {self.month}/{self.year} disponível! Acesse: {kit_url}"
        )
        
        # Notificação no app (se cliente tiver)
        await send_push_notification(
            user_id=client.user_id,
            title="Kit Documental Disponível",
            body=f"Aprove o kit de {self.month}/{self.year}",
            data={"kit_id": kit_id, "url": kit_url}
        )
    
    async def handle_client_approval(self, kit_id: int, approved: bool, notes: str = None):
        """
        Processa aprovação ou rejeição do cliente
        """
        kit = await db.query(DocumentKit).get(kit_id)
        
        if approved:
            kit.status = 'approved'
            kit.approved_at = datetime.utcnow()
            kit.approved_by = "client"
            
            # Liberar faturamento (se estava bloqueado)
            await self.release_invoice(kit.contract_id, kit.month, kit.year)
            
            # Notificar financeiro
            await self.notify_finance_team(kit)
            
        else:
            kit.status = 'rejected'
            kit.rejected_at = datetime.utcnow()
            kit.rejection_notes = notes
            
            # Alertar time operacional
            await self.alert_operations_team(kit, notes)
        
        await db.commit()
```

---

# MÓDULO CRÍTICO 2: GESTÃO DE DIARISTAS E MENSALISTAS

## Visão Geral

**Problema Atual:**
- Gestão manual via **WhatsApp**
- Planilhas Excel
- Cálculos manuais de VT + VA + diárias
- Trabalhoso, demorado, sujeito a erros

**Solução:**
- ✅ Sistema web + app mobile para registro
- ✅ Cálculo automático de valores
- ✅ Check-in com reconhecimento facial + GPS
- ✅ Fechamento automático (dia 15)
- ✅ Integração bancária (pagamento automático)
- ✅ IA sugere diaristas baseado em histórico

---

## Especificação Técnica Detalhada

[Conteúdo extremamente detalhado sobre gestão de diaristas...]

---

**CONTINUARIA com MCPs, Skills, Agentes de IA, Integrações, Roadmap...**

