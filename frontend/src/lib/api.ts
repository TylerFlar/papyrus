import type { CitationGraph, Conversation, ConversationListItem, Paper, PaperStatus } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

// Papers
export async function uploadPaper(file: File): Promise<Paper> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/api/papers/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Upload failed: ${body}`);
  }
  return res.json();
}

export async function listPapers(): Promise<Paper[]> {
  return fetchJSON("/api/papers");
}

export async function getPaper(id: string): Promise<Paper> {
  return fetchJSON(`/api/papers/${id}`);
}

export async function getPaperStatus(id: string): Promise<PaperStatus> {
  return fetchJSON(`/api/papers/${id}/status`);
}

export async function deletePaper(id: string): Promise<void> {
  await fetchJSON(`/api/papers/${id}`, { method: "DELETE" });
}

// Conversations
export async function createConversation(paperIds: string[]): Promise<Conversation> {
  return fetchJSON("/api/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paper_ids: paperIds }),
  });
}

export async function listConversations(): Promise<ConversationListItem[]> {
  return fetchJSON("/api/conversations");
}

export async function getConversation(id: string): Promise<Conversation> {
  return fetchJSON(`/api/conversations/${id}`);
}

export async function deleteConversation(id: string): Promise<void> {
  await fetchJSON(`/api/conversations/${id}`, { method: "DELETE" });
}

export function sendMessageStream(
  conversationId: string,
  message: string,
  paperIds?: string[],
  mode?: string,
  section?: string,
): { response: Promise<Response>; abort: () => void } {
  const controller = new AbortController();
  const response = fetch(`${API_URL}/api/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      paper_ids: paperIds,
      mode: mode || "default",
      section: section || null,
    }),
    signal: controller.signal,
  });
  return { response, abort: () => controller.abort() };
}

// Citations
export async function getCitationGraph(): Promise<CitationGraph> {
  return fetchJSON("/api/citations/graph");
}
