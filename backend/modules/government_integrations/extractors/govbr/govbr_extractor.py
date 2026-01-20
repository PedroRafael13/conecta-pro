"""
Extrator de dados do Gov.br.

Implementa:
- Autenticação OAuth2 via Gov.br
- Consulta de dados cadastrais
- Integração com serviços federais
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID
import asyncio
import logging
import base64
import hashlib
import secrets

from ..base_extractor import ExtratorBase, DocumentoExtraido, ResultadoExtracao
from ...core.credentials import ProvedorCredenciais, TipoCredencial

logger = logging.getLogger(__name__)


class ExtratorGovBR(ExtratorBase):
    """
    Extrator de dados do Gov.br.

    Utiliza OAuth2 para autenticação e acesso a serviços federais.

    Serviços disponíveis:
    - Dados cadastrais (CPF/CNPJ)
    - Procurações eletrônicas
    - Certificados digitais
    - Integração com sistemas federais
    """

    URLS = {
        "producao": {
            "authorize": "https://sso.acesso.gov.br/authorize",
            "token": "https://sso.acesso.gov.br/token",
            "userinfo": "https://sso.acesso.gov.br/userinfo",
            "services": "https://api.gov.br/",
        },
        "homologacao": {
            "authorize": "https://sso.staging.acesso.gov.br/authorize",
            "token": "https://sso.staging.acesso.gov.br/token",
            "userinfo": "https://sso.staging.acesso.gov.br/userinfo",
            "services": "https://api.staging.gov.br/",
        },
    }

    SCOPES = [
        "openid",
        "email",
        "phone",
        "profile",
        "govbr_empresa",
        "govbr_confiabilidades",
    ]

    @property
    def tipo_servico(self) -> str:
        return "govbr"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.RECEITA_FEDERAL

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        cnpjs: Optional[List[str]] = None,
        ufs: Optional[List[str]] = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Extrai dados do Gov.br.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial
            data_fim: Data final
            cnpjs: CNPJs a consultar
            incremental: Se True, busca apenas novos dados

        Returns:
            ResultadoExtracao com dados extraídos
        """
        resultado = ResultadoExtracao(
            servico=self.tipo_servico,
            inicio=datetime.utcnow(),
        )

        logger.info(f"Iniciando extração Gov.br: {tenant_id}")

        try:
            credencial = await self.credentials.obter_credencial(
                tenant_id, self.tipo_credencial
            )

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo Gov.br para CNPJ: {cnpj}")

                # Dados cadastrais
                doc_cadastro = await self._consultar_dados_cadastrais(tenant_id, cnpj)
                if doc_cadastro:
                    resultado.documentos.append(doc_cadastro)
                    resultado.documentos_processados += 1
                    if not doc_cadastro.erro:
                        resultado.documentos_novos += 1

                # Procurações
                doc_procuracoes = await self._consultar_procuracoes(tenant_id, cnpj)
                if doc_procuracoes:
                    resultado.documentos.append(doc_procuracoes)
                    resultado.documentos_processados += 1

                # Vínculos empresariais
                doc_vinculos = await self._consultar_vinculos(tenant_id, cnpj)
                if doc_vinculos:
                    resultado.documentos.append(doc_vinculos)
                    resultado.documentos_processados += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração Gov.br: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_dados_cadastrais(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> Optional[DocumentoExtraido]:
        """Consulta dados cadastrais no Gov.br."""
        try:
            dados = {
                "cnpj": cnpj,
                "tipo": "dados_cadastrais",

                "empresa": {
                    "razao_social": None,
                    "nome_fantasia": None,
                    "situacao_cadastral": "verificar",
                    "data_situacao": None,
                    "natureza_juridica": None,
                    "porte": None,
                    "capital_social": None,
                },

                "endereco": {
                    "logradouro": None,
                    "numero": None,
                    "complemento": None,
                    "bairro": None,
                    "municipio": None,
                    "uf": None,
                    "cep": None,
                },

                "contato": {
                    "telefone": None,
                    "email": None,
                },

                "atividades": {
                    "principal": None,
                    "secundarias": [],
                },

                "socios": [],

                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"govbr_cadastro_{cnpj}",
                tipo="dados_cadastrais_govbr",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar dados cadastrais Gov.br: {e}")
            return DocumentoExtraido(
                id=f"govbr_cadastro_{cnpj}",
                tipo="dados_cadastrais_govbr",
                dados={"cnpj": cnpj},
                erro=str(e),
            )

    async def _consultar_procuracoes(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> Optional[DocumentoExtraido]:
        """Consulta procurações eletrônicas."""
        try:
            dados = {
                "cnpj": cnpj,
                "tipo": "procuracoes",

                "procuracoes_concedidas": [],
                # Exemplo:
                # {
                #     "procurador": "12345678901",
                #     "nome_procurador": "Nome do Procurador",
                #     "servicos": ["eSocial", "REINF"],
                #     "data_inicio": "2024-01-01",
                #     "data_fim": "2024-12-31",
                #     "situacao": "vigente",
                # }

                "procuracoes_recebidas": [],

                "resumo": {
                    "total_concedidas": 0,
                    "total_recebidas": 0,
                    "vigentes": 0,
                    "expiradas": 0,
                },

                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"govbr_procuracoes_{cnpj}",
                tipo="procuracoes_govbr",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar procurações: {e}")
            return None

    async def _consultar_vinculos(
        self,
        tenant_id: UUID,
        cnpj: str,
    ) -> Optional[DocumentoExtraido]:
        """Consulta vínculos empresariais no Gov.br."""
        try:
            dados = {
                "cnpj": cnpj,
                "tipo": "vinculos_empresariais",

                "vinculos": [],
                # Exemplo:
                # {
                #     "tipo_vinculo": "socio",
                #     "cnpj_empresa": "12345678000190",
                #     "razao_social": "Empresa XYZ Ltda",
                #     "qualificacao": "Sócio-Administrador",
                #     "data_entrada": "2020-01-01",
                #     "participacao": 50.0,
                # }

                "resumo": {
                    "total_vinculos": 0,
                    "como_socio": 0,
                    "como_administrador": 0,
                    "como_representante": 0,
                },

                "consultado_em": datetime.utcnow().isoformat(),
                "status": "consulta_manual_necessaria",
            }

            return DocumentoExtraido(
                id=f"govbr_vinculos_{cnpj}",
                tipo="vinculos_govbr",
                dados=dados,
                processado=True,
            )

        except Exception as e:
            logger.error(f"Erro ao consultar vínculos: {e}")
            return None

    def gerar_url_autorizacao(
        self,
        client_id: str,
        redirect_uri: str,
        state: Optional[str] = None,
        ambiente: str = "producao",
    ) -> Dict[str, str]:
        """
        Gera URL para autenticação OAuth2 no Gov.br.

        Args:
            client_id: ID do cliente OAuth
            redirect_uri: URL de callback
            state: Estado para CSRF protection
            ambiente: producao ou homologacao

        Returns:
            Dicionário com URL e parâmetros
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        # PKCE
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")

        urls = self.URLS[ambiente]

        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        authorize_url = f"{urls['authorize']}?{query_string}"

        return {
            "url": authorize_url,
            "state": state,
            "code_verifier": code_verifier,
        }

    async def trocar_codigo_por_token(
        self,
        client_id: str,
        client_secret: str,
        code: str,
        redirect_uri: str,
        code_verifier: str,
        ambiente: str = "producao",
    ) -> Dict[str, Any]:
        """
        Troca código de autorização por token de acesso.

        Args:
            client_id: ID do cliente OAuth
            client_secret: Secret do cliente
            code: Código de autorização
            redirect_uri: URL de callback
            code_verifier: Verificador PKCE
            ambiente: producao ou homologacao

        Returns:
            Dicionário com tokens
        """
        try:
            import aiohttp

            urls = self.URLS[ambiente]

            data = {
                "grant_type": "authorization_code",
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(urls["token"], data=data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        erro = await response.text()
                        return {"erro": f"Erro {response.status}: {erro}"}

        except Exception as e:
            logger.error(f"Erro ao trocar código por token: {e}")
            return {"erro": str(e)}

    async def obter_informacoes_usuario(
        self,
        access_token: str,
        ambiente: str = "producao",
    ) -> Dict[str, Any]:
        """
        Obtém informações do usuário autenticado.

        Args:
            access_token: Token de acesso OAuth
            ambiente: producao ou homologacao

        Returns:
            Dicionário com informações do usuário
        """
        try:
            import aiohttp

            urls = self.URLS[ambiente]

            headers = {"Authorization": f"Bearer {access_token}"}

            async with aiohttp.ClientSession() as session:
                async with session.get(urls["userinfo"], headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        erro = await response.text()
                        return {"erro": f"Erro {response.status}: {erro}"}

        except Exception as e:
            logger.error(f"Erro ao obter informações do usuário: {e}")
            return {"erro": str(e)}
