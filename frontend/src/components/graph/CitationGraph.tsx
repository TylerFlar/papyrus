"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import dynamic from "next/dynamic";
import type { CitationGraph as CitationGraphData } from "@/types";

// Dynamic import to avoid SSR issues with canvas
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

interface CitationGraphProps {
  data: CitationGraphData;
}

interface ForceNode {
  id: string;
  title: string;
  is_uploaded: boolean;
  citation_count: number;
  x?: number;
  y?: number;
}

export function CitationGraph({ data }: CitationGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.clientWidth,
          height: containerRef.current.clientHeight,
        });
      }
    };
    updateDimensions();
    window.addEventListener("resize", updateDimensions);
    return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const graphData = {
    nodes: data.nodes.map((n) => ({
      id: n.id,
      title: n.title,
      is_uploaded: n.is_uploaded,
      citation_count: n.citation_count,
    })),
    links: data.edges.map((e) => ({
      source: e.source,
      target: e.target,
    })),
  };

  const nodeCanvasObject = useCallback(
    (node: ForceNode, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const label = node.title.length > 30 ? node.title.slice(0, 30) + "..." : node.title;
      const fontSize = Math.max(10 / globalScale, 2);
      const radius = node.is_uploaded
        ? Math.max(5, 3 + node.citation_count * 2)
        : Math.max(3, 2 + node.citation_count);

      // Node circle
      ctx.beginPath();
      ctx.arc(node.x!, node.y!, radius, 0, 2 * Math.PI);
      ctx.fillStyle = node.is_uploaded ? "#3b82f6" : "#94a3b8";
      ctx.fill();

      if (node.is_uploaded) {
        ctx.strokeStyle = "#1d4ed8";
        ctx.lineWidth = 1.5 / globalScale;
        ctx.stroke();
      }

      // Label
      if (globalScale > 0.8 || node.is_uploaded) {
        ctx.font = `${fontSize}px sans-serif`;
        ctx.textAlign = "center";
        ctx.textBaseline = "top";
        ctx.fillStyle = node.is_uploaded ? "#1e293b" : "#64748b";
        ctx.fillText(label, node.x!, node.y! + radius + 2);
      }
    },
    []
  );

  return (
    <div ref={containerRef} className="w-full h-full">
      <ForceGraph2D
        {...({
          width: dimensions.width,
          height: dimensions.height,
          graphData,
          nodeId: "id",
          nodeLabel: "title",
          nodeCanvasObject,
          linkDirectionalArrowLength: 4,
          linkDirectionalArrowRelPos: 1,
          linkColor: () => "#cbd5e1",
          linkWidth: 1,
          cooldownTicks: 100,
          onNodeClick: (node: ForceNode) => {
            if (node.is_uploaded) {
              window.location.href = `/library`;
            }
          },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        } as any)}
      />
    </div>
  );
}
