from eligibility import determine_eligibility, EligibilityStatus

def test_classifier_conflicts():
    # ACCEPT
    assert determine_eligibility("Software Engineering Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Data Science Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Machine Learning Intern", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Software Engineering Co-op", "") == EligibilityStatus.ELIGIBLE
    assert determine_eligibility("Working Student - Software Engineering", "", employment_type="Student") == EligibilityStatus.ELIGIBLE
    
    # REJECT
    assert determine_eligibility("Senior Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Staff Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Principal Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Engineering Manager", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Director of Engineering", "") == EligibilityStatus.NON_INTERNSHIP
    assert determine_eligibility("Software Engineer", "") == EligibilityStatus.NON_INTERNSHIP
    
    # UNCERTAIN
    assert determine_eligibility("Student Software Developer", "") == EligibilityStatus.UNCERTAIN
    assert determine_eligibility("Graduate Software Engineer", "") == EligibilityStatus.UNCERTAIN
    assert determine_eligibility("Apprentice Developer", "") == EligibilityStatus.UNCERTAIN
    
    # CONFLICT CASES
    # AI intern + Full-Time
    assert determine_eligibility("A.I. Engineering Intern", "", employment_type="Full-Time") == EligibilityStatus.ELIGIBLE
    # Intern + Part-Time
    assert determine_eligibility("Intern", "", employment_type="Part-Time") == EligibilityStatus.ELIGIBLE
    # Working Student + Part-Time
    assert determine_eligibility("Working Student", "", employment_type="Part-Time") == EligibilityStatus.ELIGIBLE
    # Internship in desc, title is SWE
    assert determine_eligibility("Software Engineer", "This is an internship role") == EligibilityStatus.UNCERTAIN
    # Intern to the VP
    assert determine_eligibility("Intern to the VP", "") == EligibilityStatus.NON_INTERNSHIP

def test_freshness_filtering():
    from datetime import datetime, timezone, timedelta
    from scan import InternshipScannerPipeline
    
    now = datetime.now(timezone.utc)
    fresh_date = now - timedelta(hours=12)
    stale_date = now - timedelta(hours=48)
    
    j_fresh = {"title": "A Intern", "company": "A", "url": "http://a.com", "posted_at": fresh_date}
    j_stale = {"title": "B Intern", "company": "B", "url": "http://b.com", "posted_at": stale_date}
    j_missing = {"title": "C Intern", "company": "C", "url": "http://c.com", "posted_at": None}
    
    pipeline = InternshipScannerPipeline(".")
    pipeline.config = {"max_age_hours": 24}
    
    assert pipeline.is_fresh(j_fresh, now) == True
    assert pipeline.is_fresh(j_stale, now) == False
    assert pipeline.is_fresh(j_missing, now) == True # Missing dates are usually accepted
