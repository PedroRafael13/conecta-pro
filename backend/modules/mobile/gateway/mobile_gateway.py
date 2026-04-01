"""Gateway otimizado para requisições mobile."""

import gzip
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from fastapi import Request

logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Informações do dispositivo extraídas do request."""

    device_type: str
    platform: str
    os_version: str | None
    app_version: str | None
    connection_type: str
    battery_level: str
    is_low_bandwidth: bool
    is_low_battery: bool


@dataclass
class ProcessingResult:
    """Resultado do processamento de request."""

    data: Any
    compressed: bool
    original_size: int
    final_size: int
    processing_time_ms: float


class MobileGateway:
    """
    Gateway otimizado para requisições mobile.

    Funcionalidades:
    - Compressão de resposta adaptativa
    - Detecção de dispositivo e rede
    - Otimização para conexões lentas
    - Economia de bateria
    - Batch processing
    """

    def __init__(
        self,
        compression_threshold: int = 1024,
        batch_timeout_ms: int = 200,
        max_batch_size: int = 10,
    ) -> None:
        """
        Inicializa o gateway.

        Args:
            compression_threshold: Tamanho mínimo para compressão (bytes)
            batch_timeout_ms: Timeout para batch de operações
            max_batch_size: Máximo de operações em um batch
        """
        self.compression_threshold = compression_threshold
        self.batch_timeout = batch_timeout_ms
        self.max_batch_size = max_batch_size

        # Configurações por tipo de conexão
        self.connection_configs = {
            "wifi": {
                "max_response_size": 1024 * 1024,  # 1MB
                "compression_level": 6,
                "image_quality": 90,
                "include_optional_data": True,
            },
            "4g": {
                "max_response_size": 512 * 1024,  # 512KB
                "compression_level": 7,
                "image_quality": 80,
                "include_optional_data": True,
            },
            "3g": {
                "max_response_size": 256 * 1024,  # 256KB
                "compression_level": 8,
                "image_quality": 60,
                "include_optional_data": False,
            },
            "slow": {
                "max_response_size": 128 * 1024,  # 128KB
                "compression_level": 9,
                "image_quality": 40,
                "include_optional_data": False,
            },
            "unknown": {
                "max_response_size": 256 * 1024,
                "compression_level": 7,
                "image_quality": 70,
                "include_optional_data": True,
            },
        }

    async def process_request(
        self,
        request: Request,
    ) -> DeviceInfo:
        """
        Processa requisição e extrai informações do dispositivo.

        Args:
            request: Requisição HTTP

        Returns:
            DeviceInfo com informações do dispositivo
        """
        user_agent = request.headers.get("user-agent", "")
        device_info = self._parse_device_info(user_agent, request.headers)

        logger.debug(
            f"Device: {device_info.platform}, "
            f"Connection: {device_info.connection_type}, "
            f"Battery: {device_info.battery_level}"
        )

        return device_info

    def _parse_device_info(
        self,
        user_agent: str,
        headers: dict,
    ) -> DeviceInfo:
        """Extrai informações do dispositivo do user agent e headers."""
        # Detectar plataforma
        if "ConectaPRO-Android" in user_agent:
            platform = "android"
        elif "ConectaPRO-iOS" in user_agent:
            platform = "ios"
        elif "Mobile" in user_agent or "Android" in user_agent or "iPhone" in user_agent:
            platform = "mobile-web"
        else:
            platform = "unknown"

        # Extrair versão do app
        app_version = None
        if "/" in user_agent:
            parts = user_agent.split("/")
            for part in parts:
                if part.startswith("ConectaPRO"):
                    continue
                if part[0].isdigit():
                    app_version = part.split(" ")[0]
                    break

        # Conexão (via header customizado ou Network Information API)
        connection_type = headers.get("x-connection-type", "unknown")
        if connection_type not in ["wifi", "4g", "3g", "slow"]:
            connection_type = "unknown"

        # Battery (via header customizado)
        battery_level = headers.get("x-battery-level", "normal")
        is_low_battery = battery_level == "low" or headers.get("x-low-power-mode") == "true"

        # Determinar se é low bandwidth
        is_low_bandwidth = connection_type in ["3g", "slow"]

        return DeviceInfo(
            device_type="mobile" if platform != "unknown" else "desktop",
            platform=platform,
            os_version=headers.get("x-os-version"),
            app_version=app_version,
            connection_type=connection_type,
            battery_level=battery_level,
            is_low_bandwidth=is_low_bandwidth,
            is_low_battery=is_low_battery,
        )

    async def optimize_response(
        self,
        data: Any,
        device_info: DeviceInfo,
        accept_encoding: str = "",
    ) -> ProcessingResult:
        """
        Otimiza resposta para o dispositivo.

        Args:
            data: Dados da resposta
            device_info: Informações do dispositivo
            accept_encoding: Header Accept-Encoding

        Returns:
            ProcessingResult com dados otimizados
        """
        start_time = time.time()

        # Converter para JSON
        json_data = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        original_size = len(json_data.encode("utf-8"))

        # Obter configuração para tipo de conexão
        config = self.connection_configs.get(
            device_info.connection_type,
            self.connection_configs["unknown"],
        )

        # Reduzir dados se conexão lenta ou bateria baixa
        if device_info.is_low_bandwidth or device_info.is_low_battery:
            data = self._reduce_data(data, config)
            json_data = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

        # Comprimir se necessário e aceito
        compressed = False
        final_data = json_data.encode("utf-8")

        if "gzip" in accept_encoding and len(final_data) > self.compression_threshold:
            compressed_data = gzip.compress(
                final_data,
                compresslevel=config["compression_level"],
            )
            # Só usar compressão se realmente reduzir o tamanho
            if len(compressed_data) < len(final_data):
                final_data = compressed_data
                compressed = True

        processing_time = (time.time() - start_time) * 1000

        return ProcessingResult(
            data=final_data,
            compressed=compressed,
            original_size=original_size,
            final_size=len(final_data),
            processing_time_ms=processing_time,
        )

    def _reduce_data(self, data: Any, config: dict) -> Any:
        """Reduz dados removendo campos opcionais."""
        if not config.get("include_optional_data", True):
            if isinstance(data, dict):
                return self._filter_essential_fields(data)
            elif isinstance(data, list):
                return [self._filter_essential_fields(item) for item in data]
        return data

    def _filter_essential_fields(self, data: dict) -> dict:
        """Remove campos não essenciais."""
        # Campos opcionais comuns que podem ser removidos
        optional_fields = {
            "metadata",
            "extra",
            "debug",
            "audit_log",
            "full_description",
            "history",
            "attachments",
            "comments",
        }

        return {key: value for key, value in data.items() if key not in optional_fields}

    def get_config_for_device(self, device_info: DeviceInfo) -> dict:
        """Retorna configuração para o dispositivo."""
        return self.connection_configs.get(
            device_info.connection_type,
            self.connection_configs["unknown"],
        )

    def should_use_lightweight_response(self, device_info: DeviceInfo) -> bool:
        """Verifica se deve usar resposta lightweight."""
        return (
            device_info.is_low_bandwidth or device_info.is_low_battery or device_info.connection_type in ["3g", "slow"]
        )

    async def process_low_bandwidth(
        self,
        data: Any,
        essential_fields: list[str] | None = None,
    ) -> Any:
        """
        Processa dados para conexões lentas.

        Mantém apenas campos essenciais.
        """
        if essential_fields and isinstance(data, dict):
            return {key: value for key, value in data.items() if key in essential_fields}
        elif essential_fields and isinstance(data, list):
            return [
                {key: value for key, value in item.items() if key in essential_fields}
                for item in data
                if isinstance(item, dict)
            ]
        return data

    async def process_battery_saving(
        self,
        data: Any,
    ) -> Any:
        """
        Processa dados no modo economia de bateria.

        Remove dados que exigem processamento intensivo.
        """
        # Remove imagens, vídeos e dados pesados
        heavy_fields = {"images", "videos", "attachments", "charts", "graphs"}

        if isinstance(data, dict):
            return {key: value for key, value in data.items() if key not in heavy_fields}
        return data
