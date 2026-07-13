"use client";
import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  UploadCloud,
  MessageSquare,
  Network,
  ShieldCheck,
  Wrench,
  Activity,
  Cpu,
  Clock,
  Database,
} from "lucide-react";

interface HealthState {
  status: string;
  model_loaded: boolean;
  backend: string;
  ram_used_gb: number;
  ram_total_gb: number;
  cpu_percent: number;
  uptime_seconds: number;
}

const NAV_ITEMS = [
  { href: "/", label: "Command Center", icon: LayoutDashboard, sheetNo: "OB/HOME" },
  { href: "/upload", label: "Ingestion Studio", icon: UploadCloud, sheetNo: "OB/01" },
  { href: "/copilot", label: "Ask Plant Co-Pilot", icon: MessageSquare, sheetNo: "OB/02" },
  { href: "/graph", label: "Graph Explorer", icon: Network, sheetNo: "OB/03" },
  { href: "/compliance", label: "Compliance Audit", icon: ShieldCheck, sheetNo: "OB/04" },
  { href: "/maintenance", label: "Maintenance & RCA", icon: Wrench, sheetNo: "OB/05" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [health, setHealth] = useState<HealthState | null>(null);
  const [isReachable, setIsReachable] = useState(false);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/health", { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
          setIsReachable(true);
        } else {
          setIsReachable(false);
        }
      } catch {
        setIsReachable(false);
      }
    };

    fetchHealth();
    const interval = setInterval(fetchHealth, 4000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (seconds: number) => {
    if (!seconds || isNaN(seconds)) return "—";
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins < 60) return `${mins}m ${secs}s`;
    const hours = Math.floor(mins / 60);
    return `${hours}h ${mins % 60}m`;
  };

  return (
    <aside className="w-72 bg-[#14315C] text-[#E7ECF6] flex flex-col border-r border-white/10 shrink-0 min-h-screen select-none">
      {/* Brand & Title */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 bg-blue-600 rounded-lg text-white font-bold shadow-md">
            <Activity className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h1 className="font-[family-name:var(--font-display)] font-bold text-lg text-white tracking-tight">
              Ops Brain Local
            </h1>
            <p className="font-[family-name:var(--font-mono)] text-[10px] text-[#9AABC9] tracking-widest uppercase">
              INDUSTRIAL AI ENGINE &middot; v1.0
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 p-4 space-y-1.5">
        <div className="px-3 pb-2 font-[family-name:var(--font-mono)] text-[11px] font-semibold text-[#9AABC9] uppercase tracking-wider">
          Modules &amp; Sheets
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-3.5 py-2.5 rounded-lg transition-all duration-150 group ${
                isActive
                  ? "bg-white/15 text-white font-semibold border-l-4 border-[#F2A73B] shadow-sm"
                  : "text-[#CBD3E0] hover:bg-white/10 hover:text-white"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-[#F2A73B]" : "text-[#9AABC9] group-hover:text-white"}`} />
                <span className="text-sm">{item.label}</span>
              </div>
              <span className="font-[family-name:var(--font-mono)] text-[10px] text-[#9AABC9] opacity-75 group-hover:opacity-100">
                {item.sheetNo}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* Asset Tag Chips Reference */}
      <div className="p-4 mx-4 mb-4 rounded-xl bg-white/5 border border-white/10">
        <div className="font-[family-name:var(--font-display)] text-[11px] font-bold uppercase text-[#C6D0E2] tracking-wider mb-2 flex items-center justify-between">
          <span>Key Plant Asset Tags</span>
          <Database className="w-3.5 h-3.5 text-[#9AABC9]" />
        </div>
        <div className="flex flex-wrap gap-1.5 font-[family-name:var(--font-mono)] text-xs">
          {["P-204", "HX-301", "V-112", "C-401", "T-501"].map((tag) => (
            <span
              key={tag}
              className="px-2 py-0.5 rounded bg-[#1C4176] text-[#E7ECF6] border border-white/15 hover:border-[#F2A73B] transition-colors cursor-pointer"
              title={`Asset Tag ${tag}`}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Live Engine Diagnostics Instrument Card */}
      <div className="p-4 m-4 rounded-xl bg-white/5 border border-white/10 shadow-inner">
        <div className="flex items-center justify-between font-[family-name:var(--font-display)] text-[11px] font-bold tracking-wider uppercase text-[#C6D0E2] mb-3">
          <span>Engine Diagnostics</span>
          <span className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full inline-block ${
                isReachable && health?.status === "HEALTHY" ? "bg-[#3DD68C] animate-pulse" : "bg-[#F27060]"
              }`}
            ></span>
            <span className={isReachable && health?.status === "HEALTHY" ? "text-[#3DD68C]" : "text-[#F27060]"}>
              {isReachable ? health?.status || "ONLINE" : "OFFLINE"}
            </span>
          </span>
        </div>

        <div className="space-y-2 text-xs divide-y divide-white/10">
          <div className="flex justify-between items-center pt-1.5">
            <span className="text-[#9AABC9] flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5" /> Backend
            </span>
            <span className="font-[family-name:var(--font-mono)] font-semibold text-white">
              {health?.backend || "Disconnected"}
            </span>
          </div>
          <div className="flex justify-between items-center pt-1.5">
            <span className="text-[#9AABC9] flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" /> RAM Used
            </span>
            <span className="font-[family-name:var(--font-mono)] font-semibold text-white">
              {health?.ram_used_gb !== undefined ? `${health.ram_used_gb} GB` : "—"}
            </span>
          </div>
          <div className="flex justify-between items-center pt-1.5">
            <span className="text-[#9AABC9] flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" /> Uptime
            </span>
            <span className="font-[family-name:var(--font-mono)] font-semibold text-white">
              {formatUptime(health?.uptime_seconds || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-white/10 text-center font-[family-name:var(--font-mono)] text-[10px] text-[#9AABC9]">
        <span className="text-[#C6D0E2] font-semibold">OSDHack Winning Architecture</span>
        <br />
        100% On-Premise Industrial RAG
      </div>
    </aside>
  );
}
