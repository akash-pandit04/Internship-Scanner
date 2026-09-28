import requests, json
from bs4 import BeautifulSoup
import time

roles = ['software-engineer', 'designer', 'product-manager', 'recruiting-hr', 'sales-manager', 'marketing', 'support', 'operations', 'science']
locations = ['san-francisco', 'new-york', 'los-angeles', 'seattle', 'austin', 'chicago', 'india', 'remote']

session = requests.Session()
all_ids = set()
total_fetched = 0

def fetch(role, loc=None):
    url = f'https://www.ycombinator.com/jobs/role/{role}'
    if loc:
        url += f'/{loc}'
    r = session.get(url, timeout=10)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, 'html.parser')
    node = soup.find(attrs={'data-page': True})
    if not node:
        return []
    data = json.loads(node['data-page'])
    return data['props']['jobPostings']

# Fetch base roles
for r in roles:
    jobs = fetch(r)
    total_fetched += len(jobs)
    for j in jobs:
        all_ids.add(j['id'])
    time.sleep(0.2)

# Fetch roles + locations
for r in roles:
    for l in locations:
        jobs = fetch(r, l)
        total_fetched += len(jobs)
        for j in jobs:
            all_ids.add(j['id'])
        time.sleep(0.2)

print(f'Total requests made: {len(roles) + len(roles) * len(locations)}')
print(f'Total job instances returned: {total_fetched}')
print(f'Total UNIQUE jobs found: {len(all_ids)}')
