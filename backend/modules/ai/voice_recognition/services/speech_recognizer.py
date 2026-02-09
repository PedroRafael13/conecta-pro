"""
Speech Recognizer Service - Sprint 52.

Service for speech-to-text transcription.
"""

import hashlib
import re
import time
from typing import Any


class SpeechRecognizer:
    """Service for speech recognition and transcription."""

    # Supported providers and their configs
    PROVIDERS = {
        "whisper": {"name": "OpenAI Whisper", "languages": ["pt-BR", "en-US", "es-ES"]},
        "google_speech": {"name": "Google Speech-to-Text", "languages": ["pt-BR", "en-US"]},
        "aws_transcribe": {"name": "AWS Transcribe", "languages": ["pt-BR", "en-US"]},
        "azure_speech": {"name": "Azure Speech", "languages": ["pt-BR", "en-US"]},
        "deepgram": {"name": "Deepgram", "languages": ["pt-BR", "en-US"]},
        "assemblyai": {"name": "AssemblyAI", "languages": ["en-US"]},
        "vosk": {"name": "Vosk (Local)", "languages": ["pt-BR", "en-US"]},
        "local": {"name": "Local Model", "languages": ["pt-BR"]},
    }

    # Portuguese stopwords for analysis
    STOPWORDS_PT = {
        "a",
        "o",
        "e",
        "de",
        "da",
        "do",
        "em",
        "um",
        "uma",
        "para",
        "com",
        "que",
        "por",
        "na",
        "no",
        "se",
        "os",
        "as",
        "dos",
        "das",
        "ao",
        "mais",
        "muito",
        "foi",
        "ser",
        "tem",
        "seu",
        "sua",
        "ou",
        "quando",
        "isso",
        "este",
        "esta",
        "esse",
        "essa",
        "ele",
        "ela",
        "nos",
        "me",
    }

    def __init__(self, default_provider: str = "whisper"):
        """Initialize speech recognizer."""
        self.default_provider = default_provider
        self.min_confidence = 0.6

    def transcribe(
        self,
        audio_data: bytes,
        language: str = "pt-BR",
        provider: str | None = None,
        enable_speaker_labels: bool = True,
        enable_punctuation: bool = True,
        options: dict | None = None,
    ) -> dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes
            language: Language code
            provider: Transcription provider
            enable_speaker_labels: Enable speaker diarization
            enable_punctuation: Add punctuation
            options: Additional options

        Returns:
            Transcription result
        """
        start_time = time.time()
        provider = provider or self.default_provider
        options = options or {}

        # Simulate transcription (in production, call actual provider)
        result = self._simulate_transcription(audio_data, language, enable_speaker_labels, enable_punctuation)

        processing_time_ms = int((time.time() - start_time) * 1000)

        return {
            "status": "completed",
            "provider": provider,
            "text": result["text"],
            "text_formatted": result["text_formatted"],
            "words": result["words"],
            "segments": result["segments"],
            "confidence_score": result["confidence"],
            "confidence_min": result.get("confidence_min", result["confidence"] - 0.1),
            "confidence_max": result.get("confidence_max", result["confidence"]),
            "language": language,
            "detected_language": result.get("detected_language", language),
            "language_confidence": result.get("language_confidence", 0.95),
            "speaker_count": result.get("speaker_count", 1),
            "speakers": result.get("speakers", []),
            "duration_seconds": result.get("duration_seconds", 0),
            "word_count": len(result["words"]),
            "processing_time_ms": processing_time_ms,
            "model_version": "1.0.0",
        }

    def _simulate_transcription(
        self,
        audio_data: bytes,
        language: str,
        enable_speaker_labels: bool,
        enable_punctuation: bool,
    ) -> dict[str, Any]:
        """Simulate transcription for testing."""
        # Generate deterministic "transcription" based on audio hash
        audio_hash = hashlib.sha256(audio_data).hexdigest()[:8]

        # Sample transcriptions based on hash
        sample_texts = [
            "Olá, bom dia. Como posso ajudá-lo hoje?",
            "Gostaria de fazer uma reclamação sobre o serviço.",
            "Preciso agendar uma visita técnica para amanhã.",
            "O equipamento parou de funcionar desde ontem.",
            "Qual o horário de funcionamento da portaria?",
        ]

        text_index = int(audio_hash, 16) % len(sample_texts)
        text = sample_texts[text_index]
        words = text.replace(".", "").replace(",", "").replace("?", "").split()

        # Generate word-level data
        word_data = []
        current_time = 0.0
        for _i, word in enumerate(words):
            duration = len(word) * 0.08 + 0.1
            word_data.append(
                {
                    "word": word,
                    "start": round(current_time, 2),
                    "end": round(current_time + duration, 2),
                    "confidence": 0.85 + (hash(word) % 15) / 100,
                }
            )
            current_time += duration + 0.05

        # Generate segments
        segments = []
        if enable_speaker_labels:
            segments = [
                {
                    "start": 0.0,
                    "end": current_time,
                    "text": text,
                    "speaker": "SPEAKER_00",
                    "confidence": 0.9,
                }
            ]

        return {
            "text": text.replace(".", "").replace(",", "").replace("?", ""),
            "text_formatted": text if enable_punctuation else text.replace(".", "").replace(",", "").replace("?", ""),
            "words": word_data,
            "segments": segments,
            "confidence": 0.92,
            "confidence_min": 0.85,
            "confidence_max": 0.98,
            "detected_language": language,
            "language_confidence": 0.97,
            "speaker_count": 1,
            "speakers": [{"id": "SPEAKER_00", "speaking_time": current_time}],
            "duration_seconds": current_time,
        }

    def detect_language(self, audio_data: bytes) -> dict[str, Any]:
        """Detect language from audio."""
        # Simulate language detection
        return {
            "detected_language": "pt-BR",
            "confidence": 0.95,
            "alternatives": [
                {"language": "pt-BR", "confidence": 0.95},
                {"language": "es-ES", "confidence": 0.03},
                {"language": "en-US", "confidence": 0.02},
            ],
        }

    def analyze_audio_quality(self, audio_data: bytes) -> dict[str, Any]:
        """Analyze audio quality for transcription."""
        # Simulate quality analysis
        return {
            "quality_score": 0.85,
            "noise_level": -35.0,  # dB
            "signal_to_noise": 25.0,  # dB
            "clipping_detected": False,
            "silence_ratio": 0.15,
            "issues": [],
            "recommendations": [],
            "suitable_for_transcription": True,
        }

    def extract_keywords(self, text: str, max_keywords: int = 10) -> list[dict[str, Any]]:
        """Extract keywords from text."""
        words = re.findall(r"\b\w+\b", text.lower())
        word_freq = {}

        for word in words:
            if word not in self.STOPWORDS_PT and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

        return [
            {"keyword": word, "frequency": freq, "score": freq / len(words)}
            for word, freq in sorted_words[:max_keywords]
        ]

    def split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Portuguese sentence splitting
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() for s in sentences if s.strip()]

    def calculate_speaking_rate(
        self,
        word_count: int,
        duration_seconds: float,
    ) -> dict[str, Any]:
        """Calculate speaking rate metrics."""
        if duration_seconds <= 0:
            return {"words_per_minute": 0, "rate_category": "unknown"}

        wpm = (word_count / duration_seconds) * 60

        if wpm < 100:
            category = "slow"
        elif wpm < 150:
            category = "normal"
        elif wpm < 180:
            category = "fast"
        else:
            category = "very_fast"

        return {
            "words_per_minute": round(wpm, 1),
            "rate_category": category,
            "words_per_second": round(word_count / duration_seconds, 2),
        }

    def identify_questions(self, segments: list[dict]) -> list[dict]:
        """Identify questions in transcription segments."""
        questions = []
        question_patterns = [
            r"\?$",
            r"^(qual|quais|quando|onde|como|por que|porque|quem|o que|quanto|quantos)\b",
            r"\b(pode|poderia|consegue|seria possível)\b.*\?",
        ]

        for segment in segments:
            text = segment.get("text", "").lower()
            is_question = False

            for pattern in question_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    is_question = True
                    break

            if is_question:
                questions.append(
                    {
                        "text": segment.get("text"),
                        "start": segment.get("start"),
                        "end": segment.get("end"),
                        "speaker": segment.get("speaker"),
                    }
                )

        return questions

    def get_provider_info(self, provider: str) -> dict | None:
        """Get provider information."""
        return self.PROVIDERS.get(provider)

    def list_providers(self) -> list[dict]:
        """List available transcription providers."""
        return [{"code": code, **info} for code, info in self.PROVIDERS.items()]
