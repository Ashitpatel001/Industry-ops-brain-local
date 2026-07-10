"""
ui/components/model_status.py
=============================
Renders real-time hardware acceleration diagnostics (OpenVINO INT4/ Ram Usage)
in a sleek glassmorphic dashboard card.
"""

import streamlit as st
import requests


def render_model_status(api_url: str = "http://127.0.0.1:8000"):
    """Fetch and render system health and hardware acceleration diagnostics."""
    try:
        resp = requests.get(f"{api_url}/api/v1/health", timeout=2.0)
        data = resp.json() if resp.status_code == 200 else {}
    except Exception:
        data = {
            "status": "OFFLINE",
            "model_loaded": False,
            "backend": "Backend Disconnected",
            "ram_used_gb": 0.0,
            "ram_total_gb": 0.0,
            "cpu_percent": 0.0,
        }

    status_color = "#10B981" if data.get("status") == "HEALTHY" else "#EF4444"
    model_status_text = "LOADED" if data.get("model_loaded") else "STANDBY / LAZY LOAD"
    backend_text = data.get("backend", "Unknown Backend")
    ram_str = f"{data.get('ram_used_gb', 0)} / {data.get('ram_total_gb', 0)} GB"
    cpu_str = f"{data.get('cpu_percent', 0)}%"

    st.markdown(
        f"""
        <style>
        .diag-card {{
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 12px;
            padding: 14px 18px;
            margin-bottom: 16px;
            font-family: 'Inter', sans-serif;
        }}
        .diag-header {{
            font-family: 'Outfit', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: #E2E8F0;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .diag-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        .diag-item {{
            background: rgba(15, 23, 42, 0.5);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .diag-label {{
            font-size: 0.72rem;
            color: #94A3B8;
            display: block;
            margin-bottom: 2px;
        }}
        .diag-val {{
            font-size: 0.88rem;
            font-weight: 600;
            color: #F8FAFC;
        }}
        </style>

        <div class="diag-card">
            <div class="diag-header">
                <span>⚡ AI HARDWARE ACCELERATION</span>
                <span style="color: {status_color}; font-size: 0.75rem;">● {data.get('status', 'OFFLINE')}</span>
            </div>
            <div class="diag-grid">
                <div class="diag-item">
                    <span class="diag-label">INFERENCE BACKEND</span>
                    <span class="diag-val" style="color: #38BDF8;">{backend_text}</span>
                </div>
                <div class="diag-item">
                    <span class="diag-label">MODEL STATE</span>
                    <span class="diag-val">{model_status_text}</span>
                </div>
                <div class="diag-item">
                    <span class="diag-label">SYSTEM RAM</span>
                    <span class="diag-val">{ram_str}</span>
                </div>
                <div class="diag-item">
                    <span class="diag-label">CPU LOAD</span>
                    <span class="diag-val">{cpu_str}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
