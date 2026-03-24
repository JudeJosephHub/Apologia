const API_BASE = "http://127.0.0.1:8000";

const state = {
  sermons: [],
  slides: [],
  analysisBySlideId: {},
  decisionsBySlideId: {},
  selectedSermonId: null,
  selectedSlideNumber: null,
  currentUserName: null,
  currentRole: "pastor",
  reviewMode: null,
  summaryText: "",
};

// DOM Elements
const loginModal = document.getElementById("loginModal");
const loginForm = document.getElementById("loginForm");
const loginRole = document.getElementById("loginRole");
const mainContent = document.getElementById("mainContent");
const navbarUser = document.getElementById("navbarUser");
const navbarRole = document.getElementById("navbarRole");
const dailyVerse = document.getElementById("dailyVerse");
const navbarLogoutBtn = document.getElementById("navbarLogoutBtn");
const userMenuDropdown = document.getElementById("userMenuDropdown");
const apiStatusDot = document.getElementById("apiStatusDot");
const apiStatusText = document.getElementById("apiStatusText");

// Home Page Elements
const homePage = document.getElementById("homePage");
const userPage = document.getElementById("userPage");
const uploadBtn = document.getElementById("uploadBtn");
const sermonTableBody = document.getElementById("sermonTableBody");
const userTableBody = document.getElementById("userTableBody");

// Filter elements
const filterName = document.getElementById("filterName");
const filterSeries = document.getElementById("filterSeries");
const filterDate = document.getElementById("filterDate");
const filterPastor = document.getElementById("filterPastor");
const filterStatus = document.getElementById("filterStatus");
const userFilterName = document.getElementById("userFilterName");
const userFilterSeries = document.getElementById("userFilterSeries");
const userFilterPastor = document.getElementById("userFilterPastor");
const userFilterDate = document.getElementById("userFilterDate");

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
const transcriptModal = document.getElementById("transcriptModal");
const transcriptForm = document.getElementById("transcriptForm");
const transcriptTextInput = document.getElementById("transcriptTextInput");
const closeTranscriptBtn = document.getElementById("closeTranscriptBtn");
const cancelTranscriptBtn = document.getElementById("cancelTranscriptBtn");

// Review Page Elements
const reviewPage = document.getElementById("reviewPage");
const backBtn = document.getElementById("backBtn");
const reviewTitle = document.getElementById("reviewTitle");
const reviewContainer = document.querySelector(".review-container");
const analyzeBtn = document.getElementById("analyzeBtn");
const analyzeAllBtn = document.getElementById("analyzeAllBtn");
const saveChangesBtn = document.getElementById("saveChangesBtn");
const summarizeBtn = document.getElementById("summarizeBtn");
const addTranscriptBtn = document.getElementById("addTranscriptBtn");
const generatePptxBtn = document.getElementById("generatePptxBtn");
const downloadPptxLink = document.getElementById("downloadPptxLink");
const slideList = document.getElementById("slideList");
const slidePreview = document.getElementById("slidePreview");
const suggestionsContainer = document.getElementById("suggestionsContainer");
const suggestionsTitle = document.querySelector(".suggestions-panel h3");
const reviewStatus = document.getElementById("reviewStatus");
const slideCounter = document.getElementById("slideCounter");
const prevSlideBtn = document.getElementById("prevSlideBtn");
const nextSlideBtn = document.getElementById("nextSlideBtn");
const toastContainer = document.getElementById("toastContainer");
const userDetailLayout = document.getElementById("userDetailLayout");
const userPresentationList = document.getElementById("userPresentationList");
const userSummaryContent = document.getElementById("userSummaryContent");
const userTranscriptContent = document.getElementById("userTranscriptContent");
const userPptOpenLink = document.getElementById("userPptOpenLink");
const userTranscriptToggle = document.getElementById("userTranscriptToggle");
const userTranscriptToggleIcon = document.getElementById("userTranscriptToggleIcon");

// Authentication
function checkLogin() {
  const savedName = localStorage.getItem("userName");
  const savedRole = localStorage.getItem("userRole");
  if (savedName && (savedRole === "pastor" || savedRole === "user")) {
    state.currentUserName = savedName;
    state.currentRole = savedRole;
    showMainContent(savedName, savedRole);
    checkApi();
    loadSermons();
  } else {
    localStorage.removeItem("userName");
    localStorage.removeItem("userRole");
    localStorage.removeItem("pastorName");
    showLoginModal();
  }
}

function showLoginModal() {
  loginModal.classList.add("active");
  mainContent.style.display = "none";
}

function showMainContent(userName, role) {
  loginModal.classList.remove("active");
  mainContent.style.display = "grid";
  navbarUser.textContent = userName;
  navbarRole.textContent = role === "pastor" ? "Pastor" : "Normal User";
  pastorNameInput.value = userName;
  setRoleView(role);
  loadDailyInspiration();
}

async function loadDailyInspiration() {
  if (!dailyVerse) {
    return;
  }
  dailyVerse.textContent = "Loading daily inspiration...";
  try {
    const inspiration = await apiFetch("/inspiration/daily");
    const text = (inspiration.text || "").trim();
    const citation = (inspiration.citation || "").trim();
    dailyVerse.textContent = citation ? `${text} — ${citation}` : text;
  } catch (error) {
    dailyVerse.textContent = "";
  }
}

function setRoleView(role) {
  const isPastor = role === "pastor";
  if (isPastor) {
    homePage.style.display = "block";
    userPage.style.display = "none";
  } else {
    homePage.style.display = "none";
    reviewPage.style.display = "none";
    userPage.style.display = "block";
  }
}

function setReviewMode(mode) {
  const isPastorMode = mode === "pastor";
  reviewPage.classList.toggle("review-page--user", !isPastorMode);
  reviewPage.classList.toggle("review-page--pastor", isPastorMode);
  analyzeBtn.style.display = isPastorMode ? "inline-flex" : "none";
  analyzeAllBtn.style.display = isPastorMode ? "inline-flex" : "none";
  saveChangesBtn.style.display = isPastorMode ? "inline-flex" : "none";
  generatePptxBtn.style.display = isPastorMode ? "inline-flex" : "none";
  downloadPptxLink.style.display = "none";
  summarizeBtn.style.display = isPastorMode ? "none" : "inline-flex";
  addTranscriptBtn.style.display = isPastorMode ? "none" : "inline-flex";
  suggestionsTitle.textContent = isPastorMode ? "Suggestions" : "Summary";
  if (reviewContainer) {
    reviewContainer.style.display = isPastorMode ? "grid" : "none";
  }
  if (userDetailLayout) {
    userDetailLayout.style.display = isPastorMode ? "none" : "grid";
  }
}

function setUserTranscriptExpanded(expanded) {
  if (!userTranscriptContent || !userTranscriptToggle || !userTranscriptToggleIcon) {
    return;
  }
  userTranscriptContent.classList.toggle("is-collapsed", !expanded);
  userTranscriptToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
  userTranscriptToggleIcon.textContent = expanded ? "−" : "+";
}

loginForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const userName = document.getElementById("loginPastorName").value.trim();
  const role = loginRole.value;
  if (userName) {
    localStorage.setItem("userName", userName);
    localStorage.setItem("userRole", role);
    localStorage.setItem("pastorName", userName);
    document.getElementById("loginPastorName").value = "";
    state.currentUserName = userName;
    state.currentRole = role;
    showMainContent(userName, role);
    checkApi();
    loadSermons();
  }
});

navbarLogoutBtn.addEventListener("click", () => {
  localStorage.removeItem("userName");
  localStorage.removeItem("userRole");
  localStorage.removeItem("pastorName");
  state.currentUserName = null;
  state.currentRole = "pastor";
  userMenuDropdown.classList.remove("open");
  showLoginModal();
});

navbarUser.addEventListener("click", (event) => {
  event.stopPropagation();
  userMenuDropdown.classList.toggle("open");
});

document.addEventListener("click", (event) => {
  if (!userMenuDropdown.classList.contains("open")) {
    return;
  }
  if (!event.target.closest(".user-menu")) {
    userMenuDropdown.classList.remove("open");
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    userMenuDropdown.classList.remove("open");
  }
});

// Logo click to go back to home
const logo = document.querySelector(".logo");
if (logo) {
  logo.addEventListener("click", () => {
    if (state.currentRole === "pastor" && state.selectedSermonId) {
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
    renderUserSermonsList();
  } catch (error) {
    sermonTableBody.innerHTML = '<div class="error">Unable to load sermons</div>';
    userTableBody.innerHTML = '<div class="error">Unable to load sermons</div>';
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
      <div class="col col-name">${escapeHtml(sermon.sermonName) || "-"}</div>
      <div class="col col-series">${escapeHtml(sermon.seriesName) || "-"}</div>
      <div class="col col-date">${escapeHtml(sermon.weekOrDate) || createdDate}</div>
      <div class="col col-pastor">${escapeHtml(sermon.pastorName) || "-"}</div>
      <div class="col col-status"><span class="status-badge">${escapeHtml(sermon.status)}</span></div>
      <div class="col col-actions">
        <button class="btn btn-sm btn-primary review-action" data-id="${escapeHtml(sermon.id)}">Review</button>
      </div>
    `;
    
    const reviewBtn = row.querySelector(".review-action");
    reviewBtn.addEventListener("click", () => {
      navigateToReview(sermon.id, sermon.sermonName);
    });
    
    sermonTableBody.appendChild(row);
  });
}

function renderUserSermonsList() {
  userTableBody.innerHTML = "";

  if (!state.sermons.length) {
    userTableBody.innerHTML = '<div class="empty-message">No sermons available yet</div>';
    return;
  }

  const nameFilter = (userFilterName.value || "").toLowerCase();
  const seriesFilter = (userFilterSeries.value || "").toLowerCase();
  const pastorFilter = (userFilterPastor.value || "").toLowerCase();
  const dateFilter = (userFilterDate.value || "").toLowerCase();

  const filteredSermons = state.sermons.filter((sermon) => {
    const sermonDate = (sermon.weekOrDate || "").toLowerCase();
    return (
      (!nameFilter || (sermon.sermonName || "").toLowerCase().includes(nameFilter)) &&
      (!seriesFilter || (sermon.seriesName || "").toLowerCase().includes(seriesFilter)) &&
      (!pastorFilter || (sermon.pastorName || "").toLowerCase().includes(pastorFilter)) &&
      (!dateFilter || sermonDate.includes(dateFilter))
    );
  });

  if (!filteredSermons.length) {
    userTableBody.innerHTML = '<div class="empty-message">No sermons match your search</div>';
    return;
  }

  filteredSermons.forEach((sermon) => {
    const row = document.createElement("div");
    row.className = "table-row table-row--user";
    const createdDate = new Date(sermon.createdAt).toLocaleDateString();

    row.innerHTML = `
      <div class="col col-name">${escapeHtml(sermon.sermonName) || "-"}</div>
      <div class="col col-series">${escapeHtml(sermon.seriesName) || "-"}</div>
      <div class="col col-date">${escapeHtml(sermon.weekOrDate) || createdDate}</div>
      <div class="col col-pastor">${escapeHtml(sermon.pastorName) || "-"}</div>
      <div class="col col-actions user-actions">
        <button class="btn btn-sm btn-secondary user-view-action" type="button" data-id="${escapeHtml(sermon.id)}" data-name="${escapeHtml(sermon.sermonName) || "Sermon"}">View</button>
      </div>
    `;

    const viewBtn = row.querySelector(".user-view-action");
    viewBtn.addEventListener("click", () => {
      navigateToUserSermon(sermon.id, sermon.sermonName || "Sermon");
    });

    userTableBody.appendChild(row);
  });
}

// Upload Modal Management
uploadBtn.addEventListener("click", openUploadModal);
cancelUploadBtn.addEventListener("click", closeUploadModal);
closeUploadBtn.addEventListener("click", closeUploadModal);
closeTranscriptBtn.addEventListener("click", closeTranscriptModal);
cancelTranscriptBtn.addEventListener("click", closeTranscriptModal);
modalOverlay.addEventListener("click", closeAllModals);

// Filter listeners
filterName.addEventListener("input", renderSermonsList);
filterSeries.addEventListener("input", renderSermonsList);
filterDate.addEventListener("input", renderSermonsList);
filterPastor.addEventListener("input", renderSermonsList);
filterStatus.addEventListener("change", renderSermonsList);
userFilterName.addEventListener("input", renderUserSermonsList);
userFilterSeries.addEventListener("input", renderUserSermonsList);
userFilterPastor.addEventListener("input", renderUserSermonsList);
userFilterDate.addEventListener("input", renderUserSermonsList);

function openUploadModal() {
  uploadModal.classList.add("active");
  modalOverlay.classList.add("active");
  // Set date picker to next Sunday
  weekOrDateInput.value = getNextSunday();
}

function closeUploadModal() {
  uploadModal.classList.remove("active");
  uploadForm.reset();
  uploadStatus.textContent = "";
  weekOrDateInput.value = getNextSunday();
  if (!transcriptModal.classList.contains("active")) {
    modalOverlay.classList.remove("active");
  }
}

function openTranscriptModal() {
  transcriptModal.classList.add("active");
  modalOverlay.classList.add("active");
  transcriptTextInput.focus();
}

function closeTranscriptModal() {
  transcriptModal.classList.remove("active");
  transcriptForm.reset();
  if (!uploadModal.classList.contains("active")) {
    modalOverlay.classList.remove("active");
  }
}

function closeAllModals() {
  closeUploadModal();
  closeTranscriptModal();
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
  state.reviewMode = "pastor";
  setReviewMode("pastor");
  state.summaryText = "";
  state.selectedSermonId = sermonId;
  state.slides = [];
  state.analysisBySlideId = {};
  state.decisionsBySlideId = {};
  state.selectedSlideNumber = null;
  reviewTitle.textContent = sermonName;
  homePage.style.display = "none";
  reviewPage.style.display = "block";
  reviewStatus.textContent = "Loading sermon...";
  slideList.innerHTML = "";
  slidePreview.innerHTML = '<p class="empty-state">Loading slides...</p>';
  suggestionsContainer.innerHTML = '<p class="empty-state">Loading suggestions...</p>';
  loadSermonReview(sermonId);
}

function navigateToUserSermon(sermonId, sermonName) {
  state.reviewMode = "user";
  setReviewMode("user");
  state.summaryText = "";
  state.selectedSermonId = sermonId;
  state.slides = [];
  state.analysisBySlideId = {};
  state.decisionsBySlideId = {};
  state.selectedSlideNumber = null;
  reviewTitle.textContent = sermonName;
  homePage.style.display = "none";
  userPage.style.display = "none";
  reviewPage.style.display = "block";
  reviewStatus.textContent = "Loading sermon...";
  slideList.innerHTML = "";
  slidePreview.innerHTML = '<p class="empty-state">Loading slides...</p>';
  suggestionsContainer.innerHTML = '<p class="empty-state">Click Summarize to generate a sermon summary.</p>';
  userPresentationList.innerHTML = '<p class="empty-state">Loading presentation...</p>';
  userSummaryContent.innerHTML = '<p class="empty-state">Loading summary...</p>';
  userTranscriptContent.innerHTML = '<p class="empty-state">Loading transcript...</p>';
  userPptOpenLink.href = `${API_BASE}/sermons/${sermonId}/pptx`;
  setUserTranscriptExpanded(false);
  loadUserSermonSlides(sermonId);
}

function backToHome() {
  if (state.currentRole === "pastor") {
    homePage.style.display = "block";
  } else {
    userPage.style.display = "block";
  }
  reviewPage.style.display = "none";
  state.selectedSermonId = null;
  state.slides = [];
  state.analysisBySlideId = {};
  state.decisionsBySlideId = {};
  state.selectedSlideNumber = null;
  reviewStatus.textContent = "";
  slideList.innerHTML = "";
  slidePreview.innerHTML = '<p class="empty-state">Select a slide</p>';
  suggestionsContainer.innerHTML = '<p class="empty-state">Select a slide</p>';
  slideCounter.textContent = "Slide 1 of 0";
  state.summaryText = "";
  userPresentationList.innerHTML = '<p class="empty-state">Presentation will appear here.</p>';
  userSummaryContent.innerHTML = '<p class="empty-state">Summary will appear here.</p>';
  userTranscriptContent.innerHTML = '<p class="empty-state">Transcript will appear here.</p>';
  setUserTranscriptExpanded(false);
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
    reviewStatus.textContent = "";
  } catch (error) {
    reviewStatus.textContent = "Unable to load review data: " + error.message;
  }
}

async function loadUserSermonSlides(sermonId) {
  try {
    const [slides, transcript] = await Promise.all([
      apiFetch(`/sermons/${sermonId}/slides`),
      apiFetch(`/sermons/${sermonId}/transcript`),
    ]);
    state.slides = slides;
    state.selectedSlideNumber = slides.length ? slides[0].slideNumber : null;
    renderUserPresentation();
    renderUserTranscript(transcript);

    const transcriptText = (transcript?.transcriptText || "").trim();
    if (transcriptText) {
      reviewStatus.textContent = "Generating summary from transcript...";
      const summary = await apiFetch(`/sermons/${sermonId}/summary/from-transcript`, {
        method: "POST",
      });
      state.summaryText = summary.summary || "";
      renderUserSummary(state.summaryText);
    } else {
      state.summaryText = "";
      renderUserSummary("");
    }
    reviewStatus.textContent = "";
  } catch (error) {
    reviewStatus.textContent = "Unable to load sermon: " + error.message;
  }
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderUserPresentation() {
  userPresentationList.innerHTML = "";
  if (!state.slides.length) {
    userPresentationList.innerHTML = '<p class="empty-state">No slides found in this sermon.</p>';
    return;
  }

  state.slides.forEach((slide) => {
    const card = document.createElement("article");
    card.className = "user-slide-item";
    const safe = escapeHtml(slide.originalText || "");
    const contentHtml = safe
      ? safe.replaceAll("\n", "<br>")
      : "<span class='empty-state'>No text on this slide.</span>";
    card.innerHTML = `
      <h4>Slide ${slide.slideNumber}</h4>
      <div>${contentHtml}</div>
    `;
    userPresentationList.appendChild(card);
  });
}

function renderUserSummary(summary) {
  userSummaryContent.innerHTML = "";
  if (!(summary || "").trim()) {
    userSummaryContent.innerHTML =
      '<p class="empty-state">Summary is not available yet. Click Summarize.</p>';
    return;
  }
  const paragraph = document.createElement("p");
  paragraph.style.whiteSpace = "pre-wrap";
  paragraph.textContent = summary;
  userSummaryContent.appendChild(paragraph);
}

function renderUserTranscript(transcriptDoc) {
  userTranscriptContent.innerHTML = "";
  const transcriptText = (transcriptDoc?.transcriptText || "").trim();
  if (transcriptText) {
    const paragraph = document.createElement("p");
    paragraph.style.whiteSpace = "pre-wrap";
    paragraph.textContent = transcriptText;
    userTranscriptContent.appendChild(paragraph);
    return;
  }
  const status = transcriptDoc?.status || "none";
  const note = transcriptDoc?.note || "";
  const empty = document.createElement("p");
  empty.className = "empty-state";
  empty.textContent =
    status === "ready"
      ? "Transcript is empty."
      : `Transcript is not ready yet (status: ${status}). ${note}`.trim();
  userTranscriptContent.appendChild(empty);
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
  const safeSlideText = escapeHtml(slide.originalText || "").replaceAll("\n", "<br>");
  slidePreview.innerHTML = `
    <div class="slide-content-preview">
      <div class="slide-number-badge">Slide ${slide.slideNumber}</div>
      <div class="slide-text-content">${safeSlideText || "<p class='empty-state'>No text content on this slide</p>"}</div>
    </div>
  `;

  if (state.reviewMode === "user") {
    if (state.summaryText) {
      renderSummary(state.summaryText);
    } else {
      suggestionsContainer.innerHTML = '<p class="empty-state">Click Summarize to generate a sermon summary.</p>';
    }
    return;
  }

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
    const proposedValue =
      decision.decision === "edited" && (decision.finalText || "").trim()
        ? decision.finalText
        : suggestion.proposed;
    card.innerHTML = `
      <h4>${escapeHtml(suggestion.category)}</h4>
      <p><strong>Original:</strong> ${escapeHtml(suggestion.original)}</p>
      <p class="proposed-text"><strong>Proposed:</strong> ${escapeHtml(proposedValue)}</p>
      ${suggestion.explanation ? `<p><strong>Note:</strong> ${escapeHtml(suggestion.explanation)}</p>` : ""}
    `;
    
    const actions = document.createElement("div");
    actions.className = "suggestion-actions";

    const acceptBtn = document.createElement("button");
    acceptBtn.textContent = "Accept";
    acceptBtn.className = decision.decision === "accepted" ? "btn btn-sm btn-success" : "btn btn-sm btn-secondary";
    acceptBtn.addEventListener("click", () => {
      const currentDecision = ensureDecisionMap(slideId)[suggestion.id] || {};
      const editedText = (currentDecision.finalText || "").trim();
      if (editedText) {
        setDecision(slideId, suggestion.id, "edited", editedText);
      } else {
        setDecision(slideId, suggestion.id, "accepted", "");
      }
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
      const nextText = (decision.finalText || suggestion.proposed || "").trim();
      setDecision(slideId, suggestion.id, "edited", nextText);
      renderSlideDetails();
    });

    const editInput = document.createElement("input");
    editInput.type = "text";
    editInput.className = "suggestion-input";
    editInput.placeholder = "Edit proposed text";
    editInput.value = decision.finalText || "";
    const isEditing = decision.decision === "edited";
    editInput.disabled = !isEditing;
    editInput.style.display = isEditing ? "block" : "none";
    editInput.addEventListener("input", (event) => {
      setDecision(slideId, suggestion.id, "edited", event.target.value);
      updateProposedValue(card, event.target.value);
    });
    card.appendChild(editInput);

    actions.appendChild(acceptBtn);
    actions.appendChild(rejectBtn);
    actions.appendChild(editBtn);
    card.appendChild(actions);

    const confidence = document.createElement("div");
    confidence.className = "confidence";
    if (suggestion.confidence != null) {
      const raw = Number(suggestion.confidence);
      const percent = raw <= 1 ? Math.round(raw * 100) : Math.round(raw);
      confidence.textContent = `Confidence: ${percent}%`;
      if (percent >= 80) {
        confidence.classList.add("confidence--high");
      } else if (percent >= 50) {
        confidence.classList.add("confidence--med");
      } else {
        confidence.classList.add("confidence--low");
      }
    } else {
      confidence.textContent = "Confidence: -";
      confidence.classList.add("confidence--low");
    }
    card.appendChild(confidence);
    suggestionsContainer.appendChild(card);
  });
}

function renderSummary(summary) {
  if (state.reviewMode === "user") {
    renderUserSummary(summary);
    return;
  }
  suggestionsContainer.innerHTML = "";
  const card = document.createElement("div");
  card.className = "suggestion-card";
  const paragraph = document.createElement("p");
  paragraph.style.whiteSpace = "pre-wrap";
  paragraph.textContent = summary || "No summary available.";
  card.appendChild(paragraph);
  suggestionsContainer.appendChild(card);
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

function updateProposedValue(card, text) {
  const proposed = card.querySelector(".proposed-text");
  if (!proposed) {
    return;
  }
  const safeText = text && text.trim() ? escapeHtml(text) : "—";
  proposed.innerHTML = `<strong>Proposed:</strong> ${safeText}`;
}

function showToast(message, variant = "success") {
  if (!toastContainer) {
    return;
  }
  const toast = document.createElement("div");
  toast.className = `toast toast--${variant}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.classList.add("fade-out");
    setTimeout(() => toast.remove(), 300);
  }, 2400);
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

if (userTranscriptToggle) {
  userTranscriptToggle.addEventListener("click", () => {
    const expanded = userTranscriptToggle.getAttribute("aria-expanded") === "true";
    setUserTranscriptExpanded(!expanded);
  });
}

summarizeBtn.addEventListener("click", async () => {
  if (!state.selectedSermonId) {
    reviewStatus.textContent = "Select a sermon first";
    return;
  }

  reviewStatus.textContent = "Summarizing sermon...";
  try {
    const endpoint =
      state.reviewMode === "user"
        ? `/sermons/${state.selectedSermonId}/summary/from-transcript`
        : `/sermons/${state.selectedSermonId}/summary`;
    const summary = await apiFetch(endpoint, { method: "POST" });
    state.summaryText = summary.summary || "";
    renderSummary(state.summaryText);
    reviewStatus.textContent = "";
  } catch (error) {
    const msg = String(error.message || "");
    if (state.reviewMode === "user" && msg.includes("Transcript not ready")) {
      reviewStatus.textContent =
        "Transcript is not ready yet. Use Add Transcript to paste it manually, or wait for fetch.";
      return;
    }
    reviewStatus.textContent = "Summarize failed: " + error.message;
  }
});

addTranscriptBtn.addEventListener("click", async () => {
  openTranscriptModal();
});

transcriptForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedSermonId) {
    reviewStatus.textContent = "Select a sermon first";
    return;
  }
  const cleaned = (transcriptTextInput.value || "").trim();
  if (!cleaned) {
    reviewStatus.textContent = "Transcript text cannot be empty.";
    return;
  }

  reviewStatus.textContent = "Saving transcript...";
  try {
    await apiFetch(`/sermons/${state.selectedSermonId}/transcript/manual`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transcriptText: cleaned, language: "en" }),
    });
    if (state.reviewMode === "user") {
      renderUserTranscript({
        transcriptText: cleaned,
        status: "ready",
        note: "Transcript provided manually.",
      });
    }
    closeTranscriptModal();
    reviewStatus.textContent = "Transcript saved. Generating summary...";
    const summary = await apiFetch(
      `/sermons/${state.selectedSermonId}/summary/from-transcript`,
      { method: "POST" }
    );
    state.summaryText = summary.summary || "";
    renderSummary(state.summaryText);
    reviewStatus.textContent = "";
    showToast("Transcript saved and summarized.");
  } catch (error) {
    reviewStatus.textContent = "Transcript save failed: " + error.message;
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
    renderSlideList();
  } catch (error) {
    reviewStatus.textContent = "Analysis failed: " + error.message;
  }
});

analyzeAllBtn.addEventListener("click", async () => {
  if (!state.selectedSermonId) {
    reviewStatus.textContent = "Select a sermon first";
    return;
  }
  if (!state.slides.length) {
    reviewStatus.textContent = "No slides to analyze";
    return;
  }
  analyzeAllBtn.disabled = true;
  analyzeBtn.disabled = true;
  reviewStatus.textContent = "Analyzing all slides...";
  try {
    for (const slide of state.slides) {
      const analysis = await apiFetch(
        `/sermons/${state.selectedSermonId}/slides/${slide.slideNumber}/analyze`,
        { method: "POST" }
      );
      state.analysisBySlideId[analysis.slideId] = analysis;
      renderSlideList();
    }
    reviewStatus.textContent = "";
    showToast("All slides analyzed.");
  } catch (error) {
    reviewStatus.textContent = "Analyze all failed: " + error.message;
  } finally {
    analyzeAllBtn.disabled = false;
    analyzeBtn.disabled = false;
    renderSlideDetails();
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
    renderSlideList();
    showToast("Changes saved.");
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
    showToast("PPTX generated.");
  } catch (error) {
    reviewStatus.textContent = "Generation failed: " + error.message;
  }
});

// Initialize
loadDailyInspiration();
checkLogin();
