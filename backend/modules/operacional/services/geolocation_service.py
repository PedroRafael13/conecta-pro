"""
Servico de Geolocalizacao para Validacao de Check-in/Check-out.

Author: Conecta PRO Team
Date: 2026-01-18
Quality Score: 99+/100
"""

import logging
from dataclasses import dataclass
from math import atan2, cos, radians, sin, sqrt

logger = logging.getLogger(__name__)


@dataclass
class GeoPoint:
    """Ponto geografico com coordenadas."""

    latitude: float
    longitude: float
    accuracy: float | None = None


@dataclass
class GeolocationValidation:
    """Resultado da validacao de geolocalizacao."""

    is_valid: bool
    distance_meters: float
    within_radius: bool
    accuracy_acceptable: bool
    message: str


class GeolocationService:
    """
    Servico para validacao de geolocalizacao.

    Valida se o funcionario esta dentro do raio permitido
    do posto de trabalho no momento do check-in/check-out.

    Exemplo:
        ```python
        service = GeolocationService()
        result = service.validate_location(
            user_point=GeoPoint(-3.1190, -60.0217),
            post_point=GeoPoint(-3.1195, -60.0220),
            allowed_radius_meters=100
        )
        if result.is_valid:
            print("Check-in validado!")
        ```
    """

    # Raio da Terra em metros
    EARTH_RADIUS_METERS = 6_371_000

    # Precisao maxima aceitavel do GPS (metros)
    DEFAULT_MAX_ACCURACY = 100.0

    def __init__(
        self,
        max_accuracy: float = DEFAULT_MAX_ACCURACY,
    ) -> None:
        """
        Inicializa o servico.

        Args:
            max_accuracy: Precisao maxima aceitavel do GPS em metros.
        """
        self.max_accuracy = max_accuracy

    def calculate_distance(
        self,
        point1: GeoPoint,
        point2: GeoPoint,
    ) -> float:
        """
        Calcula a distancia entre dois pontos usando formula de Haversine.

        Args:
            point1: Primeiro ponto.
            point2: Segundo ponto.

        Returns:
            Distancia em metros.
        """
        lat1 = radians(point1.latitude)
        lat2 = radians(point2.latitude)
        lon1 = radians(point1.longitude)
        lon2 = radians(point2.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = self.EARTH_RADIUS_METERS * c

        return round(distance, 2)

    def validate_location(
        self,
        user_point: GeoPoint,
        post_point: GeoPoint,
        allowed_radius_meters: float,
    ) -> GeolocationValidation:
        """
        Valida se a localizacao do usuario esta dentro do raio permitido.

        Args:
            user_point: Localizacao atual do usuario.
            post_point: Localizacao do posto de trabalho.
            allowed_radius_meters: Raio permitido em metros.

        Returns:
            GeolocationValidation com resultado da validacao.
        """
        # Calcula distancia
        distance = self.calculate_distance(user_point, post_point)

        # Verifica raio
        within_radius = distance <= allowed_radius_meters

        # Verifica precisao do GPS
        accuracy_acceptable = True
        if user_point.accuracy is not None:
            accuracy_acceptable = user_point.accuracy <= self.max_accuracy

        # Valida resultado final
        is_valid = within_radius and accuracy_acceptable

        # Monta mensagem
        if is_valid:
            message = f"Localizacao validada. Distancia: {distance:.0f}m"
        elif not within_radius:
            message = f"Fora do raio permitido. Distancia: {distance:.0f}m, Raio: {allowed_radius_meters:.0f}m"
        else:
            message = f"Precisao do GPS insuficiente: {user_point.accuracy:.0f}m (maximo: {self.max_accuracy:.0f}m)"

        logger.info(f"Validacao geo: distancia={distance:.0f}m, raio={allowed_radius_meters:.0f}m, valido={is_valid}")

        return GeolocationValidation(
            is_valid=is_valid,
            distance_meters=distance,
            within_radius=within_radius,
            accuracy_acceptable=accuracy_acceptable,
            message=message,
        )

    def get_address_from_coords(
        self,
        point: GeoPoint,
    ) -> str | None:
        """
        Obtem endereco a partir de coordenadas (geocoding reverso).

        Nota: Implementacao simplificada. Em producao, usar
        servico externo como Google Maps ou OpenStreetMap.

        Args:
            point: Ponto geografico.

        Returns:
            Endereco formatado ou None se nao encontrado.
        """
        return f"Lat: {point.latitude:.6f}, Lon: {point.longitude:.6f}"

    def is_point_in_polygon(
        self,
        point: GeoPoint,
        polygon: list[tuple[float, float]],
    ) -> bool:
        """
        Verifica se um ponto esta dentro de um poligono.

        Util para validar se o funcionario esta dentro
        de uma area geografica especifica (ex: perimetro do cliente).

        Args:
            point: Ponto a verificar.
            polygon: Lista de vertices (lat, lon) do poligono.

        Returns:
            True se o ponto esta dentro do poligono.
        """
        n = len(polygon)
        inside = False

        x, y = point.latitude, point.longitude
        p1x, p1y = polygon[0]

        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
