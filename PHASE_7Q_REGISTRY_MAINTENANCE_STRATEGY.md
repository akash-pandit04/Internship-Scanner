# Phase 7Q — ATS Registry Maintenance & Expansion Strategy

## 1. Objective
Transform the curated ATS registry from a static file into a maintainable, self-monitoring source-management subsystem. This strategy prevents uncontrolled growth, isolates failures, and ensures we retain only highly effective sources that genuinely contribute to the CSE taxonomy baseline.

## 2. Employer Lifecycle
The curated registry operates strictly through the following lifecycle:

1. **DISCOVERED**: Employer identified via market gaps (e.g., India/APAC, Cloud).
2. **AUDITED**: Verified via programmatic script (like Phase 7O) against the `boards-api.greenhouse.io` or Lever API endpoints.
3. **APPROVED**: Must return **at least one** live role that strictly passes existing `eligibility.py` and `taxonomy.py` constraints.
4. **ENABLED**: Added to `companies.json` with `"enabled": true`.
5. **MONITORED**: `scan.py` actively tracks its yield metrics at runtime.
6. **ACTIVE / LOW-YIELD / STALE / BROKEN**: State determined dynamically based on the performance telemetry (see Section 3).
7. **DISABLED or RE-AUDITED**: If an employer remains LOW-YIELD or BROKEN for > 6 months, it is toggled to `"enabled": false` without deleting its configuration or historical data.

## 3. Measuring Actual Contribution
To distinguish employers that *look* valuable from those that *actually* contribute, `scan.py` will be instrumented to track telemetry per company. This telemetry will be aggregated into `registry_metrics.json`.

For every employer in `companies.json`, we will calculate:
* **scans attempted:** Total pipeline runs.
* **successful scans:** HTTP 200 responses.
* **raw jobs:** Total jobs pulled from the board.
* **fresh jobs:** Jobs passing the 24-hour `updated_at` rule.
* **internship jobs:** Jobs passing `determine_eligibility()`.
* **CSE-taxonomy-passing jobs:** Jobs passing the `JobCategorizer`.
* **genuinely new CSE jobs:** CSE jobs that were NOT deduplicated against existing records.
* **duplicate rate:** Semantic/exact duplicates vs. genuinely new roles.
* **last successful scan:** Timestamp of the last valid API response.

## 4. Operational Policies

### 4.1 Addition & Evidence Requirements
Employers are never added speculatively. Addition requires hard evidence:
* Must possess a known, legitimate machine-readable public ATS feed (Greenhouse, Lever, etc.).
* Must demonstrably list (or have recently listed) internship/student roles.
* Those roles must strictly pass our existing CSE taxonomy. 

### 4.2 Stale / Dead Board Detection
If an ATS board URL changes or is retired (e.g., employer moves from Greenhouse to Workday), it will consistently return HTTP 404 or 403. The subsystem will track the `last successful scan` timestamp. If 30 days elapse without a successful scan, the board is flagged as **BROKEN** and manually reviewed or disabled.

### 4.3 Scan Frequency & Re-Discovery
* **Polling:** Curated employers are polled at the same frequency as standard sources (e.g., daily/weekly). API calls to Greenhouse/Lever are extremely lightweight, so performance overhead is negligible.
* **Re-Discovery:** The Phase 7O Discovery Script is executed globally *seasonally* (e.g., early August for Winter/Summer planning, January for Spring planning) to find new targets, rather than polling hundreds of speculative employers daily.

### 4.4 Disabling vs. Deleting
When an employer is no longer useful (e.g., consistently 0 CSE yield across multiple seasons), we flip `"enabled": false` in `companies.json`. 
* This prevents `scan.py` from making wasteful network calls.
* It retains the employer in our registry for potential re-auditing next year.
* It does not delete their existing valid jobs from `jobs.json` (which will organically age out via freshness rules).

### 4.5 Isolation of Source Failures
The scanner's base adapters (`GreenhouseSource`, `LeverSource`) wrap each individual company iteration in a localized `try/except` block. If `databricks` throws an HTTP 500, it is logged and skipped, ensuring the rest of the registry (and other broad sources like The Muse) proceed unaffected.

## 5. Summary
By combining the rigorous CSE taxonomy gates, 24-hour freshness checks, and dynamic per-employer telemetry tracking, the Internship Scanner ensures its data remains focused, high-yield, and entirely resistant to uncontrolled registry sprawl.
