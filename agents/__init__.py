"""
agents/__init__.py
==================
Production-ready domain agents package for Ops Brain Local.
Exports BaseAgent, AgentResponse, and the four specialized industrial agents.
"""

from agents.base import BaseAgent, AgentResponse
from agents.copilot import CopilotAgent
from agents.maintenance import MaintenanceAgent
from agents.compliance import ComplianceAgent
from agents.lessons import LessonsAgent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "CopilotAgent",
    "MaintenanceAgent",
    "ComplianceAgent",
    "LessonsAgent",
]
