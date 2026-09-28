import json
import re
from collections import Counter
from datetime import datetime, timezone
import statistics

# Load jobs
with open('docs/data/jobs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    jobs = data.get('jobs', [])

# 1. Dataset Integrity
total_records = len(jobs)
ids = [j.get('id') for j in jobs]
duplicate_ids = total_records - len(set(ids))
urls = [j.get('url') for j in jobs]
duplicate_urls = total_records - len(set(urls))

missing_companies = sum(1 for j in jobs if not j.get('company') or str(j.get('company')).lower() in ('', 'unknown'))
missing_locations = sum(1 for j in jobs if not j.get('location') or str(j.get('location')).lower() in ('', 'unknown'))
missing_categories = sum(1 for j in jobs if 'categories' not in j)
empty_categories = sum(1 for j in jobs if not j.get('categories'))
missing_source = sum(1 for j in jobs if not j.get('source'))
missing_invalid_dates = 0
ages_days = []
now = datetime.now(timezone.utc)
for j in jobs:
    d = j.get('posted_at')
    if not d:
        missing_invalid_dates += 1
    else:
        try:
            dt = datetime.fromisoformat(d)
            age = (now - dt).total_seconds() / 86400.0
            ages_days.append(age)
        except:
            missing_invalid_dates += 1

integrity_report = {
    'total_records': total_records,
    'duplicate_ids': duplicate_ids,
    'duplicate_urls': duplicate_urls,
    'missing_companies': missing_companies,
    'missing_locations': missing_locations,
    'empty_categories': empty_categories,
    'missing_source': missing_source,
    'missing_invalid_dates': missing_invalid_dates
}

# 2. Geographic Analysis
US_STATES = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC']
COUNTRY_MAP = {
    'united states': 'United States', 'usa': 'United States', 'us': 'United States', 'united kingdom': 'United Kingdom', 'uk': 'United Kingdom',
    'canada': 'Canada', 'germany': 'Germany', 'france': 'France', 'netherlands': 'Netherlands', 'ireland': 'Ireland',
    'switzerland': 'Switzerland', 'spain': 'Spain', 'italy': 'Italy', 'poland': 'Poland', 'sweden': 'Sweden', 'denmark': 'Denmark',
    'norway': 'Norway', 'finland': 'Finland', 'india': 'India', 'singapore': 'Singapore', 'japan': 'Japan', 'south korea': 'South Korea',
    'korea': 'South Korea', 'china': 'China', 'hong kong': 'Hong Kong', 'taiwan': 'Taiwan', 'australia': 'Australia',
    'new zealand': 'New Zealand', 'brazil': 'Brazil', 'mexico': 'Mexico', 'argentina': 'Argentina', 'chile': 'Chile',
    'colombia': 'Colombia', 'south africa': 'South Africa', 'uae': 'UAE', 'united arab emirates': 'UAE', 'saudi arabia': 'Saudi Arabia',
    'israel': 'Israel', 'vietnam': 'Vietnam', 'romania': 'Romania', 'hungary': 'Hungary', 'austria': 'Austria', 'belgium': 'Belgium',
    'portugal': 'Portugal', 'malaysia': 'Malaysia', 'indonesia': 'Indonesia', 'philippines': 'Philippines', 'thailand': 'Thailand'
}

CONTINENT_MAP = {
    'North America': ['United States', 'Canada', 'Mexico'],
    'South America': ['Brazil', 'Argentina', 'Chile', 'Colombia'],
    'Europe': ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Ireland', 'Switzerland', 'Spain', 'Italy', 'Poland', 'Sweden', 'Denmark', 'Norway', 'Finland', 'Romania', 'Hungary', 'Austria', 'Belgium', 'Portugal'],
    'Asia': ['India', 'Singapore', 'Japan', 'South Korea', 'China', 'Hong Kong', 'Taiwan', 'UAE', 'Saudi Arabia', 'Israel', 'Vietnam', 'Malaysia', 'Indonesia', 'Philippines', 'Thailand'],
    'Africa': ['South Africa'],
    'Oceania': ['Australia', 'New Zealand']
}

def resolve_country(loc_str):
    loc_str = str(loc_str).lower().replace('.', '')
    if 'remote' in loc_str and len(loc_str) < 10:
        return 'Remote (Global/Unknown)'
    for k, v in COUNTRY_MAP.items():
        if k in loc_str.split() or k in loc_str.split(','):
            return v
    # Check US states
    words = [w.strip(',') for w in loc_str.upper().split()]
    for state in US_STATES:
        if state in words:
            return 'United States'
    # Fallbacks for common cities
    if 'london' in loc_str: return 'United Kingdom'
    if 'berlin' in loc_str or 'munich' in loc_str: return 'Germany'
    if 'paris' in loc_str: return 'France'
    if 'toronto' in loc_str or 'vancouver' in loc_str: return 'Canada'
    if 'bengaluru' in loc_str or 'bangalore' in loc_str: return 'India'
    if 'sydney' in loc_str or 'melbourne' in loc_str: return 'Australia'
    if 'singapore' in loc_str: return 'Singapore'
    if 'dubai' in loc_str: return 'UAE'
    if 'bogota' in loc_str: return 'Colombia'
    return 'Unknown/Unresolved'

def resolve_continent(country):
    for cont, countries in CONTINENT_MAP.items():
        if country in countries:
            return cont
    return 'Unknown/Unresolved'

continents = Counter()
countries = Counter()
remote_counts = {'Remote': 0, 'Hybrid': 0, 'On-Site': 0, 'Unknown': 0}

for j in jobs:
    loc = j.get('location', '')
    country = resolve_country(loc)
    continent = resolve_continent(country)
    
    countries[country] += 1
    continents[continent] += 1
    
    # Remote vs Hybrid vs On-site
    is_remote = j.get('remote', False)
    if is_remote or 'remote' in loc.lower():
        remote_counts['Remote'] += 1
    elif 'hybrid' in loc.lower():
        remote_counts['Hybrid'] += 1
    elif loc and loc.lower() not in ('unknown', ''):
        remote_counts['On-Site'] += 1
    else:
        remote_counts['Unknown'] += 1

# 4. Category Coverage
category_counts = Counter()
for j in jobs:
    cats = j.get('categories', [])
    for c in cats:
        category_counts[c] += 1

# 6. Source Concentration
source_counts = Counter(j.get('source', 'unknown') for j in jobs)

# 7. Company Concentration
company_counts = Counter(str(j.get('company', 'Unknown')).strip() for j in jobs)

# 8. Geographic x Category Matrix
cat_groups = {
    'Software': ['Software Engineering', 'Backend Development', 'Frontend Development', 'Full-Stack Development', 'Mobile Development', 'Game Development', 'AR/VR'],
    'Data/AI': ['Data Science', 'Data Analytics', 'Data Engineering', 'AI / Machine Learning', 'NLP', 'Computer Vision'],
    'Cybersecurity': ['Cybersecurity'],
    'Cloud/DevOps': ['Cloud Computing', 'DevOps', 'SRE'],
    'Systems/Embedded': ['Systems Engineering', 'Embedded Systems', 'Firmware', 'Networking', 'Database Engineering'],
    'Other': ['QA / Testing', 'Automation', 'Blockchain/Web3', 'Research', 'Technical Product', 'UI/UX for Software']
}

matrix = {cont: {g: 0 for g in cat_groups} for cont in continents}
for j in jobs:
    cont = resolve_continent(resolve_country(j.get('location', '')))
    cats = j.get('categories', [])
    for c in cats:
        for g, g_cats in cat_groups.items():
            if c in g_cats:
                matrix[cont][g] += 1

# 9. Freshness
fresh_bins = {'0-7 days': 0, '8-14 days': 0, '15-21 days': 0, '22-30 days': 0}
for age in ages_days:
    if age <= 7: fresh_bins['0-7 days'] += 1
    elif age <= 14: fresh_bins['8-14 days'] += 1
    elif age <= 21: fresh_bins['15-21 days'] += 1
    else: fresh_bins['22-30 days'] += 1

out = {
    'integrity': integrity_report,
    'continents': dict(continents),
    'countries': dict(countries),
    'remote_counts': remote_counts,
    'category_counts': dict(category_counts),
    'source_counts': dict(source_counts),
    'company_counts': dict(company_counts),
    'matrix': matrix,
    'freshness': fresh_bins,
    'median_age': statistics.median(ages_days) if ages_days else 0,
    'oldest': max(ages_days) if ages_days else 0,
    'newest': min(ages_days) if ages_days else 0
}

with open('gap_analysis.json', 'w') as f:
    json.dump(out, f, indent=2)
