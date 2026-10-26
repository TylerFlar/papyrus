"use client";

import { useCallback, useEffect, useState } from "react";
import { Loader2, Network } from "lucide-react";
import { CitationGraph } from "@/components/graph/CitationGraph";
import { getCitationGraph } from "@/lib/api";
import type { CitationGraph as CitationGraphData } from "@/types";

export default function GraphPage() {
  const [data, setData] = useState<CitationGraphData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const graph = await getCitationGraph();
      setData(graph);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <p className="text-destructive">{error}</p>
      </div>
    );
  }

  if (!data || data.nodes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[calc(100vh-3.5rem)] text-muted-foreground">
        <Network className="h-12 w-12 mb-4" />
        <p>No citation data yet.</p>
        <p className="text-sm mt-1">Upload papers to build the citation graph.</p>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-3.5rem)] relative">
      <div className="absolute top-4 left-4 z-10 bg-card/80 backdrop-blur-sm rounded-lg border p-3 text-sm">
        <p className="font-medium mb-2">Citation Graph</p>
        <div className="space-y-1 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-blue-500" />
            Uploaded papers ({data.nodes.filter((n) => n.is_uploaded).length})
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-full bg-slate-400" />
            Referenced works ({data.nodes.filter((n) => !n.is_uploaded).length})
          </div>
          <p className="pt-1">{data.edges.length} citation links</p>
        </div>
      </div>
      <CitationGraph data={data} />
    </div>
  );
}
