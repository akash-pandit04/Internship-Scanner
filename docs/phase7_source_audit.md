# Phase 7: Global Source Discovery & Coverage Expansion

## Candidate Source Audit

### ATS (Applicant Tracking Systems)

| Source | Source type | Geographic coverage | Internship relevance | Technical/CSE relevance | Public access mechanism | Auth required | Pagination | Structured data | Freshness | Apply URL | Expected duplicate risk | robots/terms | Implementation complexity | Expected unique contribution | Decision | Reason |
|--------|-------------|---------------------|----------------------|-------------------------|-------------------------|---------------|------------|-----------------|-----------|-----------|-------------------------|--------------|---------------------------|------------------------------|----------|--------|
| Ashby | ATS | Global | High | High | JSON API (`api.ashbyhq.com/posting-api`) | No | Yes | Yes | Yes | Yes | Low | API allowed | Low | High (Many modern startups) | Candidate | Clean structured JSON API, highly relevant for tech. |
| SmartRecruiters | ATS | Global | High | High | JSON API (`api.smartrecruiters.com`) | No | Yes | Yes | Yes | Yes | Low | API allowed | Medium | High (Enterprise & mid-market) | Candidate | Standardized API endpoints available per company. |
| Workday | ATS | Global | High | High | Web/JSON | No | Yes | Yes (JSON-LD often) | Yes | Yes | Low | Varies | High | High (Fortune 500) | Candidate | Massive volume, though API requires scraping JSON from frontend. |
| Jobvite | ATS | Global | Medium | Medium | XML/JSON Feed | No | No | Yes | Yes | Yes | Low | Allowed | Low | Medium | Candidate | Easy XML feed parsing per company. |
| BambooHR | ATS | Global | Medium | Medium | XML Feed | No | No | Yes | No | Yes | Low | Allowed | Low | Low | Defer | Usually used by smaller companies, fewer internships. |
| Teamtailor | ATS | Europe/Global | High | Medium | JSON API | No | Yes | Yes | Yes | Yes | Low | Allowed | Low | Medium | Candidate | Clean API, strong in Europe. |
| Recruitee | ATS | Europe/Global | Medium | Medium | JSON API | No | No | Yes | Yes | Yes | Low | Allowed | Low | Medium | Candidate | Clean API available per company. |
| Personio | ATS | Europe | High | Medium | XML Feed | No | No | Yes | Yes | Yes | Low | Allowed | Low | Medium | Candidate | Huge presence in DACH region, simple XML. |

### Global/Regional Boards

| Source | Source type | Geographic coverage | Internship relevance | Technical/CSE relevance | Public access mechanism | Auth required | Pagination | Structured data | Freshness | Apply URL | Expected duplicate risk | robots/terms | Implementation complexity | Expected unique contribution | Decision | Reason |
|--------|-------------|---------------------|----------------------|-------------------------|-------------------------|---------------|------------|-----------------|-----------|-----------|-------------------------|--------------|---------------------------|------------------------------|----------|--------|
| EURES | Government | Europe | High | Medium | API/Web | Yes/No | Yes | Yes | Yes | Yes | Medium | API terms | High | High | Candidate | Official EU job mobility portal. Huge coverage. |
| Internshala | Board | India | High | High | Web/App | No | Yes | Mixed | Yes | Yes | High | Scraping restricted | High | High | Defer | High friction for scraping, strict terms. |
| GradConnection | Board | APAC (Aus/Asia) | High | Medium | Web | No | Yes | Mixed | Yes | Yes | Medium | Varies | High | Medium | Defer | Requires heavy scraping. |
| WayUp | Board | North America | High | Medium | Web/API | No | Yes | Yes | Yes | Yes | Medium | Varies | Medium | High | Candidate | Focused specifically on early-career/internships. |
| Naukri (Campus) | Board | India/Middle East | High | High | Web | No | Yes | Mixed | Yes | Yes | High | Strict terms | High | High | Reject | Scraping heavily blocked, requires enterprise access. |
| Bayt | Board | Middle East/Africa | Medium | Medium | Web | No | Yes | Mixed | Yes | Yes | High | Strict terms | High | Medium | Defer | Scraping restricted. |
| Computrabajo | Board | Latin America | Medium | Medium | Web | No | Yes | Mixed | Yes | Yes | High | Varies | High | Medium | Defer | Requires heavy scraping, generic roles. |

### Technology/Startup/Community

| Source | Source type | Geographic coverage | Internship relevance | Technical/CSE relevance | Public access mechanism | Auth required | Pagination | Structured data | Freshness | Apply URL | Expected duplicate risk | robots/terms | Implementation complexity | Expected unique contribution | Decision | Reason |
|--------|-------------|---------------------|----------------------|-------------------------|-------------------------|---------------|------------|-----------------|-----------|-----------|-------------------------|--------------|---------------------------|------------------------------|----------|--------|
| Wellfound (AngelList) | Community | Global | High | High | GraphQL/Web | Yes | Yes | Yes | Yes | Yes | Medium | Strict terms | High | High | Reject | Cloudflare protection + terms strictly prohibit scraping. |
| Y Combinator WaaS | Community | Global | High | High | Web/API | No | Yes | Yes | Yes | Yes | Low | Allowed | Medium | High | Candidate | Great startup tech internships. |
| Simplify.jobs | Community | North America | High | High | Web/API | No | Yes | Yes | Yes | Yes | High | Terms restrict | High | High | Reject | Competitor, strictly prohibits scraping. |
| NSF REU Sites | Gov/University | USA | High | High | Web | No | Yes | HTML | Yes | Yes | Low | Open | Medium | High | Candidate | Prime source for research internships. |
