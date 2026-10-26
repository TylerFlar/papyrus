"use client";

import { Check, FileText } from "lucide-react";
import type { Paper } from "@/types";

interface PaperSelectorProps {
  papers: Paper[];
  selectedIds: string[];
  onToggle: (paperId: string) => void;
}

export function PaperSelector({ papers, selectedIds, onToggle }: PaperSelectorProps) {
  const readyPapers = papers.filter((p) => p.status === "ready");

  if (readyPapers.length === 0) {
    return (
      <div className="text-sm text-muted-foreground py-2">
        No papers ready. Upload and process papers first.
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {readyPapers.map((paper) => {
        const selected = selectedIds.includes(paper.id);
        return (
          <button
            key={paper.id}
            onClick={() => onToggle(paper.id)}
            className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm transition-colors ${
              selected
                ? "border-primary bg-primary/10 text-primary"
                : "border-border hover:bg-muted"
            }`}
          >
            {selected ? (
              <Check className="h-3.5 w-3.5" />
            ) : (
              <FileText className="h-3.5 w-3.5" />
            )}
            <span className="max-w-[200px] truncate">{paper.title}</span>
          </button>
        );
      })}
    </div>
  );
}
