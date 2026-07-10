"""
ingestion/__init__.py
=====================
Production-grade document ingestion package for Ops Brain Local.
Exports document parsing, smart chunking, and industrial entity extraction modules.
"""

from ingestion.parser import DoclingParser
from ingestion.chunker import SmartChunker
from ingestion.extractor import EntityExtractor

__all__ = [
    "DoclingParser",
    "SmartChunker",
    "EntityExtractor",
]
