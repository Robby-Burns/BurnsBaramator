import logging
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class CareerPageValidator:
    """Validates that a job listing exists on the company's official careers page."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def find_careers_url(self, company_name: str, job_url: str) -> Optional[str]:
        """
        Attempt to find the company's official careers page URL.
        """
        # Check cache
        cached_url = self.db.get_cached_careers_url(company_name)
        if cached_url:
            logger.info(f"Using cached careers URL for {company_name}")
            return cached_url
        
        # Strategy 1: Common patterns
        common_patterns = [
            f"https://careers.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com/careers",
            f"https://{company_name.lower().replace(' ', '')}.com/jobs",
            f"https://www.{company_name.lower().replace(' ', '')}.com/careers",
        ]
        
        for pattern in common_patterns:
            if self._validate_url(pattern):
                self.db.cache_company_careers_url(company_name, pattern, True, "Found via pattern matching")
                return pattern
        
        # Strategy 2: Extract domain from job URL and look for careers page
        if job_url:
            domain = self._extract_domain(job_url)
            if domain and "linkedin" not in domain and "indeed" not in domain:
                 careers_url = self._scrape_careers_link_from_domain(domain)
                 if careers_url:
                    self.db.cache_company_careers_url(company_name, careers_url, True, "Found via domain scraping")
                    return careers_url
        
        # Strategy 3: DuckDuckGo Search
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"{company_name} careers page", max_results=1))
                if results:
                    url = results[0]['href']
                    self.db.cache_company_careers_url(company_name, url, True, "Found via search")
                    return url
        except Exception as e:
            logger.warning(f"Search failed for {company_name}: {e}")

        # Cache negative result
        self.db.cache_company_careers_url(company_name, "", False, "Careers URL not found")
        return None
    
    def _extract_domain(self, url: str) -> str:
        """Extract base domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def _validate_url(self, url: str) -> bool:
        """Check if URL is reachable and returns 200."""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False
    
    def _scrape_careers_link_from_domain(self, domain: str) -> Optional[str]:
        """Scrape the main website to find careers link."""
        try:
            url = f"https://{domain}"
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for "Careers" links
            careers_patterns = ['careers', 'jobs', 'join', 'apply', 'work with us']
            for link in soup.find_all('a', href=True):
                link_text = link.get_text().lower()
                link_href = link['href']
                
                if any(pattern in link_text for pattern in careers_patterns):
                    full_url = urljoin(url, link_href)
                    if self._validate_url(full_url):
                        return full_url
            
            return None
        except Exception as e:
            logger.warning(f"Failed to scrape {domain}: {e}")
            return None
    
    def verify_job_on_careers_page(self, job_title: str, company: str, careers_url: str) -> bool:
        """
        Verify that the job listing exists on the company's official careers page.
        """
        if not careers_url:
            logger.warning(f"No careers URL provided for {company}")
            return False
        
        try:
            # Use Playwright for dynamic content (many careers pages are SPAs)
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(careers_url, timeout=30000)
                
                # Wait for content to load
                page.wait_for_load_state("networkidle")
                
                content = page.content().lower()
                browser.close()
            
            # Normalize job title for matching
            normalized_title = job_title.lower().replace(" - ", " ").replace("(", "").replace(")", "")
            key_words = normalized_title.split()[:3]  # Check first 3 words
            
            matches = sum(1 for word in key_words if word in content)
            
            # Heuristic: If significant overlap in title words, assume it's there
            if matches >= 2:
                logger.info(f"✓ Job verified on {company} careers page")
                return True
            else:
                logger.warning(f"✗ Job NOT found on {company} careers page - likely ghost job")
                return False
        
        except Exception as e:
            logger.error(f"Error verifying job on careers page: {e}")
            # Fallback: if we can't verify, we might still want to keep it but flag it
            return False

class Scout:
    """The Scout: Finds and scrapes job listings from multiple sources."""
    
    def __init__(self, db_manager, llm_client, config: Dict):
        self.db = db_manager
        self.llm = llm_client
        self.config = config
        self.validator = CareerPageValidator(db_manager)
        self.keywords = config.get('scout', {}).get('keywords', [])
        self.locations = config.get('scout', {}).get('locations', [])
        
    def search_web(self) -> List[Dict]:
        """
        Broad web search for jobs using DuckDuckGo to find listings outside standard aggregators.
        """
        logger.info("Starting broad web search...")
        found_jobs = []
        
        with DDGS() as ddgs:
            for keyword in self.keywords:
                for location in self.locations:
                    query = f"{keyword} jobs in {location} site:greenhouse.io OR site:lever.co OR site:workday.com"
                    logger.info(f"Searching: {query}")
                    
                    try:
                        results = list(ddgs.text(query, max_results=20))
                        for r in results:
                            found_jobs.append({
                                'title': r['title'],
                                'url': r['href'],
                                'snippet': r['body'],
                                'source': 'web_search'
                            })
                        time.sleep(random.uniform(1, 3)) # Rate limiting
                    except Exception as e:
                        logger.error(f"Search error for {query}: {e}")
                        
        return found_jobs

    def scrape_job_details(self, url: str) -> Dict:
        """
        Scrape full job details from a URL using Playwright.
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                
                # Extract content
                title = page.title()
                content = page.content()
                text_content = page.inner_text("body")
                
                # Basic extraction (LLM can refine this later)
                # We rely on the LLM to parse the unstructured text into structured data
                
                browser.close()
                return {
                    'title': title,
                    'description': text_content,
                    'raw_html': content
                }
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return {}

    def parse_with_llm(self, raw_text: str, url: str) -> Dict:
        """
        Use LLM to extract structured data from raw job text.
        """
        system_prompt = """
        You are a job parser. Extract the following fields from the job description text:
        - company (string)
        - role (string)
        - location (string)
        - job_type (string)
        - description (string - summary)
        - date_posted (string - YYYY-MM-DD if available, else null)
        
        Return ONLY valid JSON.
        """
        
        try:
            # Truncate text to fit context window if needed
            truncated_text = raw_text[:15000] 
            
            structured_data = self.llm.generate_structured(
                system_prompt, 
                f"URL: {url}\n\nTEXT:\n{truncated_text}",
                {} # Schema is implicit in prompt for now, can be explicit
            )
            return structured_data
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return {}

    def run_mission(self):
        """
        Execute the full scouting mission.
        """
        logger.info("Scout mission started.")
        
        # 1. Broad Web Search
        raw_leads = self.search_web()
        logger.info(f"Found {len(raw_leads)} raw leads from web search.")
        
        for lead in raw_leads:
            url = lead['url']
            
            # Skip if already exists
            if self.db.is_duplicate(url):
                logger.info(f"Skipping duplicate: {url}")
                continue
            
            # 2. Scrape Details
            details = self.scrape_job_details(url)
            if not details or not details.get('description'):
                continue
                
            # 3. Parse with LLM
            parsed = self.parse_with_llm(details['description'], url)
            if not parsed or not parsed.get('company') or not parsed.get('role'):
                logger.warning(f"Failed to parse job from {url}")
                continue
                
            company = parsed['company']
            role = parsed['role']
            
            # 4. Verify on Careers Page (Ghost Job Check)
            # Note: For web search results that ARE careers pages (greenhouse/lever), 
            # this check is redundant but harmless.
            careers_url = self.validator.find_careers_url(company, url)
            is_verified = False
            if careers_url:
                 # If the job URL itself IS the careers page (e.g. greenhouse), it's verified by definition
                 if urlparse(url).netloc == urlparse(careers_url).netloc:
                     is_verified = True
                 else:
                    is_verified = self.validator.verify_job_on_careers_page(role, company, careers_url)
            
            # 5. Save to DB
            # We save even if not verified, but mark it. 
            # User preference "HITL" suggests we might want to see them anyway.
            # But spec says "prevent ghost jobs". 
            # Compromise: Save with is_verified flag.
            
            self.db.save_listing(
                url=url,
                company=company,
                role=role,
                description=details['description'], # Save full text
                source=lead['source'],
                location=parsed.get('location'),
                job_type=parsed.get('job_type'),
                date_posted=parsed.get('date_posted'),
                company_careers_url=careers_url,
                careers_page_verified=is_verified
            )
            
        logger.info("Scout mission complete.")
