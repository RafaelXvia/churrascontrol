"""
Backend — ChurrasControl
Núcleo de persistência, regras de negócio, inteligência artificial e integração.
"""
from backend.database import data_manager
from backend.ai import ontologia, assistente_ia

__all__ = ["data_manager", "ontologia", "assistente_ia"]
