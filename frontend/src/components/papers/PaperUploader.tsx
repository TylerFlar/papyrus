"use client";

import { useCallback, useState } from "react";
import { Upload, FileUp, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { uploadPaper } from "@/lib/api";
import type { Paper } from "@/types";

interface PaperUploaderProps {
  onUploaded: (paper: Paper) => void;
}

export function PaperUploader({ onUploaded }: PaperUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback(
    async (files: FileList | null) => {
      if (!files || files.length === 0) return;

      setError(null);
      setUploading(true);

      try {
        for (const file of Array.from(files)) {
          if (!file.name.toLowerCase().endsWith(".pdf")) {
            setError("Only PDF files are accepted");
            continue;
          }
          const paper = await uploadPaper(file);
          onUploaded(paper);
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUploaded]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`
        relative flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-12
        transition-colors cursor-pointer
        ${isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-muted-foreground/50"}
      `}
    >
      {uploading ? (
        <Loader2 className="h-10 w-10 animate-spin text-muted-foreground" />
      ) : (
        <Upload className="h-10 w-10 text-muted-foreground" />
      )}
      <p className="mt-4 text-sm text-muted-foreground">
        {uploading ? "Uploading..." : "Drag & drop PDF files here"}
      </p>
      {!uploading && (
        <>
          <p className="mt-1 text-xs text-muted-foreground">or</p>
          <Button
            variant="outline"
            size="sm"
            className="mt-2"
            onClick={() => {
              const input = document.createElement("input");
              input.type = "file";
              input.accept = ".pdf";
              input.multiple = true;
              input.onchange = () => handleFiles(input.files);
              input.click();
            }}
          >
            <FileUp className="mr-2 h-4 w-4" />
            Browse files
          </Button>
        </>
      )}
      {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
    </div>
  );
}
