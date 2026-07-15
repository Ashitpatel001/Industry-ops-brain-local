# Ops Brain Local — Open-Source Attributions & Licensing (`ATTRIBUTION.md`)

**Document Version:** `4.0-FINAL`  
**License:** MIT License (`LICENSE`)  
**Scope:** Attribution of Pretrained Models, Datasets, Libraries, and Open-Source Frameworks

---

## 1. Pretrained AI Models & Weights

**Ops Brain Local** builds upon state-of-the-art open-source foundational models and neural network compression frameworks:

| Pretrained Model / Component | Original Creator / Maintainer | Open-Source License | Usage in Ops Brain Local |
| :--- | :--- | :--- | :--- |
| **`Qwen2.5-3B-Instruct`** | Alibaba Cloud (Qwen Team) | Apache 2.0 | Primary causal language model for technical reasoning and maintenance synthesis (`core/model.py`). |
| **`all-MiniLM-L6-v2`** | Sentence-Transformers / HuggingFace | Apache 2.0 | Primary 384-dimensional dense vector embedding model (`core/embedder.py`). |
| **`en_core_web_sm` (v3.7.5)** | Explosion AI (`spaCy` team) | MIT License | Small English NLP pipeline used for Named Entity Recognition (`NER`) asset tag extraction (`agents/extractor.py`). |
| **`beehive_v0.0.5_pt` & `tableformer`** | IBM Research (`Docling` / `ds4sd`) | MIT License | Optional deep-learning layout and table recognition models for complex scanned document OCR (`ingestion/parser.py`). |

---

## 2. Core Libraries, Frameworks & Infrastructure

We gratefully acknowledge the developers and maintainers of the following open-source libraries that make this air-gapped industrial RAG architecture possible:

### 2.1 Backend AI & Inference Runtime
- **Intel OpenVINO Runtime (`openvino`) & `optimum-intel`**: Licensed under **Apache 2.0**. Used for NNCF INT4 weight quantization and high-throughput local CPU/GPU hardware acceleration (`core/model.py`).
- **ChromaDB (`chromadb`)**: Licensed under **Apache 2.0**. Used as our high-speed, local in-process embedded vector database (`data/chroma/`).
- **NetworkX (`networkx`)**: Licensed under **3-Clause BSD License**. Used for building, storing, and traversing multi-hop relational knowledge graphs (`core/graph.py`).
- **Docling (`docling` & `docling-core`)**: Licensed under **MIT License**. IBM Research's document conversion pipeline for parsing PDF tables and layout markdown (`ingestion/parser.py`).
- **pypdf (`pypdf`)**: Licensed under **3-Clause BSD License**. Pure-Python PDF extraction engine leveraged as our lightning-fast, zero-download offline PDF fallback (`_parse_pdf_fallback`).
- **spaCy (`spacy`)**: Licensed under **MIT License**. Industrial-grade Natural Language Processing library used for entity extraction (`agents/extractor.py`).
- **Transformers & HuggingFace Hub (`transformers`, `huggingface_hub`)**: Licensed under **Apache 2.0**. Used for local model loading (`local_files_only=True`).

### 2.2 Backend Web & API Services
- **FastAPI (`fastapi`) & Starlette (`starlette`)**: Licensed under **MIT License**. High-performance asynchronous REST API and WebSocket orchestration (`api/app.py`).
- **Uvicorn (`uvicorn`)**: Licensed under **3-Clause BSD License**. Lightning-fast ASGI web server implementation.
- **Pydantic (`pydantic`)**: Licensed under **MIT License**. Data validation and settings management using Python type annotations (`api/models.py`).

### 2.3 Frontend Dashboard & Styling
- **Next.js 15 (`next`) & React 19 (`react`)**: Licensed under **MIT License**. Modern full-stack frontend application framework (`web/`).
- **Tailwind CSS (`tailwindcss`)**: Licensed under **MIT License**. Utility-first CSS framework for high-precision industrial UI design (`web/src/app/globals.css`).
- **Lucide Icons (`lucide-react`)**: Licensed under **ISC License**. Clean, professional vector icon toolkit used across all 5 operational studios.

---

## 3. Industrial Standards & Statutory Datasets

To ensure realistic, enterprise-grade validation and compliance cross-checking, our knowledge graph seeds and evaluation datasets draw upon established international engineering frameworks:

- **OISD-GDN-192:** *Oil Industry Safety Directorate (India)* safety practices for inspection and maintenance of equipment in petroleum refineries and installations.
- **Factory Act 1948:** Statutory occupational safety, health, and welfare standards for heavy manufacturing and chemical processing facilities.
- **API Standard 610 / API 682:** *American Petroleum Institute* specifications for centrifugal pumps for petroleum, heavy duty chemical, and gas industry services, including mechanical seal flush configurations (`Plan 11/52`).
- **OSHA 29 CFR 1910.146:** *Occupational Safety and Health Administration* regulations for permit-required confined spaces and atmospheric gas testing.

---

## 4. Open-Source Project License

```
MIT License

Copyright (c) 2026 Ashit Patel & Ops Brain Local Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
