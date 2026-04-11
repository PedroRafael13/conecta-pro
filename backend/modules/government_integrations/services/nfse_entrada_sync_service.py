"""
NFS-e Entrada Sync Service
Busca automaticamente NFS-e emitidas CONTRA o CNPJ da empresa
no Portal Nacional e SEMEF Manaus
"""

import logging
import os
import tempfile
from datetime import datetime, timedelta

import requests
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat, pkcs12

logger = logging.getLogger(__name__)

CNPJ = os.getenv("NFSE_MANAUS_CNPJ", "35710481000103")
CERT_PATH = os.getenv("CERTIFICATE_PATH", "/app/credentials/certificates/certificado.pfx")
CERT_PASS = os.getenv("CERTIFICATE_PASSWORD", "Conecta123")
PORTAL_URL = "https://sefin.nfse.gov.br/sefinnacional"


class NFSeEntradaSyncService:
    """Sincroniza NFS-e recebidas (tomador = nosso CNPJ)"""

    def _get_mtls_certs(self):
        """Exporta certificado A1 para PEM temporário"""
        with open(CERT_PATH, "rb") as f:
            pfx_data = f.read()
        pfx_pass = CERT_PASS.encode() if CERT_PASS else b""
        priv_key, cert, _ = pkcs12.load_key_and_certificates(pfx_data, pfx_pass)
        tmp_cert = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="wb")  # noqa: SIM115
        tmp_key = tempfile.NamedTemporaryFile(delete=False, suffix=".pem", mode="wb")  # noqa: SIM115
        tmp_cert.write(cert.public_bytes(Encoding.PEM))
        tmp_key.write(priv_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        tmp_cert.close()
        tmp_key.close()
        return tmp_cert.name, tmp_key.name

    def buscar_nfse_recebidas(self, data_inicio: str | None = None, data_fim: str | None = None) -> dict:
        """
        Busca NFS-e onde nosso CNPJ é o tomador (recebidas).
        Portal Nacional — DPS/NFS-e padrão nacional v1.6+.
        data_inicio/fim: formato YYYY-MM-DD
        """
        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not data_fim:
            data_fim = datetime.now().strftime("%Y-%m-%d")

        tmp_cert, tmp_key = None, None
        try:
            tmp_cert, tmp_key = self._get_mtls_certs()
            cert_arg = (tmp_cert, tmp_key) if tmp_cert else None
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            # Portal Nacional API v1.6 — POST /nfse/consulta-tomador
            # Spec: https://www.gov.br/nfse/pt-br/biblioteca/documentacao-tecnica
            payload = {
                "cpfCnpjTomador": CNPJ,
                "dataInicial": data_inicio,
                "dataFinal": data_fim,
            }
            url_post = f"{PORTAL_URL}/nfse/consulta-tomador"
            resp = requests.post(
                url_post,
                json=payload,
                cert=cert_arg,
                timeout=30,
                headers=headers,
            )
            if resp.status_code != 405:
                return {
                    "status_http": resp.status_code,
                    "data_inicio": data_inicio,
                    "data_fim": data_fim,
                    "response": resp.json() if resp.ok else resp.text,
                    "portal": "nacional",
                    "metodo": "POST /nfse/consulta-tomador",
                }

            # Fallback: GET com cpfCnpjTomador (padrão correto do Portal Nacional)
            url_get = f"{PORTAL_URL}/nfse"
            params = {
                "cpfCnpjTomador": CNPJ,
                "dataInicial": data_inicio,
                "dataFinal": data_fim,
            }
            resp = requests.get(
                url_get,
                params=params,
                cert=cert_arg,
                timeout=30,
                headers={"Accept": "application/json"},
            )
            return {
                "status_http": resp.status_code,
                "data_inicio": data_inicio,
                "data_fim": data_fim,
                "response": resp.json() if resp.ok else resp.text,
                "portal": "nacional",
                "metodo": "GET /nfse?cpfCnpjTomador=",
                "cert_subject": "JORDAN SANTOS DE JESUS LTDA:35710481000103",
                "cert_valido_ate": "2027-01-13",
            }
        except Exception as e:
            logger.error("Erro sync NFS-e entrada: %s", e)
            return {"erro": str(e), "portal": "nacional"}
        finally:
            import os as _os

            for f in [tmp_cert, tmp_key]:
                if f:
                    try:
                        _os.unlink(f)
                    except Exception:
                        pass

    def sync_e_salvar(self, db_conn, data_inicio=None, data_fim=None):
        """Busca e salva no banco nfse_entrada"""
        resultado = self.buscar_nfse_recebidas(data_inicio, data_fim)
        if "erro" in resultado:
            return resultado

        notas = resultado.get("response", {})
        if isinstance(notas, list):
            salvos = 0
            for nota in notas:
                try:
                    cur = db_conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO nfse_entrada (
                            chave_acesso, numero_nfse, serie,
                            prestador_cnpj, prestador_nome,
                            valor_servico, valor_iss,
                            data_emissao, competencia,
                            codigo_servico, descricao_servico,
                            status, fonte, created_at, updated_at
                        ) VALUES (
                            %(chave)s, %(numero)s, %(serie)s,
                            %(prest_cnpj)s, %(prest_nome)s,
                            %(valor)s, %(iss)s,
                            %(data_em)s, %(comp)s,
                            %(cod_serv)s, %(desc)s,
                            'recebida', 'portal_nacional',
                            NOW(), NOW()
                        )
                        ON CONFLICT (chave_acesso) DO UPDATE SET
                            status = 'recebida',
                            updated_at = NOW()
                    """,
                        {
                            "chave": nota.get("chaveAcesso", ""),
                            "numero": nota.get("numero", ""),
                            "serie": nota.get("serie", ""),
                            "prest_cnpj": nota.get("prestador", {}).get("cnpj", ""),
                            "prest_nome": nota.get("prestador", {}).get("razaoSocial", ""),
                            "valor": nota.get("valorServico", 0),
                            "iss": nota.get("valorIss", 0),
                            "data_em": nota.get("dataEmissao", datetime.now().date()),
                            "comp": nota.get("competencia", ""),
                            "cod_serv": nota.get("codigoServico", ""),
                            "desc": nota.get("descricaoServico", "")[:500] if nota.get("descricaoServico") else "",
                        },
                    )
                    db_conn.commit()
                    salvos += 1
                except Exception as e:
                    logger.error(f"Erro ao salvar NFS-e entrada: {e}")
                    db_conn.rollback()
            return {"salvos": salvos, "total": len(notas)}
        return {"resultado": notas}
