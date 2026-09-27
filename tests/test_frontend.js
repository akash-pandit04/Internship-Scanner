const fs = require('fs');
const assert = require('assert');

// 1. MOCK THE DOM
class Node {
    constructor(tag) {
        this.tagName = tag;
        this.children = [];
        this._innerHTML = '';
        this.textContent = '';
        this.className = '';
        this.attributes = {};
        this.events = {};
        this.style = {};
        this.hidden = false;
        this.value = '';
    }
    set innerHTML(val) {
        this._innerHTML = val;
        if (val === '') this.children = [];
    }
    get innerHTML() {
        return this._innerHTML;
    }
    appendChild(child) {
        if (child.tagName === 'fragment') {
            this.children.push(...child.children);
        } else {
            this.children.push(child);
        }
    }
    addEventListener(evt, cb) {
        if (!this.events[evt]) this.events[evt] = [];
        this.events[evt].push(cb);
    }
    trigger(evt) {
        if (this.events[evt]) {
            this.events[evt].forEach(cb => cb());
        }
    }
}

const document = {
    elements: {},
    addEventListener: function(evt, cb) {
        if (evt === 'DOMContentLoaded') {
            this.ready = cb;
        }
    },
    getElementById: function(id) {
        if (!this.elements[id]) {
            this.elements[id] = new Node('div');
            this.elements[id].id = id;
        }
        return this.elements[id];
    },
    createElement: function(tag) {
        return new Node(tag);
    },
    createDocumentFragment: function() {
        return new Node('fragment');
    }
};

global.document = document;

// 2. MOCK FETCH
global.fetch = async (url) => {
    if (url === 'data/jobs.json') {
        const raw = fs.readFileSync('docs/data/jobs.json', 'utf8');
        return {
            ok: true,
            json: async () => JSON.parse(raw)
        };
    }
    return { ok: false };
};

// 3. LOAD APP
const appCode = fs.readFileSync('docs/app.js', 'utf8')
    .replace('let allJobs', 'var allJobs')
    .replace('let filteredJobs', 'var filteredJobs');
eval(appCode);

async function runTests() {
    console.log("Starting Frontend Tests...");

    await document.ready();

    // 1. Dataset loading
    assert(allJobs.length === 34, "Dataset should have 34 jobs");
    assert(document.elements['results-container'].children.length > 0, "Cards should render");
    assert.strictEqual(document.elements['results-count'].textContent, 34, "Count should be 34");
    console.log("✅ Dataset loading passed");

    // 2. Search
    const searchInput = document.elements['f-search'];
    searchInput.value = 'engineering';
    searchInput.trigger('input');
    assert.strictEqual(filteredJobs.length, 4, "Search 'engineering' should return 4 jobs");
    
    searchInput.value = 'impossible-term-123';
    searchInput.trigger('input');
    assert.strictEqual(filteredJobs.length, 0, "Impossible search should return 0 jobs");
    assert.strictEqual(document.elements['empty-state'].hidden, false, "Empty state should show");

    searchInput.value = 'ENGINEERING'; 
    searchInput.trigger('input');
    assert.strictEqual(filteredJobs.length, 4, "Search is case-insensitive");
    console.log("✅ Search passed");

    // 3. Category filtering
    searchInput.value = ''; 
    searchInput.trigger('input');
    
    const catSelect = document.elements['f-cat'];
    const options = catSelect.children;
    assert(options.length > 0, "Categories should be populated");
    assert(Array.from(options).some(o => o.value === 'Software Engineering'), "Software Engineering should exist");
    
    catSelect.value = 'Software Engineering';
    catSelect.trigger('change');
    assert(filteredJobs.every(j => j.categories.includes('Software Engineering')), "Category filter works");
    console.log("✅ Category filtering passed");

    // 4. Remote filtering
    catSelect.value = '';
    const remoteFilter = document.elements['f-remote'];
    remoteFilter.value = 'remote';
    remoteFilter.trigger('change');
    assert(filteredJobs.length > 0, "Remote jobs exist");
    assert(filteredJobs.every(j => j.remote === true), "Remote Only filter works");
    
    remoteFilter.value = 'all';
    remoteFilter.trigger('change');
    assert.strictEqual(filteredJobs.length, 34, "Disabling Remote Only restores jobs");
    console.log("✅ Remote filtering passed");

    // 5. Sorting
    const sortSelect = document.elements['f-sort'];
    sortSelect.value = 'newest';
    sortSelect.trigger('change');
    
    let lastTime = Infinity;
    let validDateCount = 0;
    for (const j of filteredJobs) {
        const t = j.posted_at ? new Date(j.posted_at).getTime() : 0;
        assert(t <= lastTime, "Newest sort is not descending");
        lastTime = t;
        if (t > 0) validDateCount++;
    }
    
    sortSelect.value = 'company';
    sortSelect.trigger('change');
    assert(filteredJobs[0].company.toLowerCase() <= filteredJobs[1].company.toLowerCase(), "Company A-Z works");
    
    sortSelect.value = 'relevance';
    sortSelect.trigger('change');
    assert(filteredJobs[0].score >= filteredJobs[1].score, "Highest relevance works");
    console.log("✅ Sorting passed");

    // 6. Combined filters
    searchInput.value = 'engineering';
    catSelect.value = 'Software Engineering';
    remoteFilter.value = 'remote';
    searchInput.trigger('input');
    const combinedLength = filteredJobs.length;
    assert(combinedLength <= 4, "Combined filters applied");
    console.log("✅ Combined filters passed");

    // 7. Clear Filters
    const clearBtn = document.elements['btn-clear-filters'];
    clearBtn.trigger('click');
    assert.strictEqual(searchInput.value, '', "Search cleared");
    assert.strictEqual(catSelect.value, '', "Category cleared");
    assert.strictEqual(remoteFilter.value, 'all', "Remote cleared");
    assert.strictEqual(filteredJobs.length, 34, "Clear restores 34 jobs");
    console.log("✅ Clear Filters passed");

    // 8. Apply URL integrity
    render(); 
    const cards = document.elements['results-container'].children;
    for (const card of cards) {
        let html = '';
        if (card.children) {
            html = card.children.map(c => c.innerHTML).join('');
        }
        assert(html.includes('href="http') || html.includes('href="https'), "Apply link must exist in HTML");
    }
    console.log("✅ Apply URL integrity passed");
    
    // 9. Dataset failure state
    global.fetch = async () => ({ ok: false });
    await init();
    assert.strictEqual(document.elements['error-state'].hidden, false, "Error state shown on failure");
    console.log("✅ Dataset failure state passed");

    console.log("🎉 ALL TESTS PASSED");
}

runTests().catch(e => {
    console.error("Test failed:");
    console.error(e);
    process.exit(1);
});
