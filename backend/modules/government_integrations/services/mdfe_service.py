"""
Service para MDF-e (Manifesto Eletronico de Documentos Fiscais).

Camada de servico que encapsula a logica de negocio do MDF-e.
"""

import hashlib
import logging
import os
from datetime import datetime
from decimal import Decimal
from typing import Any

from ..core.mdfe import (
    Condutor,
    DocumentoVinculado,
    MDFe,
    MDFeManager,
    ModalTransporteMDFe,
    Municipio,
    Percurso,
    Reboque,
    SituacaoMDFe,
    TipoCarroceria,
    TipoEmitente,
    TipoRodado,
    Veiculo,
)

logger = logging.getLogger(__name__)


class MDFeService:
    """
    Service para operacoes do MDF-e.

    Encapsula todas as operacoes relacionadas ao MDF-e,
    incluindo criacao, geracao de XML e eventos.
    """

    # Descricoes dos modais
    MODAIS = {
        "1": "Rodoviario",
        "2": "Aereo",
        "3": "Aquaviario",
        "4": "Ferroviario",
    }

    # Descricoes dos tipos de emitente
    TIPOS_EMITENTE = {
        "1": "Prestador de servico de transporte",
        "2": "Transportador de carga propria",
        "3": "Correios",
    }

    # Descricoes dos tipos de carroceria
    TIPOS_CARROCERIA = {
        "00": "Nao aplicavel",
        "01": "Aberta",
        "02": "Fechada/Bau",
        "03": "Graneleira",
        "04": "Porta Container",
        "05": "Sider",
    }

    def __init__(self):
        """Inicializa o service."""
        self.cnpj = os.environ.get("MDFE_CNPJ", os.environ.get("EMPRESA_CNPJ", ""))
        self.razao_social = os.environ.get("EMPRESA_RAZAO_SOCIAL", "Empresa")
        self.ie = os.environ.get("EMPRESA_IE", "")
        self.uf = os.environ.get("EMPRESA_UF", "AM")
        self.ambiente = os.environ.get("MDFE_AMBIENTE", "homologacao")

        self.manager = MDFeManager(
            cnpj=self.cnpj,
            razao_social=self.razao_social,
            inscricao_estadual=self.ie,
            uf=self.uf,
            ambiente=self.ambiente,
        )

        # Cache de MDF-e criados (em producao, usar banco de dados)
        self._mdfes: dict[str, MDFe] = {}

        logger.info(f"MDFeService iniciado: CNPJ={self.cnpj}, UF={self.uf}, Ambiente={self.ambiente}")

    def validar_status(self) -> dict[str, Any]:
        """Valida e retorna status da configuracao."""
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "inscricao_estadual": self.ie,
            "uf": self.uf,
            "ambiente": self.ambiente,
            "versao_layout": "3.00",
            "operacoes_disponiveis": [
                "criar",
                "gerar_xml",
                "encerrar",
                "incluir_condutor",
                "consultar_status_servico",
                "consultar_nao_encerrados",
            ],
        }

    def criar_mdfe(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Cria um novo MDF-e.

        Args:
            dados: Dados do MDF-e

        Returns:
            MDF-e criado
        """
        numero = dados["numero"]
        serie = dados.get("serie", 1)
        modal_str = dados.get("modal", "1")
        modal = ModalTransporteMDFe(modal_str)

        # Cria o MDF-e base
        mdfe = self.manager.criar_mdfe(numero=numero, serie=serie, modal=modal)

        # Tipo emitente
        tipo_emitente_str = dados.get("tipo_emitente", "1")
        mdfe.tipo_emitente = TipoEmitente(tipo_emitente_str)

        # UFs
        mdfe.uf_inicio = dados.get("uf_inicio", self.uf)
        mdfe.uf_fim = dados.get("uf_fim", self.uf)

        # Percurso
        if dados.get("percurso"):
            mdfe.percurso = [Percurso(uf=p["uf"]) for p in dados["percurso"]]

        # Data inicio viagem
        if dados.get("data_inicio_viagem"):
            mdfe.data_inicio_viagem = datetime.fromisoformat(dados["data_inicio_viagem"])

        # Municipios de carregamento
        if dados.get("municipios_carregamento"):
            mdfe.municipios_carregamento = [self._criar_municipio(m) for m in dados["municipios_carregamento"]]

        # Municipios de descarregamento
        if dados.get("municipios_descarregamento"):
            mdfe.municipios_descarregamento = [self._criar_municipio(m) for m in dados["municipios_descarregamento"]]
            # Conta documentos
            for mun in mdfe.municipios_descarregamento:
                for doc in mun.documentos:
                    if doc.tipo == "CTe":
                        mdfe.quantidade_cte += 1
                    elif doc.tipo == "NFe":
                        mdfe.quantidade_nfe += 1

        # Totais
        mdfe.valor_total_carga = Decimal(str(dados.get("valor_total_carga", 0)))
        mdfe.peso_bruto_total = Decimal(str(dados.get("peso_bruto_total", 0)))

        # Veiculo de tracao
        if dados.get("veiculo_tracao"):
            mdfe.veiculo_tracao = self._criar_veiculo(dados["veiculo_tracao"])

        # Reboques
        if dados.get("reboques"):
            mdfe.reboques = [self._criar_reboque(r) for r in dados["reboques"]]

        # Condutores
        if dados.get("condutores"):
            mdfe.condutores = [Condutor(cpf=c["cpf"], nome=c["nome"]) for c in dados["condutores"]]

        # CIOT
        mdfe.ciot = dados.get("ciot")
        mdfe.ciot_cnpj_cpf = dados.get("ciot_cnpj_cpf")

        # Seguro
        mdfe.seguradora_cnpj = dados.get("seguradora_cnpj")
        mdfe.seguradora_nome = dados.get("seguradora_nome")
        mdfe.numero_apolice = dados.get("numero_apolice")
        mdfe.numero_averbacao = dados.get("numero_averbacao")

        # Gera ID interno
        mdfe_id = f"mdfe_{numero}_{serie}"
        self._mdfes[mdfe_id] = mdfe

        logger.info(f"MDF-e criado: {mdfe_id}")

        return {
            "mdfe_id": mdfe_id,
            "numero": mdfe.numero,
            "serie": mdfe.serie,
            "chave": mdfe.chave,
            "modal": mdfe.modal.value,
            "tipo_emitente": mdfe.tipo_emitente.value,
            "uf_inicio": mdfe.uf_inicio,
            "uf_fim": mdfe.uf_fim,
            "situacao": mdfe.situacao.value,
            "data_emissao": mdfe.data_emissao.isoformat(),
            "valor_total_carga": str(mdfe.valor_total_carga),
            "peso_bruto_total": str(mdfe.peso_bruto_total),
            "quantidade_cte": mdfe.quantidade_cte,
            "quantidade_nfe": mdfe.quantidade_nfe,
        }

    def _criar_municipio(self, dados: dict[str, Any]) -> Municipio:
        """Cria objeto Municipio a partir dos dados."""
        documentos = []
        if dados.get("documentos"):
            documentos = [
                DocumentoVinculado(
                    tipo=d["tipo"],
                    chave=d["chave"],
                    segundo_codigo_barras=d.get("segundo_codigo_barras"),
                )
                for d in dados["documentos"]
            ]

        return Municipio(
            codigo_ibge=dados["codigo_ibge"],
            nome=dados["nome"],
            documentos=documentos,
        )

    def _criar_veiculo(self, dados: dict[str, Any]) -> Veiculo:
        """Cria objeto Veiculo a partir dos dados."""
        return Veiculo(
            placa=dados["placa"],
            renavam=dados.get("renavam"),
            uf=dados.get("uf", self.uf),
            tara=Decimal(str(dados.get("tara", 0))),
            capacidade_kg=Decimal(str(dados.get("capacidade_kg", 0))),
            capacidade_m3=Decimal(str(dados.get("capacidade_m3", 0))),
            tipo_rodado=TipoRodado(dados.get("tipo_rodado", "01")),
            tipo_carroceria=TipoCarroceria(dados.get("tipo_carroceria", "02")),
            proprietario_cnpj_cpf=dados.get("proprietario_cnpj_cpf"),
            proprietario_nome=dados.get("proprietario_nome"),
            proprietario_ie=dados.get("proprietario_ie"),
            proprietario_uf=dados.get("proprietario_uf"),
        )

    def _criar_reboque(self, dados: dict[str, Any]) -> Reboque:
        """Cria objeto Reboque a partir dos dados."""
        return Reboque(
            placa=dados["placa"],
            renavam=dados.get("renavam"),
            uf=dados.get("uf", self.uf),
            tara=Decimal(str(dados.get("tara", 0))),
            capacidade_kg=Decimal(str(dados.get("capacidade_kg", 0))),
            capacidade_m3=Decimal(str(dados.get("capacidade_m3", 0))),
            tipo_carroceria=TipoCarroceria(dados.get("tipo_carroceria", "02")),
        )

    def gerar_xml(self, mdfe_id: str) -> dict[str, Any]:
        """
        Gera XML do MDF-e.

        Args:
            mdfe_id: ID do MDF-e

        Returns:
            XML gerado
        """
        if mdfe_id not in self._mdfes:
            raise ValueError(f"MDF-e nao encontrado: {mdfe_id}")

        mdfe = self._mdfes[mdfe_id]
        xml = self.manager.gerar_xml(mdfe)

        # Calcula hash
        hash_md5 = hashlib.sha256(xml.encode()).hexdigest()

        logger.info(f"XML gerado para MDF-e {mdfe_id}")

        return {
            "mdfe_id": mdfe_id,
            "numero": mdfe.numero,
            "xml": xml,
            "hash_md5": hash_md5,
        }

    def encerrar_mdfe(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Gera evento de encerramento do MDF-e.

        Args:
            dados: Dados do encerramento

        Returns:
            Resultado do encerramento
        """
        chave = dados["chave"]
        protocolo = dados["protocolo_autorizacao"]

        # Busca MDF-e pela chave (em producao, buscar no banco)
        mdfe = None
        for m in self._mdfes.values():
            if m.chave == chave:
                mdfe = m
                break

        # Se nao encontrou, cria um temporario para o evento
        if not mdfe:
            mdfe = MDFe(chave=chave, protocolo_autorizacao=protocolo)

        # Data de encerramento
        data_enc = None
        if dados.get("data_encerramento"):
            data_enc = datetime.fromisoformat(dados["data_encerramento"])

        resultado = self.manager.encerrar(mdfe, data_enc)

        # Adiciona dados extras
        resultado["evento"]["uf_encerramento"] = dados.get("uf_encerramento", self.uf)
        resultado["evento"]["codigo_municipio"] = dados.get("codigo_municipio", "1302603")

        logger.info(f"Evento de encerramento gerado para MDF-e {chave}")

        return {
            "chave": chave,
            "tipo_evento": resultado["evento"]["tipo_evento"],
            "descricao": resultado["evento"]["descricao"],
            "status": resultado["status"],
            "protocolo": protocolo,
            "data_encerramento": resultado["evento"]["data_evento"],
        }

    def incluir_condutor(self, dados: dict[str, Any]) -> dict[str, Any]:
        """
        Gera evento de inclusao de condutor.

        Args:
            dados: Dados do condutor

        Returns:
            Resultado da inclusao
        """
        chave = dados["chave"]
        condutor_data = dados["condutor"]

        # Busca MDF-e pela chave
        mdfe = None
        for m in self._mdfes.values():
            if m.chave == chave:
                mdfe = m
                break

        if not mdfe:
            mdfe = MDFe(chave=chave)

        condutor = Condutor(
            cpf=condutor_data["cpf"],
            nome=condutor_data["nome"],
        )

        resultado = self.manager.incluir_condutor(mdfe, condutor)

        logger.info(f"Evento de inclusao de condutor gerado para MDF-e {chave}")

        return {
            "chave": chave,
            "tipo_evento": resultado["evento"]["tipo_evento"],
            "descricao": resultado["evento"]["descricao"],
            "condutor_cpf": condutor.cpf,
            "condutor_nome": condutor.nome,
            "status": resultado["status"],
        }

    def consultar_status_servico(self) -> dict[str, Any]:
        """
        Consulta status do servico MDF-e na SEFAZ.

        Returns:
            Status do servico
        """
        resultado = self.manager.consultar_status_servico()

        return {
            "servico": resultado["servico"],
            "url": resultado["url"],
            "ambiente": self.ambiente,
            "status": resultado["status"],
            "mensagem": resultado["mensagem"],
        }

    def consultar_nao_encerrados(self) -> dict[str, Any]:
        """
        Consulta MDF-e nao encerrados.

        Returns:
            Lista de MDF-e nao encerrados
        """
        # Em producao, consulta no banco de dados
        nao_encerrados = [
            {
                "chave": mdfe.chave,
                "numero": mdfe.numero,
                "serie": mdfe.serie,
                "data_emissao": mdfe.data_emissao.isoformat(),
                "situacao": mdfe.situacao.value,
            }
            for mdfe in self._mdfes.values()
            if mdfe.situacao in [SituacaoMDFe.AUTORIZADO, SituacaoMDFe.ASSINADO]
        ]

        # Tambem consulta na SEFAZ
        sefaz_result = self.manager.consultar_nao_encerrados()

        return {
            "quantidade": len(nao_encerrados),
            "mdfes": nao_encerrados,
            "sefaz_pendente": len(sefaz_result),
        }

    def listar_modais(self) -> dict[str, Any]:
        """Lista modais de transporte disponiveis."""
        return {"modais": [{"codigo": k, "descricao": v} for k, v in self.MODAIS.items()]}

    def listar_tipos_emitente(self) -> dict[str, Any]:
        """Lista tipos de emitente disponiveis."""
        return {"tipos_emitente": [{"codigo": k, "descricao": v} for k, v in self.TIPOS_EMITENTE.items()]}

    def listar_tipos_carroceria(self) -> dict[str, Any]:
        """Lista tipos de carroceria disponiveis."""
        return {"tipos_carroceria": [{"codigo": k, "descricao": v} for k, v in self.TIPOS_CARROCERIA.items()]}

    def buscar_mdfe(self, mdfe_id: str) -> dict[str, Any] | None:
        """
        Busca um MDF-e pelo ID.

        Args:
            mdfe_id: ID do MDF-e

        Returns:
            MDF-e encontrado ou None
        """
        if mdfe_id not in self._mdfes:
            return None

        mdfe = self._mdfes[mdfe_id]

        return {
            "mdfe_id": mdfe_id,
            "numero": mdfe.numero,
            "serie": mdfe.serie,
            "chave": mdfe.chave,
            "modal": mdfe.modal.value,
            "tipo_emitente": mdfe.tipo_emitente.value,
            "uf_inicio": mdfe.uf_inicio,
            "uf_fim": mdfe.uf_fim,
            "situacao": mdfe.situacao.value,
            "data_emissao": mdfe.data_emissao.isoformat(),
            "valor_total_carga": str(mdfe.valor_total_carga),
            "peso_bruto_total": str(mdfe.peso_bruto_total),
            "quantidade_cte": mdfe.quantidade_cte,
            "quantidade_nfe": mdfe.quantidade_nfe,
            "condutores": [{"cpf": c.cpf, "nome": c.nome} for c in mdfe.condutores],
        }

    def listar_mdfes(self) -> dict[str, Any]:
        """Lista todos os MDF-e em memoria."""
        return {
            "quantidade": len(self._mdfes),
            "mdfes": [
                {
                    "mdfe_id": mdfe_id,
                    "numero": mdfe.numero,
                    "serie": mdfe.serie,
                    "situacao": mdfe.situacao.value,
                    "data_emissao": mdfe.data_emissao.isoformat(),
                }
                for mdfe_id, mdfe in self._mdfes.items()
            ],
        }

    def limpar_dados(self) -> dict[str, Any]:
        """Limpa dados em memoria."""
        quantidade = len(self._mdfes)
        self._mdfes.clear()

        logger.info(f"Dados limpos: {quantidade} MDF-e removidos")

        return {"message": f"Dados limpos: {quantidade} MDF-e removidos"}


# Singleton
_service_instance: MDFeService | None = None


def get_mdfe_service() -> MDFeService:
    """Retorna instancia singleton do service."""
    global _service_instance
    if _service_instance is None:
        _service_instance = MDFeService()
    return _service_instance
