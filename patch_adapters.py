from pathlib import Path

def patch_file(p, old, new):
    path = Path(p)
    if not path.exists(): return
    text = path.read_text(encoding='utf-8')
    path.write_text(text.replace(old, new), encoding='utf-8')

# Greenhouse
patch_file('sources/adapters/legacy.py',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"greenhouse/{board}: {e}")\n                continue',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"greenhouse/{board}: {e}")\n                self.employer_stats[board] = {"status": "BROKEN"}\n                continue'
)
patch_file('sources/adapters/legacy.py',
           'board = board_data["id"]',
           'board = board_data["id"]\n            self.employer_stats[board] = {"status": "HEALTHY"}'
)

# Lever
patch_file('sources/adapters/legacy.py',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"lever/{c}: {e}")\n                continue',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"lever/{c}: {e}")\n                self.employer_stats[c] = {"status": "BROKEN"}\n                continue'
)
patch_file('sources/adapters/legacy.py',
           'c = board_data["id"]',
           'c = board_data["id"]\n            self.employer_stats[c] = {"status": "HEALTHY"}'
)

# Ashby
patch_file('sources/adapters/ashby.py',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"ashby/{board} failed: {e}")\n                continue',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"ashby/{board} failed: {e}")\n                self.employer_stats[board] = {"status": "BROKEN"}\n                continue'
)
patch_file('sources/adapters/ashby.py',
           'board = board_data["id"]',
           'board = board_data["id"]\n            self.employer_stats[board] = {"status": "HEALTHY"}'
)

# SmartRecruiters
patch_file('sources/adapters/smartrecruiters.py',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"smartrecruiters/{board} failed: {e}")\n                continue',
           'except Exception as e:\n                import logging\n                logging.getLogger(__name__).warning(f"smartrecruiters/{board} failed: {e}")\n                self.employer_stats[board] = {"status": "BROKEN"}\n                continue'
)
patch_file('sources/adapters/smartrecruiters.py',
           'board = board_data["id"]',
           'board = board_data["id"]\n            self.employer_stats[board] = {"status": "HEALTHY"}'
)
print('Done!')
