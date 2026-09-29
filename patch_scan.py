import re

with open('scan.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''        companies_path = self.root_dir / "companies.json"
        total_endpoints = 0
        if companies_path.exists():
            import json
            comps = json.loads(companies_path.read_text(encoding="utf-8"))
            total_endpoints += sum(len(v) if isinstance(v, list) else 1 for v in comps.values())
        total_endpoints += 10 # Add static adapters like legacy

        out_data = {
            "generated_at": now.isoformat(),
            "config": {"retention_days": self.config.get("global", {}).get("retention_days", 30)},
            "all_sources": list(adapters.keys()),
            "total_endpoints": total_endpoints,
            "source_meta": {},
            "jobs": [j.to_dict() for j in processed_jobs.values()]
        }'''

pattern = r'out_data = \{\s*"generated_at": now\.isoformat\(\),\s*"config": \{"retention_days": self\.config\.get\("global", \{\}\)\.get\("retention_days", 30\)\},\s*"all_sources": list\(adapters\.keys\(\)\),\s*"source_meta": \{\},\s*"jobs": \[j\.to_dict\(\) for j in processed_jobs\.values\(\)\]\s*\}'

text = re.sub(pattern, replacement, text)

with open('scan.py', 'w', encoding='utf-8') as f:
    f.write(text)
