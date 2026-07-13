"use client";
import React, { useState, useEffect, useCallback, useRef } from "react";
import dynamic from "next/dynamic";
import HeroHeader from "@/components/HeroHeader";
import { Network, Search, Filter, Layers, Database, AlertTriangle, ShieldCheck, Wrench, ChevronRight, X, Loader2 } from "lucide-react";

const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), { ssr: false });

interface GraphNode {
  id: string;
  label: string;
  type: string;
  name?: string;
  criticality?: string;
  mtbf?: number;
  status?: string;
  title?: string;
  description?: string;
  requirement?: string;
  [key: string]: any;
}

interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  relation: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphEdge[];
}

const NODE_COLORS: Record<string, string> = {
  Asset: "#2563EB",       // Blue
  ProcessUnit: "#8B5CF6", // Purple
  FailureMode: "#C0362C", // Red/Danger
  WorkOrder: "#F2A73B",   // Amber
  Incident: "#D97706",    // Orange
  Regulation: "#12875D",  // Green/Success
  Default: "#51607A",     // Slate
};

export default function GraphPage() {
  const [nodeId, setNodeId] = useState("P-204");
  const [depth, setDepth] = useState(2);
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fgRef = useRef<any>(null);

  const fetchGraph = useCallback(async (targetId: string, targetDepth: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/graph/${encodeURIComponent(targetId)}?depth=${targetDepth}`);
      if (!res.ok) {
        throw new Error(`Failed to load graph subgraph for node "${targetId}" (HTTP ${res.status})`);
      }
      const data = await res.json();
      const nodes = data.nodes || [];
      const edges = data.edges || [];

      setGraphData({
        nodes,
        links: edges.map((e: any) => ({
          source: e.source,
          target: e.target,
          relation: e.relation || "CONNECTED_TO",
        })),
      });

      // If root node found, select it
      const root = nodes.find((n: GraphNode) => n.id === targetId);
      if (root) setSelectedNode(root);
    } catch (err: any) {
      setError(err.message || "An error occurred while querying NetworkX database.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph(nodeId, depth);
  }, [fetchGraph, nodeId, depth]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (nodeId.trim()) {
      fetchGraph(nodeId.trim(), depth);
    }
  };

  const handleNodeClick = useCallback((node: any) => {
    setSelectedNode(node as GraphNode);
    // Center view on clicked node
    if (fgRef.current && node.x !== undefined && node.y !== undefined) {
      fgRef.current.centerAt(node.x, node.y, 400);
      fgRef.current.zoom(3, 400);
    }
  }, []);

  return (
    <div className="space-y-6">
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Graph Explorer"
        title="Interactive Knowledge Graph Topology."
        subtitle="Explore multi-hop relationships linking equipment assets (`P-204`) directly to failure modes, maintenance work orders (`WO-10234`), safety regulations (`OISD-116`), and historical flash fire incidents across our local NetworkX SQLite store."
        sheetNo="OB / 03"
      />

      {/* Search & Filter Bar */}
      <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <form onSubmit={handleSearch} className="flex flex-wrap items-center gap-3 flex-1">
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-600" />
            <span className="font-[family-name:var(--font-mono)] text-xs font-bold uppercase text-[#51607A]">
              Root Node ID:
            </span>
            <input
              type="text"
              value={nodeId}
              onChange={(e) => setNodeId(e.target.value)}
              placeholder="e.g. P-204, HX-301, WO-10234"
              className="px-3 py-1.5 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-xs text-[#0B1F3A] w-48 focus:outline-hidden focus:border-blue-600 font-semibold"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="font-[family-name:var(--font-mono)] text-xs font-bold uppercase text-[#51607A]">
              Hops Depth:
            </span>
            <select
              value={depth}
              onChange={(e) => setDepth(parseInt(e.target.value))}
              className="px-3 py-1.5 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-xs font-semibold text-[#0B1F3A] focus:outline-hidden focus:border-blue-600"
            >
              <option value={1}>1 Hop (Immediate Neighborhood)</option>
              <option value={2}>2 Hops (Extended Topology)</option>
              <option value={3}>3 Hops (Full Chain of Events)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-4 py-1.5 bg-[#14315C] hover:bg-[#1C4176] text-white rounded-lg font-semibold text-xs transition-colors flex items-center gap-1.5"
          >
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Layers className="w-3.5 h-3.5" />}
            <span>Query Topology</span>
          </button>
        </form>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-2 font-[family-name:var(--font-mono)] text-[11px]">
          {Object.entries(NODE_COLORS).map(([type, color]) => (
            <span key={type} className="flex items-center gap-1 bg-[#F5F6F8] px-2 py-0.5 rounded border border-[#E2E6ED]">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: color }} />
              <span className="text-[#0B1F3A] font-semibold">{type}</span>
            </span>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-[#FBE7E4] border border-[#F0BEB6] text-[#8C2A22] rounded-xl p-4 text-xs font-semibold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Graph Canvas & Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Canvas Area */}
        <div className="lg:col-span-3 bg-[#0B1F3A] border border-[#14315C] rounded-2xl overflow-hidden relative h-[620px] shadow-md flex items-center justify-center">
          <div className="absolute top-4 left-4 z-10 bg-white/10 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/15 text-white font-[family-name:var(--font-mono)] text-xs flex items-center gap-2">
            <Network className="w-3.5 h-3.5 text-[#F2A73B]" />
            <span>
              Showing {graphData.nodes.length} Nodes &middot; {graphData.links.length} Edges
            </span>
          </div>

          <ForceGraph2D
            ref={fgRef}
            graphData={graphData}
            width={850}
            height={620}
            nodeLabel="label"
            nodeColor={(node: any) => NODE_COLORS[node.type] || NODE_COLORS.Default}
            nodeRelSize={7}
            linkColor={() => "rgba(255, 255, 255, 0.25)"}
            linkWidth={1.5}
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={1}
            onNodeClick={handleNodeClick}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              const label = node.id || node.label || "";
              const fontSize = 12 / globalScale;
              ctx.font = `600 ${fontSize}px Inter, sans-serif`;
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map((n) => n + fontSize * 0.5);

              // Draw node circle
              ctx.beginPath();
              ctx.arc(node.x, node.y, 6, 0, 2 * Math.PI, false);
              ctx.fillStyle = NODE_COLORS[node.type] || NODE_COLORS.Default;
              ctx.fill();

              // Draw node tag pill above
              if (globalScale > 0.8) {
                ctx.fillStyle = "rgba(11, 31, 58, 0.85)";
                ctx.fillRect(
                  node.x - bckgDimensions[0] / 2,
                  node.y - 14 - fontSize,
                  bckgDimensions[0],
                  bckgDimensions[1]
                );
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillStyle = "#FFFFFF";
                ctx.fillText(label, node.x, node.y - 14 - fontSize / 2);
              }
            }}
          />
        </div>

        {/* Right Side Inspector Drawer */}
        <div className="lg:col-span-1 bg-white border border-[#E2E6ED] rounded-2xl p-5 shadow-2xs flex flex-col justify-between h-[620px] overflow-y-auto">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#E2E6ED]">
              <span className="font-[family-name:var(--font-display)] font-bold text-sm uppercase tracking-wider text-[#0B1F3A]">
                Node Inspector
              </span>
              {selectedNode && (
                <button
                  onClick={() => setSelectedNode(null)}
                  className="p-1 hover:bg-[#F5F6F8] rounded text-[#51607A]"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {selectedNode ? (
              <div className="space-y-4">
                <div>
                  <span
                    className="font-[family-name:var(--font-mono)] text-[10px] font-bold px-2 py-0.5 rounded text-white inline-block mb-2"
                    style={{ backgroundColor: NODE_COLORS[selectedNode.type] || NODE_COLORS.Default }}
                  >
                    {selectedNode.type}
                  </span>
                  <h3 className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A]">
                    {selectedNode.name || selectedNode.title || selectedNode.id}
                  </h3>
                  <p className="font-[family-name:var(--font-mono)] text-xs text-[#51607A]">
                    ID: {selectedNode.id}
                  </p>
                </div>

                <div className="space-y-2.5 text-xs border-t border-[#E2E6ED]/80 pt-3">
                  {selectedNode.criticality && (
                    <div className="flex justify-between">
                      <span className="text-[#51607A] font-medium">Criticality:</span>
                      <span className="font-bold text-[#C0362C] font-[family-name:var(--font-mono)]">
                        {selectedNode.criticality}
                      </span>
                    </div>
                  )}
                  {selectedNode.mtbf !== undefined && (
                    <div className="flex justify-between">
                      <span className="text-[#51607A] font-medium">MTBF (Days):</span>
                      <span className="font-bold font-[family-name:var(--font-mono)]">
                        {selectedNode.mtbf}
                      </span>
                    </div>
                  )}
                  {selectedNode.status && (
                    <div className="flex justify-between">
                      <span className="text-[#51607A] font-medium">Status:</span>
                      <span className="font-bold text-[#12875D] font-[family-name:var(--font-mono)]">
                        {selectedNode.status}
                      </span>
                    </div>
                  )}
                  {selectedNode.standard && (
                    <div className="flex justify-between">
                      <span className="text-[#51607A] font-medium">Standard:</span>
                      <span className="font-bold font-[family-name:var(--font-mono)]">
                        {selectedNode.standard} {selectedNode.clause ? `(${selectedNode.clause})` : ""}
                      </span>
                    </div>
                  )}
                </div>

                {selectedNode.description && (
                  <div className="border-t border-[#E2E6ED]/80 pt-3">
                    <span className="text-[11px] font-semibold uppercase text-[#51607A] block mb-1">
                      Description / Narrative:
                    </span>
                    <p className="text-xs text-[#28344A] bg-[#FAFBFC] p-3 rounded-lg border border-[#E2E6ED] leading-relaxed">
                      {selectedNode.description}
                    </p>
                  </div>
                )}

                {selectedNode.requirement && (
                  <div className="border-t border-[#E2E6ED]/80 pt-3">
                    <span className="text-[11px] font-semibold uppercase text-[#12875D] block mb-1">
                      Statutory Requirement:
                    </span>
                    <p className="text-xs text-[#0F5C3E] bg-[#E4F5EC] p-3 rounded-lg border border-[#BEE7D3] leading-relaxed">
                      {selectedNode.requirement}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-16 text-[#51607A] space-y-2">
                <Network className="w-10 h-10 mx-auto text-[#CBD3E0]" />
                <div className="font-semibold text-sm text-[#0B1F3A]">No Node Selected</div>
                <p className="text-xs leading-relaxed max-w-[200px] mx-auto">
                  Click any node on the left canvas (`ASSET`, `FAILURE_MODE`, `REGULATION`) to inspect its properties and relationships.
                </p>
              </div>
            )}
          </div>

          {selectedNode && (
            <button
              type="button"
              onClick={() => {
                setNodeId(selectedNode.id);
                fetchGraph(selectedNode.id, depth);
              }}
              className="w-full mt-4 py-2.5 bg-[#14315C] hover:bg-[#1C4176] text-white font-semibold text-xs rounded-xl flex items-center justify-center gap-2 transition-colors cursor-pointer"
            >
              <span>Center as New Root</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
