"use client";

import { Navbar } from "@/components/navbar";
import { useState } from "react";
import { encyclopediaApi, type CourseSuggestion } from "@/lib/api";

export default function CoursesPage() {
  const [topic, setTopic] = useState("");
  const [course, setCourse] = useState<CourseSuggestion | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSuggest = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await encyclopediaApi.suggestCourse(topic);
      setCourse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to suggest course");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold mb-2">Courses</h1>
        <p className="text-muted-foreground mb-8">
          Generate curated learning paths from the sermon encyclopedia.
        </p>

        <div className="flex gap-2 mb-8">
          <input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSuggest()}
            placeholder="Enter a topic (e.g. 'grace', 'salvation', 'Romans')…"
            className="flex-1 bg-card border border-border rounded-md px-4 py-2 text-foreground placeholder:text-muted-foreground"
          />
          <button
            onClick={handleSuggest}
            disabled={loading}
            className="bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {loading ? "Generating…" : "Generate Course"}
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-md mb-6">
            {error}
          </div>
        )}

        {course && (
          <div className="bg-card border border-border rounded-xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">🎓</span>
              <div>
                <h2 className="text-xl font-bold">{course.topic}</h2>
                <p className="text-sm text-muted-foreground">
                  {course.sermon_count} sermon(s) in this course
                </p>
              </div>
            </div>

            <div className="space-y-2 mb-6">
              {course.sermons.map((s, i) => (
                <div key={s.sermon_id} className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg">
                  <span className="text-muted-foreground text-sm font-mono w-6">{i + 1}.</span>
                  <div>
                    <span className="font-medium">{s.sermon_name}</span>
                    {s.pastor_name && (
                      <span className="text-sm text-muted-foreground ml-2">by {s.pastor_name}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {course.themes_covered.length > 0 && (
              <div className="mb-3">
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Themes Covered</h4>
                <div className="flex flex-wrap gap-2">
                  {course.themes_covered.map((t) => (
                    <span key={t} className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {course.scripture_refs.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Scripture References</h4>
                <div className="flex flex-wrap gap-2">
                  {course.scripture_refs.map((r) => (
                    <span key={r} className="bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded text-xs">
                      {r}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {!course && !loading && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {["Foundations of Faith", "The Psalms Journey", "Pauline Letters Deep Dive"].map(
              (title) => (
                <button
                  key={title}
                  onClick={() => {
                    setTopic(title);
                    handleSuggest();
                  }}
                  className="p-6 rounded-xl border border-border bg-card hover:shadow-md transition-shadow text-left"
                >
                  <span className="text-2xl mb-3 block">🎓</span>
                  <h3 className="font-semibold text-lg mb-2">{title}</h3>
                  <p className="text-sm text-muted-foreground">
                    Click to generate a course on this topic.
                  </p>
                </button>
              )
            )}
          </div>
        )}
      </main>
    </>
  );
}
