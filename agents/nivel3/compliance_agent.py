"""
ComplianceAgent — Monitora obrigações fiscais, certidões
e documentos com vencimento próximo.
"""

import json
import re
import subprocess
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path


BASE_URL = "http://127.0.0.1:8080"
CERT_PATH = Path("/opt/conecta-pro/credentials/")

OBRIGACOES = [
    {
        "nome": "CRF FGTS",
        "endpoint": "/api/v1/government/fgts/status",
        "alerta_dias": 15,
        "tipo": "certidao",
    },
    {
        "nome": "CND Federal",
        "endpoint": "/api/v1/government/certidoes",
        "alerta_dias": 30,
        "tipo": "certidao",
    },
    {
        "nome": "eSocial pendentes",
        "endpoint": "/api/v1/government/esocial/eventos",
        "alerta_dias": 0,
        "tipo": "esocial",
    },
    {
        "nome": "DCTFWeb",
        "endpoint": "/api/v1/government/dctfweb/status",
        "alerta_dias": 5,
        "tipo": "fiscal",
    },
]


class ComplianceAgent:
    """Monitora obrigações fiscais e certidões."""

    def __init__(self, token: str):
        self.token = token
        self.nome = "compliance"

    def _get(self, path: str) -> dict:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            return {"error": e.code}
        except Exception as e:
            return {"error": str(e)}

    def verificar_certificado_a1(self) -> list:
        alertas = []
        if not CERT_PATH.exists():
            return alertas
        for cert in CERT_PATH.glob("*.p12"):
            try:
                result = subprocess.run(
                    [
                        "openssl",
                        "pkcs12",
                        "-in",
                        str(cert),
                        "-nokeys",
                        "-passin",
                        "pass:",
                        "-legacy",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                date_match = re.search(r"notAfter=(.+)", result.stdout + result.stderr)
                if date_match:
                    expiry = datetime.strptime(
                        date_match.group(1).strip(), "%b %d %H:%M:%S %Y %Z"
                    ).date()
                    days_left = (expiry - date.today()).days
                    alertas.append(
                        {
                            "certificado": cert.name,
                            "vence_em": str(expiry),
                            "dias_restantes": days_left,
                            "status": (
                                "VENCIDO"
                                if days_left < 0
                                else "CRITICO"
                                if days_left < 7
                                else "ALERTA"
                                if days_left < 30
                                else "OK"
                            ),
                        }
                    )
            except Exception as e:
                alertas.append(
                    {"certificado": cert.name, "erro": str(e), "status": "ERRO"}
                )
        return alertas

    def auditar(self) -> dict:
        print("🔍 ComplianceAgent: verificando obrigações...")
        alertas = []
        ok = 0

        for cert in self.verificar_certificado_a1():
            if cert.get("status") in ["VENCIDO", "CRITICO", "ALERTA"]:
                alertas.append(
                    {
                        "tipo": "certificado_vencendo",
                        "nome": cert["certificado"],
                        "descricao": f"Certificado A1 {cert['certificado']}: {cert.get('dias_restantes', 0)} dias",
                        "acao_jordan": True,
                    }
                )
            else:
                ok += 1

        for obr in OBRIGACOES:
            data = self._get(obr["endpoint"])
            if "error" in data:
                continue
            if obr["tipo"] == "esocial":
                pendentes = [
                    e
                    for e in data.get("items", [])
                    if e.get("status") in ["pendente", "erro"]
                ]
                if pendentes:
                    alertas.append(
                        {
                            "tipo": "esocial_pendente",
                            "nome": obr["nome"],
                            "descricao": f"{len(pendentes)} eventos eSocial pendentes",
                            "acao_jordan": True,
                        }
                    )
                else:
                    ok += 1
            elif obr["tipo"] == "certidao":
                vencimento = (
                    data.get("vencimento") or data.get("validade") or data.get("expiry")
                )
                if vencimento:
                    try:
                        exp = datetime.fromisoformat(vencimento[:10]).date()
                        days = (exp - date.today()).days
                        if days < obr["alerta_dias"]:
                            alertas.append(
                                {
                                    "tipo": "certidao_vencendo",
                                    "nome": obr["nome"],
                                    "descricao": f"{obr['nome']}: vence em {days} dias",
                                    "acao_jordan": True,
                                }
                            )
                        else:
                            ok += 1
                    except Exception:
                        ok += 1
                else:
                    ok += 1
            else:
                ok += 1

        total = ok + len(alertas)
        score = (ok / total * 10) if total else 10.0
        resultado = {
            "agente": "compliance",
            "score": round(score, 1),
            "obrigacoes_ok": ok,
            "alertas": alertas,
            "bugs": [
                {
                    "tipo": a["tipo"],
                    "descricao": a["descricao"],
                    "acao_jordan": a.get("acao_jordan", False),
                    "autocorrigivel": False,
                }
                for a in alertas
            ],
        }
        print(
            f"  OK: {ok}/{total}, Alertas: {len(alertas)}, Score: {resultado['score']}/10"
        )
        return resultado
