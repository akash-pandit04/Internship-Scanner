import requests, json
from eligibility import determine_eligibility, EligibilityStatus
from scan import JobCategorizer

boards = {
    'greenhouse': ['figma', 'stripe', 'roblox', 'reddit', 'mongodb', 'instacart', 'twilio', 'lyft'],
    'ashby': ['linear', 'render', 'supabase'],
    'smartrecruiters': ['canva']
}

taxonomy = JobCategorizer()
results = {'raw': 0, 'internships': 0, 'cse': 0}
cse_jobs = []

for ats, companies in boards.items():
    for c in companies:
        jobs = []
        try:
            if ats == 'greenhouse':
                r = requests.get(f'https://boards-api.greenhouse.io/v1/boards/{c}/jobs', timeout=5)
                jobs = r.json().get('jobs', [])
            elif ats == 'ashby':
                r = requests.get(f'https://api.ashbyhq.com/posting-api/job-board/{c}', timeout=5)
                jobs = r.json().get('jobs', [])
            elif ats == 'smartrecruiters':
                r = requests.get(f'https://api.smartrecruiters.com/v1/companies/{c}/postings?limit=100', timeout=5)
                jobs = r.json().get('content', [])
        except Exception as e:
            continue
        
        results['raw'] += len(jobs)
        
        for j in jobs:
            title = j.get('title', j.get('name', ''))
            
            # Extract location string safely
            loc = ""
            if ats == 'greenhouse':
                loc = j.get('location', {}).get('name', '')
            elif ats == 'smartrecruiters':
                loc = j.get('location', {}).get('city', '') + ', ' + j.get('location', {}).get('country', '')
            elif ats == 'ashby':
                loc = j.get('location', '')
                
            desc = '' # No description fetched for speed, but eligibility mostly uses title
            
            # SmartRecruiters gives employment type
            emp_type = j.get('typeOfEmployment', {}).get('id', '') if ats == 'smartrecruiters' else ''
            
            elig = determine_eligibility(title, desc, emp_type)
            if elig == EligibilityStatus.NON_INTERNSHIP: continue
            
            results['internships'] += 1
            
            cats = taxonomy.categorize(title, desc)
            if cats:
                results['cse'] += 1
                cse_jobs.append(f"{c}: {title} ({loc})")
                
print('Raw:', results['raw'])
print('Internships:', results['internships'])
print('CSE:', results['cse'])
for j in cse_jobs: print(' -', j)
