const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001/api/v1";

type FetchOptions = {
  method?: string;
  body?: unknown;
  token?: string;
};

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

async function apiUpload<T>(path: string, formData: FormData, token?: string): Promise<T> {
  const headers: Record<string, string> = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers,
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

// Sermons
export const sermonsApi = {
  list: (params?: { offset?: number; limit?: number; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.offset) query.set("offset", String(params.offset));
    if (params?.limit) query.set("limit", String(params.limit));
    if (params?.search) query.set("search", params.search);
    return apiFetch<{ items: Sermon[]; total: number }>(`/sermons?${query}`);
  },
  get: (id: number) => apiFetch<Sermon>(`/sermons/${id}`),
  create: (data: SermonCreate, token: string) =>
    apiFetch<Sermon>("/sermons", { method: "POST", body: data, token }),
  delete: (id: number, token: string) =>
    apiFetch<void>(`/sermons/${id}`, { method: "DELETE", token }),
};

// AI
export const aiApi = {
  summarize: (text: string, token: string) =>
    apiFetch<{ summary: string }>("/ai/summarize", { method: "POST", body: { text }, token }),
  brainstorm: (data: BrainstormRequest, token: string) =>
    apiFetch<BrainstormResponse>("/ai/brainstorm", { method: "POST", body: data, token }),
  draft: (data: DraftRequest, token: string) =>
    apiFetch<DraftResponse>("/ai/draft", { method: "POST", body: data, token }),
};

// Semantic search
export const searchApi = {
  semantic: (query: string, limit = 10) =>
    apiFetch<{ results: SearchResult[]; total: number }>("/links/search", {
      method: "POST",
      body: { query, limit },
    }),
};

// Encyclopedia (from Apologia intelligence layer)
export const encyclopediaApi = {
  index: () => apiFetch<IndexResult>("/encyclopedia/index", { method: "POST" }),
  graph: () => apiFetch<FullGraph>("/encyclopedia/graph"),
  entities: () => apiFetch<Record<string, string[]>>("/encyclopedia/entities"),
  explore: (type: string, value: string) =>
    apiFetch<EntityExploration>(`/encyclopedia/explore/${encodeURIComponent(type)}/${encodeURIComponent(value)}`),
  search: (q: string, n = 10) => apiFetch<SearchHit[]>(`/encyclopedia/search?q=${encodeURIComponent(q)}&n=${n}`),
  suggestCourse: (topic: string, maxSermons = 10) =>
    apiFetch<CourseSuggestion>(`/encyclopedia/courses/suggest?topic=${encodeURIComponent(topic)}&max_sermons=${maxSermons}`),
  sermonIntelligence: (id: number) => apiFetch<SermonIntelligence>(`/encyclopedia/sermons/${id}/intelligence`),
  sermonRelated: (id: number, n = 5) => apiFetch<RelatedSermon[]>(`/encyclopedia/sermons/${id}/related?n=${n}`),
  sermonGraph: (id: number) => apiFetch<SermonGraph>(`/encyclopedia/sermons/${id}/graph`),
};

// PPTX (from Apologia)
export const pptxApi = {
  upload: (file: File, sermonName: string, pastorName?: string, seriesName?: string, churchName?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("sermon_name", sermonName);
    if (pastorName) formData.append("pastor_name", pastorName);
    if (seriesName) formData.append("series_name", seriesName);
    if (churchName) formData.append("church_name", churchName);
    return apiUpload<{ sermon_id: number; slides: number }>("/pptx/upload", formData);
  },
  slides: (id: number) => apiFetch<SlideContent[]>(`/pptx/${id}/slides`),
  summarize: (id: number) => apiFetch<{ summary: string }>(`/pptx/${id}/summary`, { method: "POST" }),
  analyzeSlide: (id: number, slideNumber: number) =>
    apiFetch<SlideAnalysis>(`/pptx/${id}/slides/${slideNumber}/analyze`, { method: "POST" }),
  getAnalysis: (id: number) => apiFetch<AnalysisDocument>(`/pptx/${id}/analysis`),
  saveDecisions: (id: number, slideNumber: number, decisions: SuggestionDecision[]) =>
    apiFetch<SlideDecision>(`/pptx/${id}/slides/${slideNumber}/decisions`, { method: "POST", body: { decisions } }),
  getDecisions: (id: number) => apiFetch<DecisionsDocument>(`/pptx/${id}/decisions`),
  generateUpdated: (id: number) => apiFetch<{ status: string }>(`/pptx/${id}/generate-updated-pptx`, { method: "POST" }),
  downloadOriginalUrl: (id: number) => `${API_BASE}/pptx/${id}/download-original-pptx`,
  downloadUpdatedUrl: (id: number) => `${API_BASE}/pptx/${id}/download-updated-pptx`,
  attachVideo: (id: number, youtubeUrl: string) =>
    apiFetch<{ youtube_video_id: string }>(`/pptx/${id}/video/attach`, { method: "POST", body: { youtube_url: youtubeUrl } }),
  fetchTranscript: (id: number) =>
    apiFetch<{ segments: TranscriptSegment[] }>(`/pptx/${id}/transcript/fetch`, { method: "POST" }),
  getTranscript: (id: number) => apiFetch<TranscriptDocument>(`/pptx/${id}/transcript`),
  saveManualTranscript: (id: number, text: string) =>
    apiFetch<TranscriptDocument>(`/pptx/${id}/transcript/manual`, { method: "POST", body: { text } }),
};

// Inspiration (from Apologia)
export const inspirationApi = {
  daily: () => apiFetch<DailyInspiration>("/inspiration/daily"),
};

// ── Types ────────────────────────────────────────────────────────────────

export interface Sermon {
  id: number;
  title: string;
  preacher: string;
  date_preached: string;
  denomination: string;
  source_url: string;
  audio_url: string;
  transcript: string;
  summary: string;
  outline: string;
  themes: string;
  sermonaudio_id: string;
  status: string;
  created_at: string;
  // Apologia fields
  series_name?: string;
  church_name?: string;
  youtube_url?: string;
  youtube_video_id?: string;
  video_status?: string;
  transcript_status?: string;
  file_path?: string;
  original_filename?: string;
}

export interface SermonCreate {
  title: string;
  preacher?: string;
  transcript?: string;
}

export interface BrainstormRequest {
  topic: string;
  scripture_refs?: string[];
  style?: string;
}

export interface BrainstormResponse {
  outline: string;
  key_points: string[];
  suggested_scriptures: string[];
}

export interface DraftRequest {
  topic: string;
  outline?: string;
  scripture_refs?: string[];
  style?: string;
  length?: string;
}

export interface DraftResponse {
  draft: string;
  title_suggestion: string;
}

export interface SearchResult {
  sermon_id: number;
  title: string;
  score: number;
  snippet?: string;
}

// Encyclopedia types
export interface GraphNode {
  id: number;
  sermon_name: string;
  pastor_name?: string;
  denomination?: string;
  entities: Record<string, string[]>;
}

export interface GraphEdge {
  source: number;
  target: number;
  type: string;
  weight: number;
  shared: string[];
}

export interface FullGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface SermonIntelligence {
  sermon_id: number;
  sermon_name: string;
  pastor_name?: string;
  themes: string[];
  scripture_refs: string[];
  theological_concepts: string[];
  traditions: string[];
  chunk_count: number;
  indexed_at?: string;
}

export interface RelatedSermon {
  sermon_id: number;
  sermon_name: string;
  pastor_name?: string;
  similarity?: number;
  total_weight?: number;
  edges?: { type: string; weight: number; shared: string[] }[];
}

export interface SermonGraph {
  sermon_id: number;
  entities: Record<string, string[]>;
  related_sermons: RelatedSermon[];
  edge_count: number;
}

export interface EntityExploration {
  entity_type: string;
  entity_value: string;
  sermon_count: number;
  sermons: { sermon_id: number; sermon_name: string; pastor_name?: string }[];
}

export interface CourseSuggestion {
  topic: string;
  sermon_count: number;
  sermons: { sermon_id: number; sermon_name: string; pastor_name?: string }[];
  themes_covered: string[];
  concepts_covered: string[];
  scripture_refs: string[];
}

export interface SearchHit {
  chunk_id: string;
  text: string;
  distance?: number;
  metadata: Record<string, string>;
}

export interface IndexResult {
  indexed: number;
  total_chunks: number;
  sermons: { id: number; name: string; chunks: number }[];
}

export interface DailyInspiration {
  date: string;
  kind: string;
  text: string;
  citation: string;
}

// PPTX types
export interface SlideContent {
  slideId: string;
  slideNumber: number;
  originalText: string;
}

export interface Suggestion {
  id: string;
  category: string;
  original: string;
  proposed: string;
  explanation?: string;
  confidence?: number;
}

export interface SlideAnalysis {
  slideId: string;
  slideNumber: number;
  originalText: string;
  suggestions: Suggestion[];
}

export interface AnalysisDocument {
  sermonId: string;
  createdAt: string;
  slides: SlideAnalysis[];
}

export interface SuggestionDecision {
  suggestionId: string;
  decision: "accepted" | "rejected" | "edited";
  finalText?: string;
}

export interface SlideDecision {
  slideId: string;
  slideNumber: number;
  decisions: SuggestionDecision[];
}

export interface DecisionsDocument {
  sermonId: string;
  updatedAt: string;
  slides: SlideDecision[];
}

export interface TranscriptSegment {
  start: number;
  duration: number;
  text: string;
}

export interface TranscriptDocument {
  sermonId: string;
  youtubeVideoId?: string;
  fetchedAt: string;
  segments: TranscriptSegment[];
}
