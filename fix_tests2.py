import os
def patch_file(p):
    with open(p, 'r') as f: content = f.read()
    content = content.replace('lambda k: ["notion", "empty_board"]', 'lambda k: [{"id":"notion"}, {"id":"empty_board"}]')
    content = content.replace('lambda k: ["test"]', 'lambda k: [{"id":"test"}]')
    content = content.replace('lambda k: ["bad_board", "good_board"]', 'lambda k: [{"id":"bad_board"}, {"id":"good_board"}]')
    content = content.replace('lambda k: [\n            "bad_board", "timeout_board", "malformed_json",\n            "malformed_list", "missing_total", "empty_content", "good_board"\n        ]', 'lambda k: [{"id":"bad_board"}, {"id":"timeout_board"}, {"id":"malformed_json"}, {"id":"malformed_list"}, {"id":"missing_total"}, {"id":"empty_content"}, {"id":"good_board"}]')
    with open(p, 'w') as f: f.write(content)

patch_file('tests/sources/test_ashby.py')
patch_file('tests/sources/test_smartrecruiters.py')
