"use client";

import { PaperUploader } from "@/components/papers/PaperUploader";
import { PaperList } from "@/components/papers/PaperList";
import { usePapers } from "@/hooks/usePapers";
import { deletePaper } from "@/lib/api";

export default function UploadPage() {
  const { papers, refresh } = usePapers();

  const handleDelete = async (id: string) => {
    await deletePaper(id);
    refresh();
  };

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="text-2xl font-bold mb-6">Upload Papers</h1>
      <PaperUploader onUploaded={() => refresh()} />
      {papers.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Recent Uploads</h2>
          <PaperList papers={papers} onDelete={handleDelete} />
        </div>
      )}
    </div>
  );
}
