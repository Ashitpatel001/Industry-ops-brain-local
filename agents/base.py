"""
agents/base.py
==============
Abstract base class and structured response models for Ops Brain Local domain agents.
Provides tool registration, industrial entity extraction, direct SQLite database access,
and hybrid RAG routing capabilities.
"""

import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from core.config import get_config
from core.pipeline import RAGPipeline, QueryResponse
from ingestion.extractor import EntityExtractor

logger = logging.getLogger("BaseAgent")


@dataclass
class AgentResponse:
    """Structured response object returned by any industrial domain agent."""
    answer: str
    citations: List[Dict[str, Any]] = field(default_factory=list)
    confidence: str = "MEDIUM"  # HIGH, MEDIUM, LOW
    recommended_actions: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    agent_name: str = "BaseAgent"
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def actions(self) -> List[str]:
        """Backward compatibility alias for recommended_actions."""
        return self.recommended_actions

    def to_dict(self) -> Dict[str, Any]:
        """Convert response object to serializable dictionary for API and UI rendering."""
        return {
            "answer": self.answer,
            "citations": self.citations,
            "confidence": self.confidence,
            "recommended_actions": self.recommended_actions,
            "actions": self.recommended_actions,
            "gaps": self.gaps,
            "alerts": self.alerts,
            "agent_name": self.agent_name,
            "execution_time": round(self.execution_time, 3),
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all Ops Brain Local domain agents.
    Equipped with registered helper tools, NLP entity extraction, direct SQLite connection,
    and hybrid RAG routing.
    """

    def __init__(self, name: str, intent: str, pipeline: Optional[RAGPipeline] = None):
        self.name = name
        self.intent = intent
        self.pipeline = pipeline or RAGPipeline()
        self.extractor = EntityExtractor()
        self.tools: Dict[str, Callable[..., Any]] = {}

    def get_db_connection(self) -> sqlite3.Connection:
        """Get a fast, low-latency SQLite connection to data/metadata.db for structured queries."""
        try:
            db_path = get_config().db_path
            conn = sqlite3.connect(db_path, timeout=5.0)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"[{self.name}] Error connecting to SQLite DB: {e}")
            raise

    def register_tool(self, name: str, fn: Callable[..., Any]) -> None:
        """Register a domain-specific helper tool function."""
        self.tools[name] = fn
        logger.debug(f"[{self.name}] Registered tool: '{name}'")

    def call_tool(self, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a registered tool by name."""
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' is not registered on agent '{self.name}'.")
        return self.tools[name](*args, **kwargs)

    def route_rag(
        self,
        query: str,
        intent: Optional[str] = None,
        asset_tags: Optional[List[str]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> QueryResponse:
        """Route a query through the underlying hybrid RAG pipeline."""
        target_intent = intent or self.intent
        return self.pipeline.query(
            text=query,
            intent=target_intent,
            asset_tags=asset_tags,
            stream_callback=stream_callback,
        )

    @abstractmethod
    def run(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        """Execute the agent workflow on a user query."""
        pass
