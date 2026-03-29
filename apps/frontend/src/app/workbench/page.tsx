"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { aiApi, pptxApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";

type Tab = "brainstorm" | "draft" | "summarize" | "upload";

export default function WorkbenchPage() {
  const [topic, setTopic] = useState("");
  const [scriptures, setScriptures] = useState("");
  const [style, setStyle] = useState("expository");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>("brainstorm");
  const token = useAppStore((s) => s.accessToken);

  // Summarize
  const [summaryText, setSummaryText] = useState("");

  // PPTX Upload
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadName, setUploadName] = useState("");
  const [uploadPastor, setUploadPastor] = useState("");
  const [uploadSeries, setUploadSeries] = useState("");
  const [uploadChurch, setUploadChurch] = useState("");
  const [uploadResult, setUploadResult] = useState("");

  async function handleBrainstorm() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await aiApi.brainstorm(
        {
          topic,
          scripture_refs: scriptures.split(",").map((s) => s.trim()).filter(Boolean),
          style,
        },
        token
      );
      setResult(data.outline);
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Error occurred");
    } finally {
      setLoading(false);
    }
  }

  async function handleDraft() {
    if (!token) return;
    setLoading(true);
    try {
      const data = await aiApi.draft(
        {
          topic,
          scripture_refs: scriptures.split(",").map((s) => s.trim()).filter(Boolean),
          style,
        },
        token
      );
      setResult(data.draft);
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Error occurred");
    } finally {
      setLoading(false);
    }
  }

  async function handleSummarize() {
    if (!token || !summaryText.trim()) return;
    setLoading(true);
    try {
      const data = await aiApi.summarize(summaryText, token);
      setResult(data.summary);
    } catch (err: unknown) {
      setResult(err instanceof Error ? err.message : "Error occurred");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload() {
    if (!uploadFile || !uploadName.trim()) return;
    setLoading(true);
    setUploadResult("");
    try {
      const data = await pptxApi.upload(uploadFile, uploadName, uploadPastor, uploadSeries, uploadChurch);
      setUploadResult(`Uploaded successfully! Sermon ID: ${data.sermon_id}, ${data.slides} slides extracted.`);
      setUploadFile(null);
      setUploadName("");
    } catch (err: unknown) {
      setUploadResult(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Navbar />
      <main className="flex-1 max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold mb-8">Pastor Workbench</h1>

        {!token && activeTab !== "upload" ? (
          <div className="text-center py-16 text-muted-foreground">
            <p className="text-lg mb-4">Please sign in to use the AI tools.</p>
            <a href="/login" className="text-primary hover:underline">
              Go to login
            </a>
          </div>
        ) : (
          <>
            {/* Tab buttons */}
            <div className="flex gap-1 border-b border-border mb-8">
              {(["brainstorm", "draft", "summarize", "upload"] as Tab[]).map((t) => (
                <button
                  key={t}
                  onClick={() => setActiveTab(t)}
                  className={`px-4 py-2 text-sm font-medium capitalize transition-colors ${
                    activeTab === t
                      ? "text-primary border-b-2 border-primary"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {t === "upload" ? "Upload PPTX" : t}
                </button>
              ))}
            </div>

            {/* Brainstorm / Draft tabs */}
            {(activeTab === "brainstorm" || activeTab === "draft") && (
              <div className="grid lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-1">Sermon Topic</label>
                    <input
                      type="text"
                      value={topic}
                      onChange={(e) => setTopic(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                      placeholder="e.g., The Prodigal Son and Grace"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Scripture References (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={scriptures}
                      onChange={(e) => setScriptures(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                      placeholder="e.g., Luke 15:11-32, Ephesians 2:8-9"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">Preaching Style</label>
                    <select
                      value={style}
                      onChange={(e) => setStyle(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    >
                      <option value="expository">Expository</option>
                      <option value="topical">Topical</option>
                      <option value="narrative">Narrative</option>
                      <option value="textual">Textual</option>
                    </select>
                  </div>

                  <button
                    onClick={activeTab === "brainstorm" ? handleBrainstorm : handleDraft}
                    disabled={loading || !topic.trim()}
                    className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
                  >
                    {loading ? "Generating..." : activeTab === "brainstorm" ? "Brainstorm" : "Generate Draft"}
                  </button>
                </div>

                <div className="bg-card rounded-xl border border-border p-6 min-h-[400px]">
                  <h2 className="font-semibold text-lg mb-4">
                    {activeTab === "brainstorm" ? "Brainstorm Results" : "Draft Output"}
                  </h2>
                  {result ? (
                    <div className="prose prose-sm max-w-none whitespace-pre-wrap">{result}</div>
                  ) : (
                    <p className="text-muted-foreground">
                      Your AI-generated content will appear here.
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Summarize tab */}
            {activeTab === "summarize" && (
              <div className="grid lg:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium mb-1">Text to Summarize</label>
                    <textarea
                      value={summaryText}
                      onChange={(e) => setSummaryText(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring min-h-[250px]"
                      placeholder="Paste sermon text, transcript, or notes to summarize..."
                    />
                  </div>
                  <button
                    onClick={handleSummarize}
                    disabled={loading || !summaryText.trim()}
                    className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
                  >
                    {loading ? "Summarizing..." : "Summarize"}
                  </button>
                </div>
                <div className="bg-card rounded-xl border border-border p-6 min-h-[400px]">
                  <h2 className="font-semibold text-lg mb-4">Summary</h2>
                  {result ? (
                    <div className="prose prose-sm max-w-none whitespace-pre-wrap">{result}</div>
                  ) : (
                    <p className="text-muted-foreground">
                      The AI summary will appear here.
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Upload PPTX tab */}
            {activeTab === "upload" && (
              <div className="max-w-lg space-y-6">
                <div>
                  <label className="block text-sm font-medium mb-1">PPTX File *</label>
                  <input
                    type="file"
                    accept=".pptx"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="w-full px-4 py-2 rounded-lg border border-input bg-background"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Sermon Name *</label>
                  <input
                    type="text"
                    value={uploadName}
                    onChange={(e) => setUploadName(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="e.g., The Good Shepherd"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Pastor Name</label>
                  <input
                    type="text"
                    value={uploadPastor}
                    onChange={(e) => setUploadPastor(e.target.value)}
                    className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Series</label>
                    <input
                      type="text"
                      value={uploadSeries}
                      onChange={(e) => setUploadSeries(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Church</label>
                    <input
                      type="text"
                      value={uploadChurch}
                      onChange={(e) => setUploadChurch(e.target.value)}
                      className="w-full px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    />
                  </div>
                </div>
                <button
                  onClick={handleUpload}
                  disabled={loading || !uploadFile || !uploadName.trim()}
                  className="w-full bg-primary text-primary-foreground py-3 rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
                >
                  {loading ? "Uploading..." : "Upload PPTX"}
                </button>
                {uploadResult && (
                  <div className={`p-4 rounded-lg text-sm ${
                    uploadResult.includes("success") ? "bg-green-500/10 text-green-400" : "bg-red-500/10 text-red-400"
                  }`}>
                    {uploadResult}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </>
  );
}
