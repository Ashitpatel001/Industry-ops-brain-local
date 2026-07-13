"use client";
import React, { useState, useEffect } from "react";
import HeroHeader from "@/components/HeroHeader";
import { ShieldCheck, AlertTriangle, CheckCircle2, Download, RefreshCw, FileText, Loader2 } from "lucide-react";

interface GapItem {
  reg_id: string;
  standard: string;
  clause: string;
  title: string;
  status: "COMPLIANT" | "OPEN GAP" | string;
  severity?: string;
  details?: string;
}

interface ComplianceResponse {
  gap_report: GapItem[];
  evidence_package?: any;
  regulations_indexed?: any[];
  total_gaps?: number;
}

export default function CompliancePage() {
  const [data, setData] = useState<ComplianceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState("ALL");

  const fetchCompliance = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/compliance", { cache: "no-store" });
      if (!res.ok) {
        throw new Error(`Failed to fetch compliance audit (HTTP ${res.status})`);
      }
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "An error occurred while connecting to the local compliance engine.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompliance();
  }, []);

  const handleDownloadPackage = () => {
    if (!data) return;
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `OpsBrain_Compliance_Evidence_${new Date().toISOString().split("T")[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const gapReport = data?.gap_report || [];
  const filteredReport = gapReport.filter((item) => {
    if (filterStatus === "ALL") return true;
    if (filterStatus === "COMPLIANT") return item.status?.toUpperCase() === "COMPLIANT";
    if (filterStatus === "OPEN GAP") return item.status?.toUpperCase() !== "COMPLIANT";
    return true;
  });

  const compliantCount = gapReport.filter((i) => i.status?.toUpperCase() === "COMPLIANT").length;
  const openGapCount = gapReport.length - compliantCount;

  return (
    <div className="space-y-6">
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Regulatory Studio"
        title="Automated Statutory Compliance Audit."
        subtitle="Deterministic evidence matrix cross-referencing live telemetry, work order history, and SOP logs against mandatory OISD-116 (Fire Safety), OISD-GDN-192 (Confined Space Entry), and Factory Act 1948 regulations."
        sheetNo="OB / 04"
      />

      {/* Control & KPI Bar */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-[#51607A] uppercase">Total Standards Checked</div>
            <div className="font-[family-name:var(--font-mono)] font-bold text-2xl text-[#0B1F3A] mt-1">
              {gapReport.length}
            </div>
          </div>
          <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
            <FileText className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-[#51607A] uppercase">Fully Compliant Clauses</div>
            <div className="font-[family-name:var(--font-mono)] font-bold text-2xl text-[#12875D] mt-1">
              {compliantCount}
            </div>
          </div>
          <div className="p-3 bg-[#E4F5EC] text-[#12875D] rounded-xl">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex items-center justify-between">
          <div>
            <div className="text-xs font-semibold text-[#51607A] uppercase">Open Statutory Gaps</div>
            <div className="font-[family-name:var(--font-mono)] font-bold text-2xl text-[#C0362C] mt-1">
              {openGapCount}
            </div>
          </div>
          <div className="p-3 bg-[#FBE7E4] text-[#C0362C] rounded-xl">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex items-center justify-between">
          <button
            onClick={handleDownloadPackage}
            disabled={!data || loading}
            className="w-full h-full py-2 bg-[#14315C] hover:bg-[#1C4176] disabled:bg-[#CBD3E0] text-white rounded-lg font-semibold text-xs flex flex-col items-center justify-center gap-1.5 transition-all cursor-pointer shadow-sm"
          >
            <Download className="w-5 h-5" />
            <span>Export Evidence Package (.JSON)</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs & Refresh */}
      <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex items-center justify-between">
        <div className="flex items-center gap-2">
          {["ALL", "COMPLIANT", "OPEN GAP"].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-4 py-1.5 rounded-lg font-[family-name:var(--font-mono)] text-xs font-bold transition-colors ${
                filterStatus === status
                  ? "bg-[#14315C] text-white shadow-2xs"
                  : "bg-[#FAFBFC] text-[#51607A] hover:bg-[#EEF2F9]"
              }`}
            >
              {status} {status === "ALL" ? `(${gapReport.length})` : status === "COMPLIANT" ? `(${compliantCount})` : `(${openGapCount})`}
            </button>
          ))}
        </div>

        <button
          onClick={fetchCompliance}
          disabled={loading}
          className="px-3 py-1.5 bg-[#FAFBFC] hover:bg-[#EEF2F9] border border-[#E2E6ED] text-[#14315C] font-semibold text-xs rounded-lg flex items-center gap-1.5 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
          <span>Re-run Local Audit</span>
        </button>
      </div>

      {error && (
        <div className="bg-[#FBE7E4] border border-[#F0BEB6] text-[#8C2A22] rounded-xl p-4 text-xs font-semibold flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Evidence Table */}
      <div className="bg-white border border-[#E2E6ED] rounded-2xl overflow-hidden shadow-2xs">
        {loading ? (
          <div className="p-16 text-center text-[#51607A] space-y-3">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-blue-600" />
            <div className="font-semibold text-sm">Evaluating Plant Evidence Matrix...</div>
          </div>
        ) : filteredReport.length === 0 ? (
          <div className="p-16 text-center text-[#51607A] space-y-2">
            <ShieldCheck className="w-10 h-10 mx-auto text-[#CBD3E0]" />
            <div className="font-semibold text-sm text-[#0B1F3A]">No matching regulatory items</div>
            <p className="text-xs">Adjust status filter above or run seed.py to populate statutory rules.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-[#FAFBFC] border-b border-[#E2E6ED] font-[family-name:var(--font-mono)] text-xs font-semibold text-[#51607A] uppercase tracking-wider">
                  <th className="py-3.5 px-6">Clause ID</th>
                  <th className="py-3.5 px-6">Standard &amp; Requirement</th>
                  <th className="py-3.5 px-6">Severity</th>
                  <th className="py-3.5 px-6">Audit Status</th>
                  <th className="py-3.5 px-6">Telemetry &amp; Evidence Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E2E6ED]">
                {filteredReport.map((item, idx) => {
                  const isCompliant = item.status?.toUpperCase() === "COMPLIANT";
                  return (
                    <tr key={idx} className="hover:bg-[#FAFBFC] transition-colors text-xs md:text-sm">
                      <td className="py-4 px-6 font-[family-name:var(--font-mono)] font-bold text-[#14315C] whitespace-nowrap">
                        {item.reg_id || `CLAUSE-${idx + 1}`}
                      </td>
                      <td className="py-4 px-6 max-w-md">
                        <div className="font-[family-name:var(--font-display)] font-bold text-[#0B1F3A]">
                          {item.title || item.standard} {item.clause ? `— Clause ${item.clause}` : ""}
                        </div>
                        <div className="text-xs text-[#51607A] mt-1 leading-relaxed">
                          {item.standard}
                        </div>
                      </td>
                      <td className="py-4 px-6 whitespace-nowrap">
                        <span
                          className={`font-[family-name:var(--font-mono)] text-[11px] font-bold px-2 py-1 rounded ${
                            item.severity === "HIGH" || item.severity === "CRITICAL"
                              ? "bg-[#FBE7E4] text-[#C0362C]"
                              : "bg-[#FEF6EC] text-[#B7791F]"
                          }`}
                        >
                          {item.severity || "MANDATORY"}
                        </span>
                      </td>
                      <td className="py-4 px-6 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1.5 font-[family-name:var(--font-mono)] text-xs font-bold px-3 py-1 rounded-full border ${
                            isCompliant
                              ? "bg-[#E4F5EC] text-[#12875D] border-[#BEE7D3]"
                              : "bg-[#FBE7E4] text-[#C0362C] border-[#F0BEB6]"
                          }`}
                        >
                          {isCompliant ? (
                            <CheckCircle2 className="w-3.5 h-3.5" />
                          ) : (
                            <AlertTriangle className="w-3.5 h-3.5" />
                          )}
                          <span>{item.status?.toUpperCase() || "OPEN GAP"}</span>
                        </span>
                      </td>
                      <td className="py-4 px-6 text-xs text-[#28344A] italic bg-[#FAFBFC]/50 max-w-lg leading-relaxed">
                        {item.details || "Telemetry verified against active CMMS work orders and SOP thresholds."}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
