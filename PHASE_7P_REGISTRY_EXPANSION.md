# Phase 7P — Registry Expansion

## 1. Executive Summary

Phase 7P executed a controlled production ingestion of the four curated technology employers identified in Phase 7O: Rubrik, Celonis, Databricks, and Dropbox. We successfully updated the production `companies.json` and adapter architecture and ran the full `scan.py` production pipeline. 

The test verified that our pipeline safely integrates these feeds while rigorously enforcing all existing data integrity constraints (freshness, eligibility, taxonomy, and deduplication). The addition successfully introduced 5 genuinely new CSE records targeting our weakest regional and technical gaps, while strictly rejecting stale and non-CSE postings.

## 2. Production Registry Updates

The `companies.json` file was restructured to explicitly curate specific boards under a structured object schema (enabling `id`, `name`, `region`, and `enabled` toggles). We added:
* **Rubrik** (Greenhouse)
* **Celonis** (Greenhouse)
* **Databricks** (Greenhouse)
* **Dropbox** (Greenhouse)

All pre-existing baseline adapters (`ashby.py`, `smartrecruiters.py`, `ycombinator.py`, `legacy.py`) were patched to safely consume this object format without altering their legacy targets, preserving the baseline ecosystem exactly.

## 3. Final Production Metrics

The production pipeline processed these sources alongside the existing baseline. Note that the slight drop in total records is expected as older records organically expire out of the 24-hour freshness window.

| Metric                  | Before 7P (7H) | After 7P |
| ----------------------- | -------------: | -------: |
| Total records           |            610 |      597 |
| CSE-taxonomy-passing    |             88 |       86 |
| Fresh CSE               |             88 |       86 |
| New CSE from Rubrik     |              — |        1 |
| New CSE from Celonis    |              — |        4 |
| New CSE from Databricks |              — |        0 |
| New CSE from Dropbox    |              — |        0 |
| Exact duplicates        |              0 |        0 |
| Semantic duplicates     |             36 |       39 |
| Ambiguous duplicates    |             83 |       82 |

*Note on Databricks & Dropbox:* During 7O, we observed active internships for these employers on their public board. However, the production scanner strictly enforces a `< 24 hours` freshness window (based on `updated_at`). Because Databricks and Dropbox had not updated their respective postings within the last 24 hours, the pipeline correctly discarded them as stale. This proves the pipeline's filters will not be bypassed.

## 4. Geographic & Category Contribution

The 5 successfully ingested records precisely addressed the gaps identified in Phase 7I:

* **India:** 
  * Rubrik → 1 (`Software Engineer (CPD) - Winter Intern` in Bangalore)
* **Western Europe:** 
  * Celonis → 4 (Roles in Munich, Paris, Madrid)
* **North America:** 
  * Databricks → 0 (Rejected by freshness)
* **Remote:** 
  * Dropbox → 0 (Rejected by freshness)

**Category Targeting:** All 4 Celonis roles correctly mapped to the `AI / Machine Learning` taxonomy category, while Rubrik mapped to `Software Engineering`. 

## 5. Duplicate Record Prevention Verification

As requested, we verified the handling of multi-location ATS strings (e.g., Databricks's `Bellevue, Washington; Mountain View, California; San Francisco, California`). 

The production normalization accurately passes these through as a single compound string rather than erroneously inflating the dataset by splitting it into 3 separate records. The 4 Celonis records were generated because Celonis's ATS provided 4 distinct job listings for those locations, not due to an adapter splitting error.

## 6. Project Status

| Phase                          | Status                |
| ------------------------------ | --------------------- |
| 7I Coverage Gap Analysis       | ✅ Complete            |
| 7J Regional Source Feasibility | ✅ Complete            |
| 7K Adzuna                      | ❌ Rejected            |
| 7M ATS Registry Feasibility    | ✅ Passed              |
| 7N ATS Registry Implementation | ✅ Production verified |
| 7O Expanded Registry Discovery | ✅ Complete            |
| **7P Registry Expansion**      | ✅ **Complete / Verified** |

## Conclusion

The curated ATS ingestion architecture has been successfully validated end-to-end with the tested Greenhouse employers, and it has produced 5 genuinely new CSE-taxonomy-passing records without weakening existing data-quality controls. We successfully injected targeted employer pipelines that directly address our CSE gaps without relying on broad aggregators, and the production pipeline's defenses (taxonomy mapping, freshness checking) remain firmly intact. 
