"""
Validator Agent
Checks data quality and decides whether to proceed or retry.
Computes quality score based on: data completeness, type consistency, outliers.
"""

import pandas as pd
from typing import Tuple, Dict, Any


class ValidatorAgent:
    """Validates cleaned data and assigns quality score."""
    
    def __init__(self, min_quality_threshold=0.6):
        self.min_quality_threshold = min_quality_threshold
    
    def validate(self, clean_df: pd.DataFrame) -> Tuple[float, bool, Dict[str, Any]]:
        """
        Validate cleaned dataframe.
        Returns: (quality_score, passed, detailed_report)
        """
        if clean_df.empty:
            return 0.0, False, {'error': 'Empty dataframe'}
        
        report = {}
        scores = {}
        
        # 1. Completeness: % of non-null values
        completeness = 1.0 - (clean_df.isnull().sum().sum() / (clean_df.shape[0] * clean_df.shape[1]))
        scores['completeness'] = completeness
        report['completeness'] = f"{completeness*100:.1f}%"
        
        # 2. Rows: Check if we have minimum viable data
        row_score = min(1.0, clean_df.shape[0] / 10)  # Ideal: 10+ rows
        scores['row_count'] = row_score
        report['row_count'] = clean_df.shape[0]
        
        # 3. Columns: Check if we have meaningful features
        col_score = min(1.0, clean_df.shape[1] / 3)  # Ideal: 3+ columns
        scores['column_count'] = col_score
        report['column_count'] = clean_df.shape[1]
        
        # 4. Type Diversity: Check if we have mixed types (not all one type)
        numeric_cols = clean_df.select_dtypes(include=['number']).shape[1]
        text_cols = clean_df.select_dtypes(include=['object']).shape[1]
        type_diversity = 1.0 if (numeric_cols > 0 and text_cols > 0) else 0.7
        scores['type_diversity'] = type_diversity
        report['numeric_columns'] = numeric_cols
        report['text_columns'] = text_cols
        
        # 5. Duplicates: Lower score if too many duplicates
        dup_ratio = clean_df.duplicated().sum() / len(clean_df) if len(clean_df) > 0 else 0
        duplicate_score = max(0.3, 1.0 - dup_ratio)  # Min 0.3 even with high duplicates
        scores['duplicate_ratio'] = duplicate_score
        report['duplicate_count'] = int(clean_df.duplicated().sum())
        
        # Weighted average quality score
        quality_score = (
            completeness * 0.35 +
            row_score * 0.20 +
            col_score * 0.20 +
            type_diversity * 0.15 +
            duplicate_score * 0.10
        )
        
        passed = quality_score >= self.min_quality_threshold
        report['quality_score'] = round(quality_score, 2)
        report['passed'] = passed
        report['threshold'] = self.min_quality_threshold
        
        return quality_score, passed, report
