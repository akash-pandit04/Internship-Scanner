import json
with open('docs/data/jobs.json', encoding='utf-8') as f:
    jobs = json.load(f).get('jobs', [])
yc = [j for j in jobs if j['source'] == 'ycombinator']
for i, j in enumerate(yc):
    print(f"{i+1}. {j['title']} | {j['company']} | {j['url']}")
