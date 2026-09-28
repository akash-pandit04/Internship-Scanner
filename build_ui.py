import os

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#2563eb">
<meta name="description" content="Find verified Computer Science and Engineering internships.">
<title>Internship Scanner</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="app-header">
  <div class="container header-container">
    <div class="brand-group">
      <div class="brand">Internship Scanner</div>
      <div class="brand-tagline">Curated, fresh CSE internships from verified tech employers.</div>
    </div>
    <div class="meta-info">
      <span id="update-status" aria-live="polite">Loading dataset...</span>
    </div>
  </div>
</header>

<main>
  
  <section class="dashboard container" aria-label="Dataset Overview">
    <div class="stat-card">
      <h3 class="stat-title">Total Internships</h3>
      <div id="stat-total" class="stat-value">--</div>
      <div class="stat-desc">across all categories</div>
    </div>
    <div class="stat-card highlight">
      <h3 class="stat-title">CSE Qualified</h3>
      <div id="stat-cse" class="stat-value">--</div>
      <div class="stat-desc">matching technical taxonomy</div>
    </div>
    <div class="stat-card">
      <h3 class="stat-title">Employers</h3>
      <div id="stat-companies" class="stat-value">--</div>
      <div class="stat-desc">actively hiring now</div>
    </div>
    <div class="stat-card">
      <h3 class="stat-title">Freshness</h3>
      <div id="stat-freshness" class="stat-value">24h</div>
      <div class="stat-desc">maximum posting age</div>
    </div>
  </section>

  <section class="search-section" aria-labelledby="search-heading">
    <div class="container">
      <h2 id="search-heading" class="sr-only">Search</h2>
      <div class="search-bar">
        <label for="f-search" class="sr-only">Search internships</label>
        <div class="search-input-wrapper">
          <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input id="f-search" type="search" placeholder="Search title, company, skills, or location...">
        </div>
      </div>
    </div>
  </section>

  <section class="controls container" aria-label="Filters">
    <div class="filters">
      <div class="filter-group">
        <label for="f-cse-only">View Mode</label>
        <select id="f-cse-only">
          <option value="cse" selected>CSE Qualified Only</option>
          <option value="all">All Internships</option>
        </select>
      </div>

      <div class="filter-group">
        <label for="f-cat">CSE Category</label>
        <select id="f-cat">
          <option value="">All Categories</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="f-company">Company</label>
        <select id="f-company">
          <option value="">All Companies</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="f-remote">Location</label>
        <select id="f-remote">
          <option value="all">Any Location</option>
          <option value="remote">Remote Only</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label for="f-sort">Sort By</label>
        <select id="f-sort">
          <option value="newest" selected>Newest First</option>
          <option value="relevance">Highest Relevance</option>
          <option value="company">Company A-Z</option>
        </select>
      </div>
      
      <div class="filter-actions">
        <button id="btn-clear-filters" class="btn-secondary" aria-label="Clear all filters">Clear Filters</button>
      </div>
    </div>
  </section>
  
  <section class="results container" aria-label="Internship listings">
    <div class="results-header">
      <h2 class="results-title">Available Internships</h2>
      <span id="results-count" class="badge" aria-live="polite">0</span>
    </div>

    <div id="results-container" class="cards-grid">
      <!-- Cards will be injected here -->
    </div>
    
    <div id="empty-state" class="empty-state" hidden>
      <h2>No internships match your filters.</h2>
      <p>Try adjusting your search criteria or clearing filters.</p>
      <button id="btn-empty-clear" class="btn-primary">Clear Filters</button>
    </div>
    
    <div id="error-state" class="error-state" hidden>
      <h2>Unable to load internship dataset.</h2>
      <p>The dataset might be unavailable or generating. Please try again later.</p>
    </div>
  </section>
  
</main>

<script src="app.js"></script>
</body>
</html>
"""

STYLE_CSS = """
:root {
  --bg: #f3f4f6;
  --surface: #ffffff;
  --text-main: #111827;
  --text-muted: #4b5563;
  --text-light: #9ca3af;
  --border: #e5e7eb;
  --primary: #2563eb;
  --primary-hover: #1d4ed8;
  --accent: #eff6ff;
  --success: #059669;
  --success-bg: #ecfdf5;
  --radius: 12px;
  --font: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: var(--font);
  background-color: var(--bg);
  color: var(--text-main);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border-width: 0;
}

*:focus-visible {
  outline: 3px solid var(--primary); outline-offset: 2px;
}

.container {
  max-width: 1280px; margin: 0 auto; padding: 0 1.5rem;
}

/* Header */
.app-header {
  background: var(--primary);
  color: white;
  position: sticky; top: 0; z-index: 100;
  box-shadow: var(--shadow-sm);
}
.header-container {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 1.25rem; padding-bottom: 1.25rem;
}
.brand { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.025em; }
.brand-tagline { font-size: 0.875rem; color: #bfdbfe; margin-top: 0.25rem; }
.meta-info { font-size: 0.875rem; color: #bfdbfe; text-align: right; font-weight: 500; }

/* Dashboard */
.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 2rem;
  margin-bottom: 2rem;
}
@media (min-width: 768px) {
  .dashboard { grid-template-columns: repeat(4, 1fr); }
}
.stat-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.5rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
}
.stat-card.highlight {
  border-color: #bfdbfe;
  background: var(--accent);
}
.stat-title { font-size: 0.875rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.stat-value { font-size: 2.5rem; font-weight: 800; color: var(--text-main); margin: 0.5rem 0; line-height: 1; }
.stat-card.highlight .stat-value { color: var(--primary); }
.stat-desc { font-size: 0.8125rem; color: var(--text-light); }

/* Search Section */
.search-section { padding-bottom: 2rem; }
.search-bar { max-width: 800px; margin: 0 auto; }
.search-input-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 1.25rem; color: var(--text-light); }
.search-input-wrapper input {
  width: 100%; padding: 1.25rem 1.25rem 1.25rem 3.5rem;
  font-size: 1.125rem; border: 1px solid var(--border);
  border-radius: 9999px; font-family: var(--font);
  background-color: var(--surface);
  box-shadow: var(--shadow-sm);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.search-input-wrapper input:focus {
  outline: none; border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--accent);
}

/* Controls */
.controls { padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); margin-bottom: 2rem; }
.filters { display: flex; flex-wrap: wrap; gap: 1.25rem; align-items: flex-end; }
.filter-group { display: flex; flex-direction: column; gap: 0.375rem; flex: 1 1 180px; }
.filter-group label { font-size: 0.875rem; font-weight: 600; color: var(--text-main); }
.filter-group select {
  padding: 0.625rem 0.75rem; font-size: 0.9375rem;
  border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface); font-family: var(--font);
  color: var(--text-main); cursor: pointer; box-shadow: var(--shadow-sm);
}
.filter-group select:hover { border-color: #d1d5db; }
.filter-actions { display: flex; align-items: center; }

/* Buttons */
.btn-primary, .btn-secondary {
  padding: 0.625rem 1.25rem; font-size: 0.9375rem; font-weight: 600;
  border-radius: 8px; cursor: pointer; border: none;
  font-family: var(--font); text-decoration: none;
  display: inline-flex; align-items: center; justify-content: center;
  transition: background-color 0.15s, color 0.15s;
}
.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover, .btn-primary:focus { background: var(--primary-hover); }
.btn-secondary { background: var(--surface); color: var(--text-muted); border: 1px solid var(--border); box-shadow: var(--shadow-sm); }
.btn-secondary:hover, .btn-secondary:focus { background: var(--bg); color: var(--text-main); }

/* Results */
.results { padding-bottom: 5rem; }
.results-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem; }
.results-title { font-size: 1.25rem; font-weight: 700; color: var(--text-main); }
.badge { background: var(--primary); color: white; padding: 0.125rem 0.625rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; }

.cards-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media (min-width: 768px) { .cards-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1024px) { .cards-grid { grid-template-columns: repeat(3, 1fr); } }

/* Job Card */
.job-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem;
  display: flex; flex-direction: column;
  box-shadow: var(--shadow-sm); transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.job-card:hover, .job-card:focus-within {
  transform: translateY(-2px); box-shadow: var(--shadow-md); border-color: #d1d5db;
}

.card-header { margin-bottom: 1rem; }
.job-title { font-size: 1.125rem; font-weight: 700; color: var(--text-main); line-height: 1.4; margin-bottom: 0.375rem; }
.job-company { font-size: 0.9375rem; font-weight: 600; color: var(--text-muted); }

.card-meta { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.25rem; }
.meta-tag { color: var(--text-muted); border: 1px solid var(--border); padding: 0.25rem 0.625rem; border-radius: 6px; background: var(--bg); font-weight: 500; font-size: 0.75rem; }
.meta-tag.category { background: var(--accent); color: var(--primary); border-color: #bfdbfe; font-weight: 600; }
.meta-tag.remote { background: var(--success-bg); color: var(--success); border-color: #a7f3d0; font-weight: 600; }

.card-details { font-size: 0.875rem; color: var(--text-muted); margin-top: auto; display: flex; flex-direction: column; gap: 0.5rem; }
.detail-row { display: flex; align-items: flex-start; gap: 0.5rem; }
.detail-icon { flex-shrink: 0; width: 16px; height: 16px; opacity: 0.7; margin-top: 0.125rem; }

.card-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 1.25rem; padding-top: 1.25rem; border-top: 1px solid var(--border); }
.source-text { font-size: 0.75rem; color: var(--text-light); text-transform: uppercase; font-weight: 600; letter-spacing: 0.05em; }
.apply-link { display: inline-flex; align-items: center; gap: 0.375rem; background: var(--primary); color: white; padding: 0.5rem 1rem; border-radius: 6px; font-weight: 600; font-size: 0.875rem; text-decoration: none; transition: background 0.15s; }
.apply-link:hover { background: var(--primary-hover); text-decoration: none; }

.empty-state, .error-state { text-align: center; padding: 5rem 1rem; background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); }
.empty-state h2, .error-state h2 { font-size: 1.5rem; margin-bottom: 0.75rem; color: var(--text-main); }
.empty-state p, .error-state p { color: var(--text-muted); margin-bottom: 1.5rem; font-size: 1.125rem; }

@media (max-width: 640px) {
  .brand-tagline { display: none; }
  .filter-group, .filter-actions { flex: 1 1 100%; }
  .filter-actions button { width: 100%; }
}
"""

APP_JS = """
document.addEventListener('DOMContentLoaded', init);

let allJobs = [];
let filteredJobs = [];

const DOM = {
  status: document.getElementById('update-status'),
  search: document.getElementById('f-search'),
  viewMode: document.getElementById('f-cse-only'),
  catFilter: document.getElementById('f-cat'),
  companyFilter: document.getElementById('f-company'),
  remoteFilter: document.getElementById('f-remote'),
  sortSelect: document.getElementById('f-sort'),
  clearBtn: document.getElementById('btn-clear-filters'),
  emptyClearBtn: document.getElementById('btn-empty-clear'),
  count: document.getElementById('results-count'),
  container: document.getElementById('results-container'),
  emptyState: document.getElementById('empty-state'),
  errorState: document.getElementById('error-state'),
  
  // Dashboard
  statTotal: document.getElementById('stat-total'),
  statCse: document.getElementById('stat-cse'),
  statCompanies: document.getElementById('stat-companies')
};

async function init() {
  try {
    const res = await fetch('data/jobs.json');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    
    allJobs = data.jobs || [];
    
    if (data.generated_at) {
      const genDate = new Date(data.generated_at);
      DOM.status.textContent = `Last scan: ${genDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    } else {
      DOM.status.textContent = 'Dataset live';
    }
    
    populateDashboard(allJobs);
    populateFilters(allJobs);
    setupEventListeners();
    applyFiltersAndSort();
    
  } catch (error) {
    console.error('Failed to load dataset:', error);
    DOM.status.textContent = 'Dataset unavailable';
    DOM.errorState.hidden = false;
    DOM.container.hidden = true;
  }
}

function populateDashboard(jobs) {
  const cseJobs = jobs.filter(j => Array.isArray(j.categories) && j.categories.length > 0);
  const companies = new Set(jobs.map(j => j.company).filter(Boolean));
  
  DOM.statTotal.textContent = jobs.length;
  DOM.statCse.textContent = cseJobs.length;
  DOM.statCompanies.textContent = companies.size;
}

function populateFilters(jobs) {
  const categories = new Set();
  const companies = new Set();
  
  jobs.forEach(job => {
    if (job.company) companies.add(job.company);
    if (job.categories && Array.isArray(job.categories)) {
      job.categories.forEach(c => categories.add(c));
    }
  });
  
  // Populate Categories
  Array.from(categories).sort().forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    DOM.catFilter.appendChild(opt);
  });
  
  // Populate Companies
  Array.from(companies).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase())).forEach(comp => {
    const opt = document.createElement('option');
    opt.value = comp;
    opt.textContent = comp;
    DOM.companyFilter.appendChild(opt);
  });
}

function setupEventListeners() {
  DOM.search.addEventListener('input', applyFiltersAndSort);
  DOM.viewMode.addEventListener('change', applyFiltersAndSort);
  DOM.catFilter.addEventListener('change', applyFiltersAndSort);
  DOM.companyFilter.addEventListener('change', applyFiltersAndSort);
  DOM.remoteFilter.addEventListener('change', applyFiltersAndSort);
  DOM.sortSelect.addEventListener('change', applyFiltersAndSort);
  
  const clearHandler = () => {
    DOM.search.value = '';
    DOM.viewMode.value = 'cse';
    DOM.catFilter.value = '';
    DOM.companyFilter.value = '';
    DOM.remoteFilter.value = 'all';
    DOM.sortSelect.value = 'newest';
    applyFiltersAndSort();
  };
  
  DOM.clearBtn.addEventListener('click', clearHandler);
  DOM.emptyClearBtn.addEventListener('click', clearHandler);
}

function applyFiltersAndSort() {
  const query = DOM.search.value.toLowerCase().trim();
  const viewMode = DOM.viewMode.value;
  const cat = DOM.catFilter.value;
  const company = DOM.companyFilter.value;
  const remoteOnly = DOM.remoteFilter.value === 'remote';
  const sortMode = DOM.sortSelect.value;
  
  filteredJobs = allJobs.filter(job => {
    // 1. View Mode (CSE Only)
    const isCSE = Array.isArray(job.categories) && job.categories.length > 0;
    if (viewMode === 'cse' && !isCSE) return false;
    
    // 2. Search
    if (query) {
      const tMatch = (job.title || '').toLowerCase().includes(query);
      const cMatch = (job.company || '').toLowerCase().includes(query);
      const lMatch = (job.location || '').toLowerCase().includes(query);
      const dMatch = (job.description || '').toLowerCase().includes(query);
      if (!tMatch && !cMatch && !lMatch && !dMatch) return false;
    }
    
    // 3. Category
    if (cat) {
      if (!isCSE || !job.categories.includes(cat)) return false;
    }
    
    // 4. Company
    if (company && job.company !== company) return false;
    
    // 5. Remote
    if (remoteOnly && job.remote !== true) return false;
    
    return true;
  });
  
  // Sorting
  filteredJobs.sort((a, b) => {
    if (sortMode === 'company') {
      return (a.company || '').toLowerCase().localeCompare((b.company || '').toLowerCase());
    } else if (sortMode === 'relevance') {
      const scoreA = typeof a.score === 'number' ? a.score : 0;
      const scoreB = typeof b.score === 'number' ? b.score : 0;
      return scoreB - scoreA;
    } else {
      // newest (default)
      const timeA = a.updated_at ? new Date(a.updated_at).getTime() : (a.posted_at ? new Date(a.posted_at).getTime() : 0);
      const timeB = b.updated_at ? new Date(b.updated_at).getTime() : (b.posted_at ? new Date(b.posted_at).getTime() : 0);
      return timeB - timeA;
    }
  });
  
  render();
}

function render() {
  DOM.count.textContent = filteredJobs.length;
  DOM.container.innerHTML = '';
  
  if (filteredJobs.length === 0) {
    DOM.emptyState.hidden = false;
    DOM.container.hidden = true;
    return;
  }
  
  DOM.emptyState.hidden = true;
  DOM.container.hidden = false;
  
  const fragment = document.createDocumentFragment();
  
  filteredJobs.forEach(job => {
    const card = document.createElement('article');
    card.className = 'job-card';
    
    // Header
    const header = document.createElement('div');
    header.className = 'card-header';
    header.innerHTML = `
      <h3 class="job-title">${escapeHTML(job.title || 'Unknown Title')}</h3>
      <div class="job-company">${escapeHTML(job.company || 'Unknown Company')}</div>
    `;
    card.appendChild(header);
    
    // Meta tags
    const metaBox = document.createElement('div');
    metaBox.className = 'card-meta';
    
    if (job.remote === true) {
      metaBox.innerHTML += `<span class="meta-tag remote">Remote</span>`;
    }
    
    if (Array.isArray(job.categories) && job.categories.length > 0) {
      job.categories.forEach(c => {
        metaBox.innerHTML += `<span class="meta-tag category">${escapeHTML(c)}</span>`;
      });
    }
    card.appendChild(metaBox);
    
    // Details
    const details = document.createElement('div');
    details.className = 'card-details';
    
    // Location
    const locText = job.remote === true ? 'Remote' : (job.location || 'Location Unknown');
    details.innerHTML += `
      <div class="detail-row">
        <svg class="detail-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
        <span>${escapeHTML(locText)}</span>
      </div>
    `;
    
    // Freshness (updated_at)
    if (job.updated_at || job.posted_at) {
      const dateStr = job.updated_at || job.posted_at;
      details.innerHTML += `
        <div class="detail-row">
          <svg class="detail-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          <span>${getRelativeTimeString(new Date(dateStr))}</span>
        </div>
      `;
    }
    
    card.appendChild(details);
    
    // Footer
    const footer = document.createElement('div');
    footer.className = 'card-footer';
    
    const sourceDisplay = job.source ? job.source : 'Unknown';
    footer.innerHTML = `
      <div class="source-text">Source: ${escapeHTML(sourceDisplay)}</div>
      <a href="${escapeHTML(job.url || '#')}" class="apply-link" target="_blank" rel="noopener noreferrer" aria-label="Apply to ${escapeHTML(job.company)}">
        Apply
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline></svg>
      </a>
    `;
    card.appendChild(footer);
    
    fragment.appendChild(card);
  });
  
  DOM.container.appendChild(fragment);
}

function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function getRelativeTimeString(date) {
  const now = new Date();
  const diffMs = now - date;
  
  if (diffMs < 0) return 'Updated just now';
  
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  if (diffHours < 1) {
    const mins = Math.floor(diffMs / (1000 * 60));
    return `Updated ${mins} min ago`;
  }
  if (diffHours < 24) return `Updated ${diffHours}h ago`;
  
  const diffDays = Math.floor(diffHours / 24);
  return `Updated ${diffDays}d ago`;
}
"""

import pathlib
docs_dir = pathlib.Path('docs')
docs_dir.mkdir(exist_ok=True)
(docs_dir / 'index.html').write_text(INDEX_HTML, encoding='utf-8')
(docs_dir / 'style.css').write_text(STYLE_CSS, encoding='utf-8')
(docs_dir / 'app.js').write_text(APP_JS, encoding='utf-8')
