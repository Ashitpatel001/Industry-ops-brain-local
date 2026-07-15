"""
api/app.py
==========
Single production FastAPI application for Ops Brain Local.
Provides REST endpoints for ingestion, multi-agent RAG queries, knowledge graph traversal,
plant reliability/compliance metrics, and real-time WebSocket token streaming.

Run server:
    uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
"""

import asyncio
import json
import logging
import os
import shutil
import sys

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.config import get_config
from core.pipeline import RAGPipeline
from ingestion import DoclingParser, SmartChunker, EntityExtractor
from agents import CopilotAgent, MaintenanceAgent, ComplianceAgent, LessonsAgent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("APIBackend")


# --- Pydantic Validation Schemas ---
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query text")
    intent: Optional[str] = Field("general", description="Agent routing intent: general, maintenance, compliance, lessons_learned")
    asset_tags: Optional[List[str]] = Field(None, description="Optional list of equipment asset tags")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context dictionary")


class QueryResponseModel(BaseModel):
    answer: str
    citations: List[Dict[str, Any]]
    confidence: str
    recommended_actions: List[str]
    gaps: List[str]
    alerts: List[str]
    agent_name: str
    execution_time: float
    metadata: Dict[str, Any]


class IngestStatusResponse(BaseModel):
    doc_id: str
    status: str
    message: str
    chunks_indexed: int
    entities_extracted: int


class HealthResponse(BaseModel):
    model_config = {"protected_namespaces": ()}
    status: str
    model_loaded: bool
    backend: str
    ram_used_gb: float
    ram_total_gb: float
    cpu_percent: float
    uptime_seconds: float


# --- FastAPI App Initialization ---
app = FastAPI(
    title="Ops Brain Local API",
    description="100% Offline Industrial RAG & Multi-Agent AI Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Singletons
_pipeline: Optional[RAGPipeline] = None
import threading

_agents: Dict[str, Any] = {}
_ingest_status: Dict[str, Dict[str, Any]] = {}
_start_time = time.time()
_pipeline_lock = threading.Lock()
_agents_lock = threading.Lock()


def get_pipeline() -> RAGPipeline:
    """Lazy initialize and return the global RAGPipeline singleton thread-safely."""
    global _pipeline
    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                logger.info("Initializing RAGPipeline singleton...")
                _pipeline = RAGPipeline()
    return _pipeline


def get_agent(intent: str):
    """Retrieve the domain agent corresponding to the requested intent thread-safely."""
    global _agents
    if not _agents:
        with _agents_lock:
            if not _agents:
                pipe = get_pipeline()
                _agents = {
                    "general": CopilotAgent(pipeline=pipe),
                    "maintenance": MaintenanceAgent(pipeline=pipe),
                    "compliance": ComplianceAgent(pipeline=pipe),
                    "lessons_learned": LessonsAgent(pipeline=pipe),
                }
    return _agents.get(intent.lower(), _agents["general"])


def get_db_connection() -> sqlite3.Connection:
    """Get a fast SQLite connection to data/metadata.db."""
    db_path = get_config().db_path
    conn = sqlite3.connect(db_path, timeout=5.0)
    conn.row_factory = sqlite3.Row
    return conn


@app.on_event("startup")
def start_eager_warmup():
    """Eagerly initialize RAGPipeline and Domain Agents in a background thread upon server start."""
    def _warmup():
        try:
            logger.info("🔥 Starting background eager warmup of RAGPipeline and AI Models...")
            get_pipeline()
            get_agent("general")
            logger.info("✅ Eager warmup complete! AI Engine is ready for zero-latency queries.")
        except Exception as e:
            logger.error(f"❌ Error during eager warmup: {e}", exc_info=True)
            
    threading.Thread(target=_warmup, daemon=True).start()


# --- REST API Endpoints ---

@app.post("/api/v1/query", response_model=QueryResponseModel)
def execute_query(req: QueryRequest):
    """Execute a multi-agent industrial query and return structured analysis."""
    logger.info(f"Received query [{req.intent}]: {req.query[:60]}...")
    try:
        agent = get_agent(req.intent or "general")
        ctx = {"asset_tags": req.asset_tags or [], **(req.context or {})}
        res = agent.run(query=req.query, context=ctx)
        return res.to_dict()
    except Exception as e:
        logger.error(f"Error executing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ingest", response_model=IngestStatusResponse)
async def ingest_document(file: UploadFile = File(...), doc_type: str = "Procedure"):
    """Upload and ingest an industrial document (PDF, XLSX, DOCX, etc.) into vector store and graph."""
    doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
    cfg = get_config()
    upload_dir = Path(cfg.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / f"{doc_id}_{file.filename}"
    logger.info(f"Ingesting file: {file.filename} -> {file_path}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        _ingest_status[doc_id] = {
            "doc_id": doc_id,
            "status": "PROCESSING",
            "message": f"Parsing {file.filename}...",
            "chunks_indexed": 0,
            "entities_extracted": 0,
        }
        
        # 1. Parse document
        parser = DoclingParser()
        parsed = parser.parse(file_path)
        markdown_text = parsed.get("markdown", "")
        
        # 2. Chunk document
        chunker = SmartChunker()
        chunks = chunker.chunk(markdown_text, doc_type=doc_type, doc_id=doc_id)
        
        # 3. Add to Vector Store
        pipe = get_pipeline()
        if pipe.vector_store:
            pipe.vector_store.add_chunks(chunks, doc_id=doc_id)
            
        # 4. Extract Entities & Update Graph
        extractor = EntityExtractor()
        extracted = extractor.extract(markdown_text)
        total_ents = extracted.get("total_entities", 0)
        
        # 5. Persist document metadata in SQLite
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO documents (doc_id, title, file_path, doc_type, status, indexed_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (doc_id, file.filename, str(file_path), doc_type, "INDEXED", time.strftime("%Y-%m-%d %H:%M:%S"))
                )
                conn.commit()
        except Exception as db_e:
            logger.warning(f"Could not insert doc metadata into SQLite: {db_e}")
            
        _ingest_status[doc_id] = {
            "doc_id": doc_id,
            "status": "COMPLETED",
            "message": f"Successfully indexed {file.filename}",
            "chunks_indexed": len(chunks),
            "entities_extracted": total_ents,
        }
        return _ingest_status[doc_id]
        
    except Exception as e:
        logger.error(f"Ingestion failed for {file.filename}: {e}", exc_info=True)
        _ingest_status[doc_id] = {
            "doc_id": doc_id,
            "status": "ERROR",
            "message": str(e),
            "chunks_indexed": 0,
            "entities_extracted": 0,
        }
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ingest/status/{doc_id}", response_model=IngestStatusResponse)
def get_ingest_status(doc_id: str):
    """Check indexing progress of an uploaded document."""
    if doc_id in _ingest_status:
        return _ingest_status[doc_id]
    raise HTTPException(status_code=404, detail=f"Document ID '{doc_id}' not found in job status queue.")


@app.get("/api/v1/graph/{node_id}")
def get_graph_neighborhood(node_id: str, depth: int = 2):
    """Retrieve NetworkX knowledge graph neighborhood for visualization."""
    import networkx as nx
    pipe = get_pipeline()
    if not pipe.graph or not pipe.graph.G:
        return {"nodes": [], "edges": []}
        
    if node_id.lower() == "all":
        subgraph = pipe.graph.G
    else:
        if not pipe.graph.G.has_node(node_id):
            # Try case-insensitive lookup
            matched = [n for n in pipe.graph.G.nodes() if str(n).lower() == node_id.lower()]
            if not matched:
                return {"nodes": [], "edges": []}
            node_id = matched[0]
        subgraph = nx.ego_graph(pipe.graph.G, node_id, radius=depth, undirected=True)

    nodes = []
    edges = []
    for n, attrs in subgraph.nodes(data=True):
        nodes.append({"id": n, "label": str(attrs.get("label", n)), "type": attrs.get("type", "UNKNOWN"), **attrs})
    for u, v, attrs in subgraph.edges(data=True):
        edges.append({"source": u, "target": v, "relation": attrs.get("relation", "relates_to")})
    return {"nodes": nodes, "edges": edges}


@app.get("/api/v1/assets")
def get_assets_list():
    """Retrieve list of plant assets from SQLite with computed reliability risk scores."""
    try:
        m_agent = get_agent("maintenance")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT asset_tag, name, type, criticality, process_unit, mtbf_days, status, description FROM assets ORDER BY asset_tag")
            rows = cursor.fetchall()
            
            assets = []
            for row in rows:
                data = dict(row)
                # Augment with risk score
                risk = m_agent.calculate_risk_score(data["asset_tag"])
                data["risk_score"] = risk["risk_score"]
                data["risk_category"] = risk["risk_category"]
                assets.append(data)
            return {"assets": assets, "total_count": len(assets)}
    except Exception as e:
        logger.error(f"Error fetching assets list: {e}")
        return {"assets": [], "error": str(e)}


@app.get("/api/v1/compliance")
def get_compliance_dashboard():
    """Retrieve regulatory compliance gap report and audit evidence summaries."""
    try:
        c_agent = get_agent("compliance")
        gaps = c_agent.run_gap_analysis()
        ev_pkg = c_agent.generate_evidence_package("OISD-116")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT reg_id, standard, clause, title, requirement, category, status FROM regulations ORDER BY standard, clause")
            regs = [dict(r) for r in cursor.fetchall()]
            
        return {
            "gap_report": gaps,
            "evidence_package": ev_pkg,
            "regulations_indexed": regs,
            "total_gaps": len(gaps),
        }
    except Exception as e:
        logger.error(f"Error fetching compliance data: {e}")
        return {"gap_report": [], "error": str(e)}


@app.get("/api/v1/maintenance")
def get_maintenance_dashboard():
    """Retrieve open Work Orders, top risk assets, and overdue maintenance metrics."""
    try:
        m_agent = get_agent("maintenance")
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT wo_id, asset_tag, title, status, description, date_created FROM work_orders WHERE status = 'OPEN' ORDER BY date_created DESC")
            open_wos = [dict(r) for r in cursor.fetchall()]
            
            cursor.execute("SELECT asset_tag FROM assets")
            all_tags = [r["asset_tag"] for r in cursor.fetchall()]
            
        risks = [m_agent.calculate_risk_score(t) for t in all_tags]
        risks.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return {
            "open_work_orders": open_wos,
            "top_risk_assets": risks[:5],
            "total_open_wos": len(open_wos),
        }
    except Exception as e:
        logger.error(f"Error fetching maintenance data: {e}")
        return {"open_work_orders": [], "error": str(e)}


@app.get("/api/v1/lessons")
def get_lessons_dashboard():
    """Retrieve recurring failure patterns, historical incidents, and safety warnings."""
    try:
        l_agent = get_agent("lessons_learned")
        recurring = l_agent.get_recurring_patterns(min_count=1)
        incidents = l_agent.analyze_incident_patterns()
        warnings = l_agent.generate_safety_warnings()
        
        return {
            "recurring_patterns": recurring,
            "recent_incidents": incidents,
            "safety_warnings": warnings,
        }
    except Exception as e:
        logger.error(f"Error fetching lessons data: {e}")
        return {"recurring_patterns": [], "error": str(e)}


@app.get("/api/v1/health", response_model=HealthResponse)
def get_system_health():
    """Check system health, RAM/CPU usage, model loaded status, and hardware acceleration backend."""
    pipe = get_pipeline()
    mem = psutil.virtual_memory()
    
    model_loaded = False
    backend = "Not Loaded"
    if pipe.llm:
        model_loaded = pipe.llm.pipe is not None
        backend = pipe.llm.backend_label
        
    return HealthResponse(
        status="HEALTHY",
        model_loaded=model_loaded,
        backend=backend,
        ram_used_gb=round(mem.used / (1024**3), 2),
        ram_total_gb=round(mem.total / (1024**3), 2),
        cpu_percent=psutil.cpu_percent(interval=None),
        uptime_seconds=round(time.time() - _start_time, 1),
    )


# --- Real-Time WebSocket Token Streaming Endpoint ---

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    Real-time bidirectional WebSocket endpoint for streaming LLM tokens.
    Client sends JSON: {"query": "...", "intent": "general", "asset_tags": [...]}
    Server streams back: {"type": "token", "content": "..."} followed by {"type": "done", "response": {...}}
    """
    await websocket.accept()
    loop = asyncio.get_event_loop()
    logger.info("WebSocket chat client connected.")
    
    try:
        while True:
            data = await websocket.receive_json()
            query = data.get("query", "").strip()
            intent = data.get("intent", "general")
            asset_tags = data.get("asset_tags", [])
            
            if not query:
                await websocket.send_json({"type": "error", "message": "Empty query received."})
                continue

            await websocket.send_json({"type": "start", "intent": intent})
            agent = get_agent(intent)
            
            # Queue for thread-safe token streaming between sync LLM thread and async WebSocket
            token_queue = asyncio.Queue()
            
            def sync_stream_cb(token: str):
                loop.call_soon_threadsafe(token_queue.put_nowait, token)
                
            def run_agent_task():
                res = agent.run(query=query, context={"asset_tags": asset_tags}, stream_callback=sync_stream_cb)
                loop.call_soon_threadsafe(token_queue.put_nowait, None)  # EOF sentinel
                return res

            # Execute synchronous agent in executor thread pool
            future = loop.run_in_executor(None, run_agent_task)
            
            # Stream tokens to client as they are generated
            while True:
                token = await token_queue.get()
                if token is None:
                    break
                await websocket.send_json({"type": "token", "content": token})
            
            # Send final structured metadata and citations
            response = await future
            await websocket.send_json({"type": "done", "response": response.to_dict()})
            
    except WebSocketDisconnect:
        logger.info("WebSocket chat client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
