let allJobs = [];

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('data/jobs.json');
        const data = await response.json();
        allJobs = data.jobs;
        renderJobs(allJobs);
        setupEventListeners();
    } catch (error) {
        document.getElementById('job-list').innerHTML = '<p>Error loading internships. Please try again later.</p>';
    }
});

function renderJobs(jobs) {
    const container = document.getElementById('job-list');
    container.innerHTML = '';
    
    if (jobs.length === 0) {
        container.innerHTML = '<p>No internships found for this category.</p>';
        return;
    }

    jobs.forEach(job => {
        const card = document.createElement('div');
        card.className = 'job-card';
        card.innerHTML = 
            <div class="job-header">
                <h3></h3>
                <span class="category-badge"></span>
            </div>
            <p class="company"><strong></strong> - </p>
            <p class="posted">Posted: </p>
            <a href="" target="_blank" class="apply-btn">Apply Now</a>
        ;
        container.appendChild(card);
    });
}

function setupEventListeners() {
    // Category Filtering
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Update active state
            filterBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            
            const category = e.target.getAttribute('data-category');
            if (category === 'All') {
                renderJobs(sortJobs(allJobs));
            } else {
                const filtered = allJobs.filter(job => job.category === category);
                renderJobs(sortJobs(filtered));
            }
        });
    });

    // Sorting
    const sortSelect = document.getElementById('sort-select');
    sortSelect.addEventListener('change', () => {
        const activeCategory = document.querySelector('.filter-btn.active').getAttribute('data-category');
        let currentJobs = activeCategory === 'All' ? allJobs : allJobs.filter(job => job.category === activeCategory);
        renderJobs(sortJobs(currentJobs));
    });
}

function sortJobs(jobs) {
    const sortBy = document.getElementById('sort-select').value;
    return [...jobs].sort((a, b) => {
        if (sortBy === 'recent') {
            return new Date(b.posted_at) - new Date(a.posted_at);
        } else {
            return b.score - a.score;
        }
    });
}
