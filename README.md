# Internship Scanner v1.1.0

A production-ready, static internship discovery product backed by a telemetry-driven multi-source ingestion pipeline. 

This platform continuously acquires, filters, classifies, deduplicates, measures, and presents real internship data with strict deterministic validation. It focuses specifically on Computer Science and Engineering (CSE) roles globally.

## The Pipeline Architecture

The project has evolved into a highly coherent, resilient data pipeline:

1. **Public ATS Discovery** — Fetches unstructured raw job data from public sources and a curated ATS registry (`companies.json`).
2. **Normalization** — Maps disparate ATS schema dialects (Greenhouse, Lever, Ashby, SmartRecruiters, YCombinator) into a unified `JobRecord`.
3. **24-Hour Freshness** — Strictly expires listings older than 24 hours to prevent stale data buildup.
4. **Eligibility Validation** — Deterministic regex pattern-matching eliminates senior, non-intern, uncompensated, or unrelated roles.
5. **CSE Taxonomy** — Multi-pass classification tagging roles into 28 canonical Computer Science sub-disciplines (e.g., *AI/ML*, *Cloud/DevOps*, *Data Engineering*).
6. **Deduplication** — Semantic and exact URL hashing prevents pipeline flooding.
7. **Telemetry** — Observational metrics (`registry_metrics.json`) track source health independently from CSE yield.
8. **Static Frontend** — A high-performance, client-side dataset-aware UI (`docs/`) visualizing the curated baseline.

## Features

- **Strict Data Integrity:** Only fresh (<24h), eligible, and deduped records survive the ingestion funnel. 
- **Dataset-Aware UI:** The frontend natively calculates analytics (Total Internships, CSE Qualified, Locations, Companies) dynamically from the payload without backend database dependencies.
- **Provenance:** Direct application URLs and ATS source origins are securely passed through without mutation.
- **Robust Test Suite:** 29 independent isolation/regression tests (`pytest`) covering adapter logic, HTTP failure isolation, and taxonomy precision.

## Development Progression

The project successfully proved that a targeted ATS expansion strategy could sustainably grow the dataset while retaining strict quality gates:

- **Phase 7 (Hardening):** 86 CSE-qualified baseline
- **Phase 8A (Expansion):** 119 CSE-qualified baseline
- **Phase 8C (Expansion):** 137 CSE-qualified baseline
- **Phase 10 (v1.1.0):** Integrated Personio XML feeds

## Local Development

```bash
# Run the test suite
python -m pytest

# Run the ingestion pipeline
python scan.py

# Serve the frontend locally
cd docs
python -m http.server
```

## Release Note
**v1.1.0** is an immutable baseline representing the completion of the core pipeline and UI product layer.
