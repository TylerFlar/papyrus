"use client";

import { useCallback, useRef, useState } from "react";
import type { Message, Source } from "@/types";
import { sendMessageStream } from "@/lib/api";

interface UseChatOptions {
  conversationId: string;
  initialMessages?: Message[];
}

export function useChat({ conversationId, initialMessages = [] }: UseChatOptions) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sources, setSources] = useState<Source[]>([]);
  const abortRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    async (content: string, paperIds?: string[], mode?: string, section?: string) => {
      const userMsg: Message = {
        id: `temp-${Date.now()}`,
        conversation_id: conversationId,
        role: "user",
        content,
        sources: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);
      setSources([]);

      const assistantMsg: Message = {
        id: `temp-${Date.now()}-assistant`,
        conversation_id: conversationId,
        role: "assistant",
        content: "",
        sources: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      const { response, abort } = sendMessageStream(conversationId, content, paperIds, mode, section);
      abortRef.current = abort;

      try {
        const res = await response;
        if (!res.ok) {
          throw new Error(`Stream failed: ${res.status}`);
        }
        if (!res.body) {
          throw new Error("No response body");
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              continue;
            }
            if (line.startsWith("data: ")) {
              const data = line.slice(6);
              try {
                const parsed = JSON.parse(data);
                if ("text" in parsed) {
                  setMessages((prev) => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    if (last.role === "assistant") {
                      updated[updated.length - 1] = {
                        ...last,
                        content: last.content + parsed.text,
                      };
                    }
                    return updated;
                  });
                } else if ("sources" in parsed) {
                  setSources(parsed.sources);
                  setMessages((prev) => {
                    const updated = [...prev];
                    const last = updated[updated.length - 1];
                    if (last.role === "assistant") {
                      updated[updated.length - 1] = {
                        ...last,
                        sources: JSON.stringify(parsed.sources),
                      };
                    }
                    return updated;
                  });
                }
              } catch {
                // skip malformed JSON
              }
            }
          }
        }
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") {
          // User cancelled
        } else {
          setMessages((prev) => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last.role === "assistant") {
              updated[updated.length - 1] = {
                ...last,
                content: last.content || "An error occurred. Please try again.",
              };
            }
            return updated;
          });
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [conversationId]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.();
  }, []);

  return { messages, isStreaming, sources, sendMessage, stopStreaming };
}
