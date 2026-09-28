# Phase 7K — Adzuna Feasibility & Coverage Audit

## 1. Executive Summary

FAIL

The audit has encountered a hard failure at GATE 2 (Terms Compatibility). Adzuna's Terms of Service explicitly prohibit the use of their API to build a competing service (a job discovery engine) and restrict the aggregation and persistent redistribution of their data without a formal commercial license. Additionally, no API keys are available in the environment to perform the controlled coverage test. Therefore, the source must be rejected prior to implementation.

## 2. Official Sources Reviewed

| Source | URL | Topic | What it establishes |
|---|---|---|---|
| Adzuna Developer Portal | `https://developer.adzuna.com/` | API Access & Limits | Requires `app_id` and `app_key`. Strict limits of 25 hits/min, 250 hits/day, 1,000/week, 2,500/month. |
| Adzuna Terms of Service | `https://developer.adzuna.com/docs/terms_of_service` | Allowed Usage | Prohibits using the API to build a competing service. Requires specific "Jobs by Adzuna" image attribution. Restricts aggregation and ongoing persistent storage beyond a 14-day trial without explicit written consent. |

## 3. API Access

- **Authentication:** Required (`app_id` and `app_key`).
- **Registration:** Required.
- **Free tier:** Available (14-day trial for any use beyond personal research).
- **Rate limits:** 25 hits/minute, 250 hits/day.
- **Geography:** Supported via specific country codes (e.g., `/gb`, `/in`).
- **Categories:** Supported (e.g., IT jobs).
- **Pagination:** Supported.

## 4. Terms & Architecture Compatibility

| Requirement | Status | Evidence | Risk |
|---|---|---|---|
| API access | PASS | Free tier exists with registration. | Low |
| Data processing | UNKNOWN | Terms restrict using data in aggregation without consent. | High |
| Persistent storage | FAIL | Terms explicitly restrict storing data for ongoing work without a license. | Critical |
| jobs.json publication | FAIL | Prohibited redistribution of aggregate data. | Critical |
| Static frontend | FAIL | Cannot guarantee strict Adzuna logo requirements on bare JSON / third-party static forks. | High |
| Attribution | UNKNOWN | Requires specific "Jobs by Adzuna" hyperlinked image. | High |
| Source links | PASS | Supported by our architecture. | Low |
| Caching | FAIL | Persistent caching for public redistribution violates data rights. | Critical |
| Periodic refresh | FAIL | 250 hits/day limit severely restricts polling depth. | High |
| Combining with other sources | FAIL | Prohibits building a competing aggregated job discovery engine. | Critical |

## 5. Controlled API Experiment

UNKNOWN / REQUIRES CONFIRMATION. No legitimate API credentials were found in the project environment. Per audit rules, fake data, bypassing authentication, and scraping are strictly prohibited. 

## 6. Pipeline Funnel

| Stage | Count |
|---|---:|
| Raw | UNKNOWN |
| Normalized | UNKNOWN |
| Schema accepted | UNKNOWN |
| Fresh | UNKNOWN |
| Stale | UNKNOWN |
| Internship eligible | UNKNOWN |
| Non-internship | UNKNOWN |
| Uncertain | UNKNOWN |
| CSE taxonomy pass | UNKNOWN |
| Exact duplicates | UNKNOWN |
| Semantic duplicates | UNKNOWN |
| Ambiguous duplicates | UNKNOWN |
| Genuinely new CSE | UNKNOWN |

## 7. CSE Taxonomy Yield

UNKNOWN / REQUIRES CONFIRMATION.

## 8. India/APAC Coverage

| Geography | Fresh Eligible CSE | Genuinely New CSE |
|---|---:|---:|
| India | UNKNOWN | UNKNOWN |
| Singapore | UNKNOWN | UNKNOWN |
| Japan | UNKNOWN | UNKNOWN |
| South Korea | UNKNOWN | UNKNOWN |
| Australia | UNKNOWN | UNKNOWN |
| New Zealand | UNKNOWN | UNKNOWN |
| Other APAC | UNKNOWN | UNKNOWN |

## 9. Deduplication Results

UNKNOWN / REQUIRES CONFIRMATION.

## 10. Source Orthogonality

UNKNOWN / REQUIRES CONFIRMATION.

## 11. Data Quality

UNKNOWN / REQUIRES CONFIRMATION.

## 12. Compliance Risk Register

| Risk | Severity | Evidence | Status | Action |
|---|---|---|---|---|
| Competitive product | Critical | Adzuna terms forbid building a competing service. | FAIL | Reject source |
| Redistribution | Critical | `jobs.json` is a publicly redistributed asset. | FAIL | Reject source |
| Rate Limit Exhaustion | High | 250 hits/day limit is inadequate for robust pagination across multiple countries. | FAIL | Reject source |

## 13. Gate Results

| Gate | Result | Reason |
|---|---|---|
| Legitimate Access | PASS | API exists. |
| Terms Compatibility | FAIL | Terms explicitly prohibit competing services and unauthorized redistribution. |
| Freshness | UNKNOWN | Missing credentials. |
| Internship Quality | UNKNOWN | Missing credentials. |
| CSE Yield | UNKNOWN | Missing credentials. |
| Orthogonality | UNKNOWN | Missing credentials. |
| Operational Cost | FAIL | 250 requests/day is extremely low for global coverage. |

## 14. Final Decision

REJECT

The integration fails at the Terms of Service gate. Adzuna's API explicitly prohibits persistent redistribution, aggregated dataset publication, and building competitive discovery engines. Furthermore, the 250 hits/day rate limit makes deep automated polling impossible.

## 15. What Must NOT Be Implemented Yet

DO NOT implement an Adzuna adapter. DO NOT modify `jobs.json` or any production configuration.

## 16. Recommended Next Step

Phase 7M — ATS Registry Feasibility. Target Indian/APAC tech employers specifically using their authorized public ATS feeds (e.g., Workable, Greenhouse, Lever), avoiding third-party aggregators entirely.

============================================================
ADZUNA AUDIT RESULT
-------------------

Legitimate API Access:       PASS
Terms Compatibility:         FAIL
Freshness:                   UNKNOWN
Internship Quality:          UNKNOWN
CSE Taxonomy Yield:          UNKNOWN
India/APAC Value:            UNKNOWN
Orthogonality:               UNKNOWN
Operational Cost:            FAIL

Current CSE Baseline:        88
Adzuna Fresh CSE:            UNKNOWN
Adzuna Genuinely New CSE:    UNKNOWN

Final Decision:
    REJECT

Production Changes:
    NONE

jobs.json Changes:
    NONE

Commit:
    NONE
