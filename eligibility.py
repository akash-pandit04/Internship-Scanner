import re

class EligibilityStatus:
    ELIGIBLE = "ELIGIBLE_INTERNSHIP"
    NON_INTERNSHIP = "NON_INTERNSHIP"
    UNCERTAIN = "UNCERTAIN"

def determine_eligibility(title: str, description: str, employment_type: str = "") -> str:
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    emp_lower = (employment_type or "").lower()

    # Strong negative signals (indicating a full-time, experienced, or leadership role)
    strong_negative_terms = ['senior', 'staff', 'principal', 'lead', 'manager', 'director', 'head', 'vice president', 'vp', 'full-time', 'full time']
    
    # Strong positive signals
    strong_positive_terms = ['intern', 'internship', 'co-op', 'coop', 'cooperative education', 'internship program', 'working student', 'werkstudent', 'praktikant']
    
    # Contextual signals
    contextual_terms = ['student', 'undergraduate', 'university', 'campus', 'placement', 'summer program', 'graduate program', 'graduate', 'apprentice']

    has_strong_negative = any(re.search(r'\b' + flag + r'\b', title_lower) for flag in strong_negative_terms)
    has_strong_positive_title = any(re.search(r'\b' + term + r'\b', title_lower) for term in strong_positive_terms)
    has_strong_positive_emp = any(term in emp_lower for term in strong_positive_terms)
    has_contextual_title = any(re.search(r'\b' + term + r'\b', title_lower) for term in contextual_terms)
    has_strong_positive_desc = any(re.search(r'\b' + term + r'\b', desc_lower) for term in strong_positive_terms)

    # 1. If it has a strong negative signal in the title, we must be very careful.
    if has_strong_negative:
        # If the employment type explicitly confirms it's an internship, we can keep it.
        # Otherwise, "Intern to the VP" (with no emp type) gets rejected.
        if has_strong_positive_emp:
            return EligibilityStatus.ELIGIBLE
        return EligibilityStatus.NON_INTERNSHIP

    # 2. Strong positive in title or employment type usually means it's an internship.
    if has_strong_positive_title or has_strong_positive_emp:
        return EligibilityStatus.ELIGIBLE

    # 3. Contextual signals need additional evidence
    if has_contextual_title:
        if has_strong_positive_desc:
            return EligibilityStatus.ELIGIBLE
        return EligibilityStatus.UNCERTAIN

    # 4. Mentions internship in description but title gives no hints
    # It might be "You will work with interns" or it might actually be an internship.
    if has_strong_positive_desc:
        return EligibilityStatus.UNCERTAIN

    # If no signals matched, it's a regular job.
    return EligibilityStatus.NON_INTERNSHIP
