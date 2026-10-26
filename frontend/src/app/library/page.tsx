"use client";

import { PaperList } from "@/components/papers/PaperList";
import { usePapers } from "@/hooks/usePapers";
import { deletePaper } from "@/lib/api";
import { Loader2 } from "lucide-react";

export default function LibraryPage() {
  const { papers, loading, error, refresh } = usePapers();

  const handleDelete = async (id: string) => {
    await deletePaper(id);
    refresh();
  };

  return (
    <div className="mx-auto max-w-6xl px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Paper Library</h1>
        <span className="text-sm text-muted-foreground">
          {papers.length} paper{papers.length !== 1 ? "s" : ""}
        </span>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="text-center py-12 text-destructive">{error}</div>
      ) : (
        <PaperList papers={papers} onDelete={handleDelete} />
      )}
    </div>
  );
}
