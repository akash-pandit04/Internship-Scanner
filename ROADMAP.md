# CSE Internship Scanner & SaaS Platform - Development Roadmap

This roadmap outlines the step-by-step construction of the platform, ensuring it solves a massive real-world problem for students while perfectly aligning with the **Siemens Energy Target Stack** (Python OOP, MATLAB, Software Testing, CI/CD).

## Phase 1: Architecture & Foundations (Completed & Ongoing)
*Objective: Build an enterprise-grade software foundation to prove architectural competence to recruiters.*
*   [x] Unzip and analyze the initial job-scanner repository.
*   [x] Set up the **GitHub Actions CI/CD pipeline** to run automated tasks in the cloud.
*   [x] Initialize the **Software Testing (PyTest)** suite framework.
*   [ ] Refactor the core `scan.py` script into a clean **Python Object-Oriented Programming (OOP)** structure.

## Phase 2: The Global Aggregator & Categorization Engine (Backend)
*Objective: Transform the script from a hardcoded scraper into a smart, global internship aggregator.*
*   [ ] **Broaden the Data Sources:** Modify the API connections to pull data from global sources, capturing *all* companies.
*   [ ] **The "Intern" Filter:** Write strict Python logic to instantly reject any job that is not an entry-level or internship role (removing Seniors, Managers, etc.).
*   [ ] **Auto-Categorization (Python OOP):** Build the `JobCategorizer` class. This AI-like engine will read job descriptions and automatically tag them (e.g., *Data & AI*, *Cloud/DevOps*, *Cybersecurity*, *Software Engineering*).

## Phase 3: MATLAB Data Analytics Integration
*Objective: Satisfy the heavy engineering/math requirement for Siemens Energy.*
*   [ ] Write a **MATLAB script** (`analytics.m`) that Python triggers after a scan.
*   [ ] Have MATLAB analyze the JSON data to calculate industry trends (e.g., "Which tech category has the highest internship volume this month?").
*   [ ] Export these statistics to be visualized on the frontend dashboard.

## Phase 4: Frontend Dashboard & UX (User Experience)
*Objective: Build a clean, usable interface for CSE students to actually use the product.*
*   [ ] Update the HTML/CSS/JS frontend to read the new categorized JSON data.
*   [ ] Implement **Interactive Category Filters** (Clicking "Data & AI" only shows data internships).
*   [ ] Implement **"Sort by Most Recent"** functionality so students can see internships posted in the last 24 hours.

## Phase 5: The Premium SaaS Tier (Playwright Auto-Applier)
*Objective: Elevate the project from a scanner to a monetizable SaaS platform to show product/business acumen.*
*   [ ] Build a **Proof-of-Concept Auto-Filler**.
*   [ ] Write a Python Web Automation script (using Playwright or Selenium) that can take a user's mock profile data and automatically inject it into a standard Greenhouse ATS application form.
*   [ ] Document this architecture in the README as the "Premium Monetized Tier."

## Phase 6: Final Testing & GitHub Deployment
*Objective: Final polish before adding it to the resume.*
*   [ ] Run the full PyTest suite to ensure 100% passing tests.
*   [ ] Push all final code to GitHub.
*   [ ] Add the project to the Resume!
