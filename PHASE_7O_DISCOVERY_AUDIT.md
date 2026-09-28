# Phase 7O — Expanded Registry Discovery

## 1. Executive Summary

We executed a programmatic discovery scan across 150+ high-value global and regional technology employers to identify those with **currently active CSE internship listings** in our historically weak geographic and technical categories (India/APAC, Western Europe, AI/ML, Data Engineering). 

This scan utilized our verified unauthenticated ATS polling architecture (Greenhouse/Lever/Ashby). No HTML scraping was performed. Raw listings were routed through our production `eligibility.py` and `taxonomy.py` logic to guarantee that they meet the strict CSE-focus constraint before being recommended.

**Result:** We successfully identified 4 new high-value technology employers possessing active, CSE-taxonomy-passing internships that directly address our coverage gaps.

## 2. Discovery Funnel & Methodology

* **Candidate Pool:** 150+ known technology unicorns and enterprise software firms (including specialized targets across Data, AI, Cloud, and Indian regional tech).
* **Endpoints Tested:** `boards-api.greenhouse.io`, `api.lever.co`, `api.ashbyhq.com`.
* **Filtration:** Jobs were strictly required to pass both `determine_eligibility()` (e.g., must be a student/internship role) and `JobCategorizer` (must belong to one of the 28 CSE domains). 
* **Outcome:** 4 employers definitively passed with live, verified CSE internships. Countless non-CSE internships (HR, Sales, Marketing) were correctly rejected by the scanner, proving the taxonomy accurately defends our product scope.

## 3. Verified Employer Candidates

### Candidate 1: Rubrik
* **ATS Profile:** Greenhouse (`rubrik`)
* **Regional Value:** India / APAC
* **Category Value:** Cloud Computing / Software Engineering
* **Current Evidence:** 
  * `Software Engineer - Winter Intern` | Bangalore, India | CSE Category: `Software Engineering`
  * `Software Engineer (CPD) - Winter Intern` | Bangalore, India | CSE Category: `Software Engineering`
* **Recommendation:** **ADD TO REGISTRY**. Directly addresses the India geographic gap with high-quality core software engineering internships.

### Candidate 2: Celonis
* **ATS Profile:** Greenhouse (`celonis`)
* **Regional Value:** Western Europe (Munich, London, Paris)
* **Category Value:** AI / Machine Learning, Data Engineering
* **Current Evidence:** 
  * `Intern Deployment Engineer - Data & AI` | Munich, Germany | CSE Category: `AI / Machine Learning`
  * `Intern Technology Consultant - Data & AI` | Munich, Germany | CSE Category: `AI / Machine Learning`
  * `AI & Management Consulting Intern (Value Engineering)` | London/Paris | CSE Category: `AI / Machine Learning`
* **Recommendation:** **ADD TO REGISTRY**. Addresses the Nordic/Western Europe geographic gap and the highly sought-after AI/ML specialization.

### Candidate 3: Databricks
* **ATS Profile:** Greenhouse (`databricks`)
* **Regional Value:** North America / Global
* **Category Value:** Data Science, AI / Machine Learning, Software Engineering
* **Current Evidence:**
  * `PhD GenAI Research Scientist Intern` | San Francisco, CA | CSE Category: `Data Science`, `Research`
  * `Software Engineering Intern (2027 Start) - Winter` | Multiple Locations | CSE Category: `Software Engineering`
* **Recommendation:** **ADD TO REGISTRY**. Provides elite tier AI/ML and Data Science research internships.

### Candidate 4: Dropbox
* **ATS Profile:** Greenhouse (`dropbox`)
* **Regional Value:** Remote (US/Global)
* **Category Value:** Core Software Engineering
* **Current Evidence:**
  * `Software Engineering Intern (Summer 2027)` | Remote | CSE Category: `Software Engineering`
* **Recommendation:** **ADD TO REGISTRY**. Strong addition to our Remote/WFA internship offerings.

## 4. Unsuccessful / Non-Target Candidates

* **High-Volume Rejections:** Employers like *InMobi* successfully resolved via Greenhouse but were rejected because their active internships (e.g., `Intern - Creative & Communications, People Team`) failed the CSE taxonomy check. 
* **No Active Internships:** Companies like *BrowserStack*, *Swiggy*, and *Gojek* were checked, but either had no live job board on the standard token or 0 active internships today.

## 5. Architectural Compliance

* **Public Machine-Readable Feed:** Yes. All recommended candidates use `boards-api.greenhouse.io`.
* **No Authentication:** Yes.
* **Usage Audit:** Conforms to Greenhouse syndication design.

## 6. Next Steps (Phase 7P)

Since this phase was strictly an audit/discovery process, I have **not** modified `companies.json`. 

**Phase 7P (Registry Expansion)** is recommended to formally append Rubrik, Celonis, Databricks, and Dropbox to the production `companies.json` registry and execute a production scan to finally ingest these newly verified CSE records into the dataset.
