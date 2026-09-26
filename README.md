# Internship Scanner

A comprehensive data aggregation and web automation platform designed to find and auto-apply to Computer Science Engineering (CSE) Internships globally.

## The Architecture (Enterprise Architecture)
This project is built using enterprise-level architecture, specifically aligning with modern software development and testing requirements:

*   **Python (OOP):** Core engine handles global data aggregation, API routing, and Playwright-based browser automation for the 'Auto-Apply' tier.
*   **Software Testing (PyTest):** Comprehensive unit and integration test suite ensures scraper reliability and form-injection accuracy.
*   **CI/CD (GitHub Actions):** Automated pipelines run the PyTest suite and deploy the live dashboard automatically.
*   **MATLAB Data Analytics:** A dedicated analytics engine (src/analytics.m) processes the aggregated job data to run statistical models and predict in-demand skills and hiring trends in the engineering sector.

## Features
*   **Free Tier:** Global aggregation of Software Engineering and CSE internship postings.
*   **Premium Tier:** One-click Playwright automation to inject user profiles into standard ATS forms (Greenhouse/Lever).
