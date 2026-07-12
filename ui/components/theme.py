"""
ui/components/theme.py
=======================
Shared design system for Ops Brain Local.

Visual direction: "engineering drawing sheet" — a light, premium control-room
aesthetic borrowed from P&ID title blocks and instrument panels rather than
generic dashboard chrome. Cards read like drawing sheets (corner ticks, a
sheet number, a discipline label); data-heavy values sit in a monospace
face the way tag numbers and readings do on a real panel.

Tokens
------
Colour:
    --bg          #F5F6F8   page background, cool light grey
    --surface     #FFFFFF   card surface
    --ink         #0B1F3A   primary text / headings, deep navy-black
    --ink-2       #51607A   secondary text
    --border      #E2E6ED   hairline borders
    --navy        #14315C   primary brand / header rail
    --amber       #F2A73B   signature accent — hazard-amber, used sparingly
    --blue        #2563EB   interactive accent (links, active states)
    --success     #12875D
    --warning     #B7791F
    --danger      #C0362C

Type:
    Display : Space Grotesk  — headings, hero, section labels
    Body    : Inter          — paragraphs, UI copy
    Mono    : IBM Plex Mono  — asset tags, metrics, timestamps, code

Signature element:
    "Drawing-sheet" cards: a thin border, four corner ticks, and a small
    sheet number in the corner (e.g. "OB / 02"), echoing the P&ID and
    inspection-sheet numbering this tool actually works with.
"""

import streamlit as st

API_URL_DEFAULT = "http://127.0.0.1:8000"

FONT_IMPORT = (
    "https://fonts.googleapis.com/css2?"
    "family=Space+Grotesk:wght@500;600;700&"
    "family=Inter:wght@400;500;600;700&"
    "family=IBM+Plex+Mono:wght@400;500;600&display=swap"
)


def inject_global_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('{FONT_IMPORT}');

        :root {{
            --bg: #F5F6F8;
            --surface: #FFFFFF;
            --ink: #0B1F3A;
            --ink-2: #51607A;
            --border: #E2E6ED;
            --navy: #14315C;
            --amber: #F2A73B;
            --blue: #2563EB;
            --success: #12875D;
            --warning: #B7791F;
            --danger: #C0362C;
        }}

        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, sans-serif;
            color: var(--ink);
        }}

        .stApp {{
            background:
                linear-gradient(180deg, rgba(20,49,92,0.03) 0%, rgba(20,49,92,0) 240px),
                var(--bg);
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            color: var(--ink);
            letter-spacing: -0.01em;
        }}

        p, li, label, span {{
            color: var(--ink);
        }}

        code, .mono {{
            font-family: 'IBM Plex Mono', monospace !important;
        }}

        /* ---------- Sidebar ---------- */
        section[data-testid="stSidebar"] {{
            background: var(--navy);
            border-right: 1px solid rgba(255,255,255,0.06);
        }}
        section[data-testid="stSidebar"] * {{
            color: #E7ECF6 !important;
        }}
        section[data-testid="stSidebar"] hr {{
            border-color: rgba(255,255,255,0.12);
        }}

        /* ---------- Buttons ---------- */
        div.stButton > button:first-child,
        div.stDownloadButton > button:first-child {{
            background: var(--navy);
            color: #FFFFFF;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            border: 1px solid var(--navy);
            border-radius: 6px;
            padding: 0.5rem 1.25rem;
            transition: all 0.15s ease;
        }}
        div.stButton > button:first-child:hover,
        div.stDownloadButton > button:first-child:hover {{
            background: #1C4176;
            border-color: #1C4176;
            box-shadow: 0 4px 12px rgba(20,49,92,0.25);
        }}
        div.stButton > button:first-child:active {{
            transform: translateY(1px);
        }}

        /* ---------- Inputs ---------- */
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
            border-radius: 6px !important;
            border: 1px solid var(--border) !important;
            font-family: 'Inter', sans-serif;
        }}
        .stTextInput input:focus, .stTextArea textarea:focus {{
            border-color: var(--blue) !important;
            box-shadow: 0 0 0 1px var(--blue) !important;
        }}

        /* ---------- File uploader ---------- */
        [data-testid="stFileUploaderDropzone"] {{
            background: var(--surface);
            border: 1.5px dashed var(--border);
            border-radius: 10px;
        }}

        /* ---------- Tabs ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            border-bottom: 1px solid var(--border);
        }}
        .stTabs [data-baseweb="tab"] {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 600;
            color: var(--ink-2);
            padding: 10px 4px;
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--navy) !important;
            border-bottom: 2px solid var(--amber) !important;
        }}

        /* ---------- Expander ---------- */
        [data-testid="stExpander"] {{
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            background: var(--surface);
        }}

        /* ---------- Chat ---------- */
        [data-testid="stChatMessage"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 6px 4px;
        }}

        /* ---------- Metrics ---------- */
        [data-testid="stMetric"] {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 14px 16px;
        }}
        [data-testid="stMetricLabel"] {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--ink-2) !important;
        }}
        [data-testid="stMetricValue"] {{
            font-family: 'IBM Plex Mono', monospace;
            color: var(--navy) !important;
        }}

        hr {{ border-color: var(--border); }}

        /* Scrollbar polish */
        ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
        ::-webkit-scrollbar-thumb {{ background: #CBD3E0; border-radius: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(eyebrow: str, title: str, subtitle: str, sheet_no: str = "OB / 00") -> None:
    """Top-of-page hero with a faint blueprint grid backdrop and a drawing
    sheet number in the corner — the page's signature element."""
    st.markdown(
        f"""
        <style>
        .hero {{
            position: relative;
            overflow: hidden;
            background: var(--navy);
            border-radius: 14px;
            padding: 34px 38px;
            margin-bottom: 28px;
            border: 1px solid #0E2647;
        }}
        .hero::before {{
            content: "";
            position: absolute; inset: 0;
            background-image:
                linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
            background-size: 28px 28px;
            mask-image: linear-gradient(180deg, black, transparent 85%);
        }}
        .hero-sheetno {{
            position: absolute; top: 18px; right: 22px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            color: rgba(255,255,255,0.55);
            letter-spacing: 0.08em;
        }}
        .hero-eyebrow {{
            position: relative;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.72rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: var(--amber);
            margin-bottom: 10px;
        }}
        .hero-title {{
            position: relative;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 2.1rem;
            color: #FFFFFF;
            margin-bottom: 10px;
            line-height: 1.15;
        }}
        .hero-subtitle {{
            position: relative;
            font-size: 1rem;
            color: #C6D0E2;
            line-height: 1.6;
            max-width: 720px;
        }}
        </style>
        <div class="hero">
            <div class="hero-sheetno">{sheet_no}</div>
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_label(number: str, label: str) -> None:
    """Small numbered section divider — numbers here map to the actual
    step order of a workflow (upload -> parse -> index), so they carry
    real sequence information rather than decorating the page."""
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin: 22px 0 12px 0;">
            <span style="font-family:'IBM Plex Mono',monospace; font-size:0.75rem;
                background: var(--navy); color:#fff; padding:2px 8px; border-radius:4px;">
                {number}
            </span>
            <span style="font-family:'Space Grotesk',sans-serif; font-weight:700;
                font-size:1rem; color: var(--ink); text-transform:uppercase; letter-spacing:0.03em;">
                {label}
            </span>
            <span style="flex:1; height:1px; background: var(--border);"></span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card_open(sheet_no: str = "", tone: str = "default") -> str:
    """Return opening HTML for a 'drawing-sheet' card. Always pair with card_close()."""
    border = {"default": "var(--border)", "amber": "var(--amber)",
              "success": "var(--success)", "danger": "var(--danger)"}.get(tone, "var(--border)")
    tag = f'<span style="position:absolute; top:10px; right:14px; font-family:\'IBM Plex Mono\',monospace; font-size:0.68rem; color: var(--ink-2);">{sheet_no}</span>' if sheet_no else ""
    return f"""
        <div style="position:relative; background:var(--surface); border:1px solid {border};
            border-radius:12px; padding:20px 22px; margin-bottom:16px;
            box-shadow: 0 1px 2px rgba(11,31,58,0.04);">
            {tag}
    """


def card_close() -> str:
    return "</div>"


def asset_tag_chip(text: str) -> str:
    return (
        f'<span style="font-family:\'IBM Plex Mono\',monospace; font-size:0.78rem; '
        f'background:#EEF2F9; color:var(--navy); border:1px solid var(--border); '
        f'padding:2px 9px; border-radius:5px; font-weight:600;">{text}</span>'
    )


def status_pill(label: str, tone: str = "neutral") -> str:
    colors = {
        "success": ("#0F5C3E", "#E4F5EC", "#BEE7D3"),
        "warning": ("#8A5A0C", "#FDF3DF", "#F3DDA8"),
        "danger": ("#8C2A22", "#FBE7E4", "#F0BEB6"),
        "neutral": ("#3C4A63", "#EEF1F5", "#DBE1EA"),
        "info": ("#1E4FA0", "#E9F0FC", "#C6D8F5"),
    }
    text_c, bg_c, border_c = colors.get(tone, colors["neutral"])
    return (
        f'<span style="font-family:\'Space Grotesk\',sans-serif; font-weight:600; '
        f'font-size:0.72rem; letter-spacing:0.04em; text-transform:uppercase; '
        f'color:{text_c}; background:{bg_c}; border:1px solid {border_c}; '
        f'padding:3px 11px; border-radius:20px;">{label}</span>'
    )
