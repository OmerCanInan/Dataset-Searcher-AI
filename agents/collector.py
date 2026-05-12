import pandas as pd
from typing import List, Dict, Any


class DataCollector:
    """Collects and aggregates structured data from all sources."""
    
    def __init__(self):
        self.data = []
        self.source_stats = {}
    
    def add_record(self, record: Dict[str, Any]):
        """Add a structured record to the collection."""
        if isinstance(record, dict):
            self.data.append(record)
    
    def add_batch(self, records: List[Dict[str, Any]]):
        """Add multiple records at once."""
        for record in records:
            self.add_record(record)
    
    def get_dataframe(self) -> pd.DataFrame:
        """Convert collected data to pandas DataFrame."""
        if not self.data:
            return pd.DataFrame()
        return pd.DataFrame(self.data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            'total_records': len(self.data),
            'sources': list(set([r.get('source', 'unknown') for r in self.data]))
        }
    
    def clear(self):
        """Clear the collection."""
        self.data = []
        self.source_stats = {}


def convert_hunter_results_to_structured(hunter_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert raw Hunter results to uniform structured format."""
    structured_data = []
    
    for result in hunter_results:
        structured_record = {
            'source': result.get('tip', 'unknown'),
            'title': result.get('baslik', ''),
            'link': result.get('link', ''),
            'description': result.get('ozet', ''),
            'type': result.get('tip', '').lower(),
            'timestamp': str(pd.Timestamp.now())
        }
        structured_data.append(structured_record)
    
    return structured_data
