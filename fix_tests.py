from pathlib import Path

def patch_file(p, old, new):
    path = Path(p)
    if not path.exists(): return
    text = path.read_text(encoding='utf-8')
    path.write_text(text.replace(old, new), encoding='utf-8')

patch_file('tests/sources/test_ashby.py', 'lambda k: ["canva"]', 'lambda k: [{"id": "canva"}]')
patch_file('tests/sources/test_ashby.py', 'lambda k: [\n        "bad_board", "timeout_board", "malformed_json",\n        "malformed_list", "missing_jobUrl", "empty_jobs", "good_board"\n    ]', 'lambda k: [\n        {"id": "bad_board"}, {"id": "timeout_board"}, {"id": "malformed_json"},\n        {"id": "malformed_list"}, {"id": "missing_jobUrl"}, {"id": "empty_jobs"}, {"id": "good_board"}\n    ]')

patch_file('tests/sources/test_smartrecruiters.py', 'lambda k: ["canva"]', 'lambda k: [{"id": "canva"}]')
patch_file('tests/sources/test_smartrecruiters.py', 'lambda k: [\n        "bad_board", "timeout_board", "malformed_json",\n        "malformed_list", "missing_total", "empty_content", "good_board"\n    ]', 'lambda k: [\n        {"id": "bad_board"}, {"id": "timeout_board"}, {"id": "malformed_json"},\n        {"id": "malformed_list"}, {"id": "missing_total"}, {"id": "empty_content"}, {"id": "good_board"}\n    ]')

patch_file('tests/test_greenhouse_isolation.py', 'return ["good_company", "fail_company"]', 'return [{"id": "good_company"}, {"id": "fail_company"}]')

print('Done fixing tests!')
