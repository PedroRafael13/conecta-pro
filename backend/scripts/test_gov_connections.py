#!/usr/bin/env python3
"""
Script de Teste de Conexão Real com Serviços Governamentais.

Testa conectividade com:
- Receita Federal / e-CAC
- eSocial
- SEFAZ (NF-e, CT-e, MDF-e)
- FGTS Digital
- DCTFWeb
- EFD-Reinf
- NFS-e Manaus
- SPED
"""

import asyncio
import logging
import os
import ssl
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any

import defusedxml.ElementTree as ET  # noqa: N817
import httpx

# Adicionar path do projeto
sys.path.insert(0, "/opt/conecta-pro/backend")

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)8s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================


@dataclass
class CredenciaisGov:
    """Credenciais para serviços governamentais."""

    cnpj: str = "35710481000103"
    cert_path: str = "/opt/conecta-pro/credentials/certificates/certificado.pfx"
    cert_password: str = "Conecta123"  # noqa: S105
    cert_pem: str = "/opt/conecta-pro/credentials/certificates/a1_cert.pem"
    key_pem: str = "/opt/conecta-pro/credentials/certificates/a1_key.pem"
    nfse_usuario: str = "35710481000103"
    nfse_senha: str = "jordan0612"
    uf: str = "AM"
    ambiente: str = "producao"  # producao ou homologacao


class StatusConexao(StrEnum):
    OK = "✅ OK"
    ERRO = "❌ ERRO"
    TIMEOUT = "⏱️ TIMEOUT"
    NAO_CONFIGURADO = "⚙️ NÃO CONFIGURADO"
    PARCIAL = "⚠️ PARCIAL"


@dataclass
class ResultadoTeste:
    """Resultado de um teste de conexão."""

    servico: str
    status: StatusConexao
    tempo_ms: float = 0
    mensagem: str = ""
    detalhes: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# URLS DOS SERVIÇOS GOVERNAMENTAIS
# =============================================================================

URLS_GOV = {
    # Receita Federal
    "receita_cnpj": "https://www.receitaws.com.br/v1/cnpj/{cnpj}",
    "receita_consulta": "https://servicos.receita.fazenda.gov.br/servicos/ConsultaCnpj/consulta.asp",
    # eSocial
    "esocial_producao": "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc",
    "esocial_homologacao": "https://webservices.producaorestrita.esocial.gov.br/servicos/empregador/enviarloteeventos/WsEnviarLoteEventos.svc",
    # SEFAZ - NF-e (AM - Amazonas)
    "nfe_autorizacao_am_prod": "https://nfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
    "nfe_autorizacao_am_hom": "https://homnfe.sefaz.am.gov.br/services2/services/NfeAutorizacao4",
    "nfe_consulta_am_prod": "https://nfe.sefaz.am.gov.br/services2/services/NfeConsultaProtocolo4",
    "nfe_consulta_am_hom": "https://homnfe.sefaz.am.gov.br/services2/services/NfeConsultaProtocolo4",
    "nfe_status_am_prod": "https://nfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
    "nfe_status_am_hom": "https://homnfe.sefaz.am.gov.br/services2/services/NfeStatusServico4",
    # SEFAZ - SVRS (Sefaz Virtual Rio Grande do Sul - backup)
    "nfe_status_svrs_prod": "https://nfe.svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx",
    "nfe_status_svrs_hom": "https://nfe-homologacao.svrs.rs.gov.br/ws/NfeStatusServico/NfeStatusServico4.asmx",
    # CT-e
    "cte_status_svrs_prod": "https://cte.svrs.rs.gov.br/ws/ctestatus/CteStatusServico.asmx",
    "cte_status_svrs_hom": "https://cte-homologacao.svrs.rs.gov.br/ws/ctestatus/CteStatusServico.asmx",
    # MDF-e
    "mdfe_status_prod": "https://mdfe.svrs.rs.gov.br/ws/MDFeStatusServico/MDFeStatusServico.asmx",
    "mdfe_status_hom": "https://mdfe-homologacao.svrs.rs.gov.br/ws/MDFeStatusServico/MDFeStatusServico.asmx",
    # FGTS Digital (Portal oficial)
    "fgts_digital": "https://www.fgts.gov.br/",
    "conectividade_social": "https://conectividadesocial.caixa.gov.br/",
    # DCTFWeb / e-CAC
    "dctfweb": "https://www.gov.br/receitafederal/pt-br",
    "ecac": "https://cav.receita.fazenda.gov.br/autenticacao/login",
    # EFD-Reinf
    "reinf_producao": "https://www.gov.br/esocial/pt-br",
    "reinf_consulta": "https://consulta-reinf.rfb.gov.br/",
    # NFS-e Manaus
    "nfse_manaus_portal": "https://nfse.manaus.am.gov.br/",
    "nfse_manaus_prod": "https://nfse-prd.manaus.am.gov.br/nfse/servlet",
    "nfse_manaus_hom": "https://nfse-hml.manaus.am.gov.br/nfse/servlet",
    # NFS-e Nacional
    "nfse_nacional": "https://www.gov.br/nfse/",
    # SPED
    "sped_consulta": "https://sped.rfb.gov.br/",
}


# =============================================================================
# FUNÇÕES DE TESTE
# =============================================================================


async def verificar_certificado(creds: CredenciaisGov) -> ResultadoTeste:
    """Verifica se o certificado digital está válido."""
    inicio = datetime.now()

    try:
        from cryptography import x509
        from cryptography.hazmat.backends import default_backend

        # Tentar ler o certificado PEM
        if os.path.exists(creds.cert_pem):
            with open(creds.cert_pem, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

            # Verificar validade
            now = datetime.utcnow()
            not_before = cert.not_valid_before_utc.replace(tzinfo=None)
            not_after = cert.not_valid_after_utc.replace(tzinfo=None)

            if now < not_before:
                return ResultadoTeste(
                    servico="Certificado Digital A1",
                    status=StatusConexao.ERRO,
                    tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
                    mensagem="Certificado ainda não é válido",
                    detalhes={
                        "valido_a_partir": str(not_before),
                        "subject": str(cert.subject),
                    },
                )

            if now > not_after:
                return ResultadoTeste(
                    servico="Certificado Digital A1",
                    status=StatusConexao.ERRO,
                    tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
                    mensagem="Certificado expirado!",
                    detalhes={
                        "expirou_em": str(not_after),
                        "subject": str(cert.subject),
                    },
                )

            dias_restantes = (not_after - now).days

            return ResultadoTeste(
                servico="Certificado Digital A1",
                status=StatusConexao.OK,
                tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
                mensagem=f"Válido por mais {dias_restantes} dias",
                detalhes={
                    "subject": str(cert.subject),
                    "issuer": str(cert.issuer),
                    "valido_ate": str(not_after),
                    "dias_restantes": dias_restantes,
                    "serial": str(cert.serial_number),
                },
            )
        else:
            return ResultadoTeste(
                servico="Certificado Digital A1",
                status=StatusConexao.NAO_CONFIGURADO,
                tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
                mensagem=f"Arquivo não encontrado: {creds.cert_pem}",
            )

    except Exception as e:
        return ResultadoTeste(
            servico="Certificado Digital A1",
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=str(e),
        )


async def testar_url_simples(
    nome: str,
    url: str,
    timeout: float = 10.0,
    verificar_ssl: bool = True,
) -> ResultadoTeste:
    """Testa conectividade com uma URL."""
    inicio = datetime.now()

    try:
        async with httpx.AsyncClient(
            verify=verificar_ssl,
            timeout=timeout,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)

            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            if response.status_code in [200, 301, 302, 401, 403, 405]:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.OK,
                    tempo_ms=tempo_ms,
                    mensagem=f"HTTP {response.status_code}",
                    detalhes={
                        "status_code": response.status_code,
                        "url_final": str(response.url),
                        "content_type": response.headers.get("content-type", "N/A"),
                    },
                )
            else:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.PARCIAL,
                    tempo_ms=tempo_ms,
                    mensagem=f"HTTP {response.status_code}",
                    detalhes={"status_code": response.status_code},
                )

    except httpx.TimeoutException:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.TIMEOUT,
            tempo_ms=timeout * 1000,
            mensagem=f"Timeout após {timeout}s",
        )
    except httpx.ConnectError as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=f"Erro de conexão: {str(e)[:100]}",
        )
    except Exception as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=str(e)[:100],
        )


async def testar_webservice_soap(
    nome: str,
    url: str,
    creds: CredenciaisGov,
    soap_action: str = "",
    timeout: float = 15.0,
) -> ResultadoTeste:
    """Testa conectividade com WebService SOAP usando certificado."""
    inicio = datetime.now()

    try:
        # Criar contexto SSL com certificado
        ssl_context = ssl.create_default_context()

        if os.path.exists(creds.cert_pem) and os.path.exists(creds.key_pem):
            ssl_context.load_cert_chain(
                certfile=creds.cert_pem,
                keyfile=creds.key_pem,
            )

        # Envelope SOAP mínimo para teste
        envelope = """<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
    <soap:Header/>
    <soap:Body>
        <nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeStatusServico4">
            <consStatServ versao="4.00" xmlns="http://www.portalfiscal.inf.br/nfe">
                <tpAmb>2</tpAmb>
                <cUF>13</cUF>
                <xServ>STATUS</xServ>
            </consStatServ>
        </nfeDadosMsg>
    </soap:Body>
</soap:Envelope>"""

        headers = {
            "Content-Type": "application/soap+xml; charset=utf-8",
            "SOAPAction": soap_action,
        }

        async with httpx.AsyncClient(
            verify=ssl_context,
            timeout=timeout,
        ) as client:
            response = await client.post(
                url,
                content=envelope,
                headers=headers,
            )

            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            # Verificar resposta
            if response.status_code == 200:
                # Tentar parsear XML de resposta
                try:
                    root = ET.fromstring(response.content)
                    # Procurar status na resposta
                    status_elem = root.find(".//{http://www.portalfiscal.inf.br/nfe}cStat")
                    if status_elem is not None:
                        return ResultadoTeste(
                            servico=nome,
                            status=StatusConexao.OK,
                            tempo_ms=tempo_ms,
                            mensagem=f"WebService respondendo (cStat: {status_elem.text})",
                            detalhes={
                                "cStat": status_elem.text,
                                "response_size": len(response.content),
                            },
                        )
                except Exception as e:
                    logger.debug(f"Erro ao extrair status: {e}")

                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.OK,
                    tempo_ms=tempo_ms,
                    mensagem="WebService respondendo",
                    detalhes={"response_size": len(response.content)},
                )
            else:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.PARCIAL,
                    tempo_ms=tempo_ms,
                    mensagem=f"HTTP {response.status_code}",
                    detalhes={"status_code": response.status_code},
                )

    except ssl.SSLError as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=f"Erro SSL: {str(e)[:80]}",
        )
    except httpx.TimeoutException:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.TIMEOUT,
            tempo_ms=timeout * 1000,
            mensagem=f"Timeout após {timeout}s",
        )
    except Exception as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=str(e)[:100],
        )


async def testar_nfse_manaus(creds: CredenciaisGov) -> ResultadoTeste:
    """Testa conexão com WebService NFS-e de Manaus."""
    inicio = datetime.now()
    nome = "NFS-e Manaus"

    # Testar portal principal primeiro
    url_portal = URLS_GOV["nfse_manaus_portal"]
    url_ws = URLS_GOV["nfse_manaus_prod"]

    try:
        async with httpx.AsyncClient(timeout=15.0, verify=False) as client:  # noqa: S501  # nosec B501
            # Testar portal
            response_portal = await client.get(url_portal, follow_redirects=True)
            portal_ok = response_portal.status_code in [200, 302]

            # Testar webservice
            response_ws = await client.get(url_ws)
            ws_responde = response_ws.status_code in [200, 404, 405, 500]  # 404/405 = endpoint existe mas precisa POST

            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            if portal_ok and ws_responde:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.OK,
                    tempo_ms=tempo_ms,
                    mensagem="Portal OK, WebService respondendo",
                    detalhes={
                        "url_portal": url_portal,
                        "url_webservice": url_ws,
                        "portal_status": response_portal.status_code,
                        "ws_status": response_ws.status_code,
                    },
                )
            elif portal_ok:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.PARCIAL,
                    tempo_ms=tempo_ms,
                    mensagem=f"Portal OK, WebService HTTP {response_ws.status_code}",
                    detalhes={"portal_status": response_portal.status_code, "ws_status": response_ws.status_code},
                )
            else:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.ERRO,
                    tempo_ms=tempo_ms,
                    mensagem=f"Portal HTTP {response_portal.status_code}",
                    detalhes={"portal_status": response_portal.status_code},
                )

    except Exception as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=str(e)[:100],
        )


async def testar_receita_federal(creds: CredenciaisGov) -> ResultadoTeste:
    """Testa consulta de CNPJ na Receita Federal."""
    inicio = datetime.now()
    nome = "Receita Federal (CNPJ)"

    try:
        # Usar API pública de consulta CNPJ
        url = f"https://www.receitaws.com.br/v1/cnpj/{creds.cnpj}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)

            tempo_ms = (datetime.now() - inicio).total_seconds() * 1000

            if response.status_code == 200:
                dados = response.json()
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.OK,
                    tempo_ms=tempo_ms,
                    mensagem=f"CNPJ: {dados.get('nome', 'N/A')[:50]}",
                    detalhes={
                        "razao_social": dados.get("nome"),
                        "situacao": dados.get("situacao"),
                        "uf": dados.get("uf"),
                        "municipio": dados.get("municipio"),
                        "cnae_principal": dados.get("atividade_principal", [{}])[0].get("text", "N/A")[:50],
                    },
                )
            elif response.status_code == 429:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.PARCIAL,
                    tempo_ms=tempo_ms,
                    mensagem="Rate limit (muitas consultas)",
                )
            else:
                return ResultadoTeste(
                    servico=nome,
                    status=StatusConexao.ERRO,
                    tempo_ms=tempo_ms,
                    mensagem=f"HTTP {response.status_code}",
                )

    except Exception as e:
        return ResultadoTeste(
            servico=nome,
            status=StatusConexao.ERRO,
            tempo_ms=(datetime.now() - inicio).total_seconds() * 1000,
            mensagem=str(e)[:100],
        )


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================


async def executar_todos_testes():
    """Executa todos os testes de conexão."""

    print("\n" + "=" * 70)
    print("  TESTE DE CONEXÃO - SERVIÇOS GOVERNAMENTAIS")
    print("  Conecta PRO - " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    print("=" * 70 + "\n")

    creds = CredenciaisGov()
    resultados = []

    # 1. Verificar certificado
    print("📜 Verificando Certificado Digital...")
    resultado = await verificar_certificado(creds)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem}")
    if resultado.detalhes:
        for k, v in resultado.detalhes.items():
            print(f"      • {k}: {v}")
    print()

    # 2. Receita Federal
    print("🏛️  Testando Receita Federal...")
    resultado = await testar_receita_federal(creds)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    if resultado.detalhes and resultado.status == StatusConexao.OK:
        print(f"      • Razão Social: {resultado.detalhes.get('razao_social', 'N/A')}")
        print(f"      • Situação: {resultado.detalhes.get('situacao', 'N/A')}")
    print()

    # 3. e-CAC
    print("🔐 Testando e-CAC...")
    resultado = await testar_url_simples("e-CAC", URLS_GOV["ecac"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 4. eSocial
    print("👥 Testando eSocial...")
    resultado = await testar_url_simples("eSocial", "https://www.gov.br/esocial/pt-br")
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 5. SEFAZ NF-e (Amazonas) - usar verify=False para certificados ICP-Brasil
    print("📄 Testando SEFAZ NF-e (AM)...")
    # Produção
    resultado = await testar_url_simples(
        "SEFAZ NF-e AM (Produção)", URLS_GOV["nfe_status_am_prod"], verificar_ssl=False
    )
    resultados.append(resultado)
    print(f"   Produção: {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    # Homologação
    resultado_hom = await testar_url_simples(
        "SEFAZ NF-e AM (Homologação)", URLS_GOV["nfe_status_am_hom"], verificar_ssl=False
    )
    resultados.append(resultado_hom)
    print(f"   Homologação: {resultado_hom.status.value} - {resultado_hom.mensagem} ({resultado_hom.tempo_ms:.0f}ms)")
    print()

    # 6. SEFAZ Virtual (SVRS - backup nacional)
    print("📄 Testando SEFAZ Virtual RS (SVRS)...")
    resultado = await testar_url_simples("SVRS NF-e (Produção)", URLS_GOV["nfe_status_svrs_prod"], verificar_ssl=False)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 7. CT-e
    print("🚚 Testando CT-e...")
    resultado = await testar_url_simples("CT-e SVRS (Produção)", URLS_GOV["cte_status_svrs_prod"], verificar_ssl=False)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 8. MDF-e
    print("📋 Testando MDF-e...")
    resultado = await testar_url_simples("MDF-e (Produção)", URLS_GOV["mdfe_status_prod"], verificar_ssl=False)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 9. FGTS Digital
    print("💰 Testando FGTS Digital...")
    resultado = await testar_url_simples("FGTS Digital", URLS_GOV["fgts_digital"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 10. Conectividade Social
    print("🔗 Testando Conectividade Social (CAIXA)...")
    resultado = await testar_url_simples("Conectividade Social", URLS_GOV["conectividade_social"], timeout=15.0)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 11. Portal Receita Federal (DCTFWeb)
    print("📊 Testando Portal Receita Federal...")
    resultado = await testar_url_simples("Portal Receita Federal", URLS_GOV["dctfweb"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 12. Portal eSocial/EFD-Reinf
    print("📑 Testando Portal eSocial (EFD-Reinf)...")
    resultado = await testar_url_simples("Portal eSocial", URLS_GOV["reinf_producao"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 13. NFS-e Nacional
    print("🏛️  Testando NFS-e Nacional...")
    resultado = await testar_url_simples("NFS-e Nacional", URLS_GOV["nfse_nacional"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 13. NFS-e Manaus
    print("🏢 Testando NFS-e Manaus...")
    resultado = await testar_nfse_manaus(creds)
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # 14. SPED
    print("📚 Testando Portal SPED...")
    resultado = await testar_url_simples("Portal SPED", URLS_GOV["sped_consulta"])
    resultados.append(resultado)
    print(f"   {resultado.status.value} - {resultado.mensagem} ({resultado.tempo_ms:.0f}ms)")
    print()

    # ==========================================================================
    # RESUMO
    # ==========================================================================

    print("\n" + "=" * 70)
    print("  RESUMO DOS TESTES")
    print("=" * 70 + "\n")

    ok_count = sum(1 for r in resultados if r.status == StatusConexao.OK)
    erro_count = sum(1 for r in resultados if r.status == StatusConexao.ERRO)
    timeout_count = sum(1 for r in resultados if r.status == StatusConexao.TIMEOUT)
    parcial_count = sum(1 for r in resultados if r.status == StatusConexao.PARCIAL)
    nao_config_count = sum(1 for r in resultados if r.status == StatusConexao.NAO_CONFIGURADO)

    total = len(resultados)

    print(f"  ✅ OK:              {ok_count:2d}/{total}")
    print(f"  ⚠️  Parcial:         {parcial_count:2d}/{total}")
    print(f"  ❌ Erro:            {erro_count:2d}/{total}")
    print(f"  ⏱️  Timeout:         {timeout_count:2d}/{total}")
    print(f"  ⚙️  Não configurado: {nao_config_count:2d}/{total}")
    print()

    # Taxa de sucesso
    taxa_sucesso = ((ok_count + parcial_count) / total) * 100 if total > 0 else 0
    print(f"  Taxa de sucesso: {taxa_sucesso:.1f}%")
    print()

    # Listar erros
    erros = [r for r in resultados if r.status in [StatusConexao.ERRO, StatusConexao.TIMEOUT]]
    if erros:
        print("  ⚠️  Serviços com problemas:")
        for r in erros:
            print(f"     • {r.servico}: {r.mensagem}")
        print()

    print("=" * 70)
    print()

    return resultados


if __name__ == "__main__":
    asyncio.run(executar_todos_testes())
