"use client";

import { useCallback, useEffect, useState } from "react";
import type { Paper } from "@/types";
import { listPapers, getPaperStatus } from "@/lib/api";

export function usePapers() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const data = await listPapers();
      setPapers(data);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load papers");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // Poll for processing papers
  useEffect(() => {
    const processing = papers.filter(
      (p) => p.status === "uploading" || p.status === "processing"
    );
    if (processing.length === 0) return;

    const interval = setInterval(async () => {
      let changed = false;
      const updated = await Promise.all(
        papers.map(async (paper) => {
          if (paper.status !== "uploading" && paper.status !== "processing") {
            return paper;
          }
          try {
            const status = await getPaperStatus(paper.id);
            if (status.status !== paper.status) {
              changed = true;
              return { ...paper, ...status };
            }
          } catch {
            // ignore polling errors
          }
          return paper;
        })
      );
      if (changed) {
        setPapers(updated);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [papers]);

  return { papers, loading, error, refresh };
}
