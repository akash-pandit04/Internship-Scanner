const fs = require('fs');
const assert = require('assert');
const { JSDOM } = require('jsdom');

async function runTests() {
    console.log("Starting Frontend Tests with JSDOM...");
    const html = fs.readFileSync('docs/index.html', 'utf8');
    const dom = new JSDOM(html, { runScripts: "outside-only", url: "http://localhost" });
    const { window } = dom;
    const document = window.document;

    window.fetch = async (url) => {
        if (url === 'data/jobs.json') {
            const raw = fs.readFileSync('docs/data/jobs.json', 'utf8');
            return { ok: true, json: async () => JSON.parse(raw) };
        }
        return { ok: false };
    };

    const appCode = fs.readFileSync('docs/app.js', 'utf8');
    window.eval(appCode);
    await new Promise(resolve => setTimeout(resolve, 500));
    const STATE = window.STATE;

    // 1. Dataset loading
    assert(STATE.jobs.length >= 2, "Dataset should have at least 2 jobs");
    assert.strictEqual(document.getElementById('stat-total').textContent, String(STATE.jobs.length), "Count should match");
    console.log("✅ Dataset loading passed");

    // 2. Views and Navigation
    const listingView = document.getElementById('view-listing');
    const landingView = document.getElementById('view-landing');
    assert(landingView.classList.contains('active-view'), "Landing view active by default");
    
    document.querySelector('[data-navigate="listing"]').click();
    assert(listingView.classList.contains('active-view'), "Listing view should be active after navigation");
    console.log("✅ Navigation passed");

    // 3. Filters
    const resultsGrid = document.getElementById('listing-results-grid');
    const radioAll = document.querySelector('input[name="f_mode"][value="all"]');
    radioAll.checked = true;
    radioAll.dispatchEvent(new window.Event('change', { bubbles: true }));
    assert(resultsGrid.children.length === STATE.jobs.length, "All internships should be shown");

    const fRemote = document.getElementById('f-remote');
    fRemote.value = 'remote';
    fRemote.dispatchEvent(new window.Event('change', { bubbles: true }));
    const remoteCount = STATE.jobs.filter(j => j.remote).length;
    assert(resultsGrid.children.length === remoteCount, "Remote filter should work");
    console.log("✅ Filter controls passed");

    // 4. Detail view
    const firstJobId = STATE.jobs[0].id;
    window.openDetail(String(firstJobId));
    
    const detailView = document.getElementById('view-detail');
    assert(detailView.classList.contains('active-view'), "Detail view active after click");
    assert(document.getElementById('detail-title').textContent.length > 0, "Detail title populated");
    console.log("✅ Detail view passed");

    console.log("🎉 ALL FRONTEND TESTS PASSED");
}

runTests().catch(e => {
    console.error("Test failed:", e);
    process.exit(1);
});
