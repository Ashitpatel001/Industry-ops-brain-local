"""
core/graph.py
=============
In-memory industrial knowledge graph using NetworkX.
Supports multi-hop neighborhood retrieval, recurring failure pattern analysis,
and interactive visualization export via PyVis.
"""

import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional
import networkx as nx
from core.config import get_config

logger = logging.getLogger("KnowledgeGraph")


class KnowledgeGraph:
    """
    NetworkX knowledge graph managing industrial entities and relationships:
    Asset, ProcessUnit, WorkOrder, Incident, FailureMode, Regulation, Procedure.
    """

    def __init__(self, graph_path: Optional[str] = None):
        cfg = get_config()
        self.graph_path = Path(graph_path or cfg.graph_path)
        self.G: nx.MultiDiGraph = nx.MultiDiGraph()
        self.load()

    def add_node(self, node_id: str, node_type: str, **attrs: Any) -> None:
        """Add or update a graph node with metadata attributes."""
        if not node_id:
            return
        attrs["type"] = node_type
        attrs["label"] = str(attrs.get("name") or attrs.get("title") or node_id)
        self.G.add_node(str(node_id), **attrs)

    def add_edge(self, src: str, tgt: str, relation: str, **attrs: Any) -> None:
        """Add a directed relationship edge between two nodes."""
        if not src or not tgt or not self.G.has_node(src) or not self.G.has_node(tgt):
            return
        attrs["relation"] = relation
        self.G.add_edge(str(src), str(tgt), key=relation, **attrs)

    def get_neighborhood(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """
        Retrieve neighborhood context around a target node up to n hops.
        Returns structured dictionary grouped by node types (work_orders, failure_modes, etc.).
        """
        if not node_id or not self.G.has_node(node_id):
            return {"node_id": node_id, "found": False, "neighbors": {}}

        # Ego graph gets all nodes within distance `depth`
        subgraph = nx.ego_graph(self.G, node_id, radius=depth, undirected=True)
        
        grouped: Dict[str, List[Dict[str, Any]]] = {
            "assets": [],
            "work_orders": [],
            "failure_modes": [],
            "incidents": [],
            "regulations": [],
            "process_units": [],
            "procedures": [],
            "other": []
        }

        for n, data in subgraph.nodes(data=True):
            if n == node_id:
                continue
            ntype = data.get("type", "other").lower()
            node_info = {"id": n, **data}
            
            if ntype in ["asset"]:
                grouped["assets"].append(node_info)
            elif ntype in ["workorder", "work_order"]:
                grouped["work_orders"].append(node_info)
            elif ntype in ["failuremode", "failure_mode"]:
                grouped["failure_modes"].append(node_info)
            elif ntype in ["incident"]:
                grouped["incidents"].append(node_info)
            elif ntype in ["regulation"]:
                grouped["regulations"].append(node_info)
            elif ntype in ["processunit", "process_unit"]:
                grouped["process_units"].append(node_info)
            elif ntype in ["procedure", "sop"]:
                grouped["procedures"].append(node_info)
            else:
                grouped["other"].append(node_info)

        return {
            "node_id": node_id,
            "found": True,
            "target_data": self.G.nodes[node_id],
            "neighbors": {k: v for k, v in grouped.items() if v}
        }

    def get_recurring_failures(self, min_count: int = 2) -> List[Dict[str, Any]]:
        """
        Identify recurring failure modes across assets by analyzing degree centrality
        and incoming edges from WorkOrders and Incidents.
        """
        recurring = []
        for n, data in self.G.nodes(data=True):
            if data.get("type") == "FailureMode":
                # Count incoming edges of type CAUSED_BY or ADDRESSES_FAILURE or HAS_FAILURE_MODE
                in_edges = self.G.in_edges(n, data=True)
                count = len(in_edges)
                if count >= min_count:
                    affected_assets = list({src for src, _, _ in in_edges if self.G.nodes.get(src, {}).get("type") == "Asset"})
                    recurring.append({
                        "failure_mode": n,
                        "mode_id": data.get("mode_id", n),
                        "category": data.get("category", "General"),
                        "occurrence_count": count,
                        "affected_assets": affected_assets,
                        "recommended_action": data.get("action", "Inspect and review maintenance logs.")
                    })
        # Sort by highest occurrence count
        recurring.sort(key=lambda x: x["occurrence_count"], reverse=True)
        return recurring

    def to_pyvis(self) -> Any:
        """
        Export graph to an interactive PyVis Network object for Streamlit UI rendering.
        Applies custom colors and dark theme styling.
        """
        try:
            from pyvis.network import Network
        except ImportError:
            logger.warning("pyvis package not found. Cannot export graph.")
            return None

        net = Network(height="600px", width="100%", bgcolor="#0d1117", font_color="#e2e8f0", directed=True)
        net.force_atlas_2based(gravity=-50, central_gravity=0.01, spring_length=100, spring_strength=0.08)

        # Color palette by node type
        color_map = {
            "Asset": "#3b82f6",        # Blue
            "FailureMode": "#ef4444",  # Red
            "Incident": "#f97316",     # Orange
            "WorkOrder": "#22c55e",    # Green
            "ProcessUnit": "#a855f7",  # Purple
            "Regulation": "#eab308",   # Yellow
            "Procedure": "#06b6d4"     # Cyan
        }

        for n, data in self.G.nodes(data=True):
            ntype = data.get("type", "Other")
            color = color_map.get(ntype, "#64748b")
            label = str(data.get("label", n))
            title = f"<b>{ntype}:</b> {label}<br/>" + "<br/>".join([f"<i>{k}:</i> {v}" for k, v in data.items() if k not in ["type", "label", "name"]])
            
            # Highlight high criticality assets or severe incidents
            size = 25 if ntype in ["Asset", "ProcessUnit"] else 18
            if data.get("criticality") == "HIGH" or data.get("severity") in ["HIGH", "CRITICAL"]:
                size = 32
                color = "#ff0033" if ntype == "Asset" else color

            net.add_node(str(n), label=label[:25], title=title, color=color, size=size)

        for u, v, data in self.G.edges(data=True):
            rel = data.get("relation", "")
            net.add_edge(str(u), str(v), title=rel, label=rel, color="#475569", arrows="to")

        return net

    def save(self) -> None:
        """Serialize NetworkX graph to disk via pickle."""
        try:
            self.graph_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.graph_path, "wb") as f:
                pickle.dump(self.G, f)
            logger.info(f"Knowledge graph saved ({self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges) -> {self.graph_path}")
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")

    def load(self) -> None:
        """Load NetworkX graph from disk if available."""
        if self.graph_path.exists() and self.graph_path.stat().st_size > 0:
            try:
                with open(self.graph_path, "rb") as f:
                    self.G = pickle.load(f)
                logger.info(f"Knowledge graph loaded ({self.G.number_of_nodes()} nodes, {self.G.number_of_edges()} edges) from {self.graph_path}")
            except Exception as e:
                logger.warning(f"Could not load graph from {self.graph_path}: {e}. Starting fresh.")
                self.G = nx.MultiDiGraph()
        else:
            self.G = nx.MultiDiGraph()
