"use client";

import { PaperCard } from "./PaperCard";
import type { Paper } from "@/types";

interface PaperListProps {
  papers: Paper[];
  onDelete?: (id: string) => void;
}

export function PaperList({ papers, onDelete }: PaperListProps) {
  if (papers.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <p>No papers uploaded yet.</p>
        <p className="text-sm mt-1">Upload a PDF to get started.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {papers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} onDelete={onDelete} />
      ))}
    </div>
  );
}
