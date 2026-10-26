export interface Paper {
  id: string;
  title: string;
  authors: string | null;
  abstract: string | null;
  filename: string;
  page_count: number;
  chunk_count: number;
  status: "uploading" | "processing" | "ready" | "error";
  error_message: string | null;
  uploaded_at: string;
  processed_at: string | null;
}

export interface PaperStatus {
  id: string;
  status: Paper["status"];
  chunk_count: number;
  error_message: string | null;
}

export interface ConversationListItem {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  paper_ids: string[];
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  sources: string | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  paper_ids: string[];
  messages: Message[];
}

export interface Source {
  paper_id: string;
  paper_title: string;
  page_number: number | null;
  chunk_index: number;
  score: number;
}

export interface GraphNode {
  id: string;
  title: string;
  is_uploaded: boolean;
  citation_count: number;
}

export interface GraphEdge {
  source: string;
  target: string;
}

export interface CitationGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}
