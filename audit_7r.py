import json
from datetime import datetime, timezone
from collections import Counter

with open('docs/data/jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
jobs = data.get('jobs', [])
print(f'Total jobs: {len(jobs)}')

cse_count = sum(1 for j in jobs if j.get('categories'))
uncategorized = sum(1 for j in jobs if not j.get('categories'))
print(f'CSE taxonomy passing: {cse_count}')
print(f'categories: []: {uncategorized}')

cats = Counter()
for j in jobs:
    for c in j.get('categories', []):
        cats[c] += 1
print('\nCategory breakdown:')
for k, v in cats.most_common():
    print(f'  {k}: {v}')
    
# Freshness
print('\nFreshness distribution (hours old relative to now):')
now = datetime.now(timezone.utc)
hours_old = []
for j in jobs:
    if j.get('updated_at'):
        try:
            dt = datetime.fromisoformat(j['updated_at'].replace('Z', '+00:00'))
            diff = (now - dt).total_seconds() / 3600
            hours_old.append(diff)
        except: pass

if hours_old:
    print(f'  Min hours: {min(hours_old):.2f}')
    print(f'  Max hours: {max(hours_old):.2f}')
    print(f'  Avg hours: {sum(hours_old)/len(hours_old):.2f}')
    under_24 = sum(1 for h in hours_old if h <= 24)
    over_24 = sum(1 for h in hours_old if h > 24)
    print(f'  <= 24h: {under_24}')
    print(f'  > 24h: {over_24}')
else:
    print('  No parsable updated_at fields found.')

print('\nSample CSE records (first 3):')
for j in [j for j in jobs if j.get('categories')][:3]:
    print(f"  - {j.get('title')} at {j.get('company')} ({j.get('categories')})")

print('\nSample uncategorized (first 3):')
for j in [j for j in jobs if not j.get('categories')][:3]:
    print(f"  - {j.get('title')} at {j.get('company')}")
