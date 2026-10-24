"""Application dependency-injection providers used by FastAPI routes."""
from functools import lru_cache
from config import get_settings
from graph import build_graph

@lru_cache(maxsize=1)
def get_settings_dependency():
    return get_settings()

@lru_cache(maxsize=1)
def get_helpdesk_graph():
    return build_graph()
