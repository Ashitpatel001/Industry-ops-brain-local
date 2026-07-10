"""
agents/copilot.py
=================
General industrial plant Q&A co-pilot agent.
Handles general inquiries, equipment status checks, and safety advice
by combining vector search and knowledge graph neighborhood traversal.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional
from agents.base import BaseAgent, AgentResponse

logger = logging.getLogger("CopilotAgent")


class CopilotAgent(BaseAgent):
    """
    General industrial plant Q&A co-pilot.
    Provides fast, accurate answers to day-to-day operations and safety questions.
    """

    def __init__(self, pipeline=None):
        super().__init__(name="CopilotAgent", intent="general", pipeline=pipeline)

    def run(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        start_time = time.time()
        ctx = context or {}

        # 1. Extract asset tags from query or context
        asset_tags = ctx.get("asset_tags", [])
        if not asset_tags:
            extracted = self.extractor.extract(query)
            asset_tags = extracted.get("asset_tags", [])

        logger.info(f"[{self.name}] Executing query: '{query[:50]}...' with tags: {asset_tags}")

        # 2. Route through hybrid RAG pipeline
        rag_res = self.route_rag(
            query=query,
            intent=self.intent,
            asset_tags=asset_tags,
            stream_callback=stream_callback,
        )

        # 3. Detect safety alerts or documentation gaps
        alerts = []
        gaps = []
        q_lower = query.lower()
        if any(w in q_lower for w in ["leak", "fire", "vibration", "smoke", "spill", "trip", "emergency"]):
            alerts.append("CRITICAL SAFETY ALERT: Ensure immediate personal safety and follow emergency shutdown procedures if active hazard is present.")
        
        if not rag_res.citations or rag_res.confidence == "LOW":
            gaps.append(f"No direct standard operating procedure (SOP) indexed for query regarding: {', '.join(asset_tags) if asset_tags else 'general query'}.")

        exec_time = time.time() - start_time
        return AgentResponse(
            answer=rag_res.answer,
            citations=rag_res.citations,
            confidence=rag_res.confidence,
            recommended_actions=rag_res.recommended_actions,
            gaps=gaps,
            alerts=alerts,
            agent_name=self.name,
            execution_time=exec_time,
            metadata={
                **rag_res.metadata,
                "asset_tags_detected": asset_tags,
                "agent_intent": self.intent,
            },
        )
