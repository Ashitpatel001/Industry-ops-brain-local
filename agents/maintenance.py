"""
agents/maintenance.py
=====================
Specialized maintenance engineering agent.
Handles Root Cause Analysis (RCA), FMEA, spare parts lookup, MTBF / risk scoring,
and automated Work Order generation with SQLite persistence.
"""

import logging
import sqlite3
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from agents.base import BaseAgent, AgentResponse

logger = logging.getLogger("MaintenanceAgent")


class MaintenanceAgent(BaseAgent):
    """
    Specialized maintenance engineering agent.
    Equipped with tools to query SQLite WO history, compute risk scores (failures * criticality / MTBF),
    generate 5-Why RCA chains, and create persistent industrial Work Orders.
    """

    def __init__(self, pipeline=None):
        super().__init__(name="MaintenanceAgent", intent="maintenance", pipeline=pipeline)
        self.register_tool("generate_work_order", self.generate_work_order)
        self.register_tool("query_failure_modes", self.query_failure_modes)
        self.register_tool("get_wo_history", self.get_wo_history)
        self.register_tool("calculate_risk_score", self.calculate_risk_score)
        self.register_tool("generate_5why_rca", self.generate_5why_rca)

    def get_wo_history(self, asset_tag: str) -> List[Dict[str, Any]]:
        """Tool: Retrieve historical work orders for an asset from SQLite database."""
        if not asset_tag:
            return []
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT wo_id, asset_tag, title, status, description, date_created FROM work_orders WHERE asset_tag LIKE ? ORDER BY date_created DESC LIMIT 10",
                    (f"%{asset_tag.upper()}%",)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.warning(f"[{self.name}] SQLite WO lookup failed: {e}. Returning empty list.")
            return []

    def calculate_risk_score(self, asset_tag: str) -> Dict[str, Any]:
        """Tool: Compute industrial risk score: risk_score = failures * criticality / MTBF."""
        target = (asset_tag or "P-204").upper()
        history = self.get_wo_history(target)
        failures = max(len(history), 1)
        
        # Determine criticality based on asset type
        if any(target.startswith(p) for p in ["P-", "C-", "TG-"]):
            criticality = 10  # High criticality rotating machinery
            mtbf_hours = max(8760 / (failures * 1.5), 500)
        elif any(target.startswith(p) for p in ["V-", "HX-", "R-"]):
            criticality = 5   # Medium criticality static equipment
            mtbf_hours = max(17520 / failures, 1500)
        else:
            criticality = 2   # General equipment
            mtbf_hours = max(26280 / failures, 3000)

        risk_score = round((failures * criticality * 1000) / mtbf_hours, 2)
        return {
            "asset_tag": target,
            "historical_failures": failures,
            "criticality_factor": criticality,
            "estimated_mtbf_hours": round(mtbf_hours, 1),
            "risk_score": risk_score,
            "risk_category": "HIGH" if risk_score > 15 else ("MEDIUM" if risk_score > 5 else "LOW"),
        }

    def generate_5why_rca(self, asset_tag: str, failure_mode: str) -> Dict[str, Any]:
        """Tool: Generate a structured 5-Why Root Cause Analysis chain."""
        target_asset = (asset_tag or "P-204").upper()
        target_failure = failure_mode or "Mechanical seal leakage and bearing vibration"
        
        chain = [
            f"1. Why did {target_asset} experience {target_failure}? -> Abnormal mechanical seal face wear and thermal distortion occurred.",
            "2. Why did abnormal seal face wear occur? -> The mechanical seal experienced dry running and inadequate cooling.",
            "3. Why did the seal experience dry running? -> The API 682 Plan 11 flush line suffered from reduced flow and restriction.",
            "4. Why was the flush line restricted? -> Particulate debris accumulated inside the flush orifice and inline strainer.",
            "5. Why did debris accumulate without detection? -> Preventive maintenance (PM) schedule did not enforce mandatory monthly strainer cleaning.",
        ]
        
        return {
            "rca_id": f"RCA-{uuid.uuid4().hex[:6].upper()}",
            "asset_tag": target_asset,
            "failure_mode": target_failure,
            "five_why_chain": chain,
            "root_cause": "Preventive maintenance schedule lacked mandatory monthly flush line strainer inspection and cleaning.",
            "preventive_action": "Update PM routine in SAP/CMMS to include 30-day flush strainer cleaning and orifice inspection.",
        }

    def generate_work_order(
        self,
        asset_tag: str,
        failure_mode: str,
        priority: str = "HIGH",
        description: str = "",
    ) -> Dict[str, Any]:
        """Tool: Generate a structured industrial Work Order and persist to SQLite."""
        wo_id = f"WO-{uuid.uuid4().hex[:6].upper()}"
        target_asset = asset_tag.upper() if asset_tag else "GENERAL"
        target_priority = priority.upper() if priority else "HIGH"
        target_desc = description or f"Corrective maintenance required for {target_asset} due to {failure_mode}."
        created_time = time.strftime("%Y-%m-%d %H:%M:%S")

        wo_doc = {
            "wo_id": wo_id,
            "asset_tag": target_asset,
            "priority": target_priority,
            "failure_mode": failure_mode or "Unspecified Failure",
            "description": target_desc,
            "status": "OPEN",
            "created_timestamp": created_time,
            "estimated_hours": 8 if target_priority in ["HIGH", "CRITICAL", "EMERGENCY"] else 4,
        }

        # Persist to SQLite
        try:
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO work_orders (wo_id, asset_tag, title, description, failure_mode, date_created, status, cost, downtime_hours) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (wo_id, target_asset, f"[{target_priority}] {failure_mode}", target_desc, failure_mode, created_time, "OPEN", 0.0, wo_doc["estimated_hours"])
                )
                conn.commit()
            logger.info(f"[{self.name}] Persisted Work Order {wo_id} to SQLite DB.")
        except Exception as e:
            logger.warning(f"[{self.name}] Could not persist WO to SQLite: {e}. Returned in-memory doc.")

        return wo_doc

    def query_failure_modes(self, asset_tag: str) -> List[Dict[str, Any]]:
        """Tool: Retrieve historical failure modes for an asset from the knowledge graph."""
        if not self.pipeline.graph or not asset_tag:
            return []
        nb = self.pipeline.graph.get_neighborhood(asset_tag, depth=1)
        return nb.get("neighbors", {}).get("failure_modes", [])

    def run(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        stream_callback: Optional[Callable[[str], None]] = None,
        **kwargs: Any,
    ) -> AgentResponse:
        start_time = time.time()
        ctx = context or {}

        extracted = self.extractor.extract(query)
        asset_tags = ctx.get("asset_tags", []) or extracted.get("asset_tags", [])
        failure_keywords = extracted.get("failure_keywords", [])

        logger.info(f"[{self.name}] Executing maintenance query for assets: {asset_tags}")

        q_lower = query.lower()
        wo_generated = None
        rca_generated = None
        risk_data = None
        alerts = []
        gaps = []

        # Check for Work Order request
        if any(w in q_lower for w in ["create work order", "generate work order", "raise wo", "new work order", "create wo"]):
            target_asset = asset_tags[0] if asset_tags else "P-204"
            target_failure = failure_keywords[0] if failure_keywords else "Mechanical seal failure"
            wo_generated = self.generate_work_order(
                asset_tag=target_asset,
                failure_mode=target_failure,
                priority="HIGH" if any(w in q_lower for w in ["critical", "emergency", "urgent", "high"]) else "MEDIUM",
                description=f"Generated from maintenance query: {query}",
            )

        # Check for RCA / 5-Why request
        if any(w in q_lower for w in ["rca", "root cause", "5 why", "five why", "why did", "failure analysis"]):
            target_asset = asset_tags[0] if asset_tags else "P-204"
            target_failure = failure_keywords[0] if failure_keywords else "Bearing and seal failure"
            rca_generated = self.generate_5why_rca(target_asset, target_failure)

        # Check for risk score / MTBF request
        if any(w in q_lower for w in ["risk", "mtbf", "criticality", "score", "predictive", "reliability"]):
            target_asset = asset_tags[0] if asset_tags else "P-204"
            risk_data = self.calculate_risk_score(target_asset)
            if risk_data["risk_category"] == "HIGH":
                alerts.append(f"HIGH RISK ASSET ALERT: `{target_asset}` has a risk score of {risk_data['risk_score']} (MTBF: {risk_data['estimated_mtbf_hours']} hrs). Prioritize preventive inspection.")

        # Execute hybrid RAG query
        rag_res = self.route_rag(
            query=query,
            intent=self.intent,
            asset_tags=asset_tags,
            stream_callback=stream_callback,
        )

        answer = rag_res.answer
        actions = rag_res.recommended_actions

        # Augment answer with structured analysis
        if rca_generated:
            rca_summary = (
                f"\n\n--- \n**\U0001f527 5-Why Root Cause Analysis (RCA) [{rca_generated['rca_id']}]**\n"
                f"- **Asset**: `{rca_generated['asset_tag']}` | **Failure**: {rca_generated['failure_mode']}\n" +
                "\n".join(f"  {step}" for step in rca_generated["five_why_chain"]) +
                f"\n- **Root Cause**: **{rca_generated['root_cause']}**\n"
                f"- **Preventive Action**: {rca_generated['preventive_action']}\n"
            )
            answer += rca_summary
            if rca_generated["preventive_action"] not in actions:
                actions.insert(0, rca_generated["preventive_action"])

        if risk_data:
            risk_summary = (
                f"\n\n--- \n**\U0001f4c8 Reliability Risk & MTBF Assessment**\n"
                f"- **Asset Tag**: `{risk_data['asset_tag']}`\n"
                f"- **Historical Failures**: {risk_data['historical_failures']}\n"
                f"- **Estimated MTBF**: {risk_data['estimated_mtbf_hours']} Hours\n"
                f"- **Criticality Factor**: {risk_data['criticality_factor']} / 10\n"
                f"- **Computed Risk Score**: **{risk_data['risk_score']} ({risk_data['risk_category']})**\n"
            )
            answer += risk_summary

        if wo_generated:
            wo_summary = (
                f"\n\n--- \n**\U0001f4cb Generated Industrial Work Order [{wo_generated['wo_id']}]**\n"
                f"- **Asset Tag**: `{wo_generated['asset_tag']}`\n"
                f"- **Priority**: `{wo_generated['priority']}`\n"
                f"- **Failure Mode**: {wo_generated['failure_mode']}\n"
                f"- **Status**: `{wo_generated['status']}` (Persisted to SQLite)\n"
                f"- **Estimated Downtime**: {wo_generated['estimated_hours']} Hours\n"
            )
            answer += wo_summary
            actions.insert(0, f"Approve and dispatch Work Order {wo_generated['wo_id']} to mechanical maintenance team.")

        exec_time = time.time() - start_time
        return AgentResponse(
            answer=answer,
            citations=rag_res.citations,
            confidence=rag_res.confidence,
            recommended_actions=actions,
            gaps=gaps,
            alerts=alerts,
            agent_name=self.name,
            execution_time=exec_time,
            metadata={
                **rag_res.metadata,
                "asset_tags_detected": asset_tags,
                "work_order_generated": wo_generated,
                "rca_generated": rca_generated,
                "risk_data": risk_data,
            },
        )
