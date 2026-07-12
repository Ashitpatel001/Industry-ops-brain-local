"""
ui/pages/4_✅_Compliance.py
==========================
Regulatory Compliance & Evidence Matrix Studio for Ops Brain Local.

Per the current API contract, GET /api/v1/compliance returns the list of
compliance rules/documents indexed in the system. This page reads that list
defensively (several reasonable key names are checked) since the exact gap /
evidence-package shape isn't pinned down in the contract — swap the
`_extract_items()` mapping below to match your backend's exact field names.
"""

import sys
from pathlib import Path
_root = Path(__file__).resolve().parent
while _root.name and _root.name != "ui" and _root != _root.parent: _root = _root.parent
if _root.name == "ui" and str(_root.parent) not in sys.path: sys.path.insert(0, str(_root.parent))

import streamlit as st
import requests
import json

st.set_page_config(page_title="Compliance Audit | Ops Brain Local", page_icon="🛡️", layout="wide")

from ui.components.theme import inject_global_css, render_hero, render_section_label, status_pill
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status

inject_global_css()

with st.sidebar:
    st.markdown("<p style='font-family:Space Grotesk; font-weight:700; color:#fff;'>Diagnostics</p>", unsafe_allow_html=True)
    render_model_status()

render_privacy_banner()
render_hero(
    eyebrow="Compliance Audit",
    title="Regulatory coverage, verified against the plant record.",
    subtitle="Deterministic gap detection against OISD-116, OISD-GDN-192, the Factory Act 1948 and PESO safety rules.",
    sheet_no="OB / 04",
)

API_URL = "http://127.0.0.1:8000"


def _extract_items(data):
    """Best-effort extraction of a list of rule/regulation records from
    whatever shape the backend returns."""
    if isinstance(data, list):
        return data
    for key in ("regulations", "rules", "items", "gap_report", "regulations_indexed"):
        if isinstance(data.get(key), list):
            return data.get(key)
    return []


with st.spinner("Running compliance audit and evidence verification..."):
    try:
        resp = requests.get(f"{API_URL}/api/v1/compliance", timeout=10.0)
        if resp.status_code == 200:
            raw = resp.json()
            items = _extract_items(raw if isinstance(raw, (list, dict)) else {})

            total = len(items)
            open_gaps = sum(1 for it in items if str(it.get("status", "")).upper() not in ("COMPLIANT", "OK", "PASS"))
            compliant = total - open_gaps

            render_section_label("01", "Audit Summary")
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Regulations indexed", total)
            with m2:
                st.metric("Compliant", compliant)
            with m3:
                st.metric("Open gaps", open_gaps)

            render_section_label("02", "Regulation Register")

            if items:
                for idx, it in enumerate(items):
                    clause = it.get("clause") or it.get("rule_id") or it.get("id") or f"ITEM-{idx+1}"
                    title = it.get("title") or it.get("requirement") or it.get("name") or "Untitled requirement"
                    standard = it.get("standard") or it.get("target_standard") or "—"
                    status = str(it.get("status", "PENDING")).upper()
                    severity = str(it.get("severity", "")).upper()
                    asset = it.get("asset", "GEN")

                    tone = "success" if status in ("COMPLIANT", "OK", "PASS") else ("danger" if severity == "HIGH" else "warning")

                    st.markdown(
                        f"""
                        <div style="background:#FFFFFF; border:1px solid #E2E6ED; border-left:4px solid
                            {'#12875D' if tone=='success' else ('#C0362C' if tone=='danger' else '#B7791F')};
                            border-radius:8px; padding:16px 20px; margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:#0B1F3A;">
                                    <span style="font-family:'IBM Plex Mono',monospace; color:#51607A; font-size:0.8rem;">[{asset}]</span> {clause}
                                </span>
                                {status_pill(status, tone)}
                            </div>
                            <p style="color:#51607A; font-size:0.87rem; margin-bottom:4px;">
                                <strong style="color:#0B1F3A;">Standard:</strong> {standard}
                            </p>
                            <p style="color:#51607A; font-size:0.87rem;">{title}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No compliance records returned by the backend yet.")

            render_section_label("03", "Evidence Package")
            st.download_button(
                label="⬇ Download Audit Snapshot (JSON)",
                data=json.dumps(raw, indent=2),
                file_name="compliance_snapshot.json",
                mime="application/json",
            )
        else:
            st.error(f"Failed to retrieve compliance audit: {resp.text}")
    except Exception as e:
        st.error(f"Connection error to local API backend: {e}")
