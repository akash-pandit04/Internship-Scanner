# Phase 7I: Coverage Gap Report

## Dataset Snapshot
* **Total Verified Records**: 610
* **Data Integrity Anomalies**: 
    * `missing_locations`: 1
    * `duplicate_ids` / `duplicate_urls`: 0
    * `missing_invalid_posted_at`: 0
    * `empty_categories`: 522
* **Unique Companies**: 101
* **Active Sources**: 6

---

## 1. Geographic Coverage

### By Continent
| Continent | Count | % of Dataset |
| :--- | :---: | :---: |
| North America | 350 | 57.3% |
| Europe | 122 | 20.0% |
| Asia | 82 | 13.4% |
| Unknown/Unresolved | 41 | 6.7% |
| South America | 12 | 1.9% |
| Oceania | 3 | 0.5% |
| Africa | 0 | 0.0% |

### By Country Representation
| Country | Count | % |
| :--- | :---: | :---: |
| United States | 323 | 53.0% |
| Germany | 42 | 6.9% |
| *Unknown/Unresolved* | 40 | 6.5% |
| Singapore | 26 | 4.3% |
| Vietnam | 18 | 2.9% |
| Hungary | 15 | 2.4% |
| Mexico | 14 | 2.3% |
| Canada | 13 | 2.1% |
| China/Hong Kong | 13 | 2.1% |
| Poland | 12 | 2.0% |
| Italy | 10 | 1.6% |
| United Kingdom | 9 | 1.5% |
| Malaysia | 9 | 1.5% |
| France | 8 | 1.3% |
| Romania | 6 | 1.0% |
| Spain | 6 | 1.0% |
| Brazil | 6 | 1.0% |
| Portugal | 5 | 0.8% |
| Japan | 4 | 0.6% |
| Colombia | 4 | 0.6% |
| Indonesia | 4 | 0.6% |
| Australia | 3 | 0.5% |
| UAE | 3 | 0.5% |
| Ireland | 3 | 0.5% |
| Switzerland | 2 | 0.3% |
| Thailand | 2 | 0.3% |
| Belgium | 2 | 0.3% |
| South Korea | 2 | 0.3% |
| Argentina | 1 | 0.2% |
| Philippines | 1 | 0.2% |
| Sweden | 1 | 0.2% |
| Chile | 1 | 0.2% |
| Netherlands | 1 | 0.2% |
| *Remote (Global)* | 1 | 0.2% |
| **Zero Representation:** | Denmark, Norway, Finland, India, Taiwan, New Zealand, South Africa, Saudi Arabia, Israel | 0.0% |

### Remote vs On-Site
* **On-Site**: 591 (96.9%)
* **Remote**: 18 (2.9%)
* **Hybrid**: 0 (0.0%)
* **Unknown**: 1 (0.2%)

---

## 2. Category Coverage (CSE Taxonomy)

* **Uncategorized (`categories: []`)**: 522 (85.6%)

| CSE Category | Count | % of Dataset |
| :--- | :---: | :---: |
| AI / Machine Learning | 18 | 2.9% |
| Research | 18 | 2.9% |
| Software Engineering | 13 | 2.1% |
| Cybersecurity | 6 | 1.0% |
| QA / Testing | 5 | 0.8% |
| Data Analytics | 4 | 0.6% |
| Embedded Systems | 4 | 0.6% |
| Data Science | 4 | 0.6% |
| Data Engineering | 3 | 0.5% |
| Networking | 3 | 0.5% |
| Technical Product | 3 | 0.5% |
| Mobile Development | 3 | 0.5% |
| DevOps | 3 | 0.5% |
| Frontend Development | 2 | 0.3% |
| Backend Development | 2 | 0.3% |
| Systems Engineering | 2 | 0.3% |
| Game Development | 2 | 0.3% |
| Firmware | 2 | 0.3% |
| UI/UX for Software | 1 | 0.2% |
| Automation | 1 | 0.2% |
| NLP | 1 | 0.2% |
| **Zero Representation:** | Full-Stack, Computer Vision, Cloud Computing, SRE, Database Engineering, Blockchain/Web3, AR/VR | 0.0% |

---

## 3. Geographic × Category Matrix

| Region | Software | Data/AI | Cybersecurity | Cloud/DevOps | Sys/Embedded | Other |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **North America** | 15 | 16 | 4 | 2 | 7 | 14 |
| **Europe** | 1 | 8 | 2 | 0 | 2 | 4 |
| **Asia** | 4 | 4 | 0 | 0 | 1 | 8 |
| **South America** | 0 | 0 | 0 | 0 | 0 | 0 |
| **Oceania** | 0 | 0 | 0 | 0 | 0 | 1 |

---

## 4. Concentration Metrics

### Source Concentration
* **Unique Sources**: 6
* **Top 3 sources combined**: 590 (96.7%)

| Source | Count | % |
| :--- | :---: | :---: |
| themuse | 440 | 72.1% |
| smartrecruiters | 121 | 19.8% |
| arbeitnow | 29 | 4.7% |
| ycombinator | 15 | 2.4% |
| ashby | 4 | 0.6% |
| weworkremotely | 1 | 0.2% |

### Company Concentration
* **Unique Companies**: 101
* **Internships per company**: Avg 6.0
* **Top 10 Companies** represent 329 internships (53.9% of dataset)

| Top 10 Companies | Count |
| :--- | :---: |
| Boschgroup | 121 |
| Enterprise Mobility | 81 |
| TikTok | 31 |
| Schneider Electric | 30 |
| Fidelity Investments | 27 |
| Eaton | 22 |
| Labcorp | 18 |
| Navy Federal Credit Union | 17 |
| Bechtel | 16 |
| TD Bank | 16 |

---

## 5. Freshness Distribution
* **Median Age**: 11.0 days
* **Newest**: 1.5 hours
* **Oldest**: 30.0 days

| Age Bracket | Count | % |
| :--- | :---: | :---: |
| 0–7 days | 220 | 36.1% |
| 8–14 days | 172 | 28.2% |
| 15–21 days | 103 | 16.9% |
| 22–30 days | 115 | 18.8% |

---

## Main Observed Gaps

1. **Massive Domain Gap (85% uncategorized)**: 522 out of 610 internships are completely rejected by our existing CSE taxonomy. The vast majority of imported listings from Workday/The Muse/SmartRecruiters are operations, finance, HR, and marketing internships.
2. **Major European Tech Deficit**: While Germany is decently represented (42), the United Kingdom has merely 9 listings, and major tech hubs like Netherlands (1), Sweden (1), and Ireland (3) are effectively empty. 
3. **Major APAC Blind Spot**: India has 0 verified CSE/general internships. South Korea (2) and Japan (4) are poorly covered. Australia/NZ combined has 3.
4. **Cloud / DevOps / Database Gap**: Extremely weak global coverage for backend infrastructure engineering (3 DevOps, 0 SRE, 0 Cloud Computing, 0 Database Engineering).
5. **Over-reliance on The Muse**: 72.1% of the dataset originates from a single source, representing an architectural single point of failure.

---

## Candidate Next Source Families (For Phase 7J Consideration)

### Candidate 1: European/UK Dedicated Aggregator (e.g., Otta or Gradcracker)
* **Target Geography/Domain:** UK / European Union (Tech/CSE Focus)
* **Why it addresses gap:** The UK (9 records) and Nordic/Western European hubs (0-1 records) are missing entirely from our pull.
* **Likely Source Type:** Aggregator / Board API
* **API Possibility:** High for modern platforms.
* **Expected Value:** High volume of localized EU roles.
* **Compliance Risk:** Medium (Aggregators often have strict scraping protections; requires official API access).
* **Priority:** High.

### Candidate 2: Early Talent / University Recruiting API (e.g., Handshake or RippleMatch)
* **Target Geography/Domain:** Global / US University Students
* **Why it addresses gap:** Reduces the 72.1% reliance on The Muse while aggressively targeting the core "internship" demographic.
* **Likely Source Type:** University Network Platform
* **API Possibility:** Moderate (Often locked behind university SSO, but public feeds may exist).
* **Expected Value:** Direct feed to fresh, verified early-career roles.
* **Compliance Risk:** High (Usually requires authenticated university/student accounts).
* **Priority:** Medium.

### Candidate 3: Indian / APAC Tech Job Board (e.g., Instahyre or Naukri)
* **Target Geography/Domain:** India & APAC
* **Why it addresses gap:** 0 records in India despite it being a massive tech hub.
* **Likely Source Type:** Regional Job Board
* **API Possibility:** Moderate.
* **Expected Value:** Solves the starkest regional blackout.
* **Compliance Risk:** Medium (Dependent on public RSS or permissive terms of use).
* **Priority:** High.

### Candidate 4: Revisit Taxonomy Rules Engine
* **Target Geography/Domain:** N/A (Internal Analytics)
* **Why it addresses gap:** 85.6% of our data is sitting uncategorized. Before adding a new source to fetch *more* CSE roles, we must decide if the platform should officially expand to support non-CSE domains (Finance, Operations) or if those 522 records should be purged at the eligibility stage to improve dataset density.
* **Likely Source Type:** Internal code modification.
* **Priority:** Critical/Pre-requisite to Phase 7J.
