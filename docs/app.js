document.addEventListener('DOMContentLoaded', init);

let allJobs = [];
let filteredJobs = [];

const DOM = {
  status: document.getElementById('update-status'),
  search: document.getElementById('f-search'),
  catFilter: document.getElementById('f-cat'),
  remoteFilter: document.getElementById('f-remote'),
  sortSelect: document.getElementById('f-sort'),
  clearBtn: document.getElementById('btn-clear-filters'),
  emptyClearBtn: document.getElementById('btn-empty-clear'),
  count: document.getElementById('results-count'),
  container: document.getElementById('results-container'),
  emptyState: document.getElementById('empty-state'),
  errorState: document.getElementById('error-state'),
};

async function init() {
  try {
    const res = await fetch('data/jobs.json');
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    const data = await res.json();
    
    allJobs = data.jobs || [];
    
    if (data.generated_at) {
      const genDate = new Date(data.generated_at);
      DOM.status.textContent = `Dataset updated: ${genDate.toLocaleString()}`;
    } else {
      DOM.status.textContent = 'Dataset loaded';
    }
    
    populateCategories(allJobs);
    setupEventListeners();
    applyFiltersAndSort();
    
  } catch (error) {
    console.error('Failed to load dataset:', error);
    DOM.status.textContent = 'Dataset unavailable';
    DOM.errorState.hidden = false;
    DOM.container.hidden = true;
  }
}

function populateCategories(jobs) {
  const categories = new Set();
  jobs.forEach(job => {
    if (job.categories && Array.isArray(job.categories)) {
      job.categories.forEach(c => categories.add(c));
    }
  });
  
  const sortedCats = Array.from(categories).sort();
  sortedCats.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat;
    opt.textContent = cat;
    DOM.catFilter.appendChild(opt);
  });
}

function setupEventListeners() {
  DOM.search.addEventListener('input', applyFiltersAndSort);
  DOM.catFilter.addEventListener('change', applyFiltersAndSort);
  DOM.remoteFilter.addEventListener('change', applyFiltersAndSort);
  DOM.sortSelect.addEventListener('change', applyFiltersAndSort);
  
  const clearHandler = () => {
    DOM.search.value = '';
    DOM.catFilter.value = '';
    DOM.remoteFilter.value = 'all';
    DOM.sortSelect.value = 'relevance';
    applyFiltersAndSort();
  };
  
  DOM.clearBtn.addEventListener('click', clearHandler);
  DOM.emptyClearBtn.addEventListener('click', clearHandler);
}

function applyFiltersAndSort() {
  const query = DOM.search.value.toLowerCase().trim();
  const cat = DOM.catFilter.value;
  const remoteOnly = DOM.remoteFilter.value === 'remote';
  const sortMode = DOM.sortSelect.value;
  
  // Filtering
  filteredJobs = allJobs.filter(job => {
    // 1. Search (title, company, skills)
    if (query) {
      const tMatch = (job.title || '').toLowerCase().includes(query);
      const cMatch = (job.company || '').toLowerCase().includes(query);
      const sMatch = Array.isArray(job.skills) && job.skills.some(s => s.toLowerCase().includes(query));
      if (!tMatch && !cMatch && !sMatch) return false;
    }
    
    // 2. Category
    if (cat) {
      if (!Array.isArray(job.categories) || !job.categories.includes(cat)) return false;
    }
    
    // 3. Remote
    if (remoteOnly && job.remote !== true) {
      return false;
    }
    
    return true;
  });
  
  // Sorting
  filteredJobs.sort((a, b) => {
    if (sortMode === 'newest') {
      const timeA = a.posted_at ? new Date(a.posted_at).getTime() : 0;
      const timeB = b.posted_at ? new Date(b.posted_at).getTime() : 0;
      return timeB - timeA; // Descending
    } else if (sortMode === 'company') {
      const compA = (a.company || '').toLowerCase();
      const compB = (b.company || '').toLowerCase();
      return compA.localeCompare(compB);
    } else {
      // relevance (default)
      const scoreA = typeof a.score === 'number' ? a.score : 0;
      const scoreB = typeof b.score === 'number' ? b.score : 0;
      return scoreB - scoreA;
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
    
    // Header (Title & Company)
    const header = document.createElement('div');
    header.className = 'card-header';
    header.innerHTML = `
      <h2 class="job-title">${escapeHTML(job.title || 'Unknown Title')}</h2>
      <div class="job-company">${escapeHTML(job.company || 'Unknown Company')}</div>
    `;
    card.appendChild(header);
    
    // Meta tags
    const metaBox = document.createElement('div');
    metaBox.className = 'card-meta';
    
    if (job.remote === true) {
      metaBox.innerHTML += `<span class="meta-tag remote">Remote</span>`;
    }
    
    if (job.employment_type) {
      metaBox.innerHTML += `<span class="meta-tag">${escapeHTML(job.employment_type)}</span>`;
    }
    
    if (Array.isArray(job.categories) && job.categories.length > 0) {
      job.categories.forEach(c => {
        metaBox.innerHTML += `<span class="meta-tag category">${escapeHTML(c)}</span>`;
      });
    }
    card.appendChild(metaBox);
    
    // Details (Location, Posted Date, Score)
    const details = document.createElement('div');
    details.className = 'card-details';
    
    // Location explicitly shown if not remote
    if (job.location && job.remote !== true) {
      details.innerHTML += `<div class="card-location">📍 ${escapeHTML(job.location)}</div>`;
    } else if (!job.location && job.remote !== true) {
      details.innerHTML += `<div class="card-location">📍 Location Unknown</div>`;
    }
    
    // Freshness
    let freshnessHtml = `<div class="card-posted">📅 Posting date unavailable</div>`;
    if (job.posted_at) {
      freshnessHtml = `<div class="card-posted">📅 ${getRelativeTimeString(new Date(job.posted_at))}</div>`;
    }
    details.innerHTML += freshnessHtml;
    
    // Score
    if (typeof job.score === 'number') {
      let scoreText = `Phase 3 relevance model`;
      if (Array.isArray(job.skills) && job.skills.length > 0) {
        scoreText = `Matched: ${job.skills.map(escapeHTML).join(' · ')}`;
      }
      details.innerHTML += `
        <div class="score-box">
          <span class="score-title">Relevance · ${job.score}</span>
          <span class="score-subtitle">${scoreText}</span>
        </div>
      `;
    }
    
    card.appendChild(details);
    
    // Actions (Source & Apply)
    const footer = document.createElement('div');
    footer.className = 'card-footer';
    
    const sourceDisplay = job.source ? `Source: ${job.source}` : 'Source unknown';
    footer.innerHTML = `
      <div class="source-text">${escapeHTML(sourceDisplay)}</div>
      <a href="${escapeHTML(job.url || '#')}" class="apply-link" target="_blank" rel="noopener noreferrer" aria-label="Apply for ${escapeHTML(job.title)}">Apply ↗</a>
    `;
    card.appendChild(footer);
    
    fragment.appendChild(card);
  });
  
  DOM.container.appendChild(fragment);
}

// Utility: Escape HTML to prevent XSS
function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Utility: Human readable relative time
function getRelativeTimeString(date) {
  const now = new Date();
  const diffMs = now - date;
  
  if (diffMs < 0) return 'Posted just now';
  
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Posted today';
  if (diffDays === 1) return 'Posted 1 day ago';
  return `Posted ${diffDays} days ago`;
}
