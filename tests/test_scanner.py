import pytest
from sources import strip_html

def test_strip_html():
    assert strip_html("<p>Software Engineer</p>") == "Software Engineer"
    assert strip_html("<div>Data <b>Scientist</b> Intern</div>") == "Data Scientist Intern"

def test_scoring_logic():
    # Placeholder for upcoming OOP scoring tests
    pass
