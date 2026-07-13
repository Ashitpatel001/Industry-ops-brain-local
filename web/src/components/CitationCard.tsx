"use client";
import React, { useState } from "react";
import { ChevronDown, ChevronUp, FileText, ExternalLink } from "lucide-react";

export interface CitationItem {
  id?: string;
  doc_id?: string;
  title?: string;
  score?: number;
  snippet?: string;
  text?: string;
}

interface CitationCardProps {
  citations: CitationItem[];
}

export default function CitationCard({ citations }: CitationCardProps) {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  if (!citations || citations.length === 0) return null;

  return (
    <div className="mt-5 space-y-2.5">
      <div className="flex items-center gap-2 font-[family-name:var(--font-display)] font-bold text-xs uppercase tracking-wider text-[#51607A]">
        <FileText className="w-3.5 h-3.5 text-[#2563EB]" />
        <span>Referenced Documents ({citations.length})</span>
      </div>

      <div className="space-y-2">
        {citations.map((cit, idx) => {
          const refId = cit.id || `[${idx + 1}]`;
          const docId = cit.doc_id || "";
          const title = cit.title || docId || `Document ${idx + 1}`;
          const score = cit.score || 0.0;
          const scorePct = score <= 1.0 ? Math.round(score * 100) : Math.round(score);
          const snippet = cit.snippet || cit.text || "No preview available.";
          const isOpen = openIdx === idx;

          let barColor = "bg-[#2563EB]";
          let textColor = "text-[#2563EB]";
          if (scorePct >= 80) {
            barColor = "bg-[#12875D]";
            textColor = "text-[#12875D]";
          } else if (scorePct >= 60) {
            barColor = "bg-[#B7791F]";
            textColor = "text-[#B7791F]";
          }

          return (
            <div
              key={idx}
              className="border border-[#E2E6ED] rounded-xl bg-[#FAFBFC] overflow-hidden transition-all shadow-2xs"
            >
              <button
                type="button"
                onClick={() => setOpenIdx(isOpen ? null : idx)}
                className="w-full flex items-center justify-between p-3.5 text-left hover:bg-white transition-colors"
              >
                <div className="flex items-center gap-2.5 pr-4">
                  <span className="font-[family-name:var(--font-mono)] text-xs font-bold text-[#14315C] bg-[#EEF2F9] px-2 py-0.5 rounded">
                    {refId}
                  </span>
                  <span className="font-semibold text-sm text-[#0B1F3A] truncate max-w-md">
                    {title}
                  </span>
                </div>
                <div className="flex items-center gap-3 shrink-0">
                  <span className={`font-[family-name:var(--font-mono)] text-xs font-bold ${textColor}`}>
                    {scorePct}% MATCH
                  </span>
                  {isOpen ? (
                    <ChevronUp className="w-4 h-4 text-[#51607A]" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-[#51607A]" />
                  )}
                </div>
              </button>

              {isOpen && (
                <div className="px-4 pb-4 pt-1 border-t border-[#E2E6ED]/60 bg-white">
                  <div className="flex justify-between items-center text-[11px] font-[family-name:var(--font-mono)] text-[#51607A] mb-2">
                    <span>DOC ID: {docId || "LOCAL_INDEX"}</span>
                    <span>RELEVANCE SCORE: {score.toFixed(3)}</span>
                  </div>
                  <div className="h-1.5 w-full bg-[#E2E6ED] rounded-full overflow-hidden mb-3">
                    <div className={`h-full ${barColor} rounded-full`} style={{ width: `${Math.min(100, scorePct)}%` }} />
                  </div>
                  <p className="text-xs md:text-sm text-[#28344A] italic leading-relaxed bg-[#FAFBFC] p-3 rounded-lg border border-[#E2E6ED]/80">
                    &ldquo;{snippet}&rdquo;
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
