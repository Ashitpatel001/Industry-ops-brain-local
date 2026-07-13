"use client";
import React, { useState } from "react";
import HeroHeader from "@/components/HeroHeader";
import { UploadCloud, FileCheck, AlertCircle, Loader2, Database, Network, Layers, CheckCircle2 } from "lucide-react";

interface IngestResponse {
  doc_id: string;
  filename: string;
  status: string;
  chunks_indexed: number;
  entities_extracted: number;
  graph_nodes_added: number;
  graph_edges_added: number;
}

const DOC_TYPES = [
  { value: "sop", label: "Standard Operating Procedure (SOP)" },
  { value: "manual", label: "Equipment OEM Manual / Datasheet" },
  { value: "drawing", label: "Engineering Drawing / P&ID Narrative" },
  { value: "regulation", label: "Safety Standard / Regulation (OISD / PESO)" },
  { value: "incident_report", label: "Root Cause / Incident Investigation Report" },
];

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState("sop");
  const [chunkSize, setChunkSize] = useState(600);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IngestResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
      setError(null);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to ingest.");
      return;
    }

    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);
      formData.append("chunk_size", chunkSize.toString());

      const response = await fetch("http://127.0.0.1:8000/api/v1/ingest", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Upload failed with HTTP status ${response.status}`);
      }

      const data: IngestResponse = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred during ingestion.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Ingestion Studio"
        title="Ingest &amp; Structure Plant Knowledge."
        subtitle="Upload raw PDF manuals, Excel equipment rosters, and text SOPs. Our local pipeline performs Docling layout OCR, Sentence-Transformer vector embedding, and spaCy NER extraction to expand the ChromaDB vector store and NetworkX knowledge graph."
        sheetNo="OB / 01"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Upload Form */}
        <div className="lg:col-span-1 bg-white border border-[#E2E6ED] rounded-xl p-6 shadow-2xs space-y-6">
          <div className="flex items-center gap-2 font-[family-name:var(--font-display)] font-bold text-sm uppercase tracking-wider text-[#0B1F3A]">
            <UploadCloud className="w-4 h-4 text-blue-600" />
            <span>Document Parameter Setup</span>
          </div>

          <form onSubmit={handleUpload} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-2">
                1. Select Document Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="w-full px-3 py-2.5 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-sm text-[#0B1F3A] font-medium focus:outline-hidden focus:border-blue-600 transition-colors"
              >
                {DOC_TYPES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-2">
                2. Target Vector Chunk Size (tokens)
              </label>
              <input
                type="number"
                min={200}
                max={2000}
                step={50}
                value={chunkSize}
                onChange={(e) => setChunkSize(parseInt(e.target.value) || 600)}
                className="w-full px-3 py-2 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-sm text-[#0B1F3A] focus:outline-hidden focus:border-blue-600 transition-colors"
              />
              <p className="text-[11px] text-[#51607A] mt-1">
                Recommended: 600 tokens for SOPs, 400 for high-density tables.
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-[#51607A] mb-2">
                3. Choose Local File
              </label>
              <label className="border-2 border-dashed border-[#CBD3E0] hover:border-blue-600 rounded-xl p-6 flex flex-col items-center justify-center text-center cursor-pointer bg-[#FAFBFC] hover:bg-blue-50/30 transition-all group">
                <UploadCloud className="w-8 h-8 text-[#51607A] group-hover:text-blue-600 mb-2 transition-colors" />
                <span className="text-sm font-semibold text-[#0B1F3A] group-hover:text-blue-600">
                  {file ? file.name : "Click or drag file here"}
                </span>
                <span className="text-xs text-[#51607A] mt-1">
                  Supports PDF, TXT, MD, CSV, XLSX
                </span>
                <input
                  type="file"
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf,.txt,.md,.csv,.xlsx"
                />
              </label>
            </div>

            <button
              type="submit"
              disabled={loading || !file}
              className={`w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-sm ${
                loading || !file
                  ? "bg-[#CBD3E0] text-white cursor-not-allowed"
                  : "bg-[#14315C] hover:bg-[#1C4176] text-white cursor-pointer"
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing &amp; Indexing Locally...</span>
                </>
              ) : (
                <>
                  <FileCheck className="w-4 h-4" />
                  <span>Ingest &amp; Extract Entities</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Ingestion Status & Live Extraction Metrics */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="bg-[#FBE7E4] border border-[#F0BEB6] text-[#8C2A22] rounded-xl p-4 flex items-start gap-3 shadow-2xs">
              <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <div className="font-bold text-sm">Ingestion Pipeline Error</div>
                <div className="text-xs mt-1 leading-relaxed">{error}</div>
              </div>
            </div>
          )}

          {result && (
            <div className="bg-white border border-[#E2E6ED] border-t-4 border-t-[#12875D] rounded-xl p-6 shadow-2xs space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 bg-[#E4F5EC] text-[#12875D] rounded-xl">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A]">
                      Document Ingestion Completed
                    </h3>
                    <p className="font-[family-name:var(--font-mono)] text-xs text-[#51607A]">
                      ID: {result.doc_id} &middot; File: {result.filename}
                    </p>
                  </div>
                </div>
                <span className="font-[family-name:var(--font-mono)] text-xs font-bold bg-[#E4F5EC] text-[#12875D] px-3 py-1 rounded-full border border-[#BEE7D3]">
                  {result.status.toUpperCase()}
                </span>
              </div>

              {/* Extraction Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
                <div className="bg-[#FAFBFC] border border-[#E2E6ED] rounded-xl p-4 text-center">
                  <div className="flex justify-center mb-1 text-blue-600">
                    <Layers className="w-5 h-5" />
                  </div>
                  <div className="font-[family-name:var(--font-mono)] font-bold text-xl text-[#0B1F3A]">
                    {result.chunks_indexed}
                  </div>
                  <div className="text-xs text-[#51607A] font-medium mt-1">Vector Chunks</div>
                </div>

                <div className="bg-[#FAFBFC] border border-[#E2E6ED] rounded-xl p-4 text-center">
                  <div className="flex justify-center mb-1 text-emerald-600">
                    <Database className="w-5 h-5" />
                  </div>
                  <div className="font-[family-name:var(--font-mono)] font-bold text-xl text-[#0B1F3A]">
                    {result.entities_extracted}
                  </div>
                  <div className="text-xs text-[#51607A] font-medium mt-1">NER Entities</div>
                </div>

                <div className="bg-[#FAFBFC] border border-[#E2E6ED] rounded-xl p-4 text-center">
                  <div className="flex justify-center mb-1 text-amber-600">
                    <Network className="w-5 h-5" />
                  </div>
                  <div className="font-[family-name:var(--font-mono)] font-bold text-xl text-[#0B1F3A]">
                    {result.graph_nodes_added}
                  </div>
                  <div className="text-xs text-[#51607A] font-medium mt-1">Graph Nodes</div>
                </div>

                <div className="bg-[#FAFBFC] border border-[#E2E6ED] rounded-xl p-4 text-center">
                  <div className="flex justify-center mb-1 text-indigo-600">
                    <Network className="w-5 h-5" />
                  </div>
                  <div className="font-[family-name:var(--font-mono)] font-bold text-xl text-[#0B1F3A]">
                    {result.graph_edges_added}
                  </div>
                  <div className="text-xs text-[#51607A] font-medium mt-1">Graph Edges</div>
                </div>
              </div>

              <div className="p-4 bg-[#EEF2F9] rounded-xl border border-[#D5E1F2] text-xs text-[#14315C] flex items-center justify-between">
                <span>
                  <strong>Knowledge Store Updated:</strong> ChromaDB and NetworkX multi-graph (`metadata.db`) have synced your new document.
                </span>
              </div>
            </div>
          )}

          {!result && !loading && (
            <div className="border-2 border-dashed border-[#CBD3E0] rounded-xl p-12 text-center text-[#51607A] space-y-3 bg-white">
              <UploadCloud className="w-12 h-12 mx-auto text-[#CBD3E0]" />
              <div className="font-[family-name:var(--font-display)] font-bold text-base text-[#0B1F3A]">
                No Ingestions Active
              </div>
              <p className="text-xs max-w-md mx-auto leading-relaxed">
                Select a document on the left panel to execute layout OCR, chunking, and local vector + knowledge graph indexing.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
