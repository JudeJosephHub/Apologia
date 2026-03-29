"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { sermonsApi, encyclopediaApi, type Sermon, type SermonIntelligence, type RelatedSermon } from "@/lib/api";
import { Navbar } from "@/components/navbar";

export default function SermonDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [sermon, setSermon] = useState<Sermon | null>(null);
  const [intelligence, setIntelligence] = useState<SermonIntelligence | null>(null);
  const [related, setRelated] = useState<RelatedSermon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = Number(params.id);
    if (isNaN(id)) {
      setError("Invalid sermon ID");
      setLoading(false);
      return;
    }
    Promise.all([
      sermonsApi.get(id),
      encyclopediaApi.sermonIntelligence(id).catch(() => null),
      encyclopediaApi.sermonRelated(id).catch(() => []),
    ])
      .then(([s, intel, rel]) => {
        setSermon(s);
        setIntelligence(intel);
        setRelated(rel);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <>
        <Navbar />
        <main className="max-w-4xl mx-auto px-4 py-10">
          <div className="text-center text-muted-foreground">Loading sermon...</div>
        </main>
      </>
    );
  }

  if (error || !sermon) {
    return (
      <>
        <Navbar />
        <main className="max-w-4xl mx-auto px-4 py-10">
          <div className="text-center text-red-500">{error || "Sermon not found"}</div>
          <button onClick={() => router.push("/sermons")} className="mt-4 text-primary hover:underline">
            &larr; Back to sermons
          </button>
        </main>
      </>
    );
  }

  const themes: string[] = (() => {
    try {
      return JSON.parse(sermon.themes || "[]");
    } catch {
      return [];
    }
  })();

  return (
    <>
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-10">
        <button onClick={() => router.push("/sermons")} className="text-sm text-muted-foreground hover:text-foreground mb-6 inline-block">
          &larr; Back to sermons
        </button>

        <article>
          <div className="flex items-start justify-between mb-2">
            <h1 className="text-3xl font-bold">{sermon.title}</h1>
            {sermon.file_path && (
              <Link
                href={`/sermons/${params.id}/review`}
                className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 text-sm whitespace-nowrap"
              >
                Review Slides
              </Link>
            )}
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-muted-foreground mb-6">
            {sermon.preacher && <span>🎤 {sermon.preacher}</span>}
            {sermon.date_preached && <span>📅 {sermon.date_preached}</span>}
            {sermon.denomination && <span>⛪ {sermon.denomination}</span>}
            {sermon.church_name && <span>🏛️ {sermon.church_name}</span>}
            {sermon.series_name && <span>📚 {sermon.series_name}</span>}
          </div>

          {themes.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-6">
              {themes.map((theme) => (
                <span key={theme} className="px-3 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary">
                  {theme}
                </span>
              ))}
            </div>
          )}

          {/* Intelligence data */}
          {intelligence && (
            <section className="mb-8 bg-card border border-border rounded-xl p-6">
              <h2 className="text-xl font-semibold mb-4">Intelligence</h2>
              <div className="grid grid-cols-2 gap-4">
                {intelligence.scripture_refs.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Scripture References</h4>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.scripture_refs.map((r) => (
                        <span key={r} className="bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded text-xs">{r}</span>
                      ))}
                    </div>
                  </div>
                )}
                {intelligence.theological_concepts.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Theological Concepts</h4>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.theological_concepts.map((c) => (
                        <span key={c} className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs">{c}</span>
                      ))}
                    </div>
                  </div>
                )}
                {intelligence.traditions.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">Traditions</h4>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.traditions.map((t) => (
                        <span key={t} className="bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded text-xs">{t}</span>
                      ))}
                    </div>
                  </div>
                )}
                {intelligence.themes.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-muted-foreground mb-2">AI Themes</h4>
                    <div className="flex flex-wrap gap-1">
                      {intelligence.themes.map((t) => (
                        <span key={t} className="bg-green-500/20 text-green-300 px-2 py-0.5 rounded text-xs">{t}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </section>
          )}

          {/* Related Sermons */}
          {related.length > 0 && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-3">Related Sermons</h2>
              <div className="space-y-2">
                {related.map((r) => (
                  <Link
                    key={r.sermon_id}
                    href={`/sermons/${r.sermon_id}`}
                    className="block p-3 bg-card border border-border rounded-lg hover:bg-secondary/30 transition-colors"
                  >
                    <span className="font-medium">{r.sermon_name}</span>
                    {r.pastor_name && (
                      <span className="text-sm text-muted-foreground ml-2">by {r.pastor_name}</span>
                    )}
                    {r.edges && r.edges.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-1">
                        {r.edges.map((e, i) => (
                          <span key={i} className="text-xs text-muted-foreground">
                            {e.type}: {e.shared.slice(0, 3).join(", ")}
                          </span>
                        ))}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            </section>
          )}

          {sermon.summary && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-3">Summary</h2>
              <p className="text-muted-foreground leading-relaxed">{sermon.summary}</p>
            </section>
          )}

          {sermon.outline && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-3">Outline</h2>
              <div className="bg-card border border-border rounded-lg p-4 whitespace-pre-wrap text-sm">
                {sermon.outline}
              </div>
            </section>
          )}

          {sermon.transcript && (
            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-3">Transcript</h2>
              <div className="text-muted-foreground leading-relaxed whitespace-pre-wrap">
                {sermon.transcript}
              </div>
            </section>
          )}

          <section className="mt-8 pt-6 border-t border-border flex gap-4">
            {sermon.source_url && (
              <a
                href={sermon.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline text-sm"
              >
                View original source &rarr;
              </a>
            )}
            {sermon.youtube_url && (
              <a
                href={sermon.youtube_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline text-sm"
              >
                Watch on YouTube &rarr;
              </a>
            )}
          </section>
        </article>
      </main>
    </>
  );
}
