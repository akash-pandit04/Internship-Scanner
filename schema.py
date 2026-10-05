from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

@dataclass
class JobRecord:
    id: str
    title: str
    company: str
    location: str
    remote: bool
    employment_type: str
    description: str
    url: str
    source: str
    posted_at: Optional[datetime]
    fetched_at: datetime
    categories: List[str]
    skills: List[str]
    score: int
    job_type: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "remote": self.remote,
            "employment_type": self.employment_type,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "categories": self.categories,
            "score": self.score,
            "job_type": getattr(self, "job_type", "internship")
        }

def validate_job_schema(job: Dict[str, Any]) -> bool:
    required_keys = [
        'title', 'company', 'location', 'remote', 
        'url', 'source', 'posted_at'
    ]
    for k in required_keys:
        if k not in job:
            return False
            
    if 'posted_at' in job and job.get('posted_at') is not None:
        if not isinstance(job.get('posted_at'), datetime):
            return False
        
    url = job.get('url', '')
    parsed = urlparse(url)
    if not (parsed.scheme in ('http', 'https') and parsed.netloc):
        return False
        
    fake_domains = {'example.com', 'test.com', 'demo.com', 'placeholder.com'}
    if any(fake in parsed.netloc for fake in fake_domains):
        return False
        
    return True
