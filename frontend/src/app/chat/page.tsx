"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, Plus, Trash2, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PaperSelector } from "@/components/chat/PaperSelector";
import { usePapers } from "@/hooks/usePapers";
import { createConversation, listConversations, deleteConversation } from "@/lib/api";
import type { ConversationListItem } from "@/types";

export default function ChatPage() {
  const router = useRouter();
  const { papers } = usePapers();
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [selectedPaperIds, setSelectedPaperIds] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const loadConversations = useCallback(async () => {
    try {
      const data = await listConversations();
      setConversations(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const handleNewConversation = async () => {
    setCreating(true);
    try {
      const conv = await createConversation(selectedPaperIds);
      router.push(`/chat/${conv.id}`);
    } catch {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    await deleteConversation(id);
    loadConversations();
  };

  const togglePaper = (paperId: string) => {
    setSelectedPaperIds((prev) =>
      prev.includes(paperId) ? prev.filter((id) => id !== paperId) : [...prev, paperId]
    );
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-bold mb-6">Chat with Papers</h1>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-base">New Conversation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-3">
            Select papers to scope this conversation (or leave empty to search all):
          </p>
          <PaperSelector
            papers={papers}
            selectedIds={selectedPaperIds}
            onToggle={togglePaper}
          />
          <Button
            className="mt-4"
            onClick={handleNewConversation}
            disabled={creating}
          >
            {creating ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Plus className="mr-2 h-4 w-4" />
            )}
            Start Conversation
          </Button>
        </CardContent>
      </Card>

      <h2 className="text-lg font-semibold mb-4">Previous Conversations</h2>
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      ) : conversations.length === 0 ? (
        <p className="text-sm text-muted-foreground text-center py-8">
          No conversations yet. Start one above.
        </p>
      ) : (
        <div className="space-y-2">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 transition-colors cursor-pointer"
              onClick={() => router.push(`/chat/${conv.id}`)}
            >
              <div className="flex items-center gap-3 min-w-0">
                <MessageSquare className="h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">
                    {conv.title || "New conversation"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {conv.paper_ids.length} paper{conv.paper_ids.length !== 1 ? "s" : ""}{" "}
                    &middot; {new Date(conv.updated_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-muted-foreground hover:text-destructive shrink-0"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(conv.id);
                }}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
