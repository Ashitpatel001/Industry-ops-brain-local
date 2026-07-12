"""
ui/pages/1_📄_Upload.py
======================
Document Ingestion Studio for Ops Brain Local.
Allows operators and engineers to upload PDFs, Excel sheets, and Word docs,
monitoring real-time OCR parsing, domain chunking, and knowledge graph extraction.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests

st.set_page_config(page_title="Document Ingestion | Ops Brain Local", page_icon="📄", layout="wide")

from ui.components.theme import inject_global_css, render_hero, render_section_label
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

inject_global_css()

with st.sidebar:
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff;'>Diagnostics</p>", unsafe_allow_html=True)
    render_model_status()

render_privacy_banner()
render_hero(
    eyebrow="Ingestion Studio",
    title="Turn plant documents into searchable knowledge.",
    subtitle="Upload SOPs, P&IDs, equipment manuals or inspection reports. The offline engine parses tables, extracts equipment tags, and indexes knowledge-graph relationships.",
    sheet_no="OB / 01",
)

API_URL = "http://127.0.0.1:8000"

render_section_label("01", "Select Document & Type")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    doc_type = st.selectbox(
        "Document category",
        ["Standard Operating Procedure (SOP)", "Equipment Maintenance Manual",
         "Regulatory Safety Standard", "Inspection & Audit Report",
         "P&ID / Engineering Specification"],
    )

    uploaded_file = st.file_uploader(
        "Upload industrial document",
        type=["pdf", "xlsx", "xls", "docx", "txt", "md"],
        help="Supported offline formats: PDF, Excel, Word, Markdown, Text.",
    )

    adv1, adv2 = st.columns(2)
    with adv1:
        chunk_size = st.number_input("Chunk size", min_value=100, max_value=2000, value=400, step=50)
    with adv2:
        chunk_overlap = st.number_input("Chunk overlap", min_value=0, max_value=500, value=80, step=10)

    if uploaded_file is not None:
        st.markdown(
            f"""
            <div style="background:#EEF2F9; border:1px solid #E2E6ED; border-radius:8px; padding:10px 14px; margin:10px 0;">
                <span style="font-family:IBM Plex Mono; font-size:0.8rem; color:#14315C;">
                    📁 {uploaded_file.name} &middot; {round(uploaded_file.size / 1024, 1)} KB
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚀 Start Offline Ingestion", use_container_width=True):
            with st.spinner("Transmitting to local ingestion engine..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {
                        "doc_type": doc_type,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap,
                    }
                    resp = requests.post(f"{API_URL}/api/v1/ingest", files=files, params=params, timeout=300.0)

                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["last_ingest"] = data
                        st.success(f"Successfully ingested **{uploaded_file.name}**")
                    else:
                        st.error(f"Ingestion failed: {resp.text}")
                except Exception as e:
                    st.error(f"Connection error to backend API: {e}")

with col2:
    render_section_label("02", "Ingestion Status")

    if "last_ingest" in st.session_state:
        data = st.session_state["last_ingest"]

        st.markdown(
            f"""
            <div style="background:#FFFFFF; border:1px solid #E2E6ED; border-top:3px solid #12875D;
                border-radius:10px; padding:20px 22px;">
                <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:#0F5C3E; margin-bottom:6px;">
                    ✅ Indexing complete &nbsp;
                    <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem; color:#51607A;">[{data.get('doc_id', '—')}]</span>
                </div>
                <p style="color:#51607A; font-size:0.87rem; margin-bottom:2px;"><strong style="color:#0B1F3A;">Status:</strong> {data.get('status', '—')}</p>
                <p style="color:#51607A; font-size:0.87rem; margin-bottom:14px;"><strong style="color:#0B1F3A;">Message:</strong> {data.get('message', '—')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Vector chunks created", data.get("chunks_indexed", 0))
        with m2:
            st.metric("Graph entities extracted", data.get("entities_extracted", 0))
    else:
        st.markdown(
            """
            <div style="background:#FAFBFC; border:1px dashed #E2E6ED; border-radius:10px; padding:28px 22px; text-align:center;">
                <span style="color:#8A9BB8; font-size:0.87rem;">Upload and ingest a document on the left to see live vector and graph extraction diagnostics here.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
