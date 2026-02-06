"""
Extrator de SPED Fiscal (EFD-ICMS/IPI).

Implementa:
- Leitura de arquivos SPED Fiscal
- Extração de dados de notas fiscais
- Consulta de escriturações transmitidas
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from uuid import UUID
import asyncio
import logging
import re

from ..base_extractor import ExtratorBase, DocumentoExtraido, ResultadoExtracao
from ...core.credentials import ProvedorCredenciais, TipoCredencial

logger = logging.getLogger(__name__)


class ExtratorSPEDFiscal(ExtratorBase):
    """
    Extrator de SPED Fiscal (EFD-ICMS/IPI).

    A Escrituração Fiscal Digital é um arquivo digital que reúne escriturações
    de documentos fiscais e outras informações de interesse dos Fiscos.

    Registros principais:
    - Bloco 0: Abertura, Identificação e Referências
    - Bloco C: Documentos Fiscais I (mercadorias)
    - Bloco D: Documentos Fiscais II (serviços)
    - Bloco E: Apuração do ICMS e IPI
    - Bloco G: CIAP (Controle de Crédito de ICMS do Ativo Permanente)
    - Bloco H: Inventário Físico
    - Bloco K: Produção e Estoque
    - Bloco 1: Outras Informações
    - Bloco 9: Controle e Encerramento
    """

    BLOCOS = {
        "0": "Abertura e Identificação",
        "C": "Documentos Fiscais - Mercadorias",
        "D": "Documentos Fiscais - Serviços",
        "E": "Apuração ICMS/IPI",
        "G": "CIAP",
        "H": "Inventário",
        "K": "Produção e Estoque",
        "1": "Outras Informações",
        "9": "Encerramento",
    }

    @property
    def tipo_servico(self) -> str:
        return "sped_fiscal"

    @property
    def tipo_credencial(self) -> TipoCredencial:
        return TipoCredencial.SPED

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
        Extrai dados de SPED Fiscal.

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

        if data_fim is None:
            data_fim = datetime.utcnow()
        if data_inicio is None:
            data_inicio = data_fim - timedelta(days=365)

        logger.info(
            f"Iniciando extração SPED Fiscal: {tenant_id} - "
            f"Período: {data_inicio.date()} a {data_fim.date()}"
        )

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
                logger.info(f"Extraindo SPED Fiscal para CNPJ: {cnpj}")

                # Consultar escriturações por período
                docs = await self._consultar_escrituracoes(
                    tenant_id, cnpj, data_inicio, data_fim
                )

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
            logger.error(f"Erro na extração SPED Fiscal: {e}")
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
    ) -> List[DocumentoExtraido]:
        """Consulta escriturações SPED Fiscal transmitidas."""
        documentos = []

        try:
            session = await self._get_session(tenant_id, with_cert=True)

            # Gerar períodos mensais
            periodo_atual = data_inicio.replace(day=1)

            while periodo_atual <= data_fim:
                periodo_str = periodo_atual.strftime("%Y-%m")

                doc = await self._criar_documento_escrituracao(
                    cnpj, periodo_str
                )

                if doc:
                    documentos.append(doc)

                # Próximo mês
                if periodo_atual.month == 12:
                    periodo_atual = periodo_atual.replace(
                        year=periodo_atual.year + 1, month=1
                    )
                else:
                    periodo_atual = periodo_atual.replace(
                        month=periodo_atual.month + 1
                    )

        except Exception as e:
            logger.error(f"Erro ao consultar escriturações SPED Fiscal: {e}")
            documentos.append(
                DocumentoExtraido(
                    id=f"sped_fiscal_{cnpj}_erro",
                    tipo="sped_fiscal",
                    dados={"cnpj": cnpj},
                    erro=str(e),
                )
            )

        return documentos

    async def _criar_documento_escrituracao(
        self,
        cnpj: str,
        periodo: str,
    ) -> DocumentoExtraido:
        """Cria documento de escrituração SPED Fiscal."""
        dados = {
            "cnpj": cnpj,
            "periodo_apuracao": periodo,
            "tipo": "sped_fiscal",

            "escrituracao": {
                "transmitida": None,
                "data_transmissao": None,
                "numero_recibo": None,
                "hash_arquivo": None,
                "versao_layout": "017",  # Versão atual
            },

            # Resumo do Bloco C (Documentos Fiscais)
            "documentos_fiscais": {
                "nfe_entrada": {
                    "quantidade": 0,
                    "valor_total": 0.0,
                    "icms_total": 0.0,
                },
                "nfe_saida": {
                    "quantidade": 0,
                    "valor_total": 0.0,
                    "icms_total": 0.0,
                },
                "nfce": {
                    "quantidade": 0,
                    "valor_total": 0.0,
                },
                "cte": {
                    "quantidade": 0,
                    "valor_total": 0.0,
                },
            },

            # Resumo do Bloco E (Apuração)
            "apuracao_icms": {
                "debitos": 0.0,
                "creditos": 0.0,
                "saldo_credor_anterior": 0.0,
                "saldo_apurado": 0.0,
                "valor_recolher": 0.0,
                "saldo_credor_transportar": 0.0,
            },

            "apuracao_ipi": {
                "debitos": 0.0,
                "creditos": 0.0,
                "saldo_apurado": 0.0,
            },

            # Resumo do Bloco H (Inventário)
            "inventario": {
                "data_inventario": None,
                "valor_total": 0.0,
                "quantidade_itens": 0,
            },

            # Resumo do Bloco K (Produção)
            "producao": {
                "possui_bloco_k": None,
                "ordens_producao": 0,
            },

            "consultado_em": datetime.utcnow().isoformat(),
            "status": "consulta_manual_necessaria",
        }

        return DocumentoExtraido(
            id=f"sped_fiscal_{cnpj}_{periodo}",
            tipo="sped_fiscal",
            dados=dados,
            data_documento=datetime.strptime(periodo, "%Y-%m"),
            processado=True,
        )

    def parsear_arquivo_sped(
        self,
        conteudo: str,
    ) -> Dict[str, Any]:
        """
        Parseia um arquivo SPED Fiscal.

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

        return resultado

    def extrair_registro_0000(
        self,
        campos: List[str],
    ) -> Dict[str, Any]:
        """Extrai dados do registro 0000 (Abertura)."""
        if len(campos) < 15:
            return {}

        return {
            "cod_ver": campos[2],  # Código da versão do leiaute
            "cod_fin": campos[3],  # Código da finalidade
            "dt_ini": campos[4],   # Data inicial
            "dt_fin": campos[5],   # Data final
            "nome": campos[6],     # Nome empresarial
            "cnpj": campos[7],
            "cpf": campos[8],
            "uf": campos[9],
            "ie": campos[10],      # Inscrição estadual
            "cod_mun": campos[11], # Código do município
            "im": campos[12],      # Inscrição municipal
            "suframa": campos[13],
            "ind_perfil": campos[14],  # Perfil de apresentação
        }

    def extrair_registro_c100(
        self,
        campos: List[str],
    ) -> Dict[str, Any]:
        """Extrai dados do registro C100 (Documento fiscal)."""
        if len(campos) < 30:
            return {}

        return {
            "ind_oper": campos[2],      # 0=Entrada, 1=Saída
            "ind_emit": campos[3],      # 0=Emissão própria, 1=Terceiros
            "cod_part": campos[4],      # Código do participante
            "cod_mod": campos[5],       # Código do modelo (55=NF-e)
            "cod_sit": campos[6],       # Código da situação
            "ser": campos[7],           # Série
            "num_doc": campos[8],       # Número do documento
            "chv_nfe": campos[9],       # Chave da NF-e
            "dt_doc": campos[10],       # Data do documento
            "dt_e_s": campos[11],       # Data entrada/saída
            "vl_doc": campos[12],       # Valor total do documento
            "ind_pgto": campos[13],     # Indicador de pagamento
            "vl_desc": campos[14],      # Valor do desconto
            "vl_abat_nt": campos[15],   # Abatimento não tributado
            "vl_merc": campos[16],      # Valor das mercadorias
            "ind_frt": campos[17],      # Indicador do frete
            "vl_frt": campos[18],       # Valor do frete
            "vl_seg": campos[19],       # Valor do seguro
            "vl_out_da": campos[20],    # Outras despesas
            "vl_bc_icms": campos[21],   # Base de cálculo ICMS
            "vl_icms": campos[22],      # Valor do ICMS
            "vl_bc_icms_st": campos[23],
            "vl_icms_st": campos[24],
            "vl_ipi": campos[25],       # Valor do IPI
            "vl_pis": campos[26],       # Valor do PIS
            "vl_cofins": campos[27],    # Valor da COFINS
            "vl_pis_st": campos[28],
            "vl_cofins_st": campos[29],
        }

    async def validar_arquivo_sped(
        self,
        conteudo: str,
    ) -> Dict[str, Any]:
        """
        Valida estrutura de um arquivo SPED Fiscal.

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

        # Verificar registro 0000 (abertura)
        if not linhas[0].startswith("|0000|"):
            resultado["valido"] = False
            resultado["erros"].append("Registro 0000 não encontrado no início")

        # Verificar registro 9999 (encerramento)
        if not linhas[-1].startswith("|9999|"):
            resultado["valido"] = False
            resultado["erros"].append("Registro 9999 não encontrado no final")

        # Verificar sequência de blocos
        blocos_esperados = ["0", "C", "D", "E", "G", "H", "K", "1", "9"]
        bloco_atual = None

        for i, linha in enumerate(linhas):
            campos = linha.split("|")
            if len(campos) < 2:
                continue

            registro = campos[1]
            bloco = registro[0] if registro else ""

            if bloco != bloco_atual:
                if bloco_atual is not None and bloco in blocos_esperados:
                    idx_atual = blocos_esperados.index(bloco_atual) if bloco_atual in blocos_esperados else -1
                    idx_novo = blocos_esperados.index(bloco)
                    if idx_novo < idx_atual:
                        resultado["avisos"].append(
                            f"Linha {i+1}: Bloco {bloco} após bloco {bloco_atual}"
                        )
                bloco_atual = bloco

        return resultado
