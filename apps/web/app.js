const API_BASE = "http://127.0.0.1:8000";

const state = {
  sermons: [],
  slides: [],
  analysisBySlideId: {},
  decisionsBySlideId: {},
  selectedSermonId: null,
  selectedSlideNumber: null,
  currentPastor: null,
};

// DOM Elements
const loginModal = document.getElementById("loginModal");
const loginForm = document.getElementById("loginForm");
const mainContent = document.getElementById("mainContent");
const navbarUser = document.getElementById("navbarUser");
const navbarLogoutBtn = document.getElementById("navbarLogoutBtn");
const apiStatusDot = document.getElementById("apiStatusDot");
const apiStatusText = document.getElementById("apiStatusText");

// Home Page Elements
const homePage = document.getElementById("homePage");
const uploadBtn = document.getElementById("uploadBtn");
const sermonTableBody = document.getElementById("sermonTableBody");

// Filter elements
const filterName = document.getElementById("filterName");
const filterSeries = document.getElementById("filterSeries");
const filterDate = document.getElementById("filterDate");
const filterPastor = document.getElementById("filterPastor");
const filterStatus = document.getElementById("filterStatus");

// Upload Modal Elements
const uploadModal = document.getElementById("uploadModal");
const uploadForm = document.getElementById("uploadForm");
const fileDropZone = document.getElementById("fileDropZone");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const sermonNameInput = document.getElementById("sermonNameInput");
const seriesNameInput = document.getElementById("seriesNameInput");
const weekOrDateInput = document.getElementById("weekOrDateInput");
const pastorNameInput = document.getElementById("pastorNameInput");
const cancelUploadBtn = document.getElementById("cancelUploadBtn");
const closeUploadBtn = document.getElementById("closeUploadBtn");
const modalOverlay = document.getElementById("modalOverlay");

// Review Page Elements
const reviewPage = document.getElementById("reviewPage");
const backBtn = document.getElementById("backBtn");
const reviewTitle = document.getElementById("reviewTitle");
const analyzeBtn = document.getElementById("analyzeBtn");
const saveChangesBtn = document.getElementById("saveChangesBtn");
const generatePptxBtn = document.getElementById("generatePptxBtn");
const downloadPptxLink = document.getElementById("downloadPptxLink");
const slideList = document.getElementById("slideList");
const suggestionsContainer = document.getElementById("suggestionsContainer");
const reviewStatus = document.getElementById("reviewStatus");
const slideCounter = document.getElementById("slideCounter");
const prevSlideBtn = document.getElementById("prevSlideBtn");
const nextSlideBtn = document.getElementById("nextSlideBtn");

// Authentication
function checkLogin() {
  const pastorName = localStorage.getItem("pastorName");
  if (pastorName) {
    state.currentPastor = pastorName;
    showMainContent(pastorName);
    checkApi();
    loadSermons();
  } else {
    showLoginModal();
  }
}

function showLoginModal() {
  loginModal.classList.add("active");
  mainContent.style.display = "none";
}

function showMainContent(pastorName) {
  loginModal.classList.remove("active");
  mainContent.style.display = "grid";
  navbarUser.textContent = pastorName;
  pastorNameInput.value = pastorName;
}

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const pastorName = document.getElementById("loginPastorName").value.trim();
  if (pastorName) {
    localStorage.setItem("pastorName", pastorName);
    document.getElementById("loginPastorName").value = "";
    state.currentPastor = pastorName;
    showMainContent(pastorName);
    checkApi();
    loadSermons();
  }
});

navbarLogoutBtn.addEventListener("click", () => {
  localStorage.removeItem("pastorName");
  state.currentPastor = null;
  showLoginModal();
});

// Logo click to go back to home
const logo = document.querySelector(".logo");
if (logo) {
  logo.addEventListener("click", () => {
    if (state.selectedSermonId) {
      backToHome();
    }
  });
}

// API Communication
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
    apiStatusDot.className = "status-dot online";
    apiStatusText.textContent = "Online";
  } catch (error) {
    apiStatusDot.className = "status-dot offline";
    apiStatusText.textContent = "Offline";
  }
}

// Load and Render Sermons
async function loadSermons() {
  try {
    state.sermons = await apiFetch("/sermons");
    renderSermonsList();
  } catch (error) {
    sermonTableBody.innerHTML = '<div class="error">Unable to load sermons</div>';
  }
}

function renderSermonsList() {
  sermonTableBody.innerHTML = "";
  
  if (!state.sermons.length) {
    sermonTableBody.innerHTML = '<div class="empty-message">No sermons uploaded yet</div>';
    return;
  }

  // Get filter values
  const nameFilter = (filterName.value || "").toLowerCase();
  const seriesFilter = (filterSeries.value || "").toLowerCase();
  const dateFilter = (filterDate.value || "").toLowerCase();
  const pastorFilter = (filterPastor.value || "").toLowerCase();
  const statusFilter = (filterStatus.value || "").toLowerCase();

  // Filter sermons
  const filteredSermons = state.sermons.filter((sermon) => {
    const matchName = !nameFilter || (sermon.sermonName || "").toLowerCase().includes(nameFilter);
    const matchSeries = !seriesFilter || (sermon.seriesName || "").toLowerCase().includes(seriesFilter);
    const matchDate = !dateFilter || (sermon.weekOrDate || "").toLowerCase().includes(dateFilter);
    const matchPastor = !pastorFilter || (sermon.pastorName || "").toLowerCase().includes(pastorFilter);
    const matchStatus = !statusFilter || (sermon.status || "").toLowerCase().includes(statusFilter);
    
    return matchName && matchSeries && matchDate && matchPastor && matchStatus;
  });

  if (filteredSermons.length === 0) {
    sermonTableBody.innerHTML = '<div class="empty-message">No sermons match the filters</div>';
    return;
  }

  filteredSermons.forEach((sermon) => {
    const row = document.createElement("div");
    row.className = "table-row";
    
    const createdDate = new Date(sermon.createdAt).toLocaleDateString();
    
    row.innerHTML = `
      <div class="col col-name">${sermon.sermonName || "-"}</div>
      <div class="col col-series">${sermon.seriesName || "-"}</div>
      <div class="col col-date">${sermon.weekOrDate || createdDate}</div>
      <div class="col col-pastor">${sermon.pastorName || "-"}</div>
      <div class="col col-status"><span class="status-badge">${sermon.status}</span></div>
      <div class="col col-actions">
        <button class="btn btn-sm btn-primary review-action" data-id="${sermon.id}">Review</button>
      </div>
    `;
    
    const reviewBtn = row.querySelector(".review-action");
    reviewBtn.addEventListener("click", () => {
      navigateToReview(sermon.id, sermon.sermonName);
    });
    
    sermonTableBody.appendChild(row);
  });
}

// Upload Modal Management
uploadBtn.addEventListener("click", openUploadModal);
cancelUploadBtn.addEventListener("click", closeUploadModal);
closeUploadBtn.addEventListener("click", closeUploadModal);
modalOverlay.addEventListener("click", closeUploadModal);

// Filter listeners
filterName.addEventListener("input", renderSermonsList);
filterSeries.addEventListener("input", renderSermonsList);
filterDate.addEventListener("input", renderSermonsList);
filterPastor.addEventListener("input", renderSermonsList);
filterStatus.addEventListener("change", renderSermonsList);

function openUploadModal() {
  uploadModal.classList.add("active");
  modalOverlay.classList.add("active");
  // Set date picker to next Sunday
  weekOrDateInput.value = getNextSunday();
}

function closeUploadModal() {
  uploadModal.classList.remove("active");
  modalOverlay.classList.remove("active");
  uploadForm.reset();
  uploadStatus.textContent = "";
  weekOrDateInput.value = getNextSunday();
}

function getNextSunday() {
  const today = new Date();
  const currentDay = today.getDay();
  const daysUntilSunday = (7 - currentDay) % 7 || 7;
  const nextSunday = new Date(today);
  nextSunday.setDate(nextSunday.getDate() + daysUntilSunday);
  
  const year = nextSunday.getFullYear();
  const month = String(nextSunday.getMonth() + 1).padStart(2, '0');
  const day = String(nextSunday.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

// File Drop Zone
fileDropZone.addEventListener("click", () => fileInput.click());
fileDropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  fileDropZone.classList.add("drag-over");
});
fileDropZone.addEventListener("dragleave", () => {
  fileDropZone.classList.remove("drag-over");
});
fileDropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  fileDropZone.classList.remove("drag-over");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    fileInput.files = files;
  }
});

fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const p = fileDropZone.querySelector("p");
    if (p) p.textContent = fileInput.files[0].name;
  }
});

// Upload Form Submission
uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const formData = new FormData(uploadForm);
  uploadStatus.textContent = "Uploading...";
  
  try {
    await apiFetch("/sermons", {
      method: "POST",
      body: formData,
    });
    uploadStatus.textContent = "Upload successful!";
    setTimeout(() => {
      closeUploadModal();
      loadSermons();
    }, 1000);
  } catch (error) {
    uploadStatus.textContent = "Upload failed: " + error.message;
  }
});

// Navigation to Review Page
function navigateToReview(sermonId, sermonName) {
  state.selectedSermonId = sermonId;
  reviewTitle.textContent = sermonName;
  homePage.style.display = "none";
  reviewPage.style.display = "block";
  loadSermonReview(sermonId);
}

function backToHome() {
  homePage.style.display = "block";
  reviewPage.style.display = "none";
  state.selectedSermonId = null;
  state.slides = [];
}

backBtn.addEventListener("click", backToHome);

// Load Review Data
async function loadSermonReview(sermonId) {
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
    
    renderSlideList();
    renderSlideDetails();
  } catch (error) {
    reviewStatus.textContent = "Unable to load review data: " + error.message;
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

// Render Slide List
function renderSlideList() {
  slideList.innerHTML = "";
  slideCounter.textContent = `Slide 1 of ${state.slides.length}`;
  
  if (!state.slides.length) {
    slideList.innerHTML = '<p class="empty-state">No slides found</p>';
    return;
  }

  state.slides.forEach((slide) => {
    const button = document.createElement("button");
    button.className = "slide-thumbnail";
    button.textContent = `Slide ${slide.slideNumber}`;
    
    if (slide.slideNumber === state.selectedSlideNumber) {
      button.classList.add("active");
    }
    
    button.addEventListener("click", () => {
      state.selectedSlideNumber = slide.slideNumber;
      renderSlideList();
      renderSlideDetails();
    });
    
    slideList.appendChild(button);
  });
}

// Render Slide Details and Suggestions
function renderSlideDetails() {
  const slide = state.slides.find(s => s.slideNumber === state.selectedSlideNumber);
  
  if (!slide) {
    slidePreview.innerHTML = '<p class="empty-state">Select a slide</p>';
    suggestionsContainer.innerHTML = '<p class="empty-state">Select a slide</p>';
    slideCounter.textContent = `Slide 1 of ${state.slides.length}`;
    return;
  }

  slideCounter.textContent = `Slide ${slide.slideNumber} of ${state.slides.length}`;
  
  // Render slide preview with content
  slidePreview.innerHTML = `
    <div class="slide-content-preview">
      <div class="slide-number-badge">Slide ${slide.slideNumber}</div>
      <div class="slide-text-content">${slide.originalText || "<p class='empty-state'>No text content on this slide</p>"}</div>
    </div>
  `;
  
  const slideId = slide.slideId;
  const analysis = state.analysisBySlideId[slideId];
  const suggestions = analysis ? analysis.suggestions : [];
  const decisionMap = ensureDecisionMap(slideId);

  suggestionsContainer.innerHTML = "";
  
  if (!suggestions.length) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "No suggestions yet. Click Analyze Slide to generate.";
    suggestionsContainer.appendChild(empty);
    return;
  }

  suggestions.forEach((suggestion) => {
    const decision = decisionMap[suggestion.id] || {};
    const card = document.createElement("div");
    card.className = "suggestion-card";
    card.innerHTML = `
      <h4>${suggestion.category}</h4>
      <p><strong>Original:</strong> ${suggestion.original}</p>
      <p><strong>Proposed:</strong> ${suggestion.proposed}</p>
      ${suggestion.explanation ? `<p><strong>Note:</strong> ${suggestion.explanation}</p>` : ""}
      <p><strong>Confidence:</strong> ${suggestion.confidence != null ? (suggestion.confidence * 100).toFixed(0) + "%" : "-"}</p>
    `;
    
    const actions = document.createElement("div");
    actions.className = "suggestion-actions";

    const acceptBtn = document.createElement("button");
    acceptBtn.textContent = "Accept";
    acceptBtn.className = decision.decision === "accepted" ? "btn btn-sm btn-success" : "btn btn-sm btn-secondary";
    acceptBtn.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "accepted", "");
      renderSlideDetails();
    });

    const rejectBtn = document.createElement("button");
    rejectBtn.textContent = "Reject";
    rejectBtn.className = decision.decision === "rejected" ? "btn btn-sm btn-danger" : "btn btn-sm btn-secondary";
    rejectBtn.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "rejected", "");
      renderSlideDetails();
    });

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.className = decision.decision === "edited" ? "btn btn-sm btn-success" : "btn btn-sm btn-secondary";
    editBtn.addEventListener("click", () => {
      setDecision(slideId, suggestion.id, "edited", suggestion.proposed);
      renderSlideDetails();
    });

    actions.appendChild(acceptBtn);
    actions.appendChild(rejectBtn);
    actions.appendChild(editBtn);
    card.appendChild(actions);
    suggestionsContainer.appendChild(card);
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

// Slide Navigation
prevSlideBtn.addEventListener("click", () => {
  if (state.selectedSlideNumber > 1) {
    state.selectedSlideNumber--;
    renderSlideList();
    renderSlideDetails();
  }
});

nextSlideBtn.addEventListener("click", () => {
  if (state.selectedSlideNumber < state.slides.length) {
    state.selectedSlideNumber++;
    renderSlideList();
    renderSlideDetails();
  }
});

// Analyze Slide
analyzeBtn.addEventListener("click", async () => {
  if (!state.selectedSermonId || !state.selectedSlideNumber) {
    reviewStatus.textContent = "Select a slide first";
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
    reviewStatus.textContent = "Analysis failed: " + error.message;
  }
});

// Save Changes
saveChangesBtn.addEventListener("click", async () => {
  if (!state.selectedSermonId || !state.selectedSlideNumber) {
    reviewStatus.textContent = "Select a slide first";
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
    reviewStatus.textContent = "Decisions saved!";
    setTimeout(() => { reviewStatus.textContent = ""; }, 2000);
  } catch (error) {
    reviewStatus.textContent = "Save failed: " + error.message;
  }
});

// Generate PPTX
generatePptxBtn.addEventListener("click", async () => {
  if (!state.selectedSermonId) {
    reviewStatus.textContent = "Select a sermon first";
    return;
  }

  reviewStatus.textContent = "Generating PPTX...";
  try {
    await apiFetch(`/sermons/${state.selectedSermonId}/generate-updated-pptx`, {
      method: "POST",
    });
    const href = `${API_BASE}/sermons/${state.selectedSermonId}/download-updated-pptx`;
    downloadPptxLink.href = href;
    downloadPptxLink.style.display = "inline-block";
    reviewStatus.textContent = "";
  } catch (error) {
    reviewStatus.textContent = "Generation failed: " + error.message;
  }
});

// Initialize
checkLogin();
