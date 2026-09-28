
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
