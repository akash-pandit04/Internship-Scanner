import requests, json
from bs4 import BeautifulSoup
import time

def fetch_yc_page(page, session):
    url = f'https://www.ycombinator.com/jobs/role/engineering?page={page}'
    r = session.get(url, timeout=10)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, 'html.parser')
    node = soup.find(attrs={'data-page': True})
    if not node:
        return None
    data = json.loads(node['data-page'])
    return data['props']['jobPostings']

session = requests.Session()
all_jobs = []
seen_ids = set()
for p in range(1, 10): # test first 9 pages to see how many we get
    jobs = fetch_yc_page(p, session)
    if not jobs:
        break
    added = 0
    for j in jobs:
        if j['id'] not in seen_ids:
            seen_ids.add(j['id'])
            all_jobs.append(j)
            added += 1
    print(f'Page {p}: got {len(jobs)} jobs, {added} new')
    if added == 0:
        break
    time.sleep(1)

with open('yc_jobs_discovery.json', 'w') as f:
    json.dump(all_jobs, f)
print(f'Total jobs fetched: {len(all_jobs)}')
