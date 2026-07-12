"""
ui/components/privacy_banner.py
===============================
Top-of-page system status strip. Same message as before (100% on-premise,
zero cloud telemetry) redrawn as a light instrument-panel readout instead
of a dark glowing badge.
"""

import streamlit as st


def render_privacy_banner() -> None:
    """Render the top-bar offline / air-gap status strip."""
    st.markdown(
        """
        <style>
        @keyframes led-pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.45; }
        }
        .status-strip {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #FFFFFF;
            border: 1px solid #E2E6ED;
            border-left: 4px solid #12875D;
            border-radius: 10px;
            padding: 10px 18px;
            margin-bottom: 22px;
            font-family: 'Inter', sans-serif;
        }
        .status-strip-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .status-led {
            width: 9px; height: 9px; border-radius: 50%;
            background: #12875D;
            animation: led-pulse 2.2s ease-in-out infinite;
            box-shadow: 0 0 0 3px rgba(18,135,93,0.15);
        }
        .status-strip-title {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            color: #0B1F3A;
            letter-spacing: 0.02em;
        }
        .status-strip-desc {
            font-size: 0.82rem;
            color: #51607A;
        }
        .status-strip-badge {
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            color: #0F5C3E;
            background: #E4F5EC;
            border: 1px solid #BEE7D3;
            padding: 4px 12px;
            border-radius: 20px;
            letter-spacing: 0.04em;
        }
        </style>

        <div class="status-strip">
            <div class="status-strip-left">
                <div class="status-led"></div>
                <div>
                    <span class="status-strip-title">AIR-GAPPED &amp; OFFLINE</span>
                    <span class="status-strip-desc"> &mdash; zero cloud telemetry. Weights, indexes and inference all run on-premise.</span>
                </div>
            </div>
            <div class="status-strip-badge">ON-PREMISE ONLY</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
