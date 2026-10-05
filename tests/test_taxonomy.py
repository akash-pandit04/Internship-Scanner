import pytest
from scan import JobCategorizer

def test_taxonomy_positive_cases():
    categorizer = JobCategorizer()
    
    # Positive explicit matches
    assert "Frontend Development" in categorizer.categorize("Frontend Developer Intern", "")
    assert "Data Engineering" in categorizer.categorize("Data Engineer Intern", "")
    assert "Backend Development" in categorizer.categorize("Backend Engineering Intern", "")
    assert "Full-Stack Development" in categorizer.categorize("Fullstack Intern", "")
    assert "AI / Machine Learning" in categorizer.categorize("Machine Learning Intern", "")
    assert "AI / Machine Learning" in categorizer.categorize("A.I. Engineering Intern", "")
    assert "Computer Vision" in categorizer.categorize("Computer Vision Intern", "")
    assert "Cybersecurity" in categorizer.categorize("Cybersecurity Intern", "")
    
    # Multi-category assignments
    multi_cats = categorizer.categorize("NLP Research Intern", "")
    assert "NLP" in multi_cats
    assert "Research" in multi_cats

    multi_cats2 = categorizer.categorize("Full-Stack Software Engineering Intern", "")
    assert "Full-Stack Development" in multi_cats2
    assert "Software Engineering" in multi_cats2

def test_taxonomy_negative_cases():
    categorizer = JobCategorizer()
    
    # Exclusions
    cats = categorizer.categorize("Data Entry Intern", "")
    assert "Data Analytics" not in cats
    
    cats = categorizer.categorize("Graphic Design Intern", "")
    assert "UI/UX for Software" not in cats
    
    cats = categorizer.categorize("HR Intern", "working with software")
    assert "Software Engineering" not in cats
    
    cats = categorizer.categorize("Intern to the VP of Engineering", "")
    assert "Software Engineering" not in cats
    assert cats == []

def test_taxonomy_hardware_cases():
    categorizer = JobCategorizer()
    
    cats = categorizer.categorize("Hardware Engineering Intern", "")
    # Hardware Engineering is not in the CSE taxonomy
    assert "Embedded Systems" not in cats
    assert "Firmware" not in cats
    assert cats == []
    
    cats = categorizer.categorize("Embedded Software Intern", "")
    assert "Embedded Systems" in cats
    
    cats = categorizer.categorize("Firmware Engineer Intern", "")
    assert "Firmware" in cats

def test_taxonomy_technology_mention_avoidance():
    categorizer = JobCategorizer()
    
    # Just mentioning a technology in description shouldn't trigger categories alone
    # Note: Description is only checked for specific desc_patterns (like "software engineering intern")
    cats = categorizer.categorize("Business Intern", "Experience with AWS and SQL preferred.")
    assert "Cloud Computing" not in cats
    assert "Database Engineering" not in cats
    assert cats == []

def test_taxonomy_no_fallback():
    categorizer = JobCategorizer()
    
    cats = categorizer.categorize("Marketing Intern", "")
    assert cats == []
    
    cats = categorizer.categorize("Finance Intern", "")
    assert cats == []
