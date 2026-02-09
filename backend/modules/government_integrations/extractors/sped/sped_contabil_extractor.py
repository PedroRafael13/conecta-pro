"""
Extrator de SPED Contábil (ECD - Escrituração Contábil Digital).

Implementa:
- Leitura de arquivos SPED Contábil
- Extração de dados de lançamentos contábeis
- Consulta de escriturações transmitidas
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from ...core.credentials import TipoCredencial
from ..base_extractor import DocumentoExtraido, ExtratorBase, ResultadoExtracao

logger = logging.getLogger(__name__)


class ExtratorSPEDContabil(ExtratorBase):
    """
    Extrator de SPED Contábil (ECD).

    A Escrituração Contábil Digital substitui a escrituração em papel
    pelos livros:
    - Diário Geral
    - Diário com Escrituração Resumida
    - Razão Auxiliar
    - Livro de Balancetes Diários e Balanços

    Registros principais:
    - Bloco 0: Abertura e Identificação
    - Bloco I: Lançamentos Contábeis
    - Bloco J: Demonstrações Contábeis
    - Bloco K: Conglomerados Econômicos
    - Bloco 9: Controle e Encerramento
    """

    BLOCOS = {
        "0": "Abertura e Identificação",
        "I": "Lançamentos Contábeis",
        "J": "Demonstrações Contábeis",
        "K": "Conglomerados Econômicos",
        "9": "Encerramento",
    }

    @property
    def tipo_servico(self) -> str:
        return "sped_contabil"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.SPED

    async def extrair(
        self,
        tenant_id: UUID,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
        cnpjs: list[str] | None = None,
        ufs: list[str] | None = None,
        incremental: bool = True,
    ) -> ResultadoExtracao:
        """
        Extrai dados de SPED Contábil.

        Args:
            tenant_id: ID do tenant
            data_inicio: Data inicial (ano-calendário)
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

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = datetime(data_fim.year - 1, 1, 1)

        logger.info(f"Iniciando extração SPED Contábil: {tenant_id} - Período: {data_inicio.year} a {data_fim.year}")

        try:
            credencial = await self.credentials.obter_credencial(tenant_id, self.tipo_credencial)

            if not credencial.valida:
                resultado.status = "falha"
                resultado.erros.append(f"Credencial inválida: {credencial.erro}")
                return resultado

            cnpjs = cnpjs or [credencial.certificado_info.cnpj_cpf]

            for cnpj in cnpjs:
                logger.info(f"Extraindo SPED Contábil para CNPJ: {cnpj}")

                # Consultar escriturações por ano
                docs = await self._consultar_escrituracoes(tenant_id, cnpj, data_inicio, data_fim)

                for doc in docs:
                    resultado.documentos.append(doc)
                    resultado.documentos_processados += 1
                    if not doc.erro:
                        resultado.documentos_novos += 1
                    else:
                        resultado.documentos_erro += 1

                await asyncio.sleep(2)

            resultado.status = "concluida" if not resultado.erros else "concluida_parcial"

        except Exception as e:
            logger.error(f"Erro na extração SPED Contábil: {e}")
            resultado.status = "falha"
            resultado.erros.append(str(e))

        finally:
            resultado.fim = datetime.utcnow()
            await self.close()

        return resultado

    async def _consultar_escrituracoes(
        self,
        tenant_id: UUID,
        cnpj: str,
        data_inicio: datetime,
        data_fim: datetime,
    ) -> list[DocumentoExtraido]:
        """Consulta escriturações SPED Contábil transmitidas."""
        documentos = []

        try:
            await self._get_session(tenant_id, with_cert=True)

            # ECD é anual
            ano_inicio = data_inicio.year
            ano_fim = data_fim.year

            for ano in range(ano_inicio, ano_fim + 1):
                doc = await self._criar_documento_escrituracao(cnpj, ano)
                if doc:
                    documentos.append(doc)

        except Exception as e:
            logger.error(f"Erro ao consultar escriturações SPED Contábil: {e}")
            documentos.append(
                DocumentoExtraido(
                    id=f"sped_contabil_{cnpj}_erro",
                    tipo="sped_contabil",
                    dados={"cnpj": cnpj},
                    erro=str(e),
                )
            )

        return documentos

    async def _criar_documento_escrituracao(
        self,
        cnpj: str,
        ano: int,
    ) -> DocumentoExtraido:
        """Cria documento de escrituração SPED Contábil."""
        dados = {
            "cnpj": cnpj,
            "ano_calendario": ano,
            "tipo": "sped_contabil",
            "escrituracao": {
                "transmitida": None,
                "data_transmissao": None,
                "numero_recibo": None,
                "hash_arquivo": None,
                "versao_layout": "10.0",
                "tipo_ecd": "G",  # G=Livro Diário Geral
            },
            # Informações do contribuinte (Bloco 0)
            "contribuinte": {
                "razao_social": None,
                "natureza_juridica": None,
                "forma_tributacao": None,  # Lucro Real/Presumido
                "contador": {
                    "nome": None,
                    "cpf": None,
                    "crc": None,
                },
            },
            # Resumo do Bloco I (Lançamentos)
            "lancamentos": {
                "quantidade_lancamentos": 0,
                "valor_total_debitos": 0.0,
                "valor_total_creditos": 0.0,
                "periodo_inicio": f"{ano}-01-01",
                "periodo_fim": f"{ano}-12-31",
            },
            # Resumo do Bloco J (Demonstrações)
            "demonstracoes": {
                "balanco_patrimonial": {
                    "ativo_total": 0.0,
                    "passivo_total": 0.0,
                    "patrimonio_liquido": 0.0,
                },
                "dre": {
                    "receita_liquida": 0.0,
                    "lucro_bruto": 0.0,
                    "lucro_operacional": 0.0,
                    "lucro_liquido": 0.0,
                },
                "dlpa": {
                    "saldo_inicial": 0.0,
                    "lucro_periodo": 0.0,
                    "dividendos": 0.0,
                    "saldo_final": 0.0,
                },
            },
            # Plano de contas
            "plano_contas": {
                "quantidade_contas": 0,
                "conta_maior_movimento": None,
            },
            "consultado_em": datetime.utcnow().isoformat(),
            "status": "consulta_manual_necessaria",
        }

        return DocumentoExtraido(
            id=f"sped_contabil_{cnpj}_{ano}",
            tipo="sped_contabil",
            dados=dados,
            data_documento=datetime(ano, 12, 31),
            processado=True,
        )

    def parsear_arquivo_sped(
        self,
        conteudo: str,
    ) -> dict[str, Any]:
        """
        Parseia um arquivo SPED Contábil.

        Args:
            conteudo: Conteúdo do arquivo SPED

        Returns:
            Dicionário com dados extraídos
        """
        resultado = {
            "registros": {},
            "totais": {
                "linhas": 0,
                "por_bloco": {},
            },
            "plano_contas": [],
            "lancamentos": [],
        }

        linhas = conteudo.strip().split("\n")
        resultado["totais"]["linhas"] = len(linhas)

        for linha in linhas:
            campos = linha.split("|")
            if len(campos) < 2:
                continue

            registro = campos[1]
            bloco = registro[0] if registro else ""

            if bloco not in resultado["registros"]:
                resultado["registros"][bloco] = []
                resultado["totais"]["por_bloco"][bloco] = 0

            resultado["registros"][bloco].append(campos)
            resultado["totais"]["por_bloco"][bloco] += 1

            # Extrair plano de contas (I050)
            if registro == "I050":
                conta = self.extrair_registro_i050(campos)
                if conta:
                    resultado["plano_contas"].append(conta)

            # Extrair lançamentos (I200)
            if registro == "I200":
                lancamento = self.extrair_registro_i200(campos)
                if lancamento:
                    resultado["lancamentos"].append(lancamento)

        return resultado

    def extrair_registro_0000(
        self,
        campos: list[str],
    ) -> dict[str, Any]:
        """Extrai dados do registro 0000 (Abertura)."""
        if len(campos) < 17:
            return {}

        return {
            "lecd": campos[2],  # LECD
            "dt_ini": campos[3],  # Data inicial
            "dt_fin": campos[4],  # Data final
            "nome": campos[5],  # Nome empresarial
            "cnpj": campos[6],
            "uf": campos[7],
            "ie": campos[8],
            "cod_mun": campos[9],
            "im": campos[10],
            "ind_sit_esp": campos[11],
            "ind_sit_ini_per": campos[12],
            "ind_nire": campos[13],
            "ind_fin_esc": campos[14],
            "cod_hash_sub": campos[15],
            "ind_grande_porte": campos[16],
        }

    def extrair_registro_i050(
        self,
        campos: list[str],
    ) -> dict[str, Any]:
        """Extrai dados do registro I050 (Plano de Contas)."""
        if len(campos) < 9:
            return {}

        return {
            "dt_alt": campos[2],  # Data da inclusão/alteração
            "cod_nat": campos[3],  # Código natureza da conta
            "ind_cta": campos[4],  # Indicador tipo de conta
            "nivel": campos[5],  # Nível da conta
            "cod_cta": campos[6],  # Código da conta analítica
            "cod_cta_sup": campos[7],  # Código da conta sintética
            "cta": campos[8],  # Nome da conta
        }

    def extrair_registro_i200(
        self,
        campos: list[str],
    ) -> dict[str, Any]:
        """Extrai dados do registro I200 (Lançamento Contábil)."""
        if len(campos) < 7:
            return {}

        return {
            "num_lcto": campos[2],  # Número do lançamento
            "dt_lcto": campos[3],  # Data do lançamento
            "vl_lcto": campos[4],  # Valor do lançamento
            "ind_lcto": campos[5],  # Indicador tipo de lançamento
        }

    def extrair_registro_j100(
        self,
        campos: list[str],
    ) -> dict[str, Any]:
        """Extrai dados do registro J100 (Balanço Patrimonial)."""
        if len(campos) < 9:
            return {}

        return {
            "cod_agl": campos[2],  # Código de aglutinação
            "nivel_agl": campos[3],  # Nível de aglutinação
            "ind_grp_bal": campos[4],  # Indicador grupo do balanço
            "descr_cta": campos[5],  # Descrição da linha
            "vl_cta": campos[6],  # Valor total da linha
            "ind_dc_cta": campos[7],  # Indicador D/C
        }

    def extrair_registro_j150(
        self,
        campos: list[str],
    ) -> dict[str, Any]:
        """Extrai dados do registro J150 (DRE)."""
        if len(campos) < 9:
            return {}

        return {
            "cod_agl": campos[2],  # Código de aglutinação
            "nivel_agl": campos[3],  # Nível de aglutinação
            "descr_cta": campos[4],  # Descrição da linha
            "vl_cta": campos[5],  # Valor da linha
            "ind_vl": campos[6],  # Indicador (D/C)
        }

    async def validar_arquivo_sped(
        self,
        conteudo: str,
    ) -> dict[str, Any]:
        """
        Valida estrutura de um arquivo SPED Contábil.

        Args:
            conteudo: Conteúdo do arquivo

        Returns:
            Resultado da validação
        """
        resultado = {
            "valido": True,
            "erros": [],
            "avisos": [],
        }

        linhas = conteudo.strip().split("\n")

        if not linhas:
            resultado["valido"] = False
            resultado["erros"].append("Arquivo vazio")
            return resultado

        # Verificar registro 0000
        if not linhas[0].startswith("|0000|"):
            resultado["valido"] = False
            resultado["erros"].append("Registro 0000 não encontrado no início")

        # Verificar registro 9999
        if not linhas[-1].startswith("|9999|"):
            resultado["valido"] = False
            resultado["erros"].append("Registro 9999 não encontrado no final")

        # Verificar blocos obrigatórios
        blocos_encontrados = set()
        for linha in linhas:
            campos = linha.split("|")
            if len(campos) >= 2:
                registro = campos[1]
                if registro:
                    blocos_encontrados.add(registro[0])

        blocos_obrigatorios = {"0", "I", "J", "9"}
        blocos_faltantes = blocos_obrigatorios - blocos_encontrados

        if blocos_faltantes:
            resultado["valido"] = False
            resultado["erros"].append(f"Blocos obrigatórios faltantes: {', '.join(sorted(blocos_faltantes))}")

        return resultado

    async def extrair_demonstracoes(
        self,
        conteudo: str,
    ) -> dict[str, Any]:
        """
        Extrai demonstrações contábeis do arquivo.

        Args:
            conteudo: Conteúdo do arquivo SPED

        Returns:
            Demonstrações extraídas
        """
        resultado = {
            "balanco_patrimonial": {
                "ativo": [],
                "passivo": [],
                "patrimonio_liquido": [],
            },
            "dre": [],
            "dlpa": [],
            "dmpl": [],
        }

        linhas = conteudo.strip().split("\n")

        for linha in linhas:
            campos = linha.split("|")
            if len(campos) < 2:
                continue

            registro = campos[1]

            # Balanço Patrimonial
            if registro == "J100":
                item = self.extrair_registro_j100(campos)
                if item:
                    ind_grp = item.get("ind_grp_bal", "")
                    if ind_grp == "1":
                        resultado["balanco_patrimonial"]["ativo"].append(item)
                    elif ind_grp == "2":
                        resultado["balanco_patrimonial"]["passivo"].append(item)
                    elif ind_grp == "4":
                        resultado["balanco_patrimonial"]["patrimonio_liquido"].append(item)

            # DRE
            elif registro == "J150":
                item = self.extrair_registro_j150(campos)
                if item:
                    resultado["dre"].append(item)

        return resultado
