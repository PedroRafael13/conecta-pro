"""Tests for Mobile Gateway."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.mobile.gateway.compression import (
    CompressionMiddleware,
    compress_data,
    decompress_data,
)
from modules.mobile.gateway.device_detector import (
    DetectedDevice,
    DeviceCapabilities,
    DeviceDetector,
)
from modules.mobile.gateway.mobile_gateway import (
    DeviceInfo,
    MobileGateway,
    ProcessingResult,
)


class TestMobileGateway:
    """Tests for MobileGateway class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.gateway = MobileGateway(
            compression_threshold=100,
            batch_timeout_ms=200,
            max_batch_size=10,
        )

    def test_init_default_values(self):
        """Test gateway initialization with defaults."""
        gateway = MobileGateway()
        assert gateway.compression_threshold == 1024
        assert gateway.batch_timeout == 200
        assert gateway.max_batch_size == 10

    def test_connection_configs(self):
        """Test connection configurations."""
        assert "wifi" in self.gateway.connection_configs
        assert "4g" in self.gateway.connection_configs
        assert "3g" in self.gateway.connection_configs
        assert "slow" in self.gateway.connection_configs
        assert "unknown" in self.gateway.connection_configs

        wifi_config = self.gateway.connection_configs["wifi"]
        assert wifi_config["max_response_size"] == 1024 * 1024
        assert wifi_config["compression_level"] == 6
        assert wifi_config["include_optional_data"] is True

        slow_config = self.gateway.connection_configs["slow"]
        assert slow_config["max_response_size"] == 128 * 1024
        assert slow_config["compression_level"] == 9
        assert slow_config["include_optional_data"] is False

    def test_parse_device_info_android(self):
        """Test parsing Android device info."""
        user_agent = "ConectaPRO-Android/2.1.0 (Build 150)"
        headers = {
            "x-connection-type": "4g",
            "x-battery-level": "75",
            "x-os-version": "13.0",
        }

        device = self.gateway._parse_device_info(user_agent, headers)

        assert device.platform == "android"
        assert device.connection_type == "4g"
        assert device.battery_level == "75"
        assert device.device_type == "mobile"
        assert device.is_low_bandwidth is False
        assert device.is_low_battery is False

    def test_parse_device_info_ios(self):
        """Test parsing iOS device info."""
        user_agent = "ConectaPRO-iOS/2.0.5"
        headers = {
            "x-connection-type": "wifi",
            "x-battery-level": "normal",
        }

        device = self.gateway._parse_device_info(user_agent, headers)

        assert device.platform == "ios"
        assert device.connection_type == "wifi"
        assert device.is_low_bandwidth is False

    def test_parse_device_info_low_bandwidth(self):
        """Test low bandwidth detection."""
        user_agent = "Mozilla/5.0 Mobile"
        headers = {
            "x-connection-type": "3g",
            "x-battery-level": "low",
        }

        device = self.gateway._parse_device_info(user_agent, headers)

        assert device.connection_type == "3g"
        assert device.is_low_bandwidth is True
        assert device.is_low_battery is True

    def test_filter_essential_fields(self):
        """Test filtering non-essential fields."""
        data = {
            "id": "123",
            "name": "Test",
            "metadata": {"extra": "info"},
            "debug": {"logs": []},
            "status": "active",
        }

        filtered = self.gateway._filter_essential_fields(data)

        assert "id" in filtered
        assert "name" in filtered
        assert "status" in filtered
        assert "metadata" not in filtered
        assert "debug" not in filtered

    def test_reduce_data_with_optional_enabled(self):
        """Test data reduction with optional data enabled."""
        config = {"include_optional_data": True}
        data = {"id": "1", "metadata": {"test": "value"}}

        result = self.gateway._reduce_data(data, config)

        assert result == data  # No reduction

    def test_reduce_data_with_optional_disabled(self):
        """Test data reduction with optional data disabled."""
        config = {"include_optional_data": False}
        data = {"id": "1", "name": "Test", "metadata": {"test": "value"}}

        result = self.gateway._reduce_data(data, config)

        assert "id" in result
        assert "name" in result
        assert "metadata" not in result

    def test_should_use_lightweight_response_3g(self):
        """Test lightweight response for 3G."""
        device = DeviceInfo(
            device_type="mobile",
            platform="android",
            os_version="13",
            app_version="2.0",
            connection_type="3g",
            battery_level="normal",
            is_low_bandwidth=True,
            is_low_battery=False,
        )

        assert self.gateway.should_use_lightweight_response(device) is True

    def test_should_use_lightweight_response_wifi(self):
        """Test full response for WiFi."""
        device = DeviceInfo(
            device_type="mobile",
            platform="ios",
            os_version="17",
            app_version="2.1",
            connection_type="wifi",
            battery_level="normal",
            is_low_bandwidth=False,
            is_low_battery=False,
        )

        assert self.gateway.should_use_lightweight_response(device) is False

    @pytest.mark.asyncio
    async def test_optimize_response_with_compression(self):
        """Test response optimization with compression."""
        # Large data that benefits from compression
        data = {"items": [{"id": i, "name": f"Item {i}" * 10} for i in range(50)]}

        device = DeviceInfo(
            device_type="mobile",
            platform="android",
            os_version="13",
            app_version="2.0",
            connection_type="wifi",
            battery_level="normal",
            is_low_bandwidth=False,
            is_low_battery=False,
        )

        result = await self.gateway.optimize_response(
            data=data,
            device_info=device,
            accept_encoding="gzip, deflate",
        )

        assert isinstance(result, ProcessingResult)
        assert result.compressed is True
        assert result.final_size < result.original_size

    @pytest.mark.asyncio
    async def test_optimize_response_without_compression(self):
        """Test response optimization without compression (small data)."""
        data = {"id": "1", "name": "Test"}

        device = DeviceInfo(
            device_type="mobile",
            platform="ios",
            os_version="17",
            app_version="2.0",
            connection_type="wifi",
            battery_level="normal",
            is_low_bandwidth=False,
            is_low_battery=False,
        )

        result = await self.gateway.optimize_response(
            data=data,
            device_info=device,
            accept_encoding="gzip",
        )

        assert result.compressed is False  # Too small to compress

    @pytest.mark.asyncio
    async def test_process_low_bandwidth(self):
        """Test processing for low bandwidth."""
        data = {
            "id": "1",
            "name": "Test",
            "description": "Long description",
            "extra": "Not needed",
        }
        essential_fields = ["id", "name"]

        result = await self.gateway.process_low_bandwidth(data, essential_fields)

        assert "id" in result
        assert "name" in result
        assert "description" not in result
        assert "extra" not in result

    @pytest.mark.asyncio
    async def test_process_battery_saving(self):
        """Test battery saving mode processing."""
        data = {
            "id": "1",
            "title": "Test",
            "images": ["img1.jpg", "img2.jpg"],
            "videos": ["video.mp4"],
        }

        result = await self.gateway.process_battery_saving(data)

        assert "id" in result
        assert "title" in result
        assert "images" not in result
        assert "videos" not in result


class TestDeviceDetector:
    """Tests for DeviceDetector class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.detector = DeviceDetector()

    @pytest.mark.asyncio
    async def test_detect_android_native_app(self):
        """Test detecting Android native app."""
        request = MagicMock()
        request.headers = {
            "user-agent": "ConectaPRO-Android/2.1.0 (Build 150)",
            "x-device-id": "device123",
            "x-connection-type": "4g",
            "x-battery-level": "80",
            "x-os-version": "13.0",
            "accept": "application/json",
            "accept-encoding": "gzip, br",
        }

        device = await self.detector.detect(request)

        assert device.is_native_app is True
        assert device.platform == "android"
        assert device.app_name == "ConectaPRO"
        assert device.app_version == "2.1.0"
        # app_build not implemented in detector
        assert device.connection_type == "4g"

    @pytest.mark.asyncio
    async def test_detect_ios_native_app(self):
        """Test detecting iOS native app."""
        request = MagicMock()
        request.headers = {
            "user-agent": "ConectaPRO-iOS/2.0.5",
            "x-device-id": "ios_device",
            "x-connection-type": "wifi",
        }

        device = await self.detector.detect(request)

        assert device.is_native_app is True
        assert device.platform == "ios"

    @pytest.mark.asyncio
    async def test_detect_mobile_web(self):
        """Test detecting mobile web browser."""
        request = MagicMock()
        request.headers = {
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0) AppleWebKit/605.1.15",
            "x-connection-type": "unknown",
        }

        device = await self.detector.detect(request)

        assert device.is_native_app is False
        assert device.is_mobile is True
        assert device.device_type == "mobile"

    @pytest.mark.asyncio
    async def test_detect_tablet(self):
        """Test detecting tablet."""
        request = MagicMock()
        request.headers = {
            "user-agent": "Mozilla/5.0 (iPad; CPU OS 17_0) AppleWebKit/605.1.15",
        }

        device = await self.detector.detect(request)

        assert device.is_tablet is True
        assert device.device_type == "tablet"

    @pytest.mark.asyncio
    async def test_detect_bot(self):
        """Test detecting bot."""
        request = MagicMock()
        request.headers = {
            "user-agent": "Googlebot/2.1",
        }

        device = await self.detector.detect(request)

        assert device.is_bot is True

    def test_is_low_end_device(self):
        """Test low-end device detection."""
        device = DetectedDevice(
            connection_type="slow",
        )

        assert self.detector.is_low_end_device(device) is True

    def test_is_low_end_device_low_memory(self):
        """Test low-end device by memory."""
        device = DetectedDevice(
            connection_type="wifi",
            capabilities=DeviceCapabilities(max_memory_mb=1024),
        )

        assert self.detector.is_low_end_device(device) is True

    def test_get_recommended_image_quality(self):
        """Test image quality recommendations."""
        device_wifi = DetectedDevice(connection_type="wifi")
        device_slow = DetectedDevice(connection_type="slow")

        assert self.detector.get_recommended_image_quality(device_wifi) == 90
        assert self.detector.get_recommended_image_quality(device_slow) == 40

    def test_get_recommended_page_size(self):
        """Test page size recommendations."""
        device_wifi = DetectedDevice(connection_type="wifi")
        device_3g = DetectedDevice(connection_type="3g")

        assert self.detector.get_recommended_page_size(device_wifi) == 50
        assert self.detector.get_recommended_page_size(device_3g) == 20


class TestCompression:
    """Tests for compression utilities."""

    @pytest.mark.asyncio
    async def test_compress_data_above_threshold(self):
        """Test compression of data above threshold."""
        data = b"x" * 2000  # 2KB of data

        compressed, was_compressed = await compress_data(data, minimum_size=1024)

        assert was_compressed is True
        assert len(compressed) < len(data)

    @pytest.mark.asyncio
    async def test_compress_data_below_threshold(self):
        """Test no compression for small data."""
        data = b"small data"

        result, was_compressed = await compress_data(data, minimum_size=1024)

        assert was_compressed is False
        assert result == data

    @pytest.mark.asyncio
    async def test_decompress_data(self):
        """Test decompression."""
        original = b"Test data for compression" * 100
        compressed, _ = await compress_data(original, minimum_size=100)

        decompressed = await decompress_data(compressed)

        assert decompressed == original

    @pytest.mark.asyncio
    async def test_decompress_invalid_data(self):
        """Test decompression of invalid data returns original."""
        data = b"not gzip data"

        result = await decompress_data(data)

        assert result == data  # Returns original on error
