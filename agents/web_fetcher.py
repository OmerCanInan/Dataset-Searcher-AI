import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
import logging
import re

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
    
    def extract_tables(self, html: str) -> List[pd.DataFrame]:
        """Extract all HTML <table> elements as DataFrames."""
        tables = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for table in soup.find_all('table'):
                rows = []
                headers = []
                # Try to get headers from <th>
                header_row = table.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                for tr in table.find_all('tr')[1:]:
                    cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if cells:
                        rows.append(cells)
                
                if rows:
                    if headers and len(headers) == len(rows[0]):
                        df = pd.DataFrame(rows, columns=headers)
                    else:
                        df = pd.DataFrame(rows)
                    if not df.empty:
                        tables.append(df)
        except Exception as e:
            logger.warning(f"Table extraction failed: {e}")
        return tables

    def extract_text(self, html: str) -> str:
        """Extract readable text from HTML — no character limit."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator='\n')
            # Collapse excessive blank lines
            text = re.sub(r'\n{3,}', '\n\n', text).strip()
            return text  # No arbitrary limit
        except Exception as e:
            logger.warning(f"Failed to extract text: {e}")
            return ""

    def extract_structured_data(self, html: str) -> Dict[str, Any]:
        """
        Try to extract the richest possible structure from a page:
        1. If the page has <table> elements, return them as DataFrames.
        2. Otherwise, return full cleaned text for the Parser agent.
        """
        tables = self.extract_tables(html)
        text = self.extract_text(html)
        return {
            'tables': tables,          # List[pd.DataFrame], may be empty
            'text': text,              # Full page text
            'has_tables': len(tables) > 0
        }
    
    def process_url(self, url: str) -> Dict[str, Any]:
        """Fetch and process content from a URL."""
        html = self.fetch_url(url)
        if not html:
            return {
                'url': url,
                'status': 'failed',
                'content': '',
                'tables': [],
                'has_tables': False,
                'content_length': 0
            }
        
        structured = self.extract_structured_data(html)
        return {
            'url': url,
            'status': 'success',
            'content': structured['text'],
            'tables': structured['tables'],
            'has_tables': structured['has_tables'],
            'content_length': len(structured['text'])
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
