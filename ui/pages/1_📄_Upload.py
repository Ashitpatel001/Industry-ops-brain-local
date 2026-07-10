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
import time

st.set_page_config(page_title="Document Ingestion | Ops Brain Local", page_icon="📄", layout="wide")

from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

render_privacy_banner()

with st.sidebar:
    st.markdown("### ⚡ Diagnostics")
    render_model_status()

st.markdown("<h1 style='color: #38BDF8;'>📄 Industrial Document Ingestion Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #94A3B8;'>Upload plant SOPs, P&IDs, equipment manuals, or inspection reports. Our offline AI engine automatically parses tables, extracts equipment tags, and indexes knowledge graph relationships.</p>", unsafe_allow_html=True)
st.markdown("---")

API_URL = "http://127.0.0.1:8000"

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 1️⃣ Select Document & Type")
    doc_type = st.selectbox(
        "Document Category",
        ["Standard Operating Procedure (SOP)", "Equipment Maintenance Manual", "Regulatory Safety Standard", "Inspection & Audit Report", "P&ID / Engineering Specification"]
    )
    
    uploaded_file = st.file_uploader(
        "Upload Industrial Document",
        type=["pdf", "xlsx", "xls", "docx", "txt", "md"],
        help="Supported offline formats: PDF, Excel, Word, Markdown, Text."
    )

    if uploaded_file is not None:
        st.info(f"📁 Selected file: **{uploaded_file.name}** ({round(uploaded_file.size / 1024, 1)} KB)")
        
        if st.button("🚀 Start Offline Ingestion"):
            with st.spinner("⏳ Transmitting to local ingestion engine..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {"doc_type": doc_type}
                    
                    resp = requests.post(f"{API_URL}/api/v1/ingest", files=files, params=params, timeout=300.0)
                    
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state["last_ingest"] = data
                        st.success(f"✅ Successfully ingested **{uploaded_file.name}**!")
                    else:
                        st.error(f"❌ Ingestion failed: {resp.text}")
                except Exception as e:
                    st.error(f"❌ Connection error to backend API: {e}")

with col2:
    st.markdown("### 2️⃣ Ingestion Status & Diagnostics")
    
    if "last_ingest" in st.session_state:
        data = st.session_state["last_ingest"]
        
        st.markdown(
            f"""
            <style>
            .res-card {{
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 12px;
                padding: 20px;
                font-family: 'Inter', sans-serif;
            }}
            </style>
            <div class="res-card">
                <h4 style="color: #10B981; margin-bottom: 12px;">✅ Indexing Complete [{data.get('doc_id')}]</h4>
                <p><strong>Status:</strong> <span style="color: #34D399;">{data.get('status')}</span></p>
                <p><strong>Message:</strong> {data.get('message')}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <div style="display: flex; justify-content: space-around; text-align: center; margin-top: 15px;">
                    <div>
                        <span style="font-size: 1.5rem; font-weight: 700; color: #38BDF8;">{data.get('chunks_indexed', 0)}</span><br>
                        <span style="font-size: 0.8rem; color: #94A3B8;">Vector Chunks Created</span>
                    </div>
                    <div>
                        <span style="font-size: 1.5rem; font-weight: 700; color: #F59E0B;">{data.get('entities_extracted', 0)}</span><br>
                        <span style="font-size: 0.8rem; color: #94A3B8;">Graph Entities Extracted</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("ℹ️ Upload and ingest a document on the left to view real-time vector and graph extraction diagnostics.")
