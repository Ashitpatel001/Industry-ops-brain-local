# Ops Brain Local

**Ops Brain Local** is an on-device, fully offline AI assistant and agent platform designed for industrial knowledge intelligence. It is optimized to run locally on consumer hardware (e.g., an 8GB Intel laptop) without sending data to the cloud, protecting data privacy and ensuring performance in remote/offline plant environments.

## Features

- **Document Parser**: Ingests PDFs, images, Excel sheets, and HTML locally using **Docling**.
- **Local LLM**: Generates cited responses in seconds using **Qwen2.5-3B INT4 (OpenVINO IR)**.
- **Hybrid Retrieval**: Employs vector search (**ChromaDB**) alongside relational knowledge graphs (**NetworkX**) to enrich prompts with precise local plant context.
- **5 Local Agents**: Specialized agents for Ingestion, Copilot, Maintenance RCA, Compliance Audit, and Incident Lessons.
- **Streamlit Dashboard**: Multi-page UI for plant querying, document uploading, graph exploration, compliance checking, and risk score visualization.

## Technical Architecture

```
[UI: Streamlit] <---> [Backend: FastAPI] <---> [RAG Pipeline]
                                                  |
                     +----------------------------+----------------------------+
                     |                            |                            |
            [Docling + spaCy]               [ChromaDB]                    [NetworkX]
           (Document Parsing)            (Vector Retrieval)           (Knowledge Graph)
```

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Download Model & Quantize
```bash
python scripts/download_model.py
```

### Step 3: Run the Unified Launcher
```bash
python run.py --demo
```
This will seed the database with sample work orders and asset tags, start the FastAPI server, and launch the Streamlit frontend.

---
*Zero bytes sent to cloud. Built for OSDHack 2026.*