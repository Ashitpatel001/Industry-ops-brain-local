"use strict";
import React from "react";
import Link from "next/link";
import HeroHeader from "@/components/HeroHeader";
import { MessageSquare, Wrench, ShieldCheck, ArrowRight, Activity, Database, CheckCircle2 } from "lucide-react";

export default function HomePage() {
  const modules = [
    {
      href: "/copilot",
      icon: MessageSquare,
      title: "Ask Plant Co-Pilot",
      desc: "Query SOPs, engineering drawings, and maintenance history in natural language, with verified citations and confidence scores attached to every answer.",
      accent: "border-t-blue-600",
      iconBg: "bg-blue-50 text-blue-600",
      sheetNo: "OB/02",
    },
    {
      href: "/maintenance",
      icon: Wrench,
      title: "Maintenance & RCA",
      desc: "Run 5-Why root cause analyses, track MTBF-based asset risk scores, and dispatch CMMS work orders straight from a diagnostic finding.",
      accent: "border-t-emerald-600",
      iconBg: "bg-emerald-50 text-emerald-600",
      sheetNo: "OB/05",
    },
    {
      href: "/compliance",
      icon: ShieldCheck,
      title: "Compliance Audit",
      desc: "Verify plant operations against OISD-116, Factory Act 1948, and PESO rules using a deterministic evidence-matrix gap detection engine.",
      accent: "border-t-amber-600",
      iconBg: "bg-amber-50 text-amber-600",
      sheetNo: "OB/04",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Executive Hero */}
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Command Center"
        title="Welcome back to the plant floor, digitised."
        subtitle="An air-gapped operations command center for refineries, chemical plants, and heavy manufacturing sites — hardware-accelerated, multi-agent reasoning turning SOPs, inspection logs, and engineering drawings into instant, verifiable reliability decisions."
        sheetNo="OB / HOME"
      />

      {/* Section 01: Choose Module */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <span className="font-[family-name:var(--font-mono)] text-xs font-bold bg-[#14315C] text-white px-2 py-0.5 rounded">
            01
          </span>
          <h2 className="font-[family-name:var(--font-display)] font-bold text-base uppercase tracking-wider text-[#0B1F3A]">
            Choose an Industrial Module
          </h2>
          <div className="flex-1 h-px bg-[#E2E6ED]" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {modules.map((m) => {
            const Icon = m.icon;
            return (
              <Link
                key={m.href}
                href={m.href}
                className={`bg-white border border-[#E2E6ED] border-t-4 ${m.accent} rounded-xl p-6 shadow-2xs hover:shadow-md transition-all duration-150 flex flex-col justify-between group`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl ${m.iconBg}`}>
                      <Icon className="w-6 h-6" />
                    </div>
                    <span className="font-[family-name:var(--font-mono)] text-xs text-[#51607A] font-semibold">
                      {m.sheetNo}
                    </span>
                  </div>
                  <h3 className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A] mb-2 group-hover:text-blue-600 transition-colors">
                    {m.title}
                  </h3>
                  <p className="text-xs md:text-sm text-[#51607A] leading-relaxed mb-6">
                    {m.desc}
                  </p>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-[#E2E6ED]/60 font-semibold text-xs text-[#14315C] group-hover:text-blue-600">
                  <span>Launch Studio</span>
                  <ArrowRight className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Section 02: Working with Asset Tags */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <span className="font-[family-name:var(--font-mono)] text-xs font-bold bg-[#14315C] text-white px-2 py-0.5 rounded">
            02
          </span>
          <h2 className="font-[family-name:var(--font-display)] font-bold text-base uppercase tracking-wider text-[#0B1F3A]">
            Working with Plant Asset Tags
          </h2>
          <div className="flex-1 h-px bg-[#E2E6ED]" />
        </div>

        <div className="bg-white border border-[#E2E6ED] rounded-xl p-6 shadow-2xs flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="space-y-1">
            <div className="font-semibold text-sm text-[#0B1F3A] flex items-center gap-2">
              <Database className="w-4 h-4 text-[#2563EB]" />
              <span>Context-Scoped Multi-Agent Routing</span>
            </div>
            <p className="text-xs md:text-sm text-[#51607A]">
              Every module recognises standard industrial equipment tags (e.g.{" "}
              <code className="font-[family-name:var(--font-mono)] font-semibold text-[#14315C] bg-[#EEF2F9] px-1.5 py-0.5 rounded">
                P-204
              </code>
              ,{" "}
              <code className="font-[family-name:var(--font-mono)] font-semibold text-[#14315C] bg-[#EEF2F9] px-1.5 py-0.5 rounded">
                HX-301
              </code>
              ,{" "}
              <code className="font-[family-name:var(--font-mono)] font-semibold text-[#14315C] bg-[#EEF2F9] px-1.5 py-0.5 rounded">
                V-112
              </code>
              ). Scope answers to specific pumps, vessels, or heat exchangers for sub-second precision.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <Link
              href="/graph"
              className="px-4 py-2 bg-[#14315C] text-white rounded-lg font-semibold text-xs hover:bg-[#1C4176] transition-colors flex items-center gap-2"
            >
              <span>Explore Asset Graph</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* System Highlights Banner */}
      <div className="bg-[#14315C] text-[#E7ECF6] rounded-xl p-6 border border-[#1C4176] grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-[#3DD68C] shrink-0 mt-0.5" />
          <div>
            <div className="font-[family-name:var(--font-display)] font-bold text-sm text-white">
              OpenVINO INT4 Acceleration
            </div>
            <div className="text-xs text-[#9AABC9] mt-0.5">
              Optimized for local consumer Intel Core / Ultra CPUs and Arc GPUs.
            </div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-[#3DD68C] shrink-0 mt-0.5" />
          <div>
            <div className="font-[family-name:var(--font-display)] font-bold text-sm text-white">
              Hybrid Vector + Graph Retrieval
            </div>
            <div className="text-xs text-[#9AABC9] mt-0.5">
              ChromaDB chunks paired with NetworkX relational multi-hop reasoning.
            </div>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-[#3DD68C] shrink-0 mt-0.5" />
          <div>
            <div className="font-[family-name:var(--font-display)] font-bold text-sm text-white">
              Deterministic Compliance Audit
            </div>
            <div className="text-xs text-[#9AABC9] mt-0.5">
              Instant matrix validation against OISD-116 and Factory Act 1948.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
