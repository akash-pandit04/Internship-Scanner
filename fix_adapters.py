import json
from pathlib import Path

ROOT = Path("C:/xampp/htdocs/Placement/job-scanner-main")

def fix_file(filename, replacements):
    path = ROOT / filename
    if not path.exists():
        return
    content = path.read_text(encoding="utf-8")
    for old, new in replacements:
        content = content.replace(old, new)
    path.write_text(content, encoding="utf-8")

# Fix legacy.py
legacy_old_comp = '''def _companies(kind):
    try:
        return json.loads((ROOT / "companies.json").read_text(encoding="utf-8-sig")).get(kind, [])
    except FileNotFoundError:
        return []'''

legacy_new_comp = '''def _companies(kind):
    try:
        data = json.loads((ROOT / "companies.json").read_text(encoding="utf-8-sig")).get(kind, [])
        out = []
        for item in data:
            if isinstance(item, dict):
                if item.get("enabled", True):
                    out.append(item)
            else:
                out.append({"id": item, "name": item.replace('-', ' ').title(), "region": "Global", "enabled": True})
        return out
    except FileNotFoundError:
        return []'''

legacy_old_gh = '''        for board in _companies("greenhouse"):
            try:
                data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", headers=HEADERS)'''
legacy_new_gh = '''        for board_data in _companies("greenhouse"):
            board = board_data["id"]
            board_name = board_data.get("name") or board.replace('-', ' ').title()
            try:
                data = fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs", headers=HEADERS)'''

legacy_old_gh_name = '''                    "company": board.replace("-", " ").title(),'''
legacy_new_gh_name = '''                    "company": board_name,'''

legacy_old_lv = '''        for c in _companies("lever"):
            try:
                jobs = fetch_json(f"https://api.lever.co/v0/postings/{c}?mode=json&limit=100", headers=HEADERS)'''
legacy_new_lv = '''        for board_data in _companies("lever"):
            c = board_data["id"]
            board_name = board_data.get("name") or c.replace('-', ' ').title()
            try:
                jobs = fetch_json(f"https://api.lever.co/v0/postings/{c}?mode=json&limit=100", headers=HEADERS)'''

legacy_old_lv_name = '''                    "title": j.get("text") or "", "company": c.replace("-", " ").title(),'''
legacy_new_lv_name = '''                    "title": j.get("text") or "", "company": board_name,'''

fix_file("sources/adapters/legacy.py", [
    (legacy_old_comp, legacy_new_comp),
    (legacy_old_gh, legacy_new_gh),
    (legacy_old_gh_name, legacy_new_gh_name),
    (legacy_old_lv, legacy_new_lv),
    (legacy_old_lv_name, legacy_new_lv_name)
])

# Fix ashby.py
ashby_old = '''        for board in _companies("ashby"):
            try:
                data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}", headers=HEADERS)'''
ashby_new = '''        for board_data in _companies("ashby"):
            board = board_data["id"]
            try:
                data = fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{board}", headers=HEADERS)'''
fix_file("sources/adapters/ashby.py", [(ashby_old, ashby_new)])

# Fix smartrecruiters.py
sr_old = '''        for board in _companies("smartrecruiters"):
            has_more = True'''
sr_new = '''        for board_data in _companies("smartrecruiters"):
            board = board_data["id"]
            has_more = True'''
fix_file("sources/adapters/smartrecruiters.py", [(sr_old, sr_new)])

# Fix ycombinator.py
yc_old = '''        for company in _companies("ycombinator"):
            try:
                # Typically just ycombinator as a dummy token in companies.json'''
yc_new = '''        for board_data in _companies("ycombinator"):
            company = board_data["id"]
            try:
                # Typically just ycombinator as a dummy token in companies.json'''
fix_file("sources/adapters/ycombinator.py", [(yc_old, yc_new)])

print("Done")
