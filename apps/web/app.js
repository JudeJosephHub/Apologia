const API_BASE = "http://127.0.0.1:8000";

const state = {
  sermons: [],
  slides: [],
  analysisBySlideId: {},
  decisionsBySlideId: {},
  selectedSermonId: null,
  selectedSlideNumber: null,
};

const apiStatus = document.getElementById("apiStatus");
const uploadForm = document.getElementById("uploadForm");
const uploadStatus = document.getElementById("uploadStatus");
const sermonTable = document.getElementById("sermonTable");
const refreshSermons = document.getElementById("refreshSermons");
const slideList = document.getElementById("slideList");
const slideText = document.getElementById("slideText");
const suggestions = document.getElementById("suggestions");
const reviewStatus = document.getElementById("reviewStatus");
const analyzeSlide = document.getElementById("analyzeSlide");
const saveDecisions = document.getElementById("saveDecisions");
const generatePptx = document.getElementById("generatePptx");
const downloadLink = document.getElementById("downloadLink");

async function apiFetch(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }
  if (response.headers.get("content-type")?.includes("application/json")) {
    return response.json();
  }
  return response;
}

async function checkApi() {
  try {
    await apiFetch("/sermons");
    apiStatus.textContent = "Online";
  } catch (error) {
    apiStatus.textContent = "Offline";
    apiStatus.style.color = "#b43e2b";
  }
}

async function loadSermons() {
  try {
    state.sermons = await apiFetch("/sermons");
    renderSermons();
  } catch (error) {
    sermonTable.textContent = "Unable to load sermons.";
  }
}

function renderSermons() {
  sermonTable.innerHTML = "";
  if (!state.sermons.length) {
    sermonTable.textContent = "No sermons yet.";
    return;
  }

  state.sermons.forEach((sermon) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <strong>${sermon.sermonName}</strong>
      <span>Series: ${sermon.seriesName || "-"}</span>
      <span>Date: ${sermon.weekOrDate || "-"}</span>
      <span>Pastor: ${sermon.pastorName || "-"}</span>
      <span>Status: ${sermon.status}</span>
      <button>Review</button>
    `;
    row.querySelector("button").addEventListener("click", () => {
      selectSermon(sermon.id);
    });
    sermonTable.appendChild(row);
  });
}

async function selectSermon(sermonId) {
  state.selectedSermonId = sermonId;
  reviewStatus.textContent = "Loading slides and analysis...";
  downloadLink.classList.add("hidden");

  try {
    const [slides, analysis, decisions] = await Promise.all([
      apiFetch(`/sermons/${sermonId}/slides`),
      apiFetch(`/sermons/${sermonId}/analysis`),
      apiFetch(`/sermons/${sermonId}/decisions`),
    ]);
    state.slides = slides;
    state.analysisBySlideId = mapAnalysis(analysis.slides || []);
    state.decisionsBySlideId = mapDecisions(decisions.slides || []);
    state.selectedSlideNumber = slides.length ? slides[0].slideNumber : null;
    renderSlides();
    reviewStatus.textContent = "";
  } catch (error) {
    reviewStatus.textContent = "Unable to load review data.";
  }
}

function mapAnalysis(slides) {
  return slides.reduce((acc, slide) => {
    acc[slide.slideId] = slide;
    return acc;
  }, {});
}

function mapDecisions(slides) {
  return slides.reduce((acc, slide) => {
    const decisionMap = {};
    (slide.decisions || []).forEach((decision) => {
      decisionMap[decision.suggestionId] = {
        decision: decision.decision,
        finalText: decision.finalText || "",
      };
    });
    acc[slide.slideId] = decisionMap;
    return acc;
  }, {});
}

function renderSlides() {
  slideList.innerHTML = "";
  if (!state.slides.length) {
    slideList.textContent = "No slides found.";
    slideText.textContent = "";
    suggestions.textContent = "";
    return;
  }

  state.slides.forEach((slide) => {
    const button = document.createElement("button");
    button.textContent = `Slide ${slide.slideNumber}`;
    if (slide.slideNumber === state.selectedSlideNumber) {
      button.classList.add("active");
    }
    button.addEventListener("click", () => {
      state.selectedSlideNumber = slide.slideNumber;
      renderSlides();
    });
    slideList.appendChild(button);
  });

  renderSlideDetails();
}

function renderSlideDetails() {
  const slide = state.slides.find(
    (item) => item.slideNumber === state.selectedSlideNumber
  );
  if (!slide) {
    slideText.textContent = "Select a slide.";
    suggestions.textContent = "";
    return;
  }

  slideText.textContent = slide.originalText || "(No text found on this slide.)";
  const slideId = slide.slideId;
  const analysis = state.analysisBySlideId[slideId];
  const suggestionList = analysis ? analysis.suggestions : [];
  const decisionMap = ensureDecisionMap(slideId);

  suggestions.innerHTML = "";
  if (!suggestionList || !suggestionList.length) {
    const empty = document.createElement("div");
    empty.className = "muted";
    empty.textContent = "No suggestions yet. Click Analyze Slide to generate.";
    suggestions.appendChild(empty);
    return;
  }

  suggestionList.forEach((suggestion) => {
    const decision = decisionMap[suggestion.id] || {};
    const card = document.createElement("div");
    card.className = "suggestion";
    card.innerHTML = `
      <h3>${suggestion.category}</h3>
      <div class="meta">Original: ${suggestion.original}</div>
      <div class="meta">Proposed: ${suggestion.proposed}</div>
      <div class="meta">${suggestion.explanation || ""}</div>
      <div class="meta">Confidence: ${
        suggestion.confidence != null ? suggestion.confidence : "-"
      }</div>
    `;

    const actions = document.createElement("div");
    actions.className = "suggestion-actions";

    const accept = document.createElement("button");
    accept.textContent = "Accept";
    accept.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "accepted", "");
      renderSlideDetails();
    });

    const reject = document.createElement("button");
    reject.textContent = "Reject";
    reject.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "rejected", "");
      renderSlideDetails();
    });

    const edit = document.createElement("button");
    edit.textContent = "Edit";
    edit.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "edited", suggestion.proposed);
      renderSlideDetails();
    });

    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Final text";
    input.value = decision.finalText || "";
    input.disabled = decision.decision !== "edited";
    input.addEventListener("input", (event) => {
      setDecision(slideId, suggestion.id, "edited", event.target.value);
    });

    if (decision.decision === "accepted") {
      accept.style.background = "#2b8a6f";
    }
    if (decision.decision === "rejected") {
      reject.style.background = "#5c4c43";
    }
    if (decision.decision === "edited") {
      edit.style.background = "#2b8a6f";
    }

    actions.appendChild(accept);
    actions.appendChild(reject);
    actions.appendChild(edit);
    actions.appendChild(input);
    card.appendChild(actions);
    suggestions.appendChild(card);
  });
}

function ensureDecisionMap(slideId) {
  if (!state.decisionsBySlideId[slideId]) {
    state.decisionsBySlideId[slideId] = {};
  }
  return state.decisionsBySlideId[slideId];
}

function setDecision(slideId, suggestionId, decision, finalText) {
  const map = ensureDecisionMap(slideId);
  map[suggestionId] = { decision, finalText };
}

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(uploadForm);
  uploadStatus.textContent = "Uploading...";
  try {
    await apiFetch("/sermons", {
      method: "POST",
      body: formData,
    });
    uploadStatus.textContent = "Upload complete.";
    uploadForm.reset();
    await loadSermons();
  } catch (error) {
    uploadStatus.textContent = "Upload failed.";
  }
});

refreshSermons.addEventListener("click", loadSermons);

analyzeSlide.addEventListener("click", async () => {
  if (!state.selectedSermonId || !state.selectedSlideNumber) {
    reviewStatus.textContent = "Select a sermon and slide first.";
    return;
  }
  reviewStatus.textContent = "Analyzing slide...";
  try {
    const analysis = await apiFetch(
      `/sermons/${state.selectedSermonId}/slides/${state.selectedSlideNumber}/analyze`,
      { method: "POST" }
    );
    state.analysisBySlideId[analysis.slideId] = analysis;
    reviewStatus.textContent = "";
    renderSlideDetails();
  } catch (error) {
    reviewStatus.textContent = "Analysis failed.";
  }
});

saveDecisions.addEventListener("click", async () => {
  if (!state.selectedSermonId || !state.selectedSlideNumber) {
    reviewStatus.textContent = "Select a sermon and slide first.";
    return;
  }
  const slideId = `${state.selectedSermonId}:${state.selectedSlideNumber}`;
  const decisionMap = state.decisionsBySlideId[slideId] || {};
  const payload = {
    decisions: Object.entries(decisionMap)
      .filter(([, value]) => value.decision)
      .map(([suggestionId, value]) => ({
        suggestionId,
        decision: value.decision,
        finalText: value.finalText || null,
      })),
  };

  reviewStatus.textContent = "Saving decisions...";
  try {
    await apiFetch(
      `/sermons/${state.selectedSermonId}/slides/${state.selectedSlideNumber}/decisions`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );
    reviewStatus.textContent = "Decisions saved.";
  } catch (error) {
    reviewStatus.textContent = "Save failed.";
  }
});

generatePptx.addEventListener("click", async () => {
  if (!state.selectedSermonId) {
    reviewStatus.textContent = "Select a sermon first.";
    return;
  }
  reviewStatus.textContent = "Generating PPTX...";
  try {
    await apiFetch(`/sermons/${state.selectedSermonId}/generate-updated-pptx`, {
      method: "POST",
    });
    const href = `${API_BASE}/sermons/${state.selectedSermonId}/download-updated-pptx`;
    downloadLink.href = href;
    downloadLink.classList.remove("hidden");
    reviewStatus.textContent = "";
  } catch (error) {
    reviewStatus.textContent = "Generation failed.";
  }
});

checkApi();
loadSermons();
