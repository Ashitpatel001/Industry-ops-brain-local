"use strict";
import React from "react";

interface HeroHeaderProps {
  eyebrow: string;
  title: string;
  subtitle: string;
  sheetNo?: string;
}

export default function HeroHeader({ eyebrow, title, subtitle, sheetNo = "OB / 00" }: HeroHeaderProps) {
  return (
    <div className="relative overflow-hidden bg-[#14315C] rounded-2xl p-8 md:p-10 mb-8 border border-[#0E2647] shadow-lg text-white select-none">
      {/* Blueprint grid backdrop overlay */}
      <div
        className="absolute inset-0 opacity-15 pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.4) 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* Sheet Number Corner Stamp */}
      <div className="absolute top-5 right-6 font-[family-name:var(--font-mono)] text-xs text-white/60 tracking-widest bg-white/10 px-2.5 py-1 rounded border border-white/15">
        {sheetNo}
      </div>

      <div className="relative z-10 max-w-3xl">
        <div className="font-[family-name:var(--font-mono)] text-xs md:text-sm tracking-widest uppercase text-[#F2A73B] font-semibold mb-2">
          {eyebrow}
        </div>
        <h1 className="font-[family-name:var(--font-display)] font-bold text-2xl md:text-4xl text-white mb-3.5 leading-tight tracking-tight">
          {title}
        </h1>
        <p className="text-sm md:text-base text-[#C6D0E2] leading-relaxed">
          {subtitle}
        </p>
      </div>
    </div>
  );
}
