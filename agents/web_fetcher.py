import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebContentFetcher:
    """Fetches and processes content from URLs."""
    
    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def fetch_url(self, url: str) -> Optional[str]:
        """Fetch raw HTML content from a URL."""
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:1000]  # Limit to first 1000 chars
        except Exception as e:
            logger.warning(f"Failed to extract text: {e}")
            return ""
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """Fetch and process content from a URL."""
        html = self.fetch_url(url)
        if not html:
            return {
                'url': url,
                'status': 'failed',
                'content': '',
                'content_length': 0
            }
        
        content = self.extract_text(html)
        return {
            'url': url,
            'status': 'success',
            'content': content,
            'content_length': len(content)
        }


def enrich_records_with_content(records: list, fetcher: Optional[WebContentFetcher] = None) -> list:
    """Enrich records with fetched web content."""
    if fetcher is None:
        fetcher = WebContentFetcher()
    
    enriched = []
    for record in records:
        link = record.get('link', '')
        if link and link.startswith('http'):
            fetched_data = fetcher.process_url(link)
            record['fetched_content'] = fetched_data['content']
            record['fetch_status'] = fetched_data['status']
        else:
            record['fetched_content'] = ''
            record['fetch_status'] = 'skipped'
        enriched.append(record)
    
    return enriched
