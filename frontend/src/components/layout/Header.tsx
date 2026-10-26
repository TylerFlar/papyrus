import Link from "next/link";
import { FileText, Upload, Library, MessageSquare, Network } from "lucide-react";

export function Header() {
  return (
    <header className="border-b bg-card">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-6 px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg">
          <FileText className="h-5 w-5" />
          Papyrus
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link
            href="/upload"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <Upload className="h-4 w-4" />
            Upload
          </Link>
          <Link
            href="/library"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <Library className="h-4 w-4" />
            Library
          </Link>
          <Link
            href="/chat"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <MessageSquare className="h-4 w-4" />
            Chat
          </Link>
          <Link
            href="/graph"
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors"
          >
            <Network className="h-4 w-4" />
            Graph
          </Link>
        </nav>
      </div>
    </header>
  );
}
