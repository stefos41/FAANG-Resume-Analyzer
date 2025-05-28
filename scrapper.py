import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict
import os

# Constants
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
JOB_CACHE_FILE = "data/job_cache.json"


def scrape_amazon_jobs(query: str = "SDE intern") -> List[Dict]:
    """Scrape Amazon Jobs API (public)"""
    url = "https://www.amazon.jobs/en/search.json"
    params = {"keywords": query, "offset": 0, "count": 10}
    
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return [{
            "company": "Amazon",
            "title": job["title"],
            "text": job["description"],
            "url": f"https://www.amazon.jobs{job['job_path']}",
            "location": job["location"]
        } for job in response.json().get("jobs", [])]
    except Exception as e:
        print(f"Amazon scrape failed: {e}")
        return []



def load_cached_jobs() -> List[Dict]:
    """Load jobs from cache if recent"""
    if os.path.exists(JOB_CACHE_FILE):
        modified_time = os.path.getmtime(JOB_CACHE_FILE)
        if (time.time() - modified_time) < 3600:  # 1 hour cache
            with open(JOB_CACHE_FILE, "r") as f:
                return json.load(f)
    return None

def scrape_faang_jobs(use_cache: bool = True) -> List[Dict]:
    """Main scraping function with cache support"""
    if use_cache:
        cached_jobs = load_cached_jobs()
        if cached_jobs:
            return cached_jobs
    
    # Scrape all sources (with rate limiting)
    jobs = []
    jobs.extend(scrape_amazon_jobs())

    
    # Cache results
    os.makedirs(os.path.dirname(JOB_CACHE_FILE), exist_ok=True)
    with open(JOB_CACHE_FILE, "w") as f:
        json.dump(jobs, f)
    
    return jobs

# Quick test
if __name__ == "__main__":
    jobs = scrape_faang_jobs()
    print(f"Scraped {len(jobs)} jobs. Example:")
    print(json.dumps(jobs, indent=2)) 