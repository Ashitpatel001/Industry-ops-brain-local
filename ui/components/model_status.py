"""
ui/components/model_status.py
=============================
Sidebar diagnostics card. Reads GET /api/v1/health, which returns:

    {"status": "HEALTHY", "backend": "MockLLM", "ram_used_gb": 10.1, "uptime_seconds": 6.8}

Renders as a compact instrument card in the (navy) sidebar.
"""

import streamlit as st
import requests

API_URL_DEFAULT = "http://127.0.0.1:8000"


def _format_uptime(seconds) -> str:
    try:
        seconds = float(seconds)
    except (TypeError, ValueError):
        return "—"
    if seconds < 60:
        return f"{seconds:.0f}s"
    minutes, sec = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


def render_model_status(api_url: str = API_URL_DEFAULT) -> None:
    """Fetch and render backend health / hardware diagnostics."""
    try:
        resp = requests.get(f"{api_url}/api/v1/health", timeout=2.0)
        data = resp.json() if resp.status_code == 200 else {}
        reachable = resp.status_code == 200
    except Exception:
        data = {}
        reachable = False

    status = data.get("status", "OFFLINE") if reachable else "OFFLINE"
    backend = data.get("backend", "Disconnected")
    ram_used = data.get("ram_used_gb")
    uptime = _format_uptime(data.get("uptime_seconds"))

    is_healthy = status == "HEALTHY"
    dot_color = "#3DD68C" if is_healthy else "#F27060"
    status_text_color = "#3DD68C" if is_healthy else "#F27060"

    ram_display = f"{ram_used} GB" if ram_used is not None else "—"

    st.markdown(
        f"""
        <style>
        .diag-card {{
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 14px;
        }}
        .diag-header {{
            display: flex; align-items: center; justify-content: space-between;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em;
            text-transform: uppercase; color: #C6D0E2; margin-bottom: 10px;
        }}
        .diag-dot {{ width: 7px; height: 7px; border-radius: 50%; background: {dot_color}; display:inline-block; margin-right:6px; }}
        .diag-row {{
            display: flex; justify-content: space-between; align-items: center;
            padding: 5px 0; border-top: 1px solid rgba(255,255,255,0.08);
        }}
        .diag-row:first-of-type {{ border-top: none; }}
        .diag-label {{ font-size: 0.74rem; color: #9AABC9; }}
        .diag-val {{ font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; color: #F5F6F8; font-weight: 600; }}
        </style>

        <div class="diag-card">
            <div class="diag-header">
                <span>Engine Diagnostics</span>
                <span style="color:{status_text_color};"><span class="diag-dot"></span>{status}</span>
            </div>
            <div class="diag-row">
                <span class="diag-label">Backend</span>
                <span class="diag-val">{backend}</span>
            </div>
            <div class="diag-row">
                <span class="diag-label">RAM used</span>
                <span class="diag-val">{ram_display}</span>
            </div>
            <div class="diag-row">
                <span class="diag-label">Uptime</span>
                <span class="diag-val">{uptime}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
