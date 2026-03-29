"use client";

import { useEffect, useState } from "react";
import { sermonsApi, type Sermon } from "@/lib/api";

export function SermonsPage() {
  const [sermons, setSermons] = useState<Sermon[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const limit = 20;

  useEffect(() => {
    setLoading(true);
    sermonsApi
      .list({ offset: page * limit, limit, search: search || undefined })
      .then((data) => {
        setSermons(data.items);
        setTotal(data.total);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [page, search]);

  return (
    <div>
      {/* Search bar */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search sermons by title or preacher..."
          className="w-full px-4 py-3 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
        />
      </div>

      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading sermons...</div>
      ) : sermons.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          No sermons found. {search && "Try a different search term."}
        </div>
      ) : (
        <>
          <div className="grid gap-4">
            {sermons.map((sermon) => (
              <a
                key={sermon.id}
                href={`/sermons/${sermon.id}`}
                className="block p-5 rounded-xl border border-border bg-card hover:shadow-md transition-shadow"
              >
                <h3 className="font-semibold text-lg">{sermon.title}</h3>
                <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                  {sermon.preacher && <span>🎤 {sermon.preacher}</span>}
                  {sermon.date_preached && <span>📅 {sermon.date_preached}</span>}
                </div>
                {sermon.summary && (
                  <p className="mt-2 text-sm text-muted-foreground line-clamp-2">
                    {sermon.summary}
                  </p>
                )}
              </a>
            ))}
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center mt-8">
            <span className="text-sm text-muted-foreground">
              Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                disabled={page === 0}
                className="px-4 py-2 rounded-md border border-border hover:bg-secondary disabled:opacity-50 transition-colors"
              >
                Previous
              </button>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={(page + 1) * limit >= total}
                className="px-4 py-2 rounded-md border border-border hover:bg-secondary disabled:opacity-50 transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
