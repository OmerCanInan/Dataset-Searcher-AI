"""
Parser Agent
Converts unstructured data (HTML/PDF text) to structured tabular format.
Uses HTML table extraction first, then LLM-based extraction or fallback pattern matching.
"""

import json
import pandas as pd
from typing import Optional, Dict, Any, List
import re


class ParserAgent:
    """Converts unstructured text to structured DataFrame."""
    
    def __init__(self, use_llm=False):
        self.use_llm = use_llm
    
    def parse_from_fetched(self, fetched_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Main entry point when given a full fetched_data dict from WebContentFetcher.
        Priority:
          1. If HTML tables were found, use the largest one.
          2. Otherwise fall back to text parsing.
        """
        tables = fetched_data.get('tables', [])
        if tables:
            # Pick the largest table by cell count
            best = max(tables, key=lambda df: df.shape[0] * df.shape[1])
            return best
        
        text = fetched_data.get('content', '')
        return self.create_dataframe(text)

    def parse_text_to_records(self, text: str) -> list:
        """
        Extract structured records from unstructured text.
        Tries CSV/TSV/pipe-delimited lines first, then key-value pairs, then raw fallback.
        """
        if self.use_llm:
            return self._parse_with_llm(text)
        return self._parse_with_patterns(text)
    
    def _parse_with_patterns(self, text: str) -> list:
        """
        Pattern-based extraction.
        Pass 1: consistent delimiter lines (CSV/TSV/pipe).
        Pass 2: key: value pairs.
        Pass 3: raw fallback.
        """
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # --- Pass 1: delimited table lines ---
        delimited = self._try_delimited_table(lines)
        if delimited:
            return delimited
        
        # --- Pass 2: key-value pairs ---
        kv_records = self._try_key_value(lines)
        if kv_records:
            return kv_records
        
        # --- Pass 3: raw fallback ---
        return [{
            'raw_text': text[:2000],
            'text_length': len(text),
            'extracted_date': self._extract_date(text),
            'extracted_numbers': str(self._extract_numbers(text))
        }]

    def _try_delimited_table(self, lines: List[str]) -> list:
        """Detect delimiter and parse all matching lines into records."""
        # Count delimiter frequencies across lines
        delimiters = ['|', '\t', ',', ';']
        best_delim = None
        best_count = 0

        for delim in delimiters:
            counts = [line.count(delim) for line in lines if line.count(delim) > 0]
            if counts:
                # Prefer delimiter that appears consistently
                from statistics import median
                med = median(counts)
                consistent = sum(1 for c in counts if abs(c - med) <= 1)
                if consistent > best_count and med >= 1:
                    best_count = consistent
                    best_delim = delim

        if not best_delim or best_count < 2:
            return []

        # Split all lines by this delimiter
        table_lines = [
            [cell.strip() for cell in line.split(best_delim)]
            for line in lines
            if line.count(best_delim) >= 1
        ]

        if not table_lines:
            return []

        # Use first row as header if it looks non-numeric
        first = table_lines[0]
        if all(not cell.replace('.', '').replace('-', '').isdigit() for cell in first if cell):
            headers = [cell if cell else f'col_{i}' for i, cell in enumerate(first)]
            data_rows = table_lines[1:]
        else:
            headers = [f'col_{i}' for i in range(len(first))]
            data_rows = table_lines

        records = []
        for row in data_rows:
            if len(row) < 2:
                continue
            record = {}
            for i, val in enumerate(row):
                key = headers[i] if i < len(headers) else f'col_{i}'
                record[key] = val
            records.append(record)

        return records

    def _try_key_value(self, lines: List[str]) -> list:
        """Parse lines like 'Key: Value' or 'Key = Value' into a single record dict."""
        kv_pattern = re.compile(r'^(.+?)[\s]*[:\=][\s]*(.+)$')
        record = {}
        for line in lines:
            m = kv_pattern.match(line)
            if m:
                record[m.group(1).strip()] = m.group(2).strip()
        return [record] if len(record) >= 2 else []

    def _parse_with_llm(self, text: str) -> list:
        """Advanced: Use Ollama to semantically extract structure."""
        # Placeholder for LLM integration
        return self._parse_with_patterns(text)
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract first date-like pattern from text."""
        date_pattern = r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}'
        match = re.search(date_pattern, text)
        return match.group(0) if match else None
    
    def _extract_numbers(self, text: str) -> list:
        """Extract all numbers from text."""
        numbers = re.findall(r'-?\d+\.?\d*', text)
        return numbers[:20]
    
    def create_dataframe(self, text: str) -> pd.DataFrame:
        """Convert text to DataFrame using pattern extraction."""
        records = self.parse_text_to_records(text)
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)

