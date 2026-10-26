"use client";

import { FileText, Loader2, CheckCircle2, AlertCircle, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Paper } from "@/types";

interface PaperCardProps {
  paper: Paper;
  onDelete?: (id: string) => void;
}

const statusConfig = {
  uploading: {
    icon: Loader2,
    label: "Uploading",
    variant: "secondary" as const,
    animate: true,
  },
  processing: {
    icon: Loader2,
    label: "Processing",
    variant: "secondary" as const,
    animate: true,
  },
  ready: {
    icon: CheckCircle2,
    label: "Ready",
    variant: "default" as const,
    animate: false,
  },
  error: {
    icon: AlertCircle,
    label: "Error",
    variant: "destructive" as const,
    animate: false,
  },
};

export function PaperCard({ paper, onDelete }: PaperCardProps) {
  const config = statusConfig[paper.status];
  const StatusIcon = config.icon;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3 min-w-0">
            <FileText className="h-5 w-5 mt-0.5 shrink-0 text-muted-foreground" />
            <div className="min-w-0">
              <CardTitle className="text-base leading-tight truncate">
                {paper.title}
              </CardTitle>
              {paper.authors && (
                <p className="text-sm text-muted-foreground mt-1 truncate">
                  {paper.authors}
                </p>
              )}
            </div>
          </div>
          <Badge variant={config.variant} className="shrink-0">
            <StatusIcon
              className={`mr-1 h-3 w-3 ${config.animate ? "animate-spin" : ""}`}
            />
            {config.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {paper.abstract && (
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {paper.abstract}
          </p>
        )}
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex gap-3">
            {paper.page_count > 0 && <span>{paper.page_count} pages</span>}
            {paper.chunk_count > 0 && <span>{paper.chunk_count} chunks</span>}
            <span>{paper.filename}</span>
          </div>
          {onDelete && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive"
              onClick={() => onDelete(paper.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          )}
        </div>
        {paper.error_message && (
          <p className="mt-2 text-sm text-destructive">{paper.error_message}</p>
        )}
      </CardContent>
    </Card>
  );
}
