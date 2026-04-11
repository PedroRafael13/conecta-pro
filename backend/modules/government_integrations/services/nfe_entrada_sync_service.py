"""
NF-e Entrada Sync Service
Consulta NF-e de compra emitidas CONTRA o CNPJ da empresa no SEFAZ
e atualiza o estoque virtual em nfe_compras_estoque.

Tabelas gerenciadas (criadas automaticamente):
  - nfe_entradas        : log de NF-e recebidas de fornecedores
  - nfe_compras_estoque : estoque virtual atualizado por media ponderada
"""

import logging
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

CNPJ_EMPRESA = os.getenv("NFSE_MANAUS_CNPJ", "35710481000103")
CERT_PATH = os.getenv("CERTIFICATE_PATH", "/app/credentials/certificates/certificado.pfx")
CERT_PASS = os.getenv("CERTIFICATE_PASSWORD", "Conecta123")
SEFAZ_DIST = "https://www1.nfe.fazenda.gov.br/NFeDistribuicaoDFe/NFeDistribuicaoDFe.asmx"
NS = "http://www.portalfiscal.inf.br/nfe"


def _get_sync_db_url() -> str:
    """Converte DATABASE_URL asyncpg → psycopg2 síncrono."""
    url = os.getenv("DATABASE_URL", "")
    return url.replace("+asyncpg", "")


class NFEEntradaSyncService:
    """Serviço para recebimento e processamento de NF-e de compra."""

    # ------------------------------------------------------------------ #
    #  DDL — cria tabelas se não existirem                                 #
    # ------------------------------------------------------------------ #

    DDL_ENTRADAS = """
    CREATE TABLE IF NOT EXISTS nfe_entradas (
        id              SERIAL PRIMARY KEY,
        chave_acesso    VARCHAR(44) UNIQUE NOT NULL,
        nsu             VARCHAR(20),
        numero          VARCHAR(20),
        serie           VARCHAR(5),
        emitente_cnpj   VARCHAR(14),
        emitente_nome   VARCHAR(200),
        destinatario_cnpj VARCHAR(14),
        data_emissao    DATE,
        valor_total     NUMERIC(15,2),
        status          VARCHAR(30) DEFAULT 'recebida',
        xml_raw         TEXT,
        processada      BOOLEAN DEFAULT FALSE,
        created_at      TIMESTAMP DEFAULT NOW()
    );
    """

    DDL_ESTOQUE = """
    CREATE TABLE IF NOT EXISTS nfe_compras_estoque (
        id                  SERIAL PRIMARY KEY,
        item_code           VARCHAR(60) UNIQUE NOT NULL,
        descricao           VARCHAR(200),
        ncm                 VARCHAR(8),
        unidade             VARCHAR(6),
        qty_on_hand         NUMERIC(15,4) DEFAULT 0,
        unit_cost           NUMERIC(15,4) DEFAULT 0,
        avg_cost            NUMERIC(15,4) DEFAULT 0,
        last_purchase_date  DATE,
        last_nfe_key        VARCHAR(44),
        updated_at          TIMESTAMP DEFAULT NOW()
    );
    """

    def _get_conn(self):
        import psycopg2

        url = _get_sync_db_url()
        return psycopg2.connect(url)

    def _ensure_tables(self, conn) -> None:
        with conn.cursor() as cur:
            cur.execute(self.DDL_ENTRADAS)
            cur.execute(self.DDL_ESTOQUE)
        conn.commit()

    # ------------------------------------------------------------------ #
    #  mTLS — extrai cert + key do PFX para arquivos temporários           #
    # ------------------------------------------------------------------ #

    def _get_mtls_certs(self) -> tuple[str, str] | tuple[None, None]:
        try:
            from cryptography.hazmat.primitives.serialization import (
                Encoding,
                NoEncryption,
                PrivateFormat,
                pkcs12,
            )

            with open(CERT_PATH, "rb") as f:
                pfx_data = f.read()

            private_key, certificate, _ = pkcs12.load_key_and_certificates(pfx_data, CERT_PASS.encode())

            cert_pem = certificate.public_bytes(Encoding.PEM)
            key_pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption())

            cert_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")  # noqa: SIM115
            cert_file.write(cert_pem)
            cert_file.flush()

            key_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")  # noqa: SIM115
            key_file.write(key_pem)
            key_file.flush()

            return cert_file.name, key_file.name
        except Exception as exc:
            logger.warning("mTLS cert extraction failed: %s", exc)
            return None, None

    # ------------------------------------------------------------------ #
    #  SEFAZ — busca NF-e recebidas via DistribuicaoDFe                   #
    # ------------------------------------------------------------------ #

    def buscar_nfe_recebidas(self, ultimo_nsu: str = "0") -> dict:
        """
        Consulta NF-e emitidas CONTRA nosso CNPJ no SEFAZ Nacional.
        Retorna dict com lista de documentos recebidos.
        """
        import requests

        envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:nfe="http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe">
  <soapenv:Body>
    <nfe:nfeDistDFeInteresse>
      <nfeDadosMsg>
        <distDFeInt xmlns="http://www.portalfiscal.inf.br/nfe" versao="1.01">
          <tpAmb>1</tpAmb>
          <cUFAutor>91</cUFAutor>
          <CNPJ>{CNPJ_EMPRESA}</CNPJ>
          <distNSU>
            <ultNSU>{ultimo_nsu.zfill(15)}</ultNSU>
          </distNSU>
        </distDFeInt>
      </nfeDadosMsg>
    </nfe:nfeDistDFeInteresse>
  </soapenv:Body>
</soapenv:Envelope>"""

        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "http://www.portalfiscal.inf.br/nfe/wsdl/NFeDistribuicaoDFe/nfeDistDFeInteresse",
        }

        cert_file, key_file = self._get_mtls_certs()
        cert_arg = (cert_file, key_file) if cert_file else None

        try:
            resp = requests.post(
                SEFAZ_DIST,
                data=envelope.encode("utf-8"),
                headers=headers,
                cert=cert_arg,
                timeout=30,
                verify=True,
            )
            resp.raise_for_status()
            return {"sucesso": True, "xml_resposta": resp.text, "status_http": resp.status_code}
        except Exception as exc:
            logger.error("SEFAZ DistribuicaoDFe error: %s", exc)
            return {"sucesso": False, "erro": str(exc)}
        finally:
            if cert_file:
                try:
                    os.unlink(cert_file)
                    os.unlink(key_file)
                except Exception:
                    pass

    # ------------------------------------------------------------------ #
    #  XML — parse NF-e e atualiza estoque                                 #
    # ------------------------------------------------------------------ #

    def processar_xml_nfe(self, xml_nfe: str, conn) -> dict:
        """
        Parseia XML de NF-e de compra e:
          1. Insere/atualiza em nfe_entradas
          2. Atualiza estoque virtual em nfe_compras_estoque
        """
        try:
            root = ET.fromstring(xml_nfe)  # noqa: S314  # nosec B314
        except ET.ParseError as exc:
            return {"sucesso": False, "erro": f"XML inválido: {exc}"}

        # Remove namespace para simplificar XPath
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}", 1)[1]

        nfe_node = root.find(".//NFe/infNFe") or root.find(".//infNFe")
        if nfe_node is None:
            return {"sucesso": False, "erro": "infNFe não encontrado no XML"}

        def _t(path: str, default: str = "") -> str:
            node = nfe_node.find(path)
            return (node.text or default) if node is not None else default

        chave_acesso = nfe_node.get("Id", "").replace("NFe", "")
        destinatario_cnpj = _t("dest/CNPJ") or _t("dest/CPF")

        # Só processa se destinatário é nossa empresa
        if destinatario_cnpj and destinatario_cnpj != CNPJ_EMPRESA:
            return {
                "sucesso": False,
                "erro": f"Destinatário {destinatario_cnpj} não é o CNPJ da empresa",
            }

        emitente_cnpj = _t("emit/CNPJ")
        emitente_nome = _t("emit/xNome")
        numero = _t("ide/nNF")
        serie = _t("ide/serie")
        data_emissao_str = _t("ide/dhEmi") or _t("ide/dEmi")
        data_emissao = None
        if data_emissao_str:
            try:
                data_emissao = datetime.fromisoformat(data_emissao_str[:10]).date()
            except ValueError:
                pass
        valor_total = Decimal(_t("total/ICMSTot/vNF", "0") or "0")

        self._ensure_tables(conn)

        with conn.cursor() as cur:
            # Upsert em nfe_entradas
            cur.execute(
                """
                INSERT INTO nfe_entradas
                    (chave_acesso, numero, serie, emitente_cnpj, emitente_nome,
                     destinatario_cnpj, data_emissao, valor_total, xml_raw)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (chave_acesso) DO UPDATE
                    SET processada = FALSE
                RETURNING id
                """,
                (
                    chave_acesso or "SEM_CHAVE",
                    numero,
                    serie,
                    emitente_cnpj,
                    emitente_nome,
                    destinatario_cnpj,
                    data_emissao,
                    float(valor_total),
                    xml_nfe,
                ),
            )
            nfe_entrada_id = cur.fetchone()[0]

            # Processa itens e atualiza estoque
            itens_processados = 0
            for det in nfe_node.findall("det"):
                prod = det.find("prod")
                if prod is None:
                    continue

                item_code = (prod.findtext("cProd") or "").strip()
                descricao = (prod.findtext("xProd") or "").strip()
                ncm = (prod.findtext("NCM") or "").strip()
                unidade = (prod.findtext("uCom") or prod.findtext("uTrib") or "UN").strip()
                try:
                    qtd = Decimal(prod.findtext("qCom") or prod.findtext("qTrib") or "0")
                    vl_unit = Decimal(prod.findtext("vUnCom") or prod.findtext("vUnTrib") or "0")
                except Exception as exc:  # noqa: S112
                    logger.debug("Item com valor inválido ignorado: %s", exc)
                    continue

                if not item_code or qtd <= 0:
                    continue

                # Custo médio ponderado
                cur.execute(
                    "SELECT qty_on_hand, avg_cost FROM nfe_compras_estoque WHERE item_code = %s",
                    (item_code,),
                )
                row = cur.fetchone()
                if row:
                    old_qty = Decimal(str(row[0]))
                    old_avg = Decimal(str(row[1]))
                    new_avg = (old_avg * old_qty + vl_unit * qtd) / (old_qty + qtd) if (old_qty + qtd) > 0 else vl_unit
                    cur.execute(
                        """
                        UPDATE nfe_compras_estoque SET
                            descricao = %s, ncm = %s, unidade = %s,
                            qty_on_hand = qty_on_hand + %s,
                            unit_cost = %s, avg_cost = %s,
                            last_purchase_date = %s, last_nfe_key = %s,
                            updated_at = NOW()
                        WHERE item_code = %s
                        """,
                        (
                            descricao,
                            ncm,
                            unidade,
                            float(qtd),
                            float(vl_unit),
                            float(new_avg),
                            data_emissao,
                            chave_acesso,
                            item_code,
                        ),
                    )
                else:
                    cur.execute(
                        """
                        INSERT INTO nfe_compras_estoque
                            (item_code, descricao, ncm, unidade, qty_on_hand,
                             unit_cost, avg_cost, last_purchase_date, last_nfe_key)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            item_code,
                            descricao,
                            ncm,
                            unidade,
                            float(qtd),
                            float(vl_unit),
                            float(vl_unit),
                            data_emissao,
                            chave_acesso,
                        ),
                    )
                itens_processados += 1

            # Marca como processada
            cur.execute(
                "UPDATE nfe_entradas SET processada = TRUE WHERE id = %s",
                (nfe_entrada_id,),
            )

        conn.commit()
        return {
            "sucesso": True,
            "chave_acesso": chave_acesso,
            "emitente": emitente_nome,
            "valor_total": float(valor_total),
            "itens_processados": itens_processados,
        }
