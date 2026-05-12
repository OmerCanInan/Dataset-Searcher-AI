"""
Parser Agent
Converts unstructured data (HTML/PDF text) to structured tabular format.
Uses LLM-based extraction or fallback pattern matching.
"""

import json
import pandas as pd
from typing import Optional, Dict, Any
import re


class ParserAgent:
    """Converts unstructured text to structured DataFrame."""
    
    def __init__(self, use_llm=False):
        self.use_llm = use_llm
    
    def parse_text_to_records(self, text: str) -> list:
        """
        Extract structured records from unstructured text.
        Fallback: Pattern matching for common data formats.
        Advanced: Call Ollama LLM for semantic extraction.
        """
        if self.use_llm:
            return self._parse_with_llm(text)
        else:
            return self._parse_with_patterns(text)
    
    def _parse_with_patterns(self, text: str) -> list:
        """
        Fallback: Pattern-based extraction.
        Looks for: tables, key-value pairs, CSV-like lines.
        """
        records = []
        
        # Try to find table-like patterns (lines with consistent delimiters)
        lines = text.split('\n')
        potential_records = []
        
        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue
            
            # Look for delimiter-separated values
            if any(delim in line for delim in ['|', '\t', '  ', ',']):
                # Split by most likely delimiter
                if '|' in line:
                    parts = [p.strip() for p in line.split('|')]
                elif '\t' in line:
                    parts = [p.strip() for p in line.split('\t')]
                elif ',' in line:
                    parts = [p.strip() for p in line.split(',')]
                else:
                    parts = [p.strip() for p in re.split(r'\s{2,}', line)]
                
                if len(parts) >= 2:
                    potential_records.append(parts)
        
        # If we found records, try to create a structured format
        if potential_records:
            # Use first row as headers if it looks like headers
            headers = [f'column_{i}' for i in range(len(potential_records[0]))]
            
            for record_list in potential_records:
                record = {}
                for i, value in enumerate(record_list):
                    key = headers[i] if i < len(headers) else f'column_{i}'
                    record[key] = value
                records.append(record)
        
        # Fallback: treat entire text as a single record
        if not records:
            records.append({
                'raw_text': text[:500],
                'text_length': len(text),
                'extracted_date': self._extract_date(text),
                'extracted_numbers': self._extract_numbers(text)
            })
        
        return records
    
    def _parse_with_llm(self, text: str) -> list:
        """
        Advanced: Use Ollama to semantically extract structure.
        TODO: Implement when Ollama is available.
        """
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
        return numbers[:10]  # Limit to first 10
    
    def create_dataframe(self, text: str) -> pd.DataFrame:
        """Main entry point: Convert text to DataFrame."""
        records = self.parse_text_to_records(text)
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        return df
