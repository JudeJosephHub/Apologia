"use client";

import { Navbar } from "@/components/navbar";
import { useEffect, useRef, useState, useCallback } from "react";
import {
  encyclopediaApi,
  type FullGraph,
  type GraphNode,
  type GraphEdge,
  type EntityExploration,
  type CourseSuggestion,
  type SearchHit,
} from "@/lib/api";

type Tab = "graph" | "search" | "explore" | "courses";

export default function GraphPage() {
  const [tab, setTab] = useState<Tab>("graph");
  const [graph, setGraph] = useState<FullGraph | null>(null);
  const [entities, setEntities] = useState<Record<string, string[]>>({});
  const [exploration, setExploration] = useState<EntityExploration | null>(null);
  const [course, setCourse] = useState<CourseSuggestion | null>(null);
  const [searchResults, setSearchResults] = useState<SearchHit[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [courseTopic, setCourseTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [error, setError] = useState("");

  const svgRef = useRef<SVGSVGElement>(null);

  const loadGraph = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [g, e] = await Promise.all([
        encyclopediaApi.graph(),
        encyclopediaApi.entities(),
      ]);
      setGraph(g);
      setEntities(e);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load graph");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  // D3 graph rendering
  useEffect(() => {
    if (!graph || !svgRef.current || tab !== "graph") return;
    const svg = svgRef.current;
    const width = svg.clientWidth || 900;
    const height = svg.clientHeight || 600;

    // Clear previous
    while (svg.firstChild) svg.removeChild(svg.firstChild);

    const ns = "http://www.w3.org/2000/svg";

    // Build simulation-like layout using basic force positioning
    const nodes = graph.nodes.map((n, i) => ({
      ...n,
      x: width / 2 + Math.cos((2 * Math.PI * i) / graph.nodes.length) * 250 + (Math.random() - 0.5) * 50,
      y: height / 2 + Math.sin((2 * Math.PI * i) / graph.nodes.length) * 200 + (Math.random() - 0.5) * 50,
    }));

    const nodeMap = new Map(nodes.map((n) => [n.id, n]));

    // Draw edges
    graph.edges.forEach((edge) => {
      const source = nodeMap.get(edge.source);
      const target = nodeMap.get(edge.target);
      if (!source || !target) return;

      const line = document.createElementNS(ns, "line");
      line.setAttribute("x1", String(source.x));
      line.setAttribute("y1", String(source.y));
      line.setAttribute("x2", String(target.x));
      line.setAttribute("y2", String(target.y));
      line.setAttribute("stroke", "#6b7280");
      line.setAttribute("stroke-opacity", String(Math.min(edge.weight * 2, 1)));
      line.setAttribute("stroke-width", String(Math.max(edge.weight * 3, 1)));
      svg.appendChild(line);
    });

    // Draw nodes
    nodes.forEach((node) => {
      const g = document.createElementNS(ns, "g");
      g.setAttribute("transform", `translate(${node.x}, ${node.y})`);
      g.style.cursor = "pointer";

      const circle = document.createElementNS(ns, "circle");
      circle.setAttribute("r", "18");
      circle.setAttribute("fill", getDenomColor(node.denomination || ""));
      circle.setAttribute("stroke", "#fff");
      circle.setAttribute("stroke-width", "2");
      g.appendChild(circle);

      const text = document.createElementNS(ns, "text");
      text.setAttribute("y", "32");
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("fill", "#d1d5db");
      text.setAttribute("font-size", "10");
      text.textContent = truncate(node.sermon_name, 20);
      g.appendChild(text);

      g.addEventListener("click", () => {
        setTab("explore");
        handleExplore("sermon", String(node.id));
      });

      svg.appendChild(g);
    });
  }, [graph, tab]);

  const handleIndex = async () => {
    setIndexing(true);
    setError("");
    try {
      await encyclopediaApi.index();
      await loadGraph();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Indexing failed");
    } finally {
      setIndexing(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const results = await encyclopediaApi.search(searchQuery);
      setSearchResults(results);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExplore = async (type: string, value: string) => {
    setLoading(true);
    try {
      const result = await encyclopediaApi.explore(type, value);
      setExploration(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Exploration failed");
    } finally {
      setLoading(false);
    }
  };

  const handleCourse = async () => {
    if (!courseTopic.trim()) return;
    setLoading(true);
    try {
      const result = await encyclopediaApi.suggestCourse(courseTopic);
      setCourse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Course suggestion failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <main className="flex-1 flex flex-col">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold">Knowledge Graph</h1>
              <p className="text-muted-foreground">
                Explore thematic, scriptural, and topical connections between sermons.
              </p>
            </div>
            <button
              onClick={handleIndex}
              disabled={indexing}
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
            >
              {indexing ? "Indexing…" : "Re-index Sermons"}
            </button>
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-md mb-4">
              {error}
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-1 border-b border-border mb-6">
            {(["graph", "search", "explore", "courses"] as Tab[]).map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                  tab === t
                    ? "text-primary border-b-2 border-primary"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Graph Tab */}
          {tab === "graph" && (
            <div className="bg-card border border-border rounded-xl overflow-hidden">
              {loading ? (
                <div className="flex items-center justify-center h-[600px] text-muted-foreground">
                  Loading graph…
                </div>
              ) : graph && graph.nodes.length > 0 ? (
                <svg
                  ref={svgRef}
                  className="w-full"
                  style={{ height: 600, background: "var(--card)" }}
                />
              ) : (
                <div className="flex flex-col items-center justify-center h-[600px] text-muted-foreground">
                  <span className="text-5xl mb-4">🕸️</span>
                  <p className="text-lg font-medium">No graph data yet</p>
                  <p className="text-sm mt-1">Click &quot;Re-index Sermons&quot; to build the knowledge graph.</p>
                </div>
              )}
              {graph && (
                <div className="border-t border-border px-4 py-3 text-sm text-muted-foreground flex gap-6">
                  <span>{graph.nodes.length} sermons</span>
                  <span>{graph.edges.length} connections</span>
                </div>
              )}
            </div>
          )}

          {/* Search Tab */}
          {tab === "search" && (
            <div>
              <div className="flex gap-2 mb-6">
                <input
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  placeholder="Search sermons semantically…"
                  className="flex-1 bg-card border border-border rounded-md px-4 py-2 text-foreground placeholder:text-muted-foreground"
                />
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
                >
                  Search
                </button>
              </div>
              {searchResults.length > 0 && (
                <div className="space-y-3">
                  {searchResults.map((hit, i) => (
                    <div key={i} className="p-4 bg-card border border-border rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs bg-secondary px-2 py-0.5 rounded">
                          {hit.metadata?.sermon_name || "Unknown"}
                        </span>
                        {hit.distance !== undefined && (
                          <span className="text-xs text-muted-foreground">
                            similarity: {(1 - hit.distance).toFixed(2)}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-foreground/80">{hit.text}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Explore Tab */}
          {tab === "explore" && (
            <div>
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">Entities</h3>
                {Object.entries(entities).map(([type, values]) => (
                  <div key={type} className="mb-4">
                    <h4 className="text-sm font-medium text-muted-foreground capitalize mb-2">{type}</h4>
                    <div className="flex flex-wrap gap-2">
                      {values.map((v) => (
                        <button
                          key={v}
                          onClick={() => handleExplore(type, v)}
                          className="bg-secondary hover:bg-secondary/80 text-foreground px-3 py-1 rounded-full text-sm transition-colors"
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              {exploration && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-1">
                    {exploration.entity_type}: {exploration.entity_value}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Found in {exploration.sermon_count} sermon(s)
                  </p>
                  <div className="space-y-2">
                    {exploration.sermons.map((s) => (
                      <div key={s.sermon_id} className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg">
                        <span className="font-medium">{s.sermon_name}</span>
                        {s.pastor_name && (
                          <span className="text-sm text-muted-foreground">by {s.pastor_name}</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Courses Tab */}
          {tab === "courses" && (
            <div>
              <div className="flex gap-2 mb-6">
                <input
                  value={courseTopic}
                  onChange={(e) => setCourseTopic(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleCourse()}
                  placeholder="Enter a topic (e.g. 'grace', 'salvation', 'prayer')…"
                  className="flex-1 bg-card border border-border rounded-md px-4 py-2 text-foreground placeholder:text-muted-foreground"
                />
                <button
                  onClick={handleCourse}
                  disabled={loading}
                  className="bg-primary text-primary-foreground px-6 py-2 rounded-md hover:bg-primary/90 disabled:opacity-50"
                >
                  Suggest Course
                </button>
              </div>
              {course && (
                <div className="bg-card border border-border rounded-xl p-6">
                  <h3 className="text-lg font-semibold mb-1">
                    Course: {course.topic}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {course.sermon_count} sermon(s) in this course
                  </p>
                  <div className="space-y-2 mb-4">
                    {course.sermons.map((s, i) => (
                      <div key={s.sermon_id} className="flex items-center gap-3 p-3 bg-secondary/30 rounded-lg">
                        <span className="text-muted-foreground text-sm w-6">{i + 1}.</span>
                        <span className="font-medium">{s.sermon_name}</span>
                        {s.pastor_name && (
                          <span className="text-sm text-muted-foreground">by {s.pastor_name}</span>
                        )}
                      </div>
                    ))}
                  </div>
                  {course.themes_covered.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-2">
                      {course.themes_covered.map((t) => (
                        <span key={t} className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-xs">
                          {t}
                        </span>
                      ))}
                    </div>
                  )}
                  {course.scripture_refs.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {course.scripture_refs.map((r) => (
                        <span key={r} className="bg-yellow-500/20 text-yellow-300 px-2 py-0.5 rounded text-xs">
                          {r}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

function getDenomColor(denom: string): string {
  const colors: Record<string, string> = {
    reformed: "#3b82f6",
    baptist: "#ef4444",
    methodist: "#22c55e",
    pentecostal: "#f97316",
    lutheran: "#a855f7",
    catholic: "#eab308",
    anglican: "#06b6d4",
    presbyterian: "#6366f1",
  };
  return colors[denom.toLowerCase()] || "#6b7280";
}

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}
