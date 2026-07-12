"""
ui.components package
=====================
Reusable UI components and the shared design system for Ops Brain Local.
"""

from ui.components.theme import (
    inject_global_css,
    render_hero,
    render_section_label,
    card_open,
    card_close,
    asset_tag_chip,
    status_pill,
)
from ui.components.privacy_banner import render_privacy_banner
from ui.components.model_status import render_model_status
from ui.components.confidence_badge import render_confidence_badge
from ui.components.citation_card import render_citation_card
from ui.components.actions_checklist import render_actions_checklist

__all__ = [
    "inject_global_css",
    "render_hero",
    "render_section_label",
    "card_open",
    "card_close",
    "asset_tag_chip",
    "status_pill",
    "render_privacy_banner",
    "render_model_status",
    "render_confidence_badge",
    "render_citation_card",
    "render_actions_checklist",
]
