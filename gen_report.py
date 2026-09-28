import json

with open('audit_sample.json', encoding='utf-8') as f:
    data = json.load(f)

with open('audit_report.md', 'w', encoding='utf-8') as f:
    f.write('# Phase 7H Deduplication Classifier Audit\n\n')
    f.write('## Semantic Duplicates (High Confidence > 80%)\n')
    for i, j in enumerate(data['semantic']):
        f.write(f"{i+1}. **{j.get('company')}** - {j.get('title')} - {j.get('location')}\n")
        
    f.write('\n## Ambiguous Duplicates (Moderate Confidence > 60%)\n')
    for i, j in enumerate(data['ambiguous']):
        f.write(f"{i+1}. **{j.get('company')}** - {j.get('title')} - {j.get('location')}\n")
        
    f.write('\n## Genuinely New (No Match)\n')
    for i, j in enumerate(data['new']):
        f.write(f"{i+1}. **{j.get('company')}** - {j.get('title')} - {j.get('location')}\n")
