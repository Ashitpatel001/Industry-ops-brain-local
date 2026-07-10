"""
core/pipeline.py
================
RAG (Retrieval-Augmented Generation) orchestration pipeline.
Combines vector similarity search (ChromaDB), knowledge graph neighborhood traversal (NetworkX),
and structured prompt formatting for local LLM inference.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
from core.config import get_config
from core.embedder import LocalEmbedder
from core.graph import KnowledgeGraph
from core.model import LocalLLM
from core.vector_store import VectorStore

logger = logging.getLogger("RAGPipeline")


@dataclass
class QueryResponse:
    """Structured response object returned by the RAG pipeline."""
    answer: str
    citations: List[Dict[str, Any]]
    confidence: str  # HIGH, MEDIUM, LOW
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "answer": self.answer,
            "citations": self.citations,
            "confidence": self.confidence,
            "recommended_actions": self.recommended_actions,
            "metadata": self.metadata,
        }


class RAGPipeline:
    """
    Hybrid RAG Engine orchestrating vector retrieval, graph traversal,
    and LLM generation with strict citation tracking and confidence estimation.
    """

    def __init__(
        self,
        llm: Optional[LocalLLM] = None,
        embedder: Optional[LocalEmbedder] = None,
        vector_store: Optional[VectorStore] = None,
        graph: Optional[KnowledgeGraph] = None,
    ):
        self.llm = llm if llm is not None else LocalLLM()
        self.embedder = embedder if embedder is not None else LocalEmbedder()
        self.vector_store = vector_store if vector_store is not None else VectorStore()
        self.graph = graph if graph is not None else KnowledgeGraph()

    def query(
        self,
        text: str,
        intent: str = "general",
        asset_tags: Optional[List[str]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> QueryResponse:
        """
        Execute an end-to-end RAG query:
        1. Embed query and search ChromaDB for top-k vector chunks.
        2. Query NetworkX knowledge graph for asset relationships & failure modes.
        3. Construct structured prompt with citations.
        4. Generate answer via local LLM and parse structured sections.
        """
        cfg = get_config()
        asset_tags = asset_tags or []

        # Track 1: Vector Retrieval
        chunks = []
        if self.embedder and self.vector_store:
            try:
                query_vec = self.embedder.embed_query(text)
                chunks = self.vector_store.search(query_vec, n_results=cfg.top_k)
            except Exception as e:
                logger.error(f"Vector search failed during query: {e}")

        # Track 2: Knowledge Graph Traversal
        graph_contexts = []
        if self.graph and asset_tags:
            for tag in asset_tags:
                nb = self.graph.get_neighborhood(tag, depth=2)
                if nb.get("found"):
                    graph_contexts.append(nb)

        # Track 3: Prompt Construction
        prompt, citations = self._build_prompt(text, chunks, graph_contexts, intent)

        # Track 4: LLM Inference
        raw_output = ""
        if self.llm:
            try:
                raw_output = self.llm.generate(
                    prompt,
                    max_new_tokens=cfg.max_new_tokens,
                    temperature=cfg.temperature,
                    stream_callback=stream_callback,
                )
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                raw_output = f"ANSWER: Error generating response: {e}\nCONFIDENCE: LOW"
        else:
            raw_output = "ANSWER: Local LLM engine is not initialized.\nCONFIDENCE: LOW"

        # Track 5: Parse Structured Output & Estimate Confidence
        parsed = self._parse_response(raw_output, citations)

        # Attach execution metadata
        parsed.metadata = {
            "backend": self.llm.backend_label if self.llm else "None",
            "intent": intent,
            "chunks_retrieved": len(chunks),
            "graph_nodes_referenced": len(graph_contexts),
            "asset_tags": asset_tags,
        }

        return parsed

    def _build_prompt(
        self,
        query: str,
        chunks: List[Dict[str, Any]],
        graph_contexts: List[Dict[str, Any]],
        intent: str,
    ) -> tuple[str, List[Dict[str, Any]]]:
        """Format retrieved context into Qwen instruct prompt template."""
        context_blocks = []
        citations = []

        # Add vector chunks
        for i, chunk in enumerate(chunks, 1):
            doc_id = chunk.get("doc_id", f"DOC-{i}")
            meta = chunk.get("metadata", {})
            title = meta.get("title") or meta.get("file_name") or doc_id
            score = chunk.get("score", 0.0)
            text_snippet = chunk.get("text", "").strip()

            citation_item = {
                "id": f"[{i}]",
                "doc_id": doc_id,
                "title": title,
                "score": score,
                "snippet": text_snippet[:150] + "..." if len(text_snippet) > 150 else text_snippet,
            }
            citations.append(citation_item)
            context_blocks.append(f"Source [{i}] ({title} - Relevance: {score}):\n{text_snippet}\n")

        # Add graph relationships
        if graph_contexts:
            graph_summary = []
            for gc in graph_contexts:
                tdata = gc.get("target_data", {})
                tlabel = tdata.get("label", gc.get("node_id"))
                graph_summary.append(f"Asset Graph Data for '{tlabel}': {tdata}")
                for rel_type, neighbors in gc.get("neighbors", {}).items():
                    names = [n.get("label", n.get("id")) for n in neighbors[:5]]
                    graph_summary.append(f"  - Related {rel_type.replace('_', ' ').title()}: {', '.join(names)}")
            
            context_blocks.append("Knowledge Graph Relationships:\n" + "\n".join(graph_summary) + "\n")

        context_str = "\n".join(context_blocks) if context_blocks else "No local document context found."

        prompt = (
            f"<|user|>\n"
            f"You are Ops Brain Local, an expert AI Industrial Safety, Maintenance, and Reliability Co-Pilot.\n"
            f"You serve plant operators, reliability engineers, and field technicians in heavy industry (refineries, manufacturing, energy plants).\n\n"
            f"GUIDELINES FOR YOUR RESPONSE:\n"
            f"1. CONVERSATIONAL & NATURAL: If the user's input is a greeting (like 'Hi', 'Hello', 'Good morning', 'Hii') or general chat, respond naturally and politely as a helpful human colleague. Introduce your capabilities (e.g., P&ID diagnostics, maintenance work orders, OISD/Factory Act compliance, 5-Why RCA analysis) without forcing unnecessary checklists or bullet points. Set RECOMMENDED ACTIONS to 'None'.\n"
            f"2. INDUSTRIAL AUTHORITATIVE DEPTH: For technical, operational, or safety queries, provide deep, authoritative, professional guidance based on the retrieved local documents and knowledge graph context below. Always cite source documents as [1], [2], etc., when referencing facts or procedures.\n"
            f"3. CONCISE ACTIONABILITY: If recommending operational steps or inspections, provide at most 3 to 4 high-impact, actionable field steps. Never generate long, repetitive, or generic lists.\n\n"
            f"=== RETRIEVED LOCAL CONTEXT ===\n{context_str}\n=== END CONTEXT ===\n\n"
            f"USER QUESTION: {query}\n\n"
            f"Respond strictly in the following structured format:\n"
            f"ANSWER: [Your natural conversational answer or detailed technical analysis citing sources]\n"
            f"CITATIONS: [List the source IDs and titles used, or 'None' if general conversation]\n"
            f"CONFIDENCE: [HIGH, MEDIUM, or LOW based on document agreement and completeness]\n"
            f"RECOMMENDED ACTIONS: [At most 3-4 concise, actionable field steps if applicable, or 'None' if general chat]\n"
            f"<|end|>\n"
            f"<|assistant|>\n"
        )
        return prompt, citations

    def _parse_response(self, raw_output: str, citations: List[Dict[str, Any]]) -> QueryResponse:
        """Parse structured sections (ANSWER, CITATIONS, CONFIDENCE, RECOMMENDED ACTIONS) from LLM output."""
        answer = raw_output
        confidence = "MEDIUM"
        actions = []

        # Extract ANSWER
        ans_match = re.search(r"ANSWER:\s*(.*?)(?=\n[A-Z\s]+:|$)", raw_output, re.DOTALL | re.IGNORECASE)
        if ans_match:
            answer = ans_match.group(1).strip()
        else:
            # If model didn't use strict formatting, take text up to CONFIDENCE or CITATIONS
            clean_text = re.sub(r"(CITATIONS|CONFIDENCE|RECOMMENDED ACTIONS):.*", "", raw_output, flags=re.DOTALL | re.IGNORECASE)
            answer = clean_text.strip() or raw_output.strip()

        # Extract CONFIDENCE
        conf_match = re.search(r"CONFIDENCE:\s*(HIGH|MEDIUM|LOW)", raw_output, re.IGNORECASE)
        if conf_match:
            confidence = conf_match.group(1).upper()
        elif not citations:
            confidence = "LOW"
        elif len(citations) >= 2 and citations[0]["score"] > 0.75:
            confidence = "HIGH"

        # Extract RECOMMENDED ACTIONS
        act_match = re.search(r"RECOMMENDED ACTIONS:\s*(.*?)(?=\n[A-Z\s]+:|$)", raw_output, re.DOTALL | re.IGNORECASE)
        if act_match:
            raw_actions = act_match.group(1).strip().split("\n")
            for line in raw_actions:
                cleaned = re.sub(r"^[\-\*\•\d\.\)]+\s*", "", line).strip()
                if cleaned and len(cleaned) > 3 and "none" not in cleaned.lower() and "general chat" not in cleaned.lower():
                    if cleaned not in actions:  # Deduplicate!
                        actions.append(cleaned)
            # Strictly cap at 4 actions to prevent verbose clutter!
            actions = actions[:4]
        
        # Check if query or answer is a greeting or general chat
        is_greeting = any(w in answer.lower()[:35] for w in ["hello", "hi ", "hi!", "hii", "welcome", "assist you", "how can i help", "good morning", "good evening", "ops brain"]) or len(answer.strip()) < 50
        if not actions and confidence == "LOW" and not is_greeting:
            actions.append("Verify field conditions manually and consult equipment OEM manual.")

        return QueryResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            recommended_actions=actions,
        )
