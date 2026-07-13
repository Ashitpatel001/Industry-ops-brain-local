"use strict";
import React from "react";
import { ShieldCheck } from "lucide-react";

export default function PrivacyBanner() {
  return (
    <div className="flex flex-wrap items-center justify-between bg-white border border-[#E2E6ED] border-l-4 border-l-[#12875D] rounded-xl px-5 py-3 mb-6 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="relative flex h-3 w-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#12875D] opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-[#12875D]"></span>
        </div>
        <div>
          <span className="font-[family-name:var(--font-display)] font-bold text-sm text-[#0B1F3A] tracking-wide mr-2">
            AIR-GAPPED &amp; OFFLINE
          </span>
          <span className="text-xs md:text-sm text-[#51607A]">
            &mdash; zero cloud telemetry. Weights, indexes, and inference all run locally on-premise.
          </span>
        </div>
      </div>
      <div className="flex items-center gap-2 mt-2 sm:mt-0 font-[family-name:var(--font-mono)] text-xs font-semibold text-[#0F5C3E] bg-[#E4F5EC] border border-[#BEE7D3] px-3 py-1 rounded-full">
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>ON-PREMISE ONLY</span>
      </div>
    </div>
  );
}
