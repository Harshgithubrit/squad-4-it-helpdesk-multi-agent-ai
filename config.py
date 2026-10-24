"""Centralized environment-based configuration."""
from dataclasses import dataclass
import os
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Settings:
    llm_provider: str = os.getenv("LLM_PROVIDER", "mock").lower()
    llm_model: str = os.getenv("LLM_MODEL", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0"))
    data_path: str = os.getenv("GOLDEN_DATA_PATH", "data/golden_it_support_tickets.csv")
    session_path: str = os.getenv("SESSION_CAPTURE_PATH", "data/session_captures.jsonl")
    otel_enabled: bool = os.getenv("OTEL_ENABLED", "false").lower() == "true"
    otel_exporter: str = os.getenv("OTEL_EXPORTER", "console").lower()
    otel_endpoint: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")

def get_settings() -> Settings:
    return Settings()
