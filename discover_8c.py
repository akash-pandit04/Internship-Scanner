import requests, json, concurrent.futures
from eligibility import determine_eligibility, EligibilityStatus
from scan import JobCategorizer

slugs = [
    'hashicorp', 'cloudflare', 'datadog', 'pagerduty', 'docker', 'digitalocean',
    'couchbase', 'elastic', 'confluent', 'redis', 'cockroachlabs', 'singlestore',
    'openai', 'anthropic', 'huggingface', 'cohere', 'scaleai',
    'revolut', 'n26', 'klarna', 'zalando', 'deliveryhero', 'criteo', 'bolt', 'wolt',
    'gitlab', 'github', 'uber', 'grab', 'gojek', 'swiggy', 'zomato', 'razorpay',
    'atlassian', 'canva', 'tiktok', 'shopee', 'rakuten', 'line', 'mercari',
    'nvidia', 'amd', 'arm', 'qualcomm', 'intel', 'tesla', 'anduril', 'palantir',
    'vercel', 'pinecone', 'weaviate', 'qdrant', 'chroma'
]

taxonomy = JobCategorizer()
results = {'raw': 0, 'internships': 0, 'cse': 0}
cse_jobs = []

def fetch_greenhouse(slug):
    try:
        r = requests.get(f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs', timeout=5)
        if r.status_code == 200: return 'greenhouse', slug, r.json().get('jobs', [])
    except: pass
    return 'greenhouse', slug, []

def fetch_lever(slug):
    try:
        r = requests.get(f'https://api.lever.co/v0/postings/{slug}?mode=json', timeout=5)
        if r.status_code == 200: return 'lever', slug, r.json()
    except: pass
    return 'lever', slug, []
    
def fetch_ashby(slug):
    try:
        r = requests.get(f'https://api.ashbyhq.com/posting-api/job-board/{slug}', timeout=5)
        if r.status_code == 200: return 'ashby', slug, r.json().get('jobs', [])
    except: pass
    return 'ashby', slug, []

futures = []
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    for slug in slugs:
        futures.append(executor.submit(fetch_greenhouse, slug))
        futures.append(executor.submit(fetch_lever, slug))
        futures.append(executor.submit(fetch_ashby, slug))
        
    for f in concurrent.futures.as_completed(futures):
        ats, slug, jobs = f.result()
        if not jobs: continue
        
        results['raw'] += len(jobs)
        
        for j in jobs:
            title = j.get('title', j.get('text', j.get('name', '')))
            loc = ''
            if ats == 'greenhouse': loc = j.get('location', {}).get('name', '')
            elif ats == 'lever': loc = j.get('categories', {}).get('location', '')
            elif ats == 'ashby': loc = j.get('location', '')
            
            elig = determine_eligibility(title, '', '')
            if elig == EligibilityStatus.NON_INTERNSHIP: continue
            
            results['internships'] += 1
            
            cats = taxonomy.categorize(title, '')
            if cats:
                results['cse'] += 1
                cse_jobs.append(f"[{ats}] {slug}: {title} ({loc})")
                
print('Raw:', results['raw'])
print('Internships:', results['internships'])
print('CSE:', results['cse'])
for j in cse_jobs: print(' -', j)
