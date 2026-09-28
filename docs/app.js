/**
 * Internship Scanner v1.3.0 Frontend Application
 */

window.STATE = {
    jobs: [],
    categories: new Set(),
    companies: new Set(),
    sources: new Set(),
    currentView: 'landing',
    filters: {
        mode: 'cse', // 'cse' or 'all'
        search: '',
        category: '',
        company: '',
        remote: false,
        source: '',
        sort: 'newest'
    },
    selectedJobId: null
};

// Elements
const els = {
    views: document.querySelectorAll('.view'),
    navLinks: document.querySelectorAll('.nav-link, .nav-brand, .view-all-link, .back-button'),
    
    // Landing
    landingSearchForm: document.getElementById('landing-search-form'),
    landingSearchInput: document.getElementById('landing-search-input'),
    heroTotal: document.getElementById('hero-stat-total'),
    heroFreshness: document.getElementById('hero-stat-freshness'),
    landingCategories: document.getElementById('landing-categories'),
    landingFresh: document.getElementById('landing-fresh-internships'),
    landingCompanies: document.getElementById('landing-companies'),
    
    // Listing
    filterForm: document.getElementById('filters-form'),
    fEligibility: document.getElementById('f-eligibility'),
    fCategory: document.getElementById('f-category'),
    fCompany: document.getElementById('f-company'),
    fRemote: document.getElementById('f-remote-check'),
    fSource: document.getElementById('f-source'),
    fSort: document.getElementById('f-sort'),
    listingSearchInput: document.getElementById('listing-search-input'),
    btnResetFilters: document.getElementById('btn-reset-filters'),
    btnEmptyClear: document.getElementById('btn-empty-clear-listing'),
    resultsGrid: document.getElementById('listing-results-grid'),
    resultsCountText: document.getElementById('results-count-text'),
    emptyState: document.getElementById('listing-empty-state'),
    
    // Mobile
    mobileMenuBtn: document.querySelector('.mobile-menu-btn'),
    navLinksContainer: document.querySelector('.nav-links'),
    mobileFilterToggle: document.getElementById('mobile-filter-toggle'),
    mobileFilterClose: document.getElementById('mobile-filter-close'),
    listingSidebar: document.querySelector('.listing-sidebar'),

    // Detail
    detailTitle: document.getElementById('detail-title'),
    detailCompany: document.getElementById('detail-company'),
    detailLocation: document.getElementById('detail-location'),
    detailRemoteBadge: document.getElementById('detail-remote-badge'),
    detailDescription: document.getElementById('detail-description'),
    detailSkills: document.getElementById('detail-skills'),
    detailSkillsSection: document.getElementById('detail-skills-section'),
    detailApplyBtn: document.getElementById('detail-apply-btn'),
    detailFreshness: document.getElementById('detail-freshness'),
    detailSource: document.getElementById('detail-source'),
    detailRelatedGrid: document.getElementById('detail-related-grid'),
    detailRelatedEmpty: document.getElementById('detail-related-empty')
};

/**
 * Initialization
 */
async function init() {
    setupEventListeners();
    await loadData();
}

async function loadData() {
    try {
        const response = await fetch('data/jobs.json');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        
        // Handle if dict { jobs: [] } or just []
        let jobsArray = Array.isArray(data) ? data : (data.jobs || []);
        
        window.STATE.jobs = jobsArray;
        processMetadata();
        
        // Initial renders
        populateFilterDropdowns();
        renderLanding();
        applyFiltersAndRender();
        
    } catch (error) {
        console.error("Error loading jobs:", error);
        // Fallback or error state could be shown
    }
}

function processMetadata() {
    let newestDate = 0;
    window.STATE.jobs.forEach(job => {
        // Collect Categories
        if (job.categories && Array.isArray(job.categories)) {
            job.categories.forEach(c => window.STATE.categories.add(c));
        }
        // Collect Companies
        if (job.company) window.STATE.companies.add(job.company);
        // Collect Sources
        if (job.source) window.STATE.sources.add(job.source);
        
        // Find newest date
        const d = new Date(job.posted_at || job.fetched_at).getTime();
        if (d > newestDate) newestDate = d;
    });

    els.heroTotal.textContent = window.STATE.jobs.length;
    if (newestDate > 0) {
        els.heroFreshness.textContent = formatTimeAgo(new Date(newestDate));
    }
}

/**
 * View Management
 */
function switchView(viewId) {
    window.STATE.currentView = viewId.replace('view-', '');
    els.views.forEach(v => {
        if (v.id === viewId) {
            v.classList.add('active-view');
        } else {
            v.classList.remove('active-view');
        }
    });
    window.scrollTo(0, 0);
    
    // Close mobile menus if open
    els.navLinksContainer.classList.remove('open');
}

/**
 * Event Listeners
 */
function setupEventListeners() {
    // Navigation
    els.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const navigateTo = link.getAttribute('data-navigate');
            if (navigateTo) {
                // If it's a hash link on same view, just let default scroll happen
                const href = link.getAttribute('href');
                if (href && href.startsWith('#') && window.STATE.currentView === navigateTo) {
                    return;
                }
                
                e.preventDefault();
                
                // Handle specific quick filters from nav
                const filter = link.getAttribute('data-filter');
                if (filter === 'remote') {
                    resetFilters();
                    window.STATE.filters.remote = true;
                    els.fRemote.checked = true;
                } else if (filter === 'all') {
                    resetFilters();
                }
                
                switchView(`view-${navigateTo}`);
                if (navigateTo === 'listing') applyFiltersAndRender();
            }
        });
    });

    // Mobile Toggles
    if (els.mobileMenuBtn) {
        els.mobileMenuBtn.addEventListener('click', () => {
            els.navLinksContainer.classList.toggle('open');
        });
    }
    if (els.mobileFilterToggle) {
        els.mobileFilterToggle.addEventListener('click', () => {
            els.listingSidebar.classList.add('open');
        });
    }
    if (els.mobileFilterClose) {
        els.mobileFilterClose.addEventListener('click', () => {
            els.listingSidebar.classList.remove('open');
        });
    }

    // Landing Search
    els.landingSearchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        window.STATE.filters.search = els.landingSearchInput.value;
        els.listingSearchInput.value = window.STATE.filters.search;
        switchView('view-listing');
        applyFiltersAndRender();
    });

    // Listing Search & Filters
    els.listingSearchInput.addEventListener('input', (e) => {
        window.STATE.filters.search = e.target.value;
        applyFiltersAndRender();
    });

    els.filterForm.addEventListener('change', (e) => {
        window.STATE.filters.mode = els.fEligibility.value;
        window.STATE.filters.category = els.fCategory.value;
        window.STATE.filters.company = els.fCompany.value;
        window.STATE.filters.remote = els.fRemote.checked;
        window.STATE.filters.source = els.fSource.value;
        applyFiltersAndRender();
    });

    els.fSort.addEventListener('change', (e) => {
        window.STATE.filters.sort = e.target.value;
        applyFiltersAndRender();
    });

    els.btnResetFilters.addEventListener('click', () => {
        resetFilters();
        applyFiltersAndRender();
    });
    
    els.btnEmptyClear.addEventListener('click', () => {
        resetFilters();
        applyFiltersAndRender();
    });
}

function resetFilters() {
    window.STATE.filters = { mode: 'cse', search: '', category: '', company: '', remote: false, source: '', sort: 'newest' };
    els.fEligibility.value = 'cse';
    els.fCategory.value = '';
    els.fCompany.value = '';
    els.fRemote.checked = false;
    els.fSource.value = '';
    els.fSort.value = 'newest';
    els.listingSearchInput.value = '';
    els.landingSearchInput.value = '';
}

function populateFilterDropdowns() {
    const cats = Array.from(window.STATE.categories).sort();
    cats.forEach(c => els.fCategory.add(new Option(c, c)));
    
    const comps = Array.from(window.STATE.companies).sort((a,b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    comps.forEach(c => els.fCompany.add(new Option(c, c)));
    
    const srcs = Array.from(window.STATE.sources).sort();
    srcs.forEach(s => els.fSource.add(new Option(s, s)));
}

/**
 * Rendering: Landing
 */
function renderLanding() {
    // 1. Categories
    const catCounts = {};
    window.STATE.jobs.forEach(j => {
        if (j.categories) j.categories.forEach(c => {
            catCounts[c] = (catCounts[c] || 0) + 1;
        });
    });
    const sortedCats = Object.entries(catCounts).sort((a,b) => b[1] - a[1]).slice(0, 8);
    
    els.landingCategories.innerHTML = sortedCats.map(([cat, count]) => `
        <div class="category-card" onclick="openCategory('${cat.replace(/'/g, "\\'")}')">
            <span class="category-name">${cat}</span>
            <span class="category-count">${count} jobs</span>
        </div>
    `).join('');

    // 2. Fresh Internships
    const freshJobs = [...window.STATE.jobs]
        .sort((a, b) => new Date(b.posted_at || b.fetched_at) - new Date(a.posted_at || a.fetched_at))
        .slice(0, 3);
    
    els.landingFresh.innerHTML = freshJobs.map(job => createJobCardHTML(job)).join('');

    // 3. Companies
    const compCounts = {};
    window.STATE.jobs.forEach(j => {
        if (j.company) compCounts[j.company] = (compCounts[j.company] || 0) + 1;
    });
    const sortedComps = Object.entries(compCounts).sort((a,b) => b[1] - a[1]).slice(0, 12);
    
    els.landingCompanies.innerHTML = sortedComps.map(([comp, count]) => `
        <div class="company-badge-card" onclick="openCompany('${comp.replace(/'/g, "\\'")}')">
            ${comp}
            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.25rem; font-weight: normal;">${count} listings</div>
        </div>
    `).join('');
}

window.openCategory = function(cat) {
    resetFilters();
    window.STATE.filters.category = cat;
    els.fCategory.value = cat;
    switchView('view-listing');
    applyFiltersAndRender();
};

window.openCompany = function(comp) {
    resetFilters();
    window.STATE.filters.company = comp;
    els.fCompany.value = comp;
    switchView('view-listing');
    applyFiltersAndRender();
};

/**
 * Rendering: Listing
 */
function applyFiltersAndRender() {
    const f = window.STATE.filters;
    const q = f.search.toLowerCase();

    let filtered = window.STATE.jobs.filter(job => {
        // Mode
        if (f.mode === 'cse' && (!job.categories || job.categories.length === 0)) return false;
        
        // Search
        if (q) {
            const text = `${job.title} ${job.company} ${job.location} ${job.description || ''} ${job.skills ? job.skills.join(' ') : ''}`.toLowerCase();
            if (!text.includes(q)) return false;
        }
        
        // Category
        if (f.category && (!job.categories || !job.categories.includes(f.category))) return false;
        
        // Company
        if (f.company && job.company !== f.company) return false;
        
        // Remote
        if (f.remote && !job.remote) return false;
        
        // Source
        if (f.source && job.source !== f.source) return false;
        
        return true;
    });

    // Sort
    if (f.sort === 'newest') {
        filtered.sort((a, b) => new Date(b.posted_at || b.fetched_at) - new Date(a.posted_at || a.fetched_at));
    } else if (f.sort === 'company') {
        filtered.sort((a, b) => (a.company || '').localeCompare(b.company || ''));
    } else if (f.sort === 'relevance' && f.search) {
        // Basic relevance: title match > company match > other
        filtered.sort((a, b) => {
            const aTitleMatch = (a.title || '').toLowerCase().includes(q) ? 1 : 0;
            const bTitleMatch = (b.title || '').toLowerCase().includes(q) ? 1 : 0;
            return bTitleMatch - aTitleMatch;
        });
    }

    // Render
    els.resultsCountText.textContent = `${filtered.length} internship${filtered.length !== 1 ? 's' : ''} found`;
    
    if (filtered.length === 0) {
        els.resultsGrid.innerHTML = '';
        els.emptyState.hidden = false;
    } else {
        els.emptyState.hidden = true;
        els.resultsGrid.innerHTML = filtered.map(job => createJobCardHTML(job)).join('');
    }
}

function createJobCardHTML(job) {
    const isRemote = job.remote ? `<span class="badge badge-green">Remote</span>` : '';
    const cats = (job.categories || []).slice(0, 2).map(c => `<span class="badge badge-blue">${c}</span>`).join('');
    const dDate = new Date(job.posted_at || job.fetched_at);
    const timeAgo = formatTimeAgo(dDate);

    // Escape quotes for inline onclick
    const safeId = String(job.id).replace(/'/g, "\\'");

    return `
        <div class="job-card" onclick="openDetail('${safeId}')" role="article" tabindex="0">
            <div class="job-card-header">
                <div>
                    <h3 class="job-card-title">${job.title}</h3>
                    <div class="job-card-company">${job.company}</div>
                </div>
                ${isRemote}
            </div>
            
            <div class="job-card-meta">
                <span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: text-bottom; margin-right: 2px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                    ${job.location || 'Location not specified'}
                </span>
            </div>
            
            <div class="tags-row" style="margin-bottom: 1.5rem;">
                ${cats}
            </div>
            
            <div class="job-card-footer">
                <div class="job-card-time">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    ${timeAgo}
                </div>
                <button class="btn btn-primary" onclick="event.stopPropagation(); window.open('${job.url}', '_blank')">Apply</button>
            </div>
        </div>
    `;
}

/**
 * Rendering: Detail
 */
window.openDetail = function(id) {
    const job = window.STATE.jobs.find(j => String(j.id) === id);
    if (!job) return;

    window.STATE.selectedJobId = id;
    
    els.detailTitle.textContent = job.title;
    els.detailCompany.textContent = job.company;
    els.detailLocation.textContent = job.location || 'Location not specified';
    els.detailRemoteBadge.hidden = !job.remote;
    
    // Description formatting
    let desc = job.description || 'No description provided by the employer.';
    if (!desc.includes('<')) {
        // Plain text to simple HTML
        desc = desc.split('\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('');
    }
    els.detailDescription.innerHTML = desc;

    // Skills & Categories
    const combinedTags = [...(job.categories || []), ...(job.skills || [])];
    if (combinedTags.length > 0) {
        els.detailSkillsSection.hidden = false;
        els.detailSkills.innerHTML = combinedTags.map(t => `<span class="badge badge-outline">${t}</span>`).join('');
    } else {
        els.detailSkillsSection.hidden = true;
    }

    // Meta & Apply
    els.detailApplyBtn.href = job.url;
    els.detailFreshness.textContent = formatTimeAgo(new Date(job.posted_at || job.fetched_at));
    els.detailSource.textContent = job.source || 'Unknown';

    // Related Internships
    renderRelated(job);

    switchView('view-detail');
};

function renderRelated(currentJob) {
    // Simple deterministic matching: same company OR overlapping categories
    let related = window.STATE.jobs.filter(j => {
        if (j.id === currentJob.id) return false;
        if (j.company === currentJob.company) return true;
        if (currentJob.categories && j.categories) {
            const intersection = currentJob.categories.filter(c => j.categories.includes(c));
            if (intersection.length > 0) return true;
        }
        return false;
    });

    // Sort by newest, take top 2
    related.sort((a, b) => new Date(b.posted_at || b.fetched_at) - new Date(a.posted_at || a.fetched_at));
    related = related.slice(0, 2);

    if (related.length === 0) {
        els.detailRelatedGrid.innerHTML = '';
        els.detailRelatedEmpty.hidden = false;
    } else {
        els.detailRelatedEmpty.hidden = true;
        els.detailRelatedGrid.innerHTML = related.map(job => createJobCardHTML(job)).join('');
    }
}

/**
 * Utilities
 */
function formatTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    let interval = seconds / 3600;
    if (interval < 1) {
        const mins = Math.floor(seconds / 60);
        return mins <= 1 ? 'Just now' : Math.floor(mins) + ' mins ago';
    }
    if (interval < 24) {
        return Math.floor(interval) + ' hours ago';
    }
    interval = seconds / 86400;
    return Math.floor(interval) + ' days ago';
}

// Start
init();
