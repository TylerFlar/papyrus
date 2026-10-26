"use client";

import { FileText, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Message, Source } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const sources: Source[] = message.sources ? JSON.parse(message.sources) : [];

  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : ""}`}>
      <div
        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        }`}
      >
        {isUser ? <User className="h-4 w-4" /> : <FileText className="h-4 w-4" />}
      </div>
      <div
        className={`flex max-w-[80%] flex-col gap-2 rounded-lg px-4 py-3 ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted"
        }`}
      >
        <div className="text-sm whitespace-pre-wrap">{message.content}</div>
        {sources.length > 0 && !isUser && (
          <div className="flex flex-wrap gap-1 pt-1">
            {sources.map((s, i) => (
              <Badge key={i} variant="secondary" className="text-xs">
                {s.paper_title}
                {s.page_number ? `, p.${s.page_number}` : ""}
              </Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
