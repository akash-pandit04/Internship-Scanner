/**
 * Internship Scanner v1.3.1 - Exact UI Match
 */


function extractCountry(loc) {
    if (!loc) return null;
    let parts = loc.split(',');
    let country = parts[parts.length - 1].trim();
    if (country.toLowerCase() === 'us' || country.toLowerCase() === 'united states' || country.toLowerCase() === 'united states of america') return 'USA';
    if (country.toLowerCase() === 'uk' || country.toLowerCase() === 'great britain') return 'United Kingdom';
    country = country.replace(/[^a-zA-Z\s\-]/g, '').trim();
    if (country.toLowerCase() === 'remote') return 'Remote';
    return country || 'Unknown';
}

window.STATE = {
    jobs: [],
    categories: new Set(),
    companies: new Set(),
    sources: new Set(),
    currentView: 'landing',
    filters: {
        mode: 'cse',
        search: '',
        category: '',
        company: '',
        location: '',
        remote: '',
        source: '',
        sort: 'newest',
        type: 'internship'
    },
    selectedJobId: null
};

const els = {
    views: document.querySelectorAll('.view'),
    navLinks: document.querySelectorAll('.nav-link, .nav-brand, .view-all-link, [data-navigate]'),
    
    // Landing
    heroSearchForm: document.getElementById('landing-search-form'),
    heroSearchInput: document.getElementById('landing-search-input'),
    statTotal: document.getElementById('stat-total'),
    statCse: document.getElementById('stat-cse'),
    statEmployers: document.getElementById('stat-employers'),
    statSources: document.getElementById('stat-sources'),
    landingCategories: document.getElementById('landing-categories'),
    landingFresh: document.getElementById('landing-fresh-internships'),
    landingAll: document.getElementById('landing-all-internships'),
    
    // Listing Sidebar
    fModeRadios: document.getElementsByName('f_mode'),
    fTimeRadios: document.getElementsByName('f_time'),
    countCse: document.getElementById('count-cse-only'),
    countAll: document.getElementById('count-all'),
    sidebarSearch: document.getElementById('listing-sidebar-search'),
    fCategory: document.getElementById('f-category'),
    fCompany: document.getElementById('f-company'),
    fLocation: document.getElementById('f-location'),
    fRemote: document.getElementById('f-remote'),
    fSource: document.getElementById('f-source'),
    fSortSidebar: document.getElementById('f-sort-sidebar'),
    btnClearFilters: document.getElementById('btn-clear-filters'),
    
    // Listing Main
    resultsCountTitle: document.getElementById('results-count-title'),
    resultsCountSubtitle: document.getElementById('results-count-subtitle'),
    fSortTop: document.getElementById('f-sort-top'),
    resultsGrid: document.getElementById('listing-results-grid'),
    emptyState: document.getElementById('listing-empty-state'),
    
    // Detail
    breadcrumbTitle: document.getElementById('breadcrumb-title'),
    detailLogo: document.getElementById('detail-logo'),
    detailTitle: document.getElementById('detail-title'),
    detailCompany: document.getElementById('detail-company-name'),
    detailLocText: document.getElementById('detail-location-text'),
    detailRemText: document.getElementById('detail-remote-text'),
    detailCatBadge: document.getElementById('detail-cat-badge'),
    detailUpdated: document.getElementById('detail-updated'),
    detailSource: document.getElementById('detail-source-text'),
    detailJobId: document.getElementById('detail-job-id'),
    detailApplyBtn: document.getElementById('detail-apply-btn'),
    detailDesc: document.getElementById('detail-desc-content'),
    detailSkills: document.getElementById('detail-skills-tags'),
    
    sideCompany: document.getElementById('side-company'),
    sideLocation: document.getElementById('side-location'),
    sideRemote: document.getElementById('side-remote'),
    sideCategory: document.getElementById('side-category'),
    sideSource: document.getElementById('side-source'),
    sideUpdated: document.getElementById('side-updated'),
    sideId: document.getElementById('side-id')
};

function getLogoUrl(companyName) {
    const clean = companyName.toLowerCase().replace(/[^a-z0-9]/g, '');
    const fallback = `https://ui-avatars.com/api/?name=${encodeURIComponent(companyName)}&background=random&color=fff&size=64`;
    // We try clearbit first, if it fails, onerror in HTML will use fallback, but let's just construct it
    return getFallback(companyName);
}
function getFallback(companyName) {
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(companyName)}&background=random&color=fff&size=64`;
}

async function init() {
    setupEventListeners();
    await loadData();
}

async function loadData() {
    try {
        const response = await fetch('data/jobs.json');
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        STATE.jobs = Array.isArray(data) ? data : (data.jobs || []);
        STATE.all_sources = data.all_sources || [];
        STATE.jobs.forEach(j => {
            if (j.location) j.location = extractCountry(j.location);
        });

        processMetadata();
        populateFilterDropdowns();
        renderLanding();
        applyFiltersAndRender();
    } catch (e) {
        console.error(e);
    }
}

function processMetadata() {
    const internshipsOnly = STATE.jobs.filter(j => j.job_type === 'internship' || !j.job_type);
    let cseCount = 0;
    internshipsOnly.forEach(job => {
        if (job.categories && job.categories.length > 0) cseCount++;
    });
    STATE.jobs.forEach(job => {
        if (job.categories) job.categories.forEach(c => STATE.categories.add(c));
        if (job.company) STATE.companies.add(job.company);
        if (job.source) STATE.sources.add(job.source);
    });

    els.statTotal.textContent = internshipsOnly.length;
    els.statCse.textContent = cseCount;
    els.statEmployers.textContent = STATE.companies.size;
    els.statSources.textContent = STATE.sources.size;
    
    // Fresh Today Count
    const now = new Date();
    const freshCount = internshipsOnly.filter(j => {
        const d = new Date(j.posted_at || j.fetched_at);
        return (now - d) / (1000 * 60 * 60) <= 24;
    }).length;
    if (document.getElementById('stat-fresh')) {
        document.getElementById('stat-fresh').textContent = freshCount;
    }
    
    els.countCse.textContent = cseCount;
    els.countAll.textContent = STATE.jobs.length;
}

function switchView(viewId) {
    STATE.currentView = viewId.replace('view-', '');
    els.views.forEach(v => {
        if (v.id === viewId) v.classList.add('active-view');
        else v.classList.remove('active-view');
    });
    window.scrollTo(0, 0);
}

function setupEventListeners() {
    els.navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const nav = link.getAttribute('data-navigate');
            if (!nav) return;
            const href = link.getAttribute('href');
            
            if (href && href.startsWith('#') && STATE.currentView === nav) {
                e.preventDefault();
                if (href === '#') {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else {
                    const target = document.querySelector(href);
                    if (target) target.scrollIntoView({ behavior: 'smooth' });
                }
                return;
            }
            e.preventDefault();
            
            const filter = link.getAttribute('data-filter');
            if (filter === 'remote') { resetFilters(); STATE.filters.remote = 'remote'; els.fRemote.value = 'remote'; STATE.filters.type = 'all'; }
            if (filter === 'all') { resetFilters(); STATE.filters.type = 'internship'; }
            if (filter === 'jobs') { resetFilters(); STATE.filters.type = 'job'; }
            
            // Update active nav state
            document.querySelectorAll('.main-nav .nav-link').forEach(n => n.classList.remove('active'));
            if (link.classList.contains('nav-link')) link.classList.add('active');

            switchView(`view-${nav}`);
            if (nav === 'listing') applyFiltersAndRender();
        });
    });

    els.heroSearchForm.addEventListener('submit', e => {
        e.preventDefault();
        STATE.filters.search = els.heroSearchInput.value;
        els.sidebarSearch.value = STATE.filters.search;
        if (document.getElementById('nav-search-input')) document.getElementById('nav-search-input').value = STATE.filters.search;
        switchView('view-listing');
        applyFiltersAndRender();
    });

    const navSearchForm = document.getElementById('nav-search-form');
    const navSearchInput = document.getElementById('nav-search-input');
    if (navSearchForm && navSearchInput) {
        navSearchForm.addEventListener('submit', e => {
            e.preventDefault();
            STATE.filters.search = navSearchInput.value;
            els.sidebarSearch.value = STATE.filters.search;
            els.heroSearchInput.value = STATE.filters.search;
            switchView('view-listing');
            applyFiltersAndRender();
        });
    }

    els.sidebarSearch.addEventListener('input', e => { STATE.filters.search = e.target.value; applyFiltersAndRender(); });
    
    // Bind all selects in sidebar
    const selects = [els.fCategory, els.fCompany, els.fLocation, els.fRemote, els.fSource, els.fSortSidebar];
    selects.forEach(sel => {
        sel.addEventListener('change', e => {
            STATE.filters[e.target.id.replace('f-', '').replace('-sidebar', '')] = e.target.value;
            if (e.target.id === 'f-sort-sidebar') els.fSortTop.value = e.target.value;
            applyFiltersAndRender();
        });
    });

    // Top sort syncs with sidebar sort
    els.fSortTop.addEventListener('change', e => {
        STATE.filters.sort = e.target.value;
        els.fSortSidebar.value = e.target.value;
        applyFiltersAndRender();
    });

    // Radio buttons
    els.fModeRadios.forEach(r => {
        r.addEventListener('change', e => {
            STATE.filters.mode = e.target.value;
            applyFiltersAndRender();
        });
    });
    els.fTimeRadios.forEach(r => {
        r.addEventListener('change', e => {
            STATE.filters.time = e.target.value;
            applyFiltersAndRender();
        });
    });

    els.btnClearFilters.addEventListener('click', e => { e.preventDefault(); resetFilters(); applyFiltersAndRender(); });
}

function resetFilters() {
    STATE.filters = { mode: 'all', time: 'all', search: '', category: '', company: '', location: '', remote: '', source: '', sort: 'newest',
        type: 'internship', type: 'internship' };
    Array.from(els.fModeRadios).find(r => r.value === 'all').checked = true;
    Array.from(els.fTimeRadios).find(r => r.value === 'all').checked = true;
    els.sidebarSearch.value = '';
    els.fCategory.value = '';
    els.fCompany.value = '';
    els.fLocation.value = '';
    els.fRemote.value = '';
    els.fSource.value = '';
    els.fSortSidebar.value = 'newest';
    els.fSortTop.value = 'newest';
    els.heroSearchInput.value = '';
}

function populateFilterDropdowns() {
    Array.from(STATE.categories).sort().forEach(c => els.fCategory.add(new Option(c, c)));
    Array.from(STATE.companies).sort().forEach(c => els.fCompany.add(new Option(c, c)));
    Array.from(STATE.sources).sort().forEach(s => els.fSource.add(new Option(s, s)));
    
    const locs = new Set();
    STATE.jobs.forEach(j => { if (j.location) locs.add(j.location); });
    Array.from(locs).sort().forEach(l => els.fLocation.add(new Option(l, l)));


    const navRolesDropdown = document.getElementById('nav-roles-dropdown');
    if (navRolesDropdown) {
        navRolesDropdown.innerHTML = Array.from(STATE.categories).sort().map(c => 
            `<a href="#" onclick="openCategory('${c.replace(/'/g,"\\'")}')">${c}</a>`
        ).join('');
    }
    const navCompaniesDropdown = document.getElementById('nav-companies-dropdown');
    if (navCompaniesDropdown) {
        navCompaniesDropdown.innerHTML = Array.from(STATE.companies).sort().map(c => 
            `<a href="#" onclick="openCompany('${c.replace(/'/g,"\\'")}')">${c}</a>`
        ).join('');
    }
    const navLocationDropdown = document.getElementById('nav-location-dropdown');
    if (navLocationDropdown) {
        navLocationDropdown.innerHTML = Array.from(locs).sort().map(l => 
            `<a href="#" onclick="openLocation('${l.replace(/'/g,"\\'")}')">${l}</a>`
        ).join('');
    }
    const navSourcesDropdown = document.getElementById('nav-sources-dropdown');
    if (navSourcesDropdown) {
        const allSources = Array.from(new Set([...Array.from(STATE.sources), ...(STATE.all_sources || [])])).sort();
        navSourcesDropdown.innerHTML = allSources.map(s => 
            `<a href="#" onclick="openSource('${s.replace(/'/g,"\\'")}')">${s}</a>`
        ).join('');
    }
}

function renderLanding() {
    // Categories
    const catIcons = {
        'Software Engineering': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>',
        'AI / Machine Learning': '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>'
    };
    const defaultIcon = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect></svg>';

    const catCounts = {};
    STATE.jobs.filter(j => j.job_type === 'internship' || !j.job_type).forEach(j => { if (j.categories) j.categories.forEach(c => catCounts[c] = (catCounts[c]||0)+1); });
    const topCats = Object.entries(catCounts).sort((a,b)=>b[1]-a[1]).slice(0, 4);
    
    els.landingCategories.innerHTML = topCats.map(([cat, count]) => `
        <div class="cat-btn" onclick="openCategory('${cat.replace(/'/g,"\\'")}')">
            <div class="cat-btn-icon">${catIcons[cat] || defaultIcon}</div>
            <div>
                <div class="cat-btn-text">${cat}</div>
                <div class="cat-btn-sub">${count} internships</div>
            </div>
        </div>
    `).join('');

    // Fresh
    const fresh = STATE.jobs.filter(j => j.job_type === 'internship' || !j.job_type).sort((a,b) => new Date(b.posted_at||b.fetched_at) - new Date(a.posted_at||a.fetched_at)).slice(0, 6);
    els.landingFresh.innerHTML = fresh.map(j => createGridCard(j)).join('');
    
    // All
    if (els.landingAll) {
        const all = STATE.jobs.filter(j => j.job_type === 'internship' || !j.job_type).sort((a,b) => new Date(b.posted_at||b.fetched_at) - new Date(a.posted_at||a.fetched_at)).slice(0, 15);
        els.landingAll.innerHTML = all.map(j => createGridCard(j)).join('');
    }
}

window.openCategory = function(cat) {
    resetFilters(); STATE.filters.category = cat; els.fCategory.value = cat; switchView('view-listing'); applyFiltersAndRender();
};
window.openCompany = function(comp) {
    resetFilters(); STATE.filters.company = comp; els.fCompany.value = comp; switchView('view-listing'); applyFiltersAndRender();
};
window.openLocation = function(loc) {
    resetFilters(); STATE.filters.location = loc; els.fLocation.value = loc; switchView('view-listing'); applyFiltersAndRender();
};
window.openSource = function(src) {
    resetFilters(); STATE.filters.source = src; els.fSource.value = src; switchView('view-listing'); applyFiltersAndRender();
};
window.openScan = function(hours) {
    resetFilters(); 
    STATE.filters.time = hours;
    const radio = Array.from(els.fTimeRadios).find(r => r.value === hours);
    if (radio) radio.checked = true;
    switchView('view-listing'); 
    applyFiltersAndRender();
};

function applyFiltersAndRender() {
    const f = STATE.filters;
    const q = f.search.toLowerCase();
    const now = new Date();

    let filtered = STATE.jobs.filter(job => {
        if (f.type && f.type !== 'all' && job.job_type !== f.type) return false;
        if (f.mode === 'cse' && (!job.categories || job.categories.length === 0)) return false;
        
        if (f.time !== 'all') {
            const hours = parseInt(f.time, 10);
            const d = new Date(job.posted_at || job.fetched_at);
            if ((now - d) / (1000 * 60 * 60) > hours) return false;
        }

        if (q) {
            const text = `${job.title} ${job.company} ${job.location}`.toLowerCase();
            if (!text.includes(q)) return false;
        }
        if (f.category && (!job.categories || !job.categories.includes(f.category))) return false;
        if (f.company && job.company !== f.company) return false;
        if (f.location && job.location !== f.location) return false;
        if (f.remote === 'remote' && !job.remote) return false;
        if (f.remote === 'onsite' && job.remote) return false;
        if (f.source && job.source !== f.source) return false;
        return true;
    });

    if (f.sort === 'newest') filtered.sort((a,b) => new Date(b.posted_at||b.fetched_at) - new Date(a.posted_at||a.fetched_at));
    else if (f.sort === 'company') filtered.sort((a,b) => (a.company||'').localeCompare(b.company||''));

    // Update Headers
    const isCse = f.mode === 'cse';
    els.resultsCountTitle.textContent = f.type === 'job' ? 'Jobs' : 'Internships';
    
    // Build active filters text
    let activeFilters = [];
    if (isCse) activeFilters.push('CSE Only');
    if (f.time !== 'all') {
        const h = parseInt(f.time, 10);
        if (h <= 24) activeFilters.push('Past 24 hours');
        else activeFilters.push(`Past ${h/24} days`);
    }
    if (f.category) activeFilters.push(f.category);
    if (f.company) activeFilters.push(f.company);
    if (f.location) activeFilters.push(f.location);
    if (f.remote) activeFilters.push(f.remote === 'remote' ? 'Remote' : 'On-site');
    if (f.source) activeFilters.push(f.source);
    
    let filterStr = activeFilters.length > 0 ? ` Filters: ${activeFilters.join(', ')}` : '';
    els.resultsCountSubtitle.textContent = `${filtered.length} opportunities found.${filterStr}`;

    if (filtered.length === 0) {
        els.resultsGrid.innerHTML = '';
        els.emptyState.hidden = false;
        if (STATE.filters.source) {
            els.emptyState.innerHTML = `<div><h3 style="font-size: 1.25rem; font-weight: 600; margin-bottom: 8px;">No active openings</h3><p>The source <b>${STATE.filters.source}</b> currently has no active listings for both internships and jobs.</p></div>`;
        } else {
            els.emptyState.innerHTML = 'No internships or jobs found matching your criteria.';
        }
    } else {
        els.emptyState.hidden = true;
        els.resultsGrid.innerHTML = filtered.map(job => createListCard(job)).join('');
    }
}

function createGridCard(job) {
    const timeAgo = formatTimeAgo(new Date(job.posted_at||job.fetched_at));
    const safeId = String(job.id).replace(/'/g, "\\'");
    const fallback = getFallback(job.company);
    return `
        <div class="card" onclick="openDetail('${safeId}')">
            <div class="card-header">
                <img src="${getLogoUrl(job.company)}" onerror="this.src='${fallback}'" class="card-company-logo">
                <button class="bookmark-btn"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg></button>
            </div>
            <h3 class="card-title">${job.title}</h3>
            <div class="card-company">${job.company}</div>
            <div class="card-tags">
                ${(job.categories||[]).slice(0,2).map(c=>`<span class="badge badge-blue">${c}</span>`).join('')}
            </div>
            <div class="card-meta">
                <div class="card-meta-row"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg> ${job.location || 'Anywhere'}</div>
                <div class="card-meta-row"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Updated ${timeAgo}</div>
                <div>Source: ${job.source}</div>
            </div>
        </div>
    `;
}

function createListCard(job) {
    const timeAgo = formatTimeAgo(new Date(job.posted_at||job.fetched_at));
    const safeId = String(job.id).replace(/'/g, "\\'");
    const fallback = getFallback(job.company);
    return `
        <div class="list-card" onclick="openDetail('${safeId}')">
            <img src="${getLogoUrl(job.company)}" onerror="this.src='${fallback}'" class="lc-logo">
            <div class="lc-body">
                <h3 class="lc-title">${job.title}</h3>
                <div class="lc-company">${job.company}</div>
                <div class="lc-tags">
                    ${(job.categories||[]).slice(0, 6).map(c=>`<span class="badge badge-blue">${c}</span>`).join('')}
                </div>
                <div class="lc-meta">
                    <span class="lc-meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg> ${job.location || 'Anywhere'}</span>
                    <span class="badge badge-bg">${job.remote ? 'Remote' : 'On-site'}</span>
                    <span class="lc-meta-item"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Updated ${timeAgo}</span>
                    <span>Source: ${job.source}</span>
                </div>
            </div>
            <div class="lc-actions">
                <button class="bookmark-btn"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path></svg></button>
                <button class="btn btn-primary" onclick="event.stopPropagation(); window.open('${job.url}', '_blank')">Apply <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg></button>
            </div>
        </div>
    `;
}

window.openDetail = function(id) {
    const job = STATE.jobs.find(j => String(j.id) === id);
    if (!job) return;
    STATE.selectedJobId = id;
    
    els.breadcrumbTitle.textContent = job.title;
    els.detailLogo.src = getLogoUrl(job.company);
    els.detailLogo.onerror = () => { els.detailLogo.src = getFallback(job.company); };
    
    els.detailTitle.textContent = job.title;
    els.detailCompany.textContent = job.company;
    els.detailLocText.textContent = job.location || 'Anywhere';
    els.detailRemText.textContent = job.remote ? 'Remote' : 'On-site';
    
    if (job.categories && job.categories.length > 0) {
        els.detailCatBadge.textContent = job.categories[0];
        els.detailCatBadge.hidden = false;
        els.sideCategory.textContent = job.categories.join(', ');
    } else {
        els.detailCatBadge.hidden = true;
        els.sideCategory.textContent = 'None';
    }

    const timeAgo = formatTimeAgo(new Date(job.posted_at||job.fetched_at));
    els.detailUpdated.textContent = `Updated ${timeAgo}`;
    els.detailSource.textContent = job.source;
    if (els.detailJobId) els.detailJobId.textContent = job.id || 'Not provided';
    els.detailApplyBtn.href = job.url;
    
    let desc = job.description || '';
    if (!desc) {
        desc = `
        <p>Join our team and work on building innovative solutions. As an intern, you will collaborate with experienced engineers and contribute to real-world projects that impact customers globally.</p>
        <h3>Responsibilities</h3>
        <ul>
            <li>Work on developing and improving backend systems</li>
            <li>Collaborate with cross-functional teams</li>
            <li>Write clean, maintainable, and well-tested code</li>
            <li>Participate in design and code reviews</li>
            <li>Learn and contribute to cloud-native technologies</li>
        </ul>
        `;
    }
    if (!desc.includes('<')) desc = desc.split('\n').map(p => p.trim() ? `<p>${p}</p>` : '').join('');
    els.detailDesc.innerHTML = desc;
    
    const tags = [...(job.categories||[]), ...(job.skills||[])];
    els.detailSkills.innerHTML = tags.map(t=>`<span class="badge badge-blue">${t}</span>`).join('');
    
    // Side
    els.sideCompany.innerHTML = `${job.company} <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>`;
    els.sideLocation.textContent = job.location || 'Anywhere';
    els.sideRemote.textContent = job.remote ? 'Remote' : 'On-site';
    els.sideSource.textContent = job.source;
    els.sideUpdated.textContent = timeAgo;
    els.sideId.textContent = job.id || 'Not provided';
    
    switchView('view-detail');
};

function formatTimeAgo(date) {
    const s = Math.floor((new Date() - date) / 1000);
    let i = s / 3600;
    if (i < 1) return Math.floor(s/60) <= 1 ? 'Just now' : Math.floor(s/60) + ' mins ago';
    if (i < 24) return Math.floor(i) + ' hours ago';
    return Math.floor(s / 86400) + ' days ago';
}

init();
