"use strict";
import React from "react";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface ConfidenceBadgeProps {
  confidence?: string;
}

export default function ConfidenceBadge({ confidence = "MEDIUM" }: ConfidenceBadgeProps) {
  const confUpper = (confidence || "MEDIUM").toUpperCase();

  let palette = {
    text: "text-[#8A5A0C]",
    bg: "bg-[#FDF3DF]",
    border: "border-[#F3DDA8]",
    dot: "●",
    icon: AlertTriangle,
  };

  if (confUpper === "HIGH") {
    palette = {
      text: "text-[#0F5C3E]",
      bg: "bg-[#E4F5EC]",
      border: "border-[#BEE7D3]",
      dot: "●",
      icon: CheckCircle2,
    };
  } else if (confUpper === "LOW") {
    palette = {
      text: "text-[#8C2A22]",
      bg: "bg-[#FBE7E4]",
      border: "border-[#F0BEB6]",
      dot: "●",
      icon: XCircle,
    };
  }

  const Icon = palette.icon;

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-[family-name:var(--font-display)] font-bold text-xs tracking-wider uppercase px-3 py-1 rounded-full border shadow-2xs ${palette.text} ${palette.bg} ${palette.border}`}
    >
      <Icon className="w-3.5 h-3.5" />
      <span>Confidence: {confUpper}</span>
    </span>
  );
}
