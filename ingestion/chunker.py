"""
ingestion/chunker.py
====================
Production-grade smart document chunker for industrial RAG.
Implements domain-adaptive chunking strategies:
- WorkOrder: Split by section headers (FINDINGS, ROOT CAUSE, ACTION TAKEN).
- Procedure (SOP): Split by numbered procedural steps.
- Regulatory: Split by standard clause numbers (OISD 7.3.2, Factory Act Sec 36).
- Default: Sliding token window with context overlap.
"""

import logging
import re
from typing import Any, Dict, List, Optional
from core.config import get_config

logger = logging.getLogger("SmartChunker")


class SmartChunker:
    """
    Domain-aware chunking engine tailored for industrial maintenance and safety documentation.
    Guarantees rich metadata tagging and preserves semantic section headers.
    """

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        cfg = get_config()
        self.chunk_size = chunk_size or cfg.chunk_size
        self.chunk_overlap = chunk_overlap or cfg.chunk_overlap

    def chunk(
        self,
        text: str,
        doc_type: str = "Default",
        doc_id: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Split document text into semantic chunks based on doc_type.

        Args:
            text (str): Raw or markdown document text.
            doc_type (str): Document category ('WorkOrder', 'Procedure', 'Regulatory', 'Default').
            doc_id (str): Unique document identifier for chunk tagging.
            metadata (dict): Base metadata to merge into every chunk.

        Returns:
            List of chunk dictionaries with keys: chunk_id, chunk_index, text, section_header, tokens, doc_type, metadata.
        """
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        dtype_lower = doc_type.lower().replace("_", "")
        base_meta = (metadata or {}).copy()

        logger.debug(f"Chunking document '{doc_id}' with strategy='{doc_type}'...")

        if dtype_lower in ["workorder", "wo", "inspectionreport", "inspection"]:
            raw_chunks = self._chunk_by_sections(clean_text)
        elif dtype_lower in ["procedure", "sop", "manual", "instruction"]:
            raw_chunks = self._chunk_by_steps(clean_text)
        elif dtype_lower in ["regulatory", "regulation", "standard", "code"]:
            raw_chunks = self._chunk_by_clauses(clean_text)
        else:
            raw_chunks = self._chunk_sliding_window(clean_text, section_header="General Content")

        # Post-process: ensure chunks are within target size limits and merge overly small chunks
        refined_chunks = self._refine_chunks(raw_chunks)

        # Format final output dictionaries
        final_chunks = []
        for idx, (header, chunk_text) in enumerate(refined_chunks):
            tokens = len(chunk_text.split())
            cid = f"{doc_id}_CHUNK_{idx+1}" if doc_id else f"CHUNK_{idx+1}"
            
            chunk_meta = {
                **base_meta,
                "section_header": header,
                "doc_type": doc_type,
                "chunk_index": idx,
                "tokens": tokens,
            }

            final_chunks.append({
                "chunk_id": cid,
                "chunk_index": idx,
                "text": chunk_text,
                "section_header": header,
                "tokens": tokens,
                "doc_type": doc_type,
                "metadata": chunk_meta,
            })

        logger.info(f"Generated {len(final_chunks)} chunks for doc_id='{doc_id}' ({doc_type}).")
        return final_chunks

    def _chunk_by_sections(self, text: str) -> List[tuple[str, str]]:
        """Split WorkOrders by industrial section headers."""
        pattern = r"(?:\n|^)(?=#+\s+|SECTION\s+|DESCRIPTION:|FINDINGS:|ACTION\s+TAKEN:|ROOT\s+CAUSE:|FAILURE\s+MODE:|RECOMMENDATION:|SUMMARY:)"
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        chunks = []
        current_header = "Work Order Overview"
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Extract header if present
            header_match = re.match(r"^(#+\s+[^\n]+|[A-Z\s]+:|[A-Z\s]+(?=\n))", part)
            if header_match:
                current_header = header_match.group(1).strip(" #:")
            chunks.append((current_header, part))
        return chunks if chunks else [("Work Order Overview", text)]

    def _chunk_by_steps(self, text: str) -> List[tuple[str, str]]:
        """Split Procedures (SOPs) by numbered procedural steps."""
        pattern = r"(?:\n|^)(?=\d+\.\s+|Step\s+\d+|[A-Z]\.\s+|\d+\.\d+\s+)"
        parts = re.split(pattern, text, flags=re.IGNORECASE)

        chunks = []
        current_header = "Procedure Overview"
        for part in parts:
            part = part.strip()
            if not part:
                continue
            step_match = re.match(r"^(\d+\.\d+|\d+\.|Step\s+\d+|[A-Z]\.)\s+([^\n]+)", part, re.IGNORECASE)
            if step_match:
                current_header = f"Step {step_match.group(1).strip()} - {step_match.group(2)[:30]}..."
            chunks.append((current_header, part))
        return chunks if chunks else [("Procedure Overview", text)]

    def _chunk_by_clauses(self, text: str) -> List[tuple[str, str]]:
        """Split Regulatory documents by clause and section numbers."""
        pattern = r"(?:\n|^)(?=\d+\.\d+(?:\.\d+)?\s+|Clause\s+\d+|Rule\s+\d+|Section\s+\d+|Article\s+\d+)"
        parts = re.split(pattern, text, flags=re.IGNORECASE)

        chunks = []
        current_header = "Regulatory Overview"
        for part in parts:
            part = part.strip()
            if not part:
                continue
            clause_match = re.match(r"^(\d+\.\d+(?:\.\d+)?|Clause\s+\d+|Rule\s+\d+|Section\s+\d+)\s+([^\n]+)", part, re.IGNORECASE)
            if clause_match:
                current_header = f"Clause {clause_match.group(1).strip()}: {clause_match.group(2)[:35]}..."
            chunks.append((current_header, part))
        return chunks if chunks else [("Regulatory Overview", text)]

    def _chunk_sliding_window(self, text: str, section_header: str = "General") -> List[tuple[str, str]]:
        """Fallback sliding token window chunker with overlap."""
        words = text.split()
        if len(words) <= self.chunk_size:
            return [(section_header, text)]

        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        for i in range(0, len(words), step):
            window = words[i : i + self.chunk_size]
            chunk_str = " ".join(window)
            chunks.append((section_header, chunk_str))
            if i + self.chunk_size >= len(words):
                break
        return chunks

    def _refine_chunks(self, raw_chunks: List[tuple[str, str]]) -> List[tuple[str, str]]:
        """Merge undersized chunks (< 20 words) and split oversized chunks."""
        refined = []
        buffer_header = ""
        buffer_text = ""

        for header, text in raw_chunks:
            words = text.split()
            
            # If chunk is too large, split it with sliding window
            if len(words) > int(self.chunk_size * 1.5):
                if buffer_text:
                    refined.append((buffer_header, buffer_text.strip()))
                    buffer_text = ""
                sub_chunks = self._chunk_sliding_window(text, section_header=header)
                refined.extend(sub_chunks)
                continue

            # If chunk is too small (< 25 words), accumulate in buffer
            if len(words) < 25 and refined:
                if not buffer_text:
                    buffer_header = header
                buffer_text += "\n\n" + text
            else:
                if buffer_text:
                    refined.append((buffer_header, buffer_text.strip()))
                    buffer_text = ""
                refined.append((header, text))

        if buffer_text:
            if refined:
                last_header, last_text = refined.pop()
                refined.append((last_header, last_text + "\n\n" + buffer_text.strip()))
            else:
                refined.append((buffer_header or "Overview", buffer_text.strip()))

        return refined
