"""
Parser PDF Folha de Pagamento — Portte Contabil / Domínio Sistemas
Extrai rubricas individuais por funcionário do Extrato Mensal

Fonte de verdade: Domínio Sistemas (Sistema A)
NÃO sobrescreve hr_payslips — apenas popula hr_payslip_items
"""

import logging
import re
from dataclasses import dataclass, field
from decimal import Decimal

logger = logging.getLogger(__name__)


@dataclass
class RubricaFolha:
    codigo: str
    descricao: str
    tipo: str  # P=provento D=desconto
    referencia: str = ""
    valor: Decimal = Decimal("0")


@dataclass
class FuncionarioFolha:
    matricula: str
    nome: str
    cpf: str
    situacao: str
    cargo: str = ""
    salario: Decimal = Decimal("0")
    data_admissao: str = ""
    total_proventos: Decimal = Decimal("0")
    total_descontos: Decimal = Decimal("0")
    liquido: Decimal = Decimal("0")
    inss_base: Decimal = Decimal("0")
    inss_valor: Decimal = Decimal("0")
    fgts_base: Decimal = Decimal("0")
    fgts_valor: Decimal = Decimal("0")
    irrf_base: Decimal = Decimal("0")
    rubricas: list[RubricaFolha] = field(default_factory=list)


def _br2dec(s: str) -> Decimal:
    """Converte string BR (1.234,56) para Decimal."""
    try:
        return Decimal(s.replace(".", "").replace(",", "."))
    except Exception:
        return Decimal("0")


class FolhaPDFParser:
    """
    Parser do Extrato Mensal Domínio Sistemas / Portte
    Formato: EXTRATO MENSAL MM/AAAA (pdfplumber)
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.funcionarios: list[FuncionarioFolha] = []
        self.competencia: str = ""

    def parse(self) -> list[FuncionarioFolha]:
        try:
            import pdfplumber
        except ImportError:
            logger.error("pdfplumber não instalado — instale com: pip install pdfplumber")
            return []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                texto = ""
                for page in pdf.pages:
                    texto += (page.extract_text() or "") + "\n"
            # Extrair competência do cabeçalho
            m = re.search(r"EXTRATO MENSAL\s+(\d{2}/\d{4})", texto)
            if m:
                self.competencia = m.group(1)
            self.funcionarios = self._parse_texto(texto)
            logger.info(f"PDF {self.pdf_path}: {len(self.funcionarios)} funcionários, competência {self.competencia}")
            return self.funcionarios
        except Exception as e:
            logger.error(f"Erro parse PDF: {e}")
            return []

    def _parse_texto(self, texto: str) -> list[FuncionarioFolha]:
        funcs = []
        # Dividir por bloco de funcionário
        # Padrão Domínio: "Empr.: 85 ADAILSON SERRA ALVES Situação: Trabalhando"
        blocos = re.split(r"(?=Empr\.:\s*\d+\s+[A-ZÁÉÍÓÚÃÕÇ])", texto)
        for bloco in blocos:
            if not bloco.strip() or "Empr.:" not in bloco:
                continue
            func = self._parse_bloco(bloco)
            if func:
                funcs.append(func)
        return funcs

    def _parse_bloco(self, bloco: str) -> "FuncionarioFolha | None":
        # Cabeçalho funcionário
        m = re.search(
            r"Empr\.:\s*(\d+)\s+(.+?)\s+Situação:\s*(.+?)\s+"
            r"CPF:\s*([\d.\-]+)\s+Adm:\s*(\d{2}/\d{2}/\d{4})",
            bloco,
        )
        if not m:
            return None
        matricula = m.group(1).strip()
        nome = m.group(2).strip()
        situacao = m.group(3).strip()
        cpf = m.group(4).strip()
        admissao = m.group(5).strip()

        # Totais Proventos/Descontos/Líquido
        t = re.search(
            r"Proventos:\s*([\d.,]+)\s+Descontos:\s*([\d.,]+)"
            r".+?Líquido:.+?([\d.,]+)\s*$",
            bloco,
            re.MULTILINE,
        )
        proventos = _br2dec(t.group(1)) if t else Decimal("0")
        descontos = _br2dec(t.group(2)) if t else Decimal("0")
        liquido = _br2dec(t.group(3)) if t else Decimal("0")

        # Bases INSS / FGTS / IRRF
        inss_base = fgts_base = fgts_valor = irrf_base = Decimal("0")
        b = re.search(
            r"Base INSS:\s*([\d.,]+).*?"
            r"Base FGTS:\s*([\d.,]+)\s+Valor FGTS:\s*([\d.,]+)"
            r".*?Base IRRF:\s*([\d.,]+)",
            bloco,
            re.DOTALL,
        )
        if b:
            inss_base = _br2dec(b.group(1))
            fgts_base = _br2dec(b.group(2))
            fgts_valor = _br2dec(b.group(3))
            irrf_base = _br2dec(b.group(4))

        # INSS valor — rubrica 998
        inss_m = re.search(r"998\s+I\.N\.S\.S\.\s+[\d.,]+\s+([\d.,]+)\s+D", bloco)
        inss_valor = _br2dec(inss_m.group(1)) if inss_m else Decimal("0")

        # Cargo e salário
        cargo_m = re.search(r"Cargo:\s*\d+\s+(.+?)\s+C\.B\.O.*?Salário:\s*([\d.,]+)", bloco)
        cargo = cargo_m.group(1).strip() if cargo_m else ""
        salario = _br2dec(cargo_m.group(2)) if cargo_m else Decimal("0")

        # Rubricas — padrão Domínio Sistemas:
        # 224 ADICIONAL DE RONDA   15,00   250,50  P
        rubricas = []
        for rm in re.finditer(
            r"^(\d{1,4})\s+([A-ZÁÉÍÓÚÃÕÇÀÂÊÎÔÛ0-9][^\n]+?)\s+"
            r"([\d:.,]+)\s+([\d.,]+)\s+([PD])\s*$",
            bloco,
            re.MULTILINE,
        ):
            try:
                rubricas.append(
                    RubricaFolha(
                        codigo=rm.group(1).strip(),
                        descricao=rm.group(2).strip(),
                        tipo=rm.group(5).strip(),
                        referencia=rm.group(3).strip(),
                        valor=_br2dec(rm.group(4)),
                    )
                )
            except Exception:
                pass

        return FuncionarioFolha(
            matricula=matricula,
            nome=nome,
            cpf=cpf,
            situacao=situacao,
            cargo=cargo,
            salario=salario,
            data_admissao=admissao,
            total_proventos=proventos,
            total_descontos=descontos,
            liquido=liquido,
            inss_base=inss_base,
            inss_valor=inss_valor,
            fgts_base=fgts_base,
            fgts_valor=fgts_valor,
            irrf_base=irrf_base,
            rubricas=rubricas,
        )

    def validar_totais(
        self,
        esperado_proventos: Decimal = Decimal("97504.07"),
        esperado_descontos: Decimal = Decimal("30826.48"),
    ) -> dict:
        tp = sum(f.total_proventos for f in self.funcionarios)
        td = sum(f.total_descontos for f in self.funcionarios)
        tl = sum(f.liquido for f in self.funcionarios)
        return {
            "competencia": self.competencia,
            "funcionarios": len(self.funcionarios),
            "total_proventos": float(tp),
            "total_descontos": float(td),
            "liquido_geral": float(tl),
            "confere_dominio_proventos": abs(tp - esperado_proventos) < 1,
            "confere_dominio_descontos": abs(td - esperado_descontos) < 1,
        }


def importar_rubricas(
    parser: FolhaPDFParser,
    competencia_mes: int,
    competencia_ano: int,
    db_conn,
) -> dict:
    """
    Popula hr_payslip_items com rubricas do PDF
    NÃO modifica hr_payslips (T2 é responsável)
    Também preenche inss_value/fgts_value/irrf_base se NULL
    """
    salvos = 0
    erros = []
    cur = db_conn.cursor()

    for func in parser.funcionarios:
        # Buscar payslip por CPF + competência
        cur.execute(
            """
            SELECT p.id, p.inss_value, p.fgts_value
            FROM hr_payslips p
            JOIN employees e ON e.id = p.employee_id
            WHERE e.cpf = %s
              AND p.reference_month = %s
              AND p.reference_year = %s
            LIMIT 1
            """,
            (func.cpf, competencia_mes, competencia_ano),
        )
        row = cur.fetchone()
        if not row:
            erros.append(f"Sem payslip: {func.nome}")
            continue

        payslip_id, inss_atual, fgts_atual = row

        # Deletar rubricas antigas
        cur.execute("DELETE FROM hr_payslip_items WHERE payslip_id = %s", (payslip_id,))

        # Inserir rubricas do PDF
        for rub in func.rubricas:
            try:
                cur.execute(
                    """
                    INSERT INTO hr_payslip_items
                      (payslip_id, codigo, descricao, tipo, referencia, valor)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        payslip_id,
                        rub.codigo,
                        rub.descricao,
                        rub.tipo,
                        rub.referencia,
                        float(rub.valor),
                    ),
                )
                salvos += 1
            except Exception as e:
                erros.append(f"Rub {rub.codigo}/{func.nome}: {e}")

        # Preencher bases fiscais se NULL (não conflita com T2)
        if inss_atual is None and func.inss_valor > 0:
            cur.execute(
                """
                UPDATE hr_payslips SET
                    inss_base = %s, inss_value = %s,
                    fgts_base = %s, fgts_value = %s,
                    irrf_base = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    float(func.inss_base),
                    float(func.inss_valor),
                    float(func.fgts_base),
                    float(func.fgts_valor),
                    float(func.irrf_base),
                    payslip_id,
                ),
            )
        db_conn.commit()

    return {
        "rubricas_salvas": salvos,
        "erros": len(erros),
        "primeiros_erros": erros[:3],
    }


async def importar_rubricas_async(
    parser: FolhaPDFParser,
    competencia_mes: int,
    competencia_ano: int,
    db,  # AsyncSession SQLAlchemy
) -> dict:
    """
    Popula hr_payslip_items com rubricas do PDF (versão async).
    NÃO modifica totais de hr_payslips — apenas insere rubricas.
    Preenche inss_value/fgts_value/irrf_base SOMENTE se NULL.
    """
    from sqlalchemy import text

    salvos = 0
    erros = []

    for func in parser.funcionarios:
        # Buscar payslip por CPF + competência
        result = await db.execute(
            text("""
                SELECT p.id, p.inss_value, p.fgts_value
                FROM hr_payslips p
                JOIN employees e ON e.id = p.employee_id
                WHERE e.cpf = :cpf
                  AND p.reference_month = :mes
                  AND p.reference_year = :ano
                LIMIT 1
            """),
            {"cpf": func.cpf, "mes": competencia_mes, "ano": competencia_ano},
        )
        row = result.fetchone()
        if not row:
            erros.append(f"Sem payslip: {func.nome} ({func.cpf})")
            continue

        payslip_id, inss_atual, fgts_atual = row

        # Deletar rubricas antigas deste payslip
        await db.execute(
            text("DELETE FROM hr_payslip_items WHERE payslip_id = :pid"),
            {"pid": payslip_id},
        )

        # Inserir rubricas extraídas do PDF
        for rub in func.rubricas:
            try:
                await db.execute(
                    text("""
                        INSERT INTO hr_payslip_items
                            (payslip_id, codigo, descricao, tipo, referencia, valor)
                        VALUES (:pid, :cod, :desc, :tipo, :ref, :val)
                    """),
                    {
                        "pid": payslip_id,
                        "cod": rub.codigo,
                        "desc": rub.descricao,
                        "tipo": rub.tipo,
                        "ref": rub.referencia,
                        "val": float(rub.valor),
                    },
                )
                salvos += 1
            except Exception as e:
                erros.append(f"Rub {rub.codigo}/{func.nome}: {e}")

        # Preencher bases fiscais se NULL (não conflita com T2)
        if inss_atual is None and func.inss_valor > 0:
            await db.execute(
                text("""
                    UPDATE hr_payslips SET
                        inss_base    = :inss_base,
                        inss_value   = :inss_val,
                        fgts_base    = :fgts_base,
                        fgts_value   = :fgts_val,
                        irrf_base    = :irrf_base,
                        updated_at   = NOW()
                    WHERE id = :pid
                """),
                {
                    "inss_base": float(func.inss_base),
                    "inss_val": float(func.inss_valor),
                    "fgts_base": float(func.fgts_base),
                    "fgts_val": float(func.fgts_valor),
                    "irrf_base": float(func.irrf_base),
                    "pid": payslip_id,
                },
            )

        await db.commit()

    return {
        "rubricas_salvas": salvos,
        "erros": len(erros),
        "primeiros_erros": erros[:5],
    }
