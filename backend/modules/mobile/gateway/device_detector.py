"""Detector de dispositivos mobile."""

import contextlib
import logging
import re
from dataclasses import dataclass

from fastapi import Request

logger = logging.getLogger(__name__)


@dataclass
class DeviceCapabilities:
    """Capacidades do dispositivo."""

    supports_webp: bool = False
    supports_avif: bool = False
    supports_gzip: bool = True
    supports_brotli: bool = False
    supports_push: bool = True
    supports_websocket: bool = True
    max_memory_mb: int | None = None
    screen_width: int | None = None
    screen_height: int | None = None
    pixel_ratio: float = 1.0


@dataclass
class DetectedDevice:
    """Informações completas do dispositivo detectado."""

    # Identificação
    device_id: str | None = None
    device_type: str = "unknown"  # mobile, tablet, desktop
    platform: str = "unknown"  # android, ios, web
    browser: str | None = None
    browser_version: str | None = None

    # Sistema
    os_name: str = "unknown"
    os_version: str | None = None

    # App
    app_name: str | None = None
    app_version: str | None = None
    app_build: int | None = None

    # Rede
    connection_type: str = "unknown"  # wifi, 4g, 3g, 2g, slow
    effective_bandwidth_mbps: float | None = None
    rtt_ms: int | None = None

    # Bateria
    battery_level: int | None = None
    is_charging: bool = False
    is_low_power_mode: bool = False

    # Capacidades
    capabilities: DeviceCapabilities = None

    # Flags
    is_mobile: bool = False
    is_tablet: bool = False
    is_bot: bool = False
    is_native_app: bool = False
    is_pwa: bool = False

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = DeviceCapabilities()


class DeviceDetector:
    """
    Detector avançado de dispositivos mobile.

    Analisa User-Agent e headers customizados para
    identificar tipo de dispositivo, plataforma e capacidades.
    """

    # Patterns para detecção
    MOBILE_PATTERNS = [
        r"Mobile",
        r"Android.*Mobile",
        r"iPhone",
        r"iPod",
        r"BlackBerry",
        r"Opera Mini",
        r"IEMobile",
        r"Windows Phone",
    ]

    TABLET_PATTERNS = [
        r"iPad",
        r"Android(?!.*Mobile)",
        r"Tablet",
        r"PlayBook",
        r"Silk",
    ]

    BOT_PATTERNS = [
        r"bot",
        r"crawler",
        r"spider",
        r"scraper",
        r"Googlebot",
        r"Bingbot",
        r"Slurp",
        r"DuckDuckBot",
        r"facebookexternalhit",
    ]

    BROWSER_PATTERNS = {
        "chrome": r"Chrome/(\d+(?:\.\d+)*)",
        "firefox": r"Firefox/(\d+(?:\.\d+)*)",
        "safari": r"Safari/(\d+(?:\.\d+)*)",
        "edge": r"Edg/(\d+(?:\.\d+)*)",
        "opera": r"OPR/(\d+(?:\.\d+)*)",
        "samsung": r"SamsungBrowser/(\d+(?:\.\d+)*)",
    }

    OS_PATTERNS = {
        "android": r"Android\s*(\d+(?:\.\d+)*)?",
        "ios": r"(?:iPhone|iPad|iPod).*?OS\s*(\d+(?:[_\.]\d+)*)",
        "windows": r"Windows NT\s*(\d+(?:\.\d+)*)",
        "macos": r"Mac OS X\s*(\d+(?:[_\.]\d+)*)",
        "linux": r"Linux",
    }

    def __init__(self) -> None:
        """Inicializa o detector."""
        # Compilar patterns
        self._mobile_re = [re.compile(p, re.IGNORECASE) for p in self.MOBILE_PATTERNS]
        self._tablet_re = [re.compile(p, re.IGNORECASE) for p in self.TABLET_PATTERNS]
        self._bot_re = [re.compile(p, re.IGNORECASE) for p in self.BOT_PATTERNS]
        self._browser_re = {k: re.compile(v, re.IGNORECASE) for k, v in self.BROWSER_PATTERNS.items()}
        self._os_re = {k: re.compile(v, re.IGNORECASE) for k, v in self.OS_PATTERNS.items()}

        # Pattern para app nativo ConectaPRO
        self._native_app_re = re.compile(
            r"ConectaPRO[/-](Android|iOS)[/-](\d+(?:\.\d+)*)(?:\s*\((\d+)\))?",
            re.IGNORECASE,
        )

    async def detect(self, request: Request) -> DetectedDevice:
        """
        Detecta informações do dispositivo a partir da requisição.

        Args:
            request: Requisição HTTP

        Returns:
            DetectedDevice com informações completas
        """
        user_agent = request.headers.get("user-agent", "")
        headers = dict(request.headers)

        device = DetectedDevice()

        # Detectar tipo básico
        device.is_bot = self._is_bot(user_agent)
        device.is_tablet = self._is_tablet(user_agent)
        device.is_mobile = self._is_mobile(user_agent) and not device.is_tablet

        if device.is_mobile:
            device.device_type = "mobile"
        elif device.is_tablet:
            device.device_type = "tablet"
        else:
            device.device_type = "desktop"

        # Detectar app nativo
        native_match = self._native_app_re.search(user_agent)
        if native_match:
            device.is_native_app = True
            device.app_name = "ConectaPRO"
            device.platform = native_match.group(1).lower()
            device.app_version = native_match.group(2)
            if native_match.group(3):
                device.app_build = int(native_match.group(3))
        else:
            # Detectar plataforma via OS
            device.platform = self._detect_platform(user_agent)

        # Detectar OS
        os_info = self._detect_os(user_agent)
        device.os_name = os_info[0]
        device.os_version = os_info[1]

        # Detectar browser
        browser_info = self._detect_browser(user_agent)
        device.browser = browser_info[0]
        device.browser_version = browser_info[1]

        # Ler headers customizados do app
        self._read_custom_headers(device, headers)

        # Detectar capacidades
        device.capabilities = self._detect_capabilities(headers)

        # Detectar PWA
        device.is_pwa = headers.get("x-pwa-mode") == "true"

        logger.debug(
            f"Detected device: type={device.device_type}, "
            f"platform={device.platform}, "
            f"native={device.is_native_app}, "
            f"connection={device.connection_type}"
        )

        return device

    def _is_mobile(self, user_agent: str) -> bool:
        """Verifica se é dispositivo mobile."""
        return any(p.search(user_agent) for p in self._mobile_re)

    def _is_tablet(self, user_agent: str) -> bool:
        """Verifica se é tablet."""
        return any(p.search(user_agent) for p in self._tablet_re)

    def _is_bot(self, user_agent: str) -> bool:
        """Verifica se é bot/crawler."""
        return any(p.search(user_agent) for p in self._bot_re)

    def _detect_platform(self, user_agent: str) -> str:
        """Detecta plataforma do dispositivo."""
        ua_lower = user_agent.lower()

        if "android" in ua_lower:
            return "android"
        elif any(x in ua_lower for x in ["iphone", "ipad", "ipod"]):
            return "ios"
        elif "windows phone" in ua_lower:
            return "windows-phone"
        elif "windows" in ua_lower:
            return "windows"
        elif "mac" in ua_lower:
            return "macos"
        elif "linux" in ua_lower:
            return "linux"

        return "unknown"

    def _detect_os(self, user_agent: str) -> tuple[str, str | None]:
        """Detecta sistema operacional e versão."""
        for os_name, pattern in self._os_re.items():
            match = pattern.search(user_agent)
            if match:
                version = match.group(1) if match.lastindex else None
                if version:
                    # Normalizar versão (iOS usa _ ao invés de .)
                    version = version.replace("_", ".")
                return os_name, version

        return "unknown", None

    def _detect_browser(self, user_agent: str) -> tuple[str | None, str | None]:
        """Detecta browser e versão."""
        for browser_name, pattern in self._browser_re.items():
            match = pattern.search(user_agent)
            if match:
                version = match.group(1) if match.lastindex else None
                return browser_name, version

        return None, None

    def _read_custom_headers(self, device: DetectedDevice, headers: dict) -> None:
        """Lê headers customizados enviados pelo app."""
        # Device ID
        device.device_id = headers.get("x-device-id")

        # Conexão
        connection = headers.get("x-connection-type", "unknown").lower()
        if connection in ["wifi", "4g", "3g", "2g", "slow", "offline"]:
            device.connection_type = connection
        else:
            # Tentar inferir de Network Information API
            ect = headers.get("ect", "").lower()
            if ect == "4g":
                device.connection_type = "4g"
            elif ect == "3g":
                device.connection_type = "3g"
            elif ect in ["2g", "slow-2g"]:
                device.connection_type = "slow"

        # Bandwidth e RTT
        if headers.get("downlink"):
            with contextlib.suppress(ValueError):
                device.effective_bandwidth_mbps = float(headers["downlink"])

        if headers.get("rtt"):
            with contextlib.suppress(ValueError):
                device.rtt_ms = int(headers["rtt"])

        # Bateria
        battery = headers.get("x-battery-level")
        if battery:
            with contextlib.suppress(ValueError):
                device.battery_level = int(battery)

        device.is_charging = headers.get("x-charging") == "true"
        device.is_low_power_mode = headers.get("x-low-power-mode") == "true"

        # OS version do header (mais preciso que UA)
        if headers.get("x-os-version"):
            device.os_version = headers["x-os-version"]

        # App version do header
        if headers.get("x-app-version"):
            device.app_version = headers["x-app-version"]

        if headers.get("x-app-build"):
            with contextlib.suppress(ValueError):
                device.app_build = int(headers["x-app-build"])

    def _detect_capabilities(self, headers: dict) -> DeviceCapabilities:
        """Detecta capacidades do dispositivo."""
        caps = DeviceCapabilities()

        # Formatos de imagem suportados
        accept = headers.get("accept", "")
        caps.supports_webp = "image/webp" in accept
        caps.supports_avif = "image/avif" in accept

        # Compressão
        accept_encoding = headers.get("accept-encoding", "")
        caps.supports_gzip = "gzip" in accept_encoding
        caps.supports_brotli = "br" in accept_encoding

        # Headers customizados de capacidade
        if headers.get("x-max-memory-mb"):
            with contextlib.suppress(ValueError):
                caps.max_memory_mb = int(headers["x-max-memory-mb"])

        # Viewport
        if headers.get("x-screen-width"):
            with contextlib.suppress(ValueError):
                caps.screen_width = int(headers["x-screen-width"])

        if headers.get("x-screen-height"):
            with contextlib.suppress(ValueError):
                caps.screen_height = int(headers["x-screen-height"])

        if headers.get("x-pixel-ratio"):
            with contextlib.suppress(ValueError):
                caps.pixel_ratio = float(headers["x-pixel-ratio"])

        return caps

    def is_low_end_device(self, device: DetectedDevice) -> bool:
        """
        Verifica se é dispositivo de baixo desempenho.

        Usado para ajustar features e qualidade de dados.
        """
        # Verificar memória
        if device.capabilities.max_memory_mb:
            if device.capabilities.max_memory_mb < 2048:  # < 2GB RAM
                return True

        # Verificar conexão
        if device.connection_type in ["2g", "slow"]:
            return True

        # Verificar bateria baixa em modo economia
        if device.is_low_power_mode and device.battery_level:
            if device.battery_level < 20:
                return True

        return False

    def should_reduce_quality(self, device: DetectedDevice) -> bool:
        """Verifica se deve reduzir qualidade das respostas."""
        if self.is_low_end_device(device):
            return True

        if device.connection_type in ["3g", "2g", "slow"]:
            return True

        if device.is_low_power_mode:
            return True

        return False

    def get_recommended_image_quality(self, device: DetectedDevice) -> int:
        """Retorna qualidade de imagem recomendada (1-100)."""
        if device.connection_type == "wifi":
            return 90
        elif device.connection_type == "4g":
            return 80
        elif device.connection_type == "3g":
            return 60
        elif device.connection_type in ["2g", "slow"]:
            return 40
        else:
            return 70  # default

    def get_recommended_page_size(self, device: DetectedDevice) -> int:
        """Retorna tamanho de página recomendado para listas."""
        if device.connection_type == "wifi":
            return 50
        elif device.connection_type == "4g":
            return 30
        elif device.connection_type == "3g":
            return 20
        elif device.connection_type in ["2g", "slow"]:
            return 10
        else:
            return 25  # default
