"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Loader2 } from "lucide-react";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { usePapers } from "@/hooks/usePapers";
import { getConversation } from "@/lib/api";
import type { Conversation } from "@/types";

export default function ConversationPage() {
  const params = useParams();
  const conversationId = params.conversationId as string;
  const { papers } = usePapers();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const conv = await getConversation(conversationId);
        setConversation(conv);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load conversation");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [conversationId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error || !conversation) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-3.5rem)]">
        <p className="text-destructive">{error || "Conversation not found"}</p>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-3.5rem)]">
      <ChatInterface
        conversationId={conversationId}
        papers={papers}
        initialMessages={conversation.messages}
        initialPaperIds={conversation.paper_ids}
      />
    </div>
  );
}
