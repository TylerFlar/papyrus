"use client";

import Link from "next/link";
import { Upload, Library, MessageSquare } from "lucide-react";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight">Papyrus</h1>
        <p className="mt-3 text-lg text-muted-foreground">
          Upload research papers, chat with them, and discover connections.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Upload className="h-5 w-5" />
              Upload Papers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Upload PDFs of research papers. They&apos;ll be processed, chunked, and
              embedded for intelligent retrieval.
            </p>
            <Link href="/upload" className={buttonVariants({ variant: "outline", size: "sm" })}>
              Upload
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Library className="h-5 w-5" />
              Paper Library
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Browse your uploaded papers. View metadata, processing status, and
              manage your collection.
            </p>
            <Link href="/library" className={buttonVariants({ variant: "outline", size: "sm" })}>
              Browse
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageSquare className="h-5 w-5" />
              Chat with Papers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Ask questions, get summaries, compare methodologies, and generate
              literature review snippets.
            </p>
            <Link href="/chat" className={buttonVariants({ variant: "outline", size: "sm" })}>
              Chat
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
