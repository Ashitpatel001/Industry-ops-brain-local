"use client";
import React, { useState, useEffect } from "react";
import HeroHeader from "@/components/HeroHeader";
import CitationCard, { CitationItem } from "@/components/CitationCard";
import ActionsChecklist from "@/components/ActionsChecklist";
import { Wrench, AlertTriangle, CheckCircle2, Send, Loader2, Database, ShieldAlert, Sparkles, RefreshCw, Cpu } from "lucide-react";

interface Asset {
  asset_tag: string;
  name: string;
  type: string;
  criticality: string;
  process_unit: string;
  mtbf_days: number;
  status: string;
  description: string;
  risk_score?: number;
}

export default function MaintenancePage() {
  const [activeTab, setActiveTab] = useState<"matrix" | "wo" | "rca">("matrix");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loadingAssets, setLoadingAssets] = useState(true);

  // Work Order Form State
  const [woAsset, setWoAsset] = useState("P-204");
  const [woPriority, setWoPriority] = useState("P1 - EMERGENCY / ENVIRONMENTAL");
  const [woFailure, setWoFailure] = useState("Mechanical Seal Failure");
  const [woDesc, setWoDesc] = useState("Primary barrier fluid leak observed on seal cartridge during morning shift inspection.");
  const [woSubmitting, setWoSubmitting] = useState(false);
  const [woResult, setWoResult] = useState<any | null>(null);

  // 5-Why RCA State
  const [rcaAsset, setRcaAsset] = useState("P-204");
  const [rcaSymptom, setRcaSymptom] = useState("Recurrent mechanical seal failure occurring every 67 operating days despite flush plan checks.");
  const [rcaSubmitting, setRcaSubmitting] = useState(false);
  const [rcaResult, setRcaResult] = useState<any | null>(null);

  useEffect(() => {
    const fetchAssets = async () => {
      setLoadingAssets(true);
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/assets");
        if (res.ok) {
          const data = await res.json();
          const rawAssets: Asset[] = data.assets || [];
          const scored = rawAssets.map((a) => {
            const critFactor = a.criticality === "HIGH" ? 3.0 : a.criticality === "MEDIUM" ? 2.0 : 1.0;
            const mtbf = Math.max(1, a.mtbf_days || 365);
            const risk = Math.round((critFactor * 1000) / mtbf);
            return { ...a, risk_score: risk };
          });
          // Sort descending by risk score
          scored.sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));
          setAssets(scored);
        }
      } catch {
        // Silently handle offline/error in tab
      } finally {
        setLoadingAssets(false);
      }
    };
    fetchAssets();
  }, []);

  const handleCreateWO = async (e: React.FormEvent) => {
    e.preventDefault();
    setWoSubmitting(true);
    setWoResult(null);
    try {
      const woText = `Create work order for ${woAsset} due to ${woFailure}. Priority: ${woPriority}. Description: ${woDesc}`;
      const res = await fetch("http://127.0.0.1:8000/api/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: woText,
          text: woText,
          intent: "maintenance",
          asset_tags: [woAsset],
        }),
      });
      if (!res.ok) throw new Error(`HTTP status ${res.status}`);
      const data = await res.json();
      setWoResult(data);
    } catch (err: any) {
      setWoResult({ error: err.message || "Failed to dispatch work order to API." });
    } finally {
      setWoSubmitting(false);
    }
  };

  const handleRunRCA = async (e: React.FormEvent) => {
    e.preventDefault();
    setRcaSubmitting(true);
    setRcaResult(null);
    try {
      const rcaText = `Generate a 5-Why RCA for ${rcaAsset} regarding ${rcaSymptom}`;
      const res = await fetch("http://127.0.0.1:8000/api/v1/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: rcaText,
          text: rcaText,
          intent: "maintenance",
          asset_tags: [rcaAsset],
        }),
      });
      if (!res.ok) throw new Error(`HTTP status ${res.status}`);
      const data = await res.json();
      setRcaResult(data);
    } catch (err: any) {
      setRcaResult({ error: err.message || "Failed to execute 5-Why analysis on API." });
    } finally {
      setRcaSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Reliability Studio"
        title="Maintenance Engineering &amp; 5-Why RCA."
        subtitle="Rank asset risks via historical MTBF scores, generate and persist CMMS work orders, or execute multi-agent 5-Why Root Cause Analyses traversing failure chains across our local knowledge graph."
        sheetNo="OB / 05"
      />

      {/* Navigation Tabs */}
      <div className="bg-white border border-[#E2E6ED] rounded-xl p-2 shadow-2xs flex gap-2">
        {[
          { id: "matrix", label: "Asset Risk Matrix (MTBF Ranking)", icon: Database },
          { id: "wo", label: "Work Order Generator", icon: Wrench },
          { id: "rca", label: "5-Why Root Cause Analysis (RCA)", icon: ShieldAlert },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold text-xs md:text-sm flex items-center justify-center gap-2.5 transition-all cursor-pointer ${
                isActive
                  ? "bg-[#14315C] text-white shadow-sm"
                  : "bg-transparent text-[#51607A] hover:bg-[#F5F6F8] hover:text-[#0B1F3A]"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Asset Risk Matrix */}
      {activeTab === "matrix" && (
        <div className="bg-white border border-[#E2E6ED] rounded-2xl overflow-hidden shadow-2xs">
          <div className="p-5 border-b border-[#E2E6ED] flex items-center justify-between">
            <div>
              <h3 className="font-[family-name:var(--font-display)] font-bold text-base text-[#0B1F3A]">
                Plant Equipment Risk Index
              </h3>
              <p className="text-xs text-[#51607A]">
                Calculated via formula: <code className="font-[family-name:var(--font-mono)] text-[#14315C] bg-[#EEF2F9] px-1.5 py-0.5 rounded">(Criticality Factor &times; 1000) / MTBF Days</code>
              </p>
            </div>
            <span className="font-[family-name:var(--font-mono)] text-xs font-bold text-[#14315C] bg-[#EEF2F9] px-3 py-1 rounded-full border border-[#D5E1F2]">
              {assets.length} Active Assets
            </span>
          </div>

          {loadingAssets ? (
            <div className="p-16 text-center text-[#51607A] space-y-3">
              <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
              <div className="font-semibold text-sm">Evaluating equipment reliability scores...</div>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-[#FAFBFC] border-b border-[#E2E6ED] font-[family-name:var(--font-mono)] text-xs font-semibold text-[#51607A] uppercase tracking-wider">
                    <th className="py-3.5 px-6">Asset Tag</th>
                    <th className="py-3.5 px-6">Equipment Name &amp; Unit</th>
                    <th className="py-3.5 px-6">Type</th>
                    <th className="py-3.5 px-6">MTBF (Days)</th>
                    <th className="py-3.5 px-6">Criticality</th>
                    <th className="py-3.5 px-6">Risk Score</th>
                    <th className="py-3.5 px-6">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E2E6ED]">
                  {assets.map((asset, idx) => {
                    const risk = asset.risk_score || 0;
                    let riskBadge = "bg-[#EEF2F9] text-[#14315C]";
                    if (risk >= 30) riskBadge = "bg-[#FBE7E4] text-[#C0362C] font-bold";
                    else if (risk >= 15) riskBadge = "bg-[#FEF6EC] text-[#B7791F] font-bold";

                    return (
                      <tr key={asset.asset_tag} className="hover:bg-[#FAFBFC] transition-colors text-xs md:text-sm">
                        <td className="py-4 px-6 font-[family-name:var(--font-mono)] font-bold text-[#14315C]">
                          {asset.asset_tag}
                        </td>
                        <td className="py-4 px-6">
                          <div className="font-[family-name:var(--font-display)] font-bold text-[#0B1F3A]">
                            {asset.name}
                          </div>
                          <div className="text-xs text-[#51607A] mt-0.5">{asset.process_unit}</div>
                        </td>
                        <td className="py-4 px-6 text-[#51607A] font-medium">{asset.type}</td>
                        <td className="py-4 px-6 font-[family-name:var(--font-mono)] font-bold">
                          {asset.mtbf_days} d
                        </td>
                        <td className="py-4 px-6 font-[family-name:var(--font-mono)] text-xs font-bold">
                          <span
                            className={`px-2 py-0.5 rounded ${
                              asset.criticality === "HIGH"
                                ? "text-[#C0362C] bg-[#FBE7E4]"
                                : asset.criticality === "MEDIUM"
                                ? "text-[#B7791F] bg-[#FEF6EC]"
                                : "text-[#51607A] bg-[#F5F6F8]"
                            }`}
                          >
                            {asset.criticality}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span className={`font-[family-name:var(--font-mono)] px-2.5 py-1 rounded-full text-xs ${riskBadge}`}>
                            {risk}
                          </span>
                        </td>
                        <td className="py-4 px-6">
                          <span
                            className={`font-[family-name:var(--font-mono)] text-xs font-bold ${
                              asset.status === "WARNING" ? "text-[#B7791F]" : "text-[#12875D]"
                            }`}
                          >
                            ● {asset.status}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Work Order Generator */}
      {activeTab === "wo" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 bg-white border border-[#E2E6ED] rounded-xl p-6 shadow-2xs space-y-5">
            <div className="flex items-center gap-2 font-[family-name:var(--font-display)] font-bold text-sm uppercase tracking-wider text-[#0B1F3A]">
              <Wrench className="w-4 h-4 text-blue-600" />
              <span>CMMS Dispatch Form</span>
            </div>

            <form onSubmit={handleCreateWO} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Target Asset Tag
                </label>
                <select
                  value={woAsset}
                  onChange={(e) => setWoAsset(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-sm text-[#0B1F3A] font-semibold focus:outline-hidden focus:border-blue-600"
                >
                  {assets.map((a) => (
                    <option key={a.asset_tag} value={a.asset_tag}>
                      {a.asset_tag} — {a.name}
                    </option>
                  ))}
                  <option value="P-204">P-204 — Crude Charge Pump A</option>
                  <option value="HX-301">HX-301 — Pre-Heat Exchanger Bank</option>
                  <option value="V-112">V-112 — High Pressure Separator</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Priority Level
                </label>
                <select
                  value={woPriority}
                  onChange={(e) => setWoPriority(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-sm text-[#0B1F3A] font-medium focus:outline-hidden focus:border-blue-600"
                >
                  <option value="P1 - EMERGENCY / ENVIRONMENTAL">P1 - EMERGENCY / ENVIRONMENTAL</option>
                  <option value="P2 - HIGH (Immediate 24h Action)">P2 - HIGH (Immediate 24h Action)</option>
                  <option value="P3 - MEDIUM (Scheduled Next PM)">P3 - MEDIUM (Scheduled Next PM)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Identified Failure Mode
                </label>
                <input
                  type="text"
                  value={woFailure}
                  onChange={(e) => setWoFailure(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-sm text-[#0B1F3A] focus:outline-hidden focus:border-blue-600"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Field Narrative &amp; Symptoms
                </label>
                <textarea
                  rows={4}
                  value={woDesc}
                  onChange={(e) => setWoDesc(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-sm text-[#0B1F3A] focus:outline-hidden focus:border-blue-600"
                />
              </div>

              <button
                type="submit"
                disabled={woSubmitting}
                className="w-full py-3 bg-[#14315C] hover:bg-[#1C4176] disabled:bg-[#CBD3E0] text-white font-semibold text-sm rounded-xl flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm"
              >
                {woSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Dispatching to local CMMS...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Generate Work Order</span>
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {woResult ? (
              <div className="bg-white border border-[#E2E6ED] rounded-2xl p-6 shadow-2xs space-y-6">
                <div className="flex items-center gap-3 pb-4 border-b border-[#E2E6ED]">
                  <div className="p-2.5 bg-[#E4F5EC] text-[#12875D] rounded-xl">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A]">
                      Work Order Generated &amp; Persisted
                    </h3>
                    <p className="font-[family-name:var(--font-mono)] text-xs text-[#51607A]">
                      Dispatched via Maintenance Engineering Agent &middot; {woAsset}
                    </p>
                  </div>
                </div>

                <div className="text-sm text-[#0B1F3A] leading-relaxed whitespace-pre-wrap bg-[#FAFBFC] p-4 rounded-xl border border-[#E2E6ED]">
                  {woResult.answer || JSON.stringify(woResult, null, 2)}
                </div>

                <CitationCard citations={woResult.citations || []} />
                <ActionsChecklist actions={woResult.recommended_actions || []} keyPrefix="wo_act" />

                <div className="pt-3 border-t border-[#E2E6ED] flex justify-between items-center text-xs font-[family-name:var(--font-mono)] text-[#51607A]">
                  <span className="flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-blue-600" /> Backend: {woResult.model_backend || "OpenVINO INT4"}
                  </span>
                  <span>Confidence: {woResult.confidence || "HIGH"}</span>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-[#CBD3E0] rounded-2xl p-16 text-center text-[#51607A] space-y-3 bg-white">
                <Wrench className="w-12 h-12 mx-auto text-[#CBD3E0]" />
                <div className="font-[family-name:var(--font-display)] font-bold text-base text-[#0B1F3A]">
                  Ready for Work Order Creation
                </div>
                <p className="text-xs max-w-md mx-auto leading-relaxed">
                  Fill out asset parameters and click generate to trigger maintenance agent validation against historical failure modes and spare part availability.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 3: 5-Why RCA Explorer */}
      {activeTab === "rca" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 bg-white border border-[#E2E6ED] rounded-xl p-6 shadow-2xs space-y-5">
            <div className="flex items-center gap-2 font-[family-name:var(--font-display)] font-bold text-sm uppercase tracking-wider text-[#0B1F3A]">
              <ShieldAlert className="w-4 h-4 text-amber-600" />
              <span>5-Why Investigation Scope</span>
            </div>

            <form onSubmit={handleRunRCA} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Target Asset Tag
                </label>
                <select
                  value={rcaAsset}
                  onChange={(e) => setRcaAsset(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-sm text-[#0B1F3A] font-semibold focus:outline-hidden focus:border-blue-600"
                >
                  {assets.map((a) => (
                    <option key={a.asset_tag} value={a.asset_tag}>
                      {a.asset_tag} — {a.name}
                    </option>
                  ))}
                  <option value="P-204">P-204 — Crude Charge Pump A</option>
                  <option value="C-401">C-401 — Make-up Gas Compressor</option>
                  <option value="V-205">V-205 — Refinery Blowdown Drum</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-1.5">
                  Observed Failure Symptom / Incident
                </label>
                <textarea
                  rows={5}
                  value={rcaSymptom}
                  onChange={(e) => setRcaSymptom(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-sm text-[#0B1F3A] focus:outline-hidden focus:border-blue-600"
                />
              </div>

              <button
                type="submit"
                disabled={rcaSubmitting}
                className="w-full py-3 bg-[#14315C] hover:bg-[#1C4176] disabled:bg-[#CBD3E0] text-white font-semibold text-sm rounded-xl flex items-center justify-center gap-2 transition-all cursor-pointer shadow-sm"
              >
                {rcaSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Traversing Graph Failure Chains...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-[#F2A73B]" />
                    <span>Execute 5-Why Root Cause Analysis</span>
                  </>
                )}
              </button>
            </form>
          </div>

          <div className="lg:col-span-2 space-y-6">
            {rcaResult ? (
              <div className="bg-white border border-[#E2E6ED] rounded-2xl p-6 shadow-2xs space-y-6">
                <div className="flex items-center gap-3 pb-4 border-b border-[#E2E6ED]">
                  <div className="p-2.5 bg-amber-50 text-amber-600 rounded-xl">
                    <ShieldAlert className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A]">
                      5-Why Root Cause Analysis Report
                    </h3>
                    <p className="font-[family-name:var(--font-mono)] text-xs text-[#51607A]">
                      Generated from multi-hop knowledge graph relationships &middot; {rcaAsset}
                    </p>
                  </div>
                </div>

                <div className="text-sm text-[#0B1F3A] leading-relaxed whitespace-pre-wrap bg-[#FAFBFC] p-5 rounded-xl border border-[#E2E6ED]">
                  {rcaResult.answer || JSON.stringify(rcaResult, null, 2)}
                </div>

                <CitationCard citations={rcaResult.citations || []} />
                <ActionsChecklist actions={rcaResult.recommended_actions || []} keyPrefix="rca_act" />

                <div className="pt-3 border-t border-[#E2E6ED] flex justify-between items-center text-xs font-[family-name:var(--font-mono)] text-[#51607A]">
                  <span className="flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-blue-600" /> Backend: {rcaResult.model_backend || "OpenVINO INT4"}
                  </span>
                  <span>Confidence: {rcaResult.confidence || "HIGH"}</span>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-[#CBD3E0] rounded-2xl p-16 text-center text-[#51607A] space-y-3 bg-white">
                <ShieldAlert className="w-12 h-12 mx-auto text-[#CBD3E0]" />
                <div className="font-[family-name:var(--font-display)] font-bold text-base text-[#0B1F3A]">
                  5-Why Analysis Engine Ready
                </div>
                <p className="text-xs max-w-md mx-auto leading-relaxed">
                  Enter an observed symptom to let the maintenance agent trace causality paths across historical incidents, work orders, and failure mode nodes.
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
