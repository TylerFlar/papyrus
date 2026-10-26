"use client";

import { useEffect, useRef, useState } from "react";
import { Send, Square, Sparkles, GitCompare, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { MessageBubble } from "./MessageBubble";
import { PaperSelector } from "./PaperSelector";
import { useChat } from "@/hooks/useChat";
import type { Message, Paper } from "@/types";

interface ChatInterfaceProps {
  conversationId: string;
  papers: Paper[];
  initialMessages?: Message[];
  initialPaperIds?: string[];
}

const SECTIONS = ["Methods", "Results", "Discussion", "Introduction", "Conclusion"];

const SUGGESTED_PROMPTS = [
  { text: "Summarize this paper in 3-4 paragraphs", mode: "default" },
  { text: "What is the main methodology used?", mode: "default" },
  { text: "What are the key findings and conclusions?", mode: "default" },
  { text: "Generate a literature review snippet", mode: "literature_review" },
];

const COMPARE_PROMPTS = [
  { text: "Compare the methodologies across these papers", mode: "compare", section: "Methods" },
  { text: "Compare the key findings", mode: "compare", section: "Results" },
  { text: "How do these papers relate to each other?", mode: "compare" },
  { text: "Generate a comparative literature review", mode: "literature_review" },
];

export function ChatInterface({
  conversationId,
  papers,
  initialMessages = [],
  initialPaperIds = [],
}: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const [selectedPaperIds, setSelectedPaperIds] = useState<string[]>(initialPaperIds);
  const [mode, setMode] = useState<string>("default");
  const [sectionFilter, setSectionFilter] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const { messages, isStreaming, sendMessage, stopStreaming } = useChat({
    conversationId,
    initialMessages,
  });

  const isMultiPaper = selectedPaperIds.length > 1;

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = (overrideMode?: string, overrideSection?: string) => {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    const sendMode = overrideMode || mode;
    const sendSection = overrideSection || sectionFilter || undefined;
    setInput("");
    sendMessage(
      trimmed,
      selectedPaperIds.length > 0 ? selectedPaperIds : undefined,
      sendMode,
      sendSection,
    );
  };

  const handlePromptClick = (prompt: { text: string; mode: string; section?: string }) => {
    setInput(prompt.text);
    // Auto-send suggested prompts
    sendMessage(
      prompt.text,
      selectedPaperIds.length > 0 ? selectedPaperIds : undefined,
      prompt.mode,
      prompt.section,
    );
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const togglePaper = (paperId: string) => {
    setSelectedPaperIds((prev) =>
      prev.includes(paperId)
        ? prev.filter((id) => id !== paperId)
        : [...prev, paperId]
    );
  };

  const prompts = isMultiPaper ? COMPARE_PROMPTS : SUGGESTED_PROMPTS;

  return (
    <div className="flex flex-col h-full">
      <div className="border-b px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs text-muted-foreground">Scope to papers:</p>
          {isMultiPaper && (
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                <Button
                  variant={mode === "default" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode("default")}
                  className="h-6 text-xs px-2"
                >
                  Default
                </Button>
                <Button
                  variant={mode === "compare" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode("compare")}
                  className="h-6 text-xs px-2"
                >
                  <GitCompare className="mr-1 h-3 w-3" />
                  Compare
                </Button>
                <Button
                  variant={mode === "literature_review" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setMode("literature_review")}
                  className="h-6 text-xs px-2"
                >
                  <BookOpen className="mr-1 h-3 w-3" />
                  Lit Review
                </Button>
              </div>
            </div>
          )}
        </div>
        <PaperSelector
          papers={papers}
          selectedIds={selectedPaperIds}
          onToggle={togglePaper}
        />
        {isMultiPaper && (
          <div className="flex gap-1 mt-2">
            <span className="text-xs text-muted-foreground mr-1 self-center">Section:</span>
            <Badge
              variant={sectionFilter === null ? "default" : "secondary"}
              className="cursor-pointer text-xs"
              onClick={() => setSectionFilter(null)}
            >
              All
            </Badge>
            {SECTIONS.map((s) => (
              <Badge
                key={s}
                variant={sectionFilter === s ? "default" : "secondary"}
                className="cursor-pointer text-xs"
                onClick={() => setSectionFilter(sectionFilter === s ? null : s)}
              >
                {s}
              </Badge>
            ))}
          </div>
        )}
      </div>

      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4 max-w-3xl mx-auto">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <Sparkles className="h-8 w-8 mx-auto text-muted-foreground mb-3" />
              <p className="text-muted-foreground mb-4">
                {isMultiPaper
                  ? "Compare and analyze across selected papers"
                  : "Ask a question about your papers"}
              </p>
              <div className="flex flex-wrap justify-center gap-2">
                {prompts.map((prompt) => (
                  <button
                    key={prompt.text}
                    onClick={() => handlePromptClick(prompt)}
                    className="rounded-md border px-3 py-1.5 text-sm text-muted-foreground hover:bg-muted transition-colors"
                  >
                    {prompt.text}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="flex gap-2 max-w-3xl mx-auto">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isMultiPaper
                ? "Ask a comparison question across papers..."
                : "Ask a question about your papers..."
            }
            className="min-h-[44px] max-h-[200px] resize-none"
            rows={1}
          />
          {isStreaming ? (
            <Button onClick={stopStreaming} variant="outline" size="icon">
              <Square className="h-4 w-4" />
            </Button>
          ) : (
            <Button onClick={() => handleSend()} disabled={!input.trim()} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
