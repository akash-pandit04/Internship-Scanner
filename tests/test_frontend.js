const fs = require('fs');
const assert = require('assert');
const { JSDOM } = require('jsdom');

async function runTests() {
    console.log("Starting Frontend Tests with JSDOM...");

    // Setup DOM
    const html = fs.readFileSync('docs/index.html', 'utf8');
    const dom = new JSDOM(html, { runScripts: "outside-only", url: "http://localhost" });
    const { window } = dom;
    const document = window.document;

    // Mock fetch
    window.fetch = async (url) => {
        if (url === 'data/jobs.json') {
            const raw = fs.readFileSync('docs/data/jobs.json', 'utf8');
            return {
                ok: true,
                json: async () => JSON.parse(raw)
            };
        }
        return { ok: false };
    };

    // Load App
    const appCode = fs.readFileSync('docs/app.js', 'utf8');
    window.eval(appCode);

    // Wait for init to finish (since it's async)
    await new Promise(resolve => setTimeout(resolve, 500));

    // Expose STATE to our test environment for easy inspection
    const STATE = window.STATE;

    // 1. Dataset loading
    assert(STATE.jobs.length >= 2, "Dataset should have at least 2 jobs");
    assert.strictEqual(document.getElementById('hero-stat-total').textContent, String(STATE.jobs.length), "Count should match");
    console.log("✅ Dataset loading passed");

    // 2. Views and Navigation
    const listingView = document.getElementById('view-listing');
    const landingView = document.getElementById('view-landing');
    assert(landingView.classList.contains('active-view'), "Landing view active by default");
    
    // Simulate clicking "Internships"
    const internshipsLink = document.querySelector('[data-navigate="listing"]');
    internshipsLink.click();
    assert(listingView.classList.contains('active-view'), "Listing view should be active after navigation");
    console.log("✅ Navigation passed");

    // 3. Filters
    const fEligibility = document.getElementById('f-eligibility');
    const resultsGrid = document.getElementById('listing-results-grid');
    const fRemote = document.getElementById('f-remote-check');

    fEligibility.value = 'all';
    fEligibility.dispatchEvent(new window.Event('change', { bubbles: true }));
    assert(resultsGrid.children.length === STATE.jobs.length, "All internships should be shown");

    fRemote.checked = true;
    fEligibility.dispatchEvent(new window.Event('change', { bubbles: true }));
    const remoteCount = STATE.jobs.filter(j => j.remote).length;
    assert(resultsGrid.children.length === remoteCount, "Remote filter should work");
    console.log("✅ Filter controls passed");

    // 4. Detail view
    const firstJobCard = resultsGrid.querySelector('.job-card');
    assert(firstJobCard, "Job card must exist to click");
    // Extract ID from the click handler or just call openDetail with the first job ID
    const firstJobId = STATE.jobs[0].id;
    window.openDetail(String(firstJobId));
    
    const detailView = document.getElementById('view-detail');
    assert(detailView.classList.contains('active-view'), "Detail view active after click");
    assert(document.getElementById('detail-title').textContent.length > 0, "Detail title populated");
    console.log("✅ Detail view passed");
    
    // 5. Back navigation
    const backBtn = document.querySelector('.back-button');
    backBtn.click();
    assert(listingView.classList.contains('active-view'), "Listing view active after back");
    console.log("✅ Back navigation passed");

    console.log("🎉 ALL FRONTEND TESTS PASSED");
}

runTests().catch(e => {
    console.error("Test failed:");
    console.error(e);
    process.exit(1);
});
