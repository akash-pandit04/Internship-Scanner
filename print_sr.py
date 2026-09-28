import json
with open('docs/data/jobs.json', 'r', encoding='utf-8') as f:
    jobs = [j for j in json.load(f)['jobs'] if j['source'] == 'smartrecruiters']
with open('sr_jobs.txt', 'w', encoding='utf-8') as out:
    for j in jobs[:20]:
        out.write(f"{j['company']} | {j['title']} | {j['location']} | {j['categories']} | {j['employment_type']}\n")
    out.write(f"Total SmartRecruiters accepted: {len(jobs)}\n")
