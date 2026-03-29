"use client";

import { Navbar } from "@/components/navbar";
import { useEffect, useState, use } from "react";
import Link from "next/link";
import {
  pptxApi,
  type SlideContent,
  type SlideAnalysis,
  type SuggestionDecision,
  type AnalysisDocument,
  type DecisionsDocument,
} from "@/lib/api";

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const sermonId = Number(id);

  const [slides, setSlides] = useState<SlideContent[]>([]);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [analysis, setAnalysis] = useState<AnalysisDocument | null>(null);
  const [decisions, setDecisions] = useState<DecisionsDocument | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  // Local decision state for current slide
  const [localDecisions, setLocalDecisions] = useState<Record<string, SuggestionDecision>>({});

  useEffect(() => {
    loadData();
  }, [sermonId]);

  const loadData = async () => {
    try {
      const [s, a, d] = await Promise.all([
        pptxApi.slides(sermonId).catch(() => []),
        pptxApi.getAnalysis(sermonId).catch(() => null),
        pptxApi.getDecisions(sermonId).catch(() => null),
      ]);
      setSlides(s);
      setAnalysis(a);
      setDecisions(d);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load sermon data");
    }
  };

  const currentSlideData = slides[currentSlide];
  const currentAnalysis = analysis?.slides?.find(
    (s) => s.slideNumber === (currentSlide + 1)
  );
  const currentDecision = decisions?.slides?.find(
    (s) => s.slideNumber === (currentSlide + 1)
  );

  const handleAnalyze = async () => {
    if (!currentSlideData) return;
    setAnalyzing(true);
    setError("");
    try {
      const result = await pptxApi.analyzeSlide(sermonId, currentSlide + 1);
      // Merge into analysis state
      setAnalysis((prev) => {
        if (!prev) {
          return {
            sermonId: String(sermonId),
            createdAt: new Date().toISOString(),
            slides: [result],
          };
        }
        const existing = prev.slides.filter((s) => s.slideNumber !== result.slideNumber);
        return { ...prev, slides: [...existing, result] };
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDecision = (suggestionId: string, decision: "accepted" | "rejected" | "edited", finalText?: string) => {
    setLocalDecisions((prev) => ({
      ...prev,
      [suggestionId]: { suggestionId, decision, finalText },
    }));
  };

  const handleSaveDecisions = async () => {
    if (!currentSlideData || Object.keys(localDecisions).length === 0) return;
    setSaving(true);
    try {
      const result = await pptxApi.saveDecisions(
        sermonId,
        currentSlide + 1,
        Object.values(localDecisions)
      );
      setDecisions((prev) => {
        if (!prev) {
          return {
            sermonId: String(sermonId),
            updatedAt: new Date().toISOString(),
            slides: [result],
          };
        }
        const existing = prev.slides.filter((s) => s.slideNumber !== result.slideNumber);
        return { ...prev, slides: [...existing, result] };
      });
      setLocalDecisions({});
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError("");
    try {
      await pptxApi.generateUpdated(sermonId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  };

  if (slides.length === 0) {
    return (
      <>
        <Navbar />
        <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <div className="text-center text-muted-foreground py-20">
            <span className="text-5xl block mb-4">📄</span>
            <p className="text-lg font-medium">No slides found</p>
            <p className="text-sm mt-1">Upload a PPTX file for this sermon to review slides.</p>
            <Link
              href={`/sermons/${id}`}
              className="inline-block mt-4 text-primary hover:underline"
            >
              Back to sermon
            </Link>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link
              href={`/sermons/${id}`}
              className="text-sm text-muted-foreground hover:text-foreground mb-1 inline-block"
            >
              ← Back to sermon
            </Link>
            <h1 className="text-2xl font-bold">Slide Review</h1>
          </div>
          <div className="flex gap-2">
            <a
              href={pptxApi.downloadOriginalUrl(sermonId)}
              className="border border-border text-foreground px-3 py-2 rounded-md hover:bg-secondary text-sm"
            >
              Download Original
            </a>
            <a
              href={pptxApi.downloadUpdatedUrl(sermonId)}
              className="border border-border text-foreground px-3 py-2 rounded-md hover:bg-secondary text-sm"
            >
              Download Updated
            </a>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50 text-sm"
            >
              {generating ? "Generating…" : "Generate Updated PPTX"}
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-md mb-4">
            {error}
          </div>
        )}

        <div className="grid grid-cols-12 gap-6">
          {/* Slide list */}
          <div className="col-span-3 space-y-1">
            <h3 className="text-sm font-medium text-muted-foreground mb-2">Slides</h3>
            {slides.map((s, i) => {
              const hasAnalysis = analysis?.slides?.some((a) => a.slideNumber === s.slideNumber);
              const hasDecisions = decisions?.slides?.some((d) => d.slideNumber === s.slideNumber);
              return (
                <button
                  key={s.slideId}
                  onClick={() => {
                    setCurrentSlide(i);
                    setLocalDecisions({});
                  }}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    currentSlide === i
                      ? "bg-primary/20 text-primary"
                      : "hover:bg-secondary text-foreground"
                  }`}
                >
                  <span className="font-mono text-xs text-muted-foreground mr-2">
                    {s.slideNumber}
                  </span>
                  <span className="truncate">
                    {s.originalText.slice(0, 30) || "(empty)"}
                  </span>
                  <div className="flex gap-1 mt-1">
                    {hasAnalysis && (
                      <span className="bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded text-[10px]">
                        analyzed
                      </span>
                    )}
                    {hasDecisions && (
                      <span className="bg-green-500/20 text-green-300 px-1.5 py-0.5 rounded text-[10px]">
                        reviewed
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Slide content & analysis */}
          <div className="col-span-9 space-y-4">
            {/* Original text */}
            <div className="bg-card border border-border rounded-xl p-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold">
                  Slide {currentSlideData?.slideNumber}
                </h3>
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="bg-secondary text-foreground px-3 py-1 rounded-md text-sm hover:bg-secondary/80 disabled:opacity-50"
                >
                  {analyzing ? "Analyzing…" : "Analyze with AI"}
                </button>
              </div>
              <pre className="whitespace-pre-wrap text-sm text-foreground/80 bg-secondary/20 p-4 rounded-lg">
                {currentSlideData?.originalText || "(empty slide)"}
              </pre>
            </div>

            {/* Suggestions */}
            {currentAnalysis && currentAnalysis.suggestions.length > 0 && (
              <div className="bg-card border border-border rounded-xl p-6">
                <h3 className="font-semibold mb-4">
                  AI Suggestions ({currentAnalysis.suggestions.length})
                </h3>
                <div className="space-y-4">
                  {currentAnalysis.suggestions.map((suggestion) => {
                    const existingDecision = currentDecision?.decisions?.find(
                      (d) => d.suggestionId === suggestion.id
                    );
                    const localDec = localDecisions[suggestion.id];
                    const decision = localDec || existingDecision;

                    return (
                      <div
                        key={suggestion.id}
                        className={`p-4 rounded-lg border ${
                          decision?.decision === "accepted"
                            ? "border-green-500/30 bg-green-500/5"
                            : decision?.decision === "rejected"
                            ? "border-red-500/30 bg-red-500/5"
                            : "border-border bg-secondary/10"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className="bg-secondary px-2 py-0.5 rounded text-xs capitalize">
                            {suggestion.category}
                          </span>
                          {suggestion.confidence !== undefined && (
                            <span className="text-xs text-muted-foreground">
                              {Math.round(suggestion.confidence * 100)}% confidence
                            </span>
                          )}
                        </div>
                        <div className="grid grid-cols-2 gap-4 mb-3">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Original</p>
                            <p className="text-sm bg-red-500/10 p-2 rounded">{suggestion.original}</p>
                          </div>
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">Proposed</p>
                            <p className="text-sm bg-green-500/10 p-2 rounded">{suggestion.proposed}</p>
                          </div>
                        </div>
                        {suggestion.explanation && (
                          <p className="text-xs text-muted-foreground mb-3">{suggestion.explanation}</p>
                        )}
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleDecision(suggestion.id, "accepted")}
                            className={`px-3 py-1 rounded text-sm ${
                              decision?.decision === "accepted"
                                ? "bg-green-600 text-white"
                                : "bg-secondary hover:bg-green-500/20 text-foreground"
                            }`}
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => handleDecision(suggestion.id, "rejected")}
                            className={`px-3 py-1 rounded text-sm ${
                              decision?.decision === "rejected"
                                ? "bg-red-600 text-white"
                                : "bg-secondary hover:bg-red-500/20 text-foreground"
                            }`}
                          >
                            Reject
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {Object.keys(localDecisions).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-border">
                    <button
                      onClick={handleSaveDecisions}
                      disabled={saving}
                      className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
                    >
                      {saving ? "Saving…" : `Save ${Object.keys(localDecisions).length} Decision(s)`}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* No analysis yet */}
            {!currentAnalysis && (
              <div className="bg-card border border-border rounded-xl p-6 text-center text-muted-foreground">
                <p>Click &quot;Analyze with AI&quot; to get improvement suggestions for this slide.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
