"use client";
import React, { useState } from "react";
import { CheckSquare, Square, CheckCircle } from "lucide-react";

interface ActionsChecklistProps {
  actions: string[];
  keyPrefix?: string;
}

export default function ActionsChecklist({ actions, keyPrefix = "act" }: ActionsChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  if (!actions || actions.length === 0) return null;

  const toggleCheck = (index: number) => {
    setCheckedItems((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="mt-5 bg-white border border-[#E2E6ED] rounded-xl p-4 shadow-2xs">
      <div className="flex items-center gap-2 font-[family-name:var(--font-display)] font-bold text-xs uppercase tracking-wider text-[#51607A] mb-3">
        <CheckCircle className="w-3.5 h-3.5 text-[#12875D]" />
        <span>Recommended Field Actions ({actions.length})</span>
      </div>

      <div className="space-y-2.5">
        {actions.map((act, index) => {
          const isDone = !!checkedItems[index];
          return (
            <div
              key={`${keyPrefix}_${index}`}
              onClick={() => toggleCheck(index)}
              className={`flex items-start gap-3 p-2.5 rounded-lg border transition-all cursor-pointer select-none ${
                isDone
                  ? "bg-[#F5F6F8] border-[#E2E6ED] text-[#8A9BB8]"
                  : "bg-white border-[#E2E6ED]/80 hover:border-[#2563EB] text-[#0B1F3A]"
              }`}
            >
              <button
                type="button"
                className="mt-0.5 text-[#2563EB] focus:outline-hidden shrink-0"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleCheck(index);
                }}
              >
                {isDone ? (
                  <CheckSquare className="w-4 h-4 text-[#12875D]" />
                ) : (
                  <Square className="w-4 h-4 text-[#51607A]" />
                )}
              </button>
              <div className="flex-1">
                <span className={`text-xs md:text-sm ${isDone ? "line-through opacity-75" : "font-medium"}`}>
                  {act}
                </span>
                <div
                  className={`mt-1 font-[family-name:var(--font-mono)] text-[10px] font-semibold ${
                    isDone ? "text-[#12875D]" : "text-[#2563EB]"
                  }`}
                >
                  {isDone ? "DONE" : "OPEN &middot; ACTION REQUIRED"}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
