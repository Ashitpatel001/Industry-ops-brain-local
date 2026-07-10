"""
ui/components/privacy_banner.py
===============================
Renders an ultra-premium, glowing 100% Offline / Air-Gapped security badge
using glassmorphism CSS and micro-animations.
"""

import streamlit as st


def render_privacy_banner():
    """Render the top-bar offline security and air-gap privacy banner."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@500;700&family=Inter:wght@400;600&display=swap');

        @keyframes pulse-glow {
            0% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.4); }
            50% { box-shadow: 0 0 15px rgba(16, 185, 129, 0.8), 0 0 30px rgba(16, 185, 129, 0.4); }
            100% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.4); }
        }

        .airgap-banner {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.85) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 12px;
            padding: 10px 20px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-family: 'Inter', sans-serif;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
        }

        .airgap-banner:hover {
            border-color: rgba(16, 185, 129, 0.6);
            transform: translateY(-1px);
        }

        .airgap-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .led-indicator {
            width: 10px;
            height: 10px;
            background-color: #10B981;
            border-radius: 50%;
            animation: pulse-glow 2s infinite;
        }

        .airgap-title {
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            font-size: 0.95rem;
            color: #F8FAFC;
            letter-spacing: 0.5px;
        }

        .airgap-desc {
            font-size: 0.85rem;
            color: #94A3B8;
        }

        .airgap-badge {
            background: rgba(16, 185, 129, 0.15);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        </style>

        <div class="airgap-banner">
            <div class="airgap-left">
                <div class="led-indicator"></div>
                <div>
                    <span class="airgap-title">AIR-GAPPED & OFFLINE SECURE</span>
                    <span class="airgap-desc"> &mdash; Zero cloud telemetry. All weights, RAG indexes, and LLM inference run 100% locally.</span>
                </div>
            </div>
            <div class="airgap-badge">🔒 ON-PREMISE ONLY</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
