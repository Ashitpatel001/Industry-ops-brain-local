"use client";
import React, { useState, useEffect, useRef } from "react";
import HeroHeader from "@/components/HeroHeader";
import CitationCard, { CitationItem } from "@/components/CitationCard";
import ConfidenceBadge from "@/components/ConfidenceBadge";
import ActionsChecklist from "@/components/ActionsChecklist";
import { MessageSquare, Send, Loader2, Sparkles, RefreshCw, Cpu, Database, AlertCircle } from "lucide-react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  intent?: string;
  confidence?: string;
  citations?: CitationItem[];
  actions?: string[];
  backend?: string;
  isStreaming?: boolean;
}

const INTENTS = [
  { id: "general", label: "General Reliability / QA" },
  { id: "maintenance", label: "Maintenance & Equipment Troubleshooting" },
  { id: "compliance", label: "Regulatory Safety & OISD / PESO Audit" },
  { id: "lessons_learned", label: "Historical Incident & RCA Lessons" },
];

export default function CopilotPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [intent, setIntent] = useState("general");
  const [assetTagsRaw, setAssetTagsRaw] = useState("P-204");
  const [isStreaming, setIsStreaming] = useState(false);
  const [useWebSocket, setUseWebSocket] = useState(true);
  const [wsStatus, setWsStatus] = useState<"CONNECTED" | "DISCONNECTED" | "CONNECTING">("DISCONNECTED");
  const wsRef = useRef<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!useWebSocket) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setWsStatus("DISCONNECTED");
      return;
    }

    const connectWs = () => {
      setWsStatus("CONNECTING");
      try {
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");
        ws.onopen = () => setWsStatus("CONNECTED");
        ws.onclose = () => setWsStatus("DISCONNECTED");
        ws.onerror = () => setWsStatus("DISCONNECTED");
        wsRef.current = ws;
      } catch {
        setWsStatus("DISCONNECTED");
      }
    };

    connectWs();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, [useWebSocket]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userPrompt = input.trim();
    setInput("");
    const tags = assetTagsRaw
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    const userMsg: ChatMessage = { role: "user", content: userPrompt };
    setMessages((prev) => [...prev, userMsg]);
    setIsStreaming(true);

    // If WebSocket connected, use real-time token streaming
    if (useWebSocket && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: "",
        intent,
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "start") {
            // Started
          } else if (data.type === "token") {
            setMessages((prev) => {
              const newArr = [...prev];
              const lastIdx = newArr.length - 1;
              if (lastIdx >= 0 && newArr[lastIdx].role === "assistant") {
                newArr[lastIdx] = {
                  ...newArr[lastIdx],
                  content: newArr[lastIdx].content + data.content,
                };
              }
              return newArr;
            });
          } else if (data.type === "done") {
            const resp = data.response || {};
            setMessages((prev) => {
              const newArr = [...prev];
              const lastIdx = newArr.length - 1;
              if (lastIdx >= 0 && newArr[lastIdx].role === "assistant") {
                newArr[lastIdx] = {
                  ...newArr[lastIdx],
                  content: resp.answer || newArr[lastIdx].content,
                  confidence: resp.confidence || "HIGH",
                  citations: resp.citations || [],
                  actions: resp.recommended_actions || [],
                  backend: resp.model_backend || "OpenVINO INT4",
                  isStreaming: false,
                };
              }
              return newArr;
            });
            setIsStreaming(false);
          } else if (data.type === "error") {
            throw new Error(data.message || "Streaming error occurred");
          }
        } catch (err: any) {
          setMessages((prev) => {
            const newArr = [...prev];
            const lastIdx = newArr.length - 1;
            if (lastIdx >= 0 && newArr[lastIdx].role === "assistant") {
              newArr[lastIdx] = {
                ...newArr[lastIdx],
                content: `Error receiving stream: ${err.message || "Connection interrupted."}`,
                isStreaming: false,
              };
            }
            return newArr;
          });
          setIsStreaming(false);
        }
      };

      wsRef.current.send(
        JSON.stringify({
          query: userPrompt,
          intent,
          asset_tags: tags,
        })
      );
    } else {
      // Fallback to HTTP POST /api/v1/query
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: "Analysing through local OpenVINO model & knowledge graph...",
        intent,
        isStreaming: true,
      };
      setMessages((prev) => [...prev, assistantMsg]);

      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/query", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: userPrompt,
            text: userPrompt,
            intent,
            asset_tags: tags,
          }),
        });

        if (!response.ok) {
          throw new Error(`API returned HTTP ${response.status}`);
        }

        const data = await response.json();
        setMessages((prev) => {
          const newArr = [...prev];
          const lastIdx = newArr.length - 1;
          if (lastIdx >= 0 && newArr[lastIdx].role === "assistant") {
            newArr[lastIdx] = {
              role: "assistant",
              content: data.answer || "No response text generated.",
              confidence: data.confidence || "HIGH",
              citations: data.citations || [],
              actions: data.recommended_actions || [],
              backend: data.model_backend || "OpenVINO INT4",
              isStreaming: false,
            };
          }
          return newArr;
        });
      } catch (err: any) {
        setMessages((prev) => {
          const newArr = [...prev];
          const lastIdx = newArr.length - 1;
          if (lastIdx >= 0 && newArr[lastIdx].role === "assistant") {
            newArr[lastIdx] = {
              role: "assistant",
              content: `Error querying local API: ${err.message || "Failed to reach backend."}`,
              isStreaming: false,
            };
          }
          return newArr;
        });
      } finally {
        setIsStreaming(false);
      }
    }
  };

  return (
    <div className="space-y-6">
      <HeroHeader
        eyebrow="Ops Brain Local &middot; Co-Pilot Studio"
        title="Ask Plant Co-Pilot Chat."
        subtitle="Multi-agent industrial intelligence running on-device. Query maintenance manuals, check regulatory compliance, or investigate root cause chains with instant streaming tokens, confidence badges, and actionable checklists."
        sheetNo="OB / 02"
      />

      {/* Control Panel Bar */}
      <div className="bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <div className="flex items-center gap-2">
            <span className="font-[family-name:var(--font-mono)] text-xs font-bold text-[#51607A] uppercase">
              Intent:
            </span>
            <select
              value={intent}
              onChange={(e) => setIntent(e.target.value)}
              disabled={isStreaming}
              className="px-3 py-1.5 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] text-xs font-semibold text-[#0B1F3A] focus:outline-hidden focus:border-blue-600"
            >
              {INTENTS.map((it) => (
                <option key={it.id} value={it.id}>
                  {it.label}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="font-[family-name:var(--font-mono)] text-xs font-bold text-[#51607A] uppercase">
              Asset Tags:
            </span>
            <input
              type="text"
              value={assetTagsRaw}
              onChange={(e) => setAssetTagsRaw(e.target.value)}
              disabled={isStreaming}
              placeholder="e.g. P-204, HX-301"
              className="px-3 py-1.5 rounded-lg border border-[#E2E6ED] bg-[#FAFBFC] font-[family-name:var(--font-mono)] text-xs text-[#0B1F3A] w-36 focus:outline-hidden focus:border-blue-600"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => setUseWebSocket(!useWebSocket)}
            className={`px-3 py-1.5 rounded-lg font-[family-name:var(--font-mono)] text-xs font-semibold border flex items-center gap-2 transition-colors ${
              useWebSocket
                ? "bg-[#EEF2F9] text-blue-600 border-[#D5E1F2]"
                : "bg-gray-100 text-[#51607A] border-gray-300"
            }`}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${wsStatus === "CONNECTING" ? "animate-spin" : ""}`} />
            <span>
              Stream Mode: {useWebSocket ? (wsStatus === "CONNECTED" ? "WS ACTIVE" : "WS FALLBACK") : "HTTP POST"}
            </span>
          </button>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="bg-white border border-[#E2E6ED] rounded-2xl p-6 min-h-[480px] max-h-[640px] overflow-y-auto space-y-6 shadow-sm">
        {messages.length === 0 ? (
          <div className="h-[400px] flex flex-col items-center justify-center text-center space-y-4 select-none">
            <div className="p-4 bg-blue-50 text-blue-600 rounded-2xl">
              <Sparkles className="w-8 h-8" />
            </div>
            <div className="font-[family-name:var(--font-display)] font-bold text-lg text-[#0B1F3A]">
              Plant Co-Pilot Ready for Inquiry
            </div>
            <p className="text-xs md:text-sm text-[#51607A] max-w-md">
              Ask about mechanical seal failures on P-204, required atmospheric oxygen test levels before V-205 vessel entry, or historical compressor valve incidents.
            </p>
            <div className="flex flex-wrap justify-center gap-2 pt-2">
              {[
                "Why did P-204 mechanical seal fail?",
                "What are the OISD-GDN-192 rules for V-205 entry?",
                "Generate a maintenance summary for C-401",
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => setInput(q)}
                  className="px-3 py-1.5 bg-[#F5F6F8] hover:bg-[#EEF2F9] text-[#14315C] border border-[#E2E6ED] hover:border-blue-600 rounded-lg text-xs font-semibold transition-colors"
                >
                  &ldquo;{q}&rdquo;
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-3xl rounded-2xl p-5 ${
                  msg.role === "user"
                    ? "bg-[#14315C] text-white shadow-sm"
                    : "bg-[#FAFBFC] border border-[#E2E6ED] text-[#0B1F3A] shadow-2xs w-full"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="flex flex-wrap items-center justify-between gap-3 pb-3 mb-3 border-b border-[#E2E6ED]/80">
                    <div className="flex items-center gap-2">
                      <div className="p-1.5 bg-blue-600 text-white rounded-lg">
                        <Sparkles className="w-3.5 h-3.5" />
                      </div>
                      <span className="font-[family-name:var(--font-display)] font-bold text-sm text-[#0B1F3A]">
                        Plant Co-Pilot Analysis
                      </span>
                    </div>
                    {!msg.isStreaming && (
                      <div className="flex items-center gap-2">
                        <ConfidenceBadge confidence={msg.confidence} />
                      </div>
                    )}
                  </div>
                )}

                <div className="text-sm leading-relaxed whitespace-pre-wrap font-sans">
                  {msg.content}
                  {msg.isStreaming && (
                    <span className="inline-block w-2 h-4 ml-1 bg-blue-600 animate-pulse align-middle" />
                  )}
                </div>

                {msg.role === "assistant" && !msg.isStreaming && (
                  <>
                    <CitationCard citations={msg.citations || []} />
                    <ActionsChecklist actions={msg.actions || []} keyPrefix={`msg_${idx}`} />
                    <div className="mt-4 pt-3 border-t border-[#E2E6ED]/60 flex justify-between items-center text-[10px] font-[family-name:var(--font-mono)] text-[#51607A]">
                      <span className="flex items-center gap-1.5">
                        <Cpu className="w-3 h-3 text-blue-600" /> Backend: {msg.backend || "OpenVINO INT4"}
                      </span>
                      <span>Intent: {(msg.intent || "general").toUpperCase()}</span>
                    </div>
                  </>
                )}
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <form onSubmit={handleSubmit} className="flex items-center gap-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isStreaming}
          placeholder={`Ask Plant Co-Pilot (${intent.toUpperCase()} mode on ${assetTagsRaw || "all assets"})...`}
          className="flex-1 px-4 py-3.5 bg-white border border-[#E2E6ED] rounded-xl text-sm text-[#0B1F3A] placeholder:text-[#9AABC9] focus:outline-hidden focus:border-blue-600 focus:ring-2 focus:ring-blue-100 shadow-2xs"
        />
        <button
          type="submit"
          disabled={!input.trim() || isStreaming}
          className={`px-6 py-3.5 rounded-xl font-semibold text-sm flex items-center gap-2 transition-all shadow-sm ${
            !input.trim() || isStreaming
              ? "bg-[#CBD3E0] text-white cursor-not-allowed"
              : "bg-[#14315C] hover:bg-[#1C4176] text-white cursor-pointer"
          }`}
        >
          {isStreaming ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Thinking...</span>
            </>
          ) : (
            <>
              <span>Ask</span>
              <Send className="w-4 h-4" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
