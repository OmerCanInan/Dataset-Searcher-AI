"""
Workflow Orchestrator
Implements the complete ADMAR pipeline with A2A protocol handoffs.
Sequence: Hunter -> Parser -> Light-EDA -> Normalizer -> Validator -> Final-EDA
"""

import streamlit as st
import pandas as pd
import json
from typing import Tuple, Dict, Any, Optional

from .orchestrator import OrchestratorManager, ADMARState
from .hunter import hunter_agent
from .parser import ParserAgent
from .eda import run_light_eda
from .normalizer import normalizer_agent
from .validator import ValidatorAgent
from .final_eda import final_eda_report
from .web_fetcher import WebContentFetcher
from .collector import DataCollector, convert_hunter_results_to_structured


class ADMARWorkflow:
    """
    Main workflow orchestrator implementing the complete ADMAR pipeline.
    Manages state transitions and agent handoffs via A2A protocol.
    """
    
    def __init__(self):
        self.orchestrator = OrchestratorManager()
        self.parser = ParserAgent(use_llm=False)
        self.validator = ValidatorAgent(min_quality_threshold=0.6)
    
    def run_complete_pipeline(self, user_query: str) -> Tuple[Optional[pd.DataFrame], Dict[str, Any]]:
        """
        Run the complete ADMAR pipeline from prompt to final analysis.
        
        Flow:
        1. Hunter: Search for data
        2. Parser: Convert unstructured -> structured
        3. Light-EDA: Analyze and generate recipe
        4. Normalizer: Apply standardization
        5. Validator: Check quality
        6. Final-EDA: Generate analysis
        """
        
        self.orchestrator.set_user_prompt(user_query)
        
        # --- STAGE 1: HUNTER (Search & Fetch) ---
        st.write("🔍 **Stage 1: Searching for data...**")
        try:
            hunter_results = hunter_agent(user_query)
            if not hunter_results:
                self.orchestrator.set_error("No data found")
                return None, self.orchestrator.get_workflow_status()
            
            # Convert and enrich with fetched content
            structured_data = convert_hunter_results_to_structured(hunter_results)
            st.write(f"✅ Found {len(structured_data)} sources")
            self.orchestrator.hunter_complete(
                urls=[r.get('link', '') for r in structured_data],
                raw_data=json.dumps(structured_data)
            )
        except Exception as e:
            self.orchestrator.set_error(f"Hunter failed: {str(e)}")
            st.error(f"Hunter error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        # --- STAGE 2: PARSER (Unstructured -> Structured) ---
        st.write("📝 **Stage 2: Converting to structured format...**")
        try:
            collector = DataCollector()
            collector.add_batch(structured_data)
            raw_df = collector.get_dataframe()
            
            if raw_df.empty:
                self.orchestrator.set_error("Parser produced empty dataframe")
                return None, self.orchestrator.get_workflow_status()
            
            st.write(f"✅ Created dataframe: {raw_df.shape[0]} rows × {raw_df.shape[1]} columns")
            self.orchestrator.parser_complete(raw_df.to_json())
        except Exception as e:
            self.orchestrator.set_error(f"Parser failed: {str(e)}")
            st.error(f"Parser error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        # --- STAGE 3: LIGHT-EDA (Discovery & Recipe) ---
        st.write("🔬 **Stage 3: Analyzing data structure (Light-EDA)...**")
        try:
            eda_report = run_light_eda(raw_df, display=False)
            normalization_recipe = {
                'missing_value_strategy': 'mean_or_mode',
                'column_types': eda_report.get('column_types', {}),
                'duplicates': eda_report.get('duplicates', 0)
            }
            st.write(f"✅ Analysis complete: {eda_report.get('duplicates', 0)} duplicates found")
            self.orchestrator.eda_discovery_complete(eda_report, normalization_recipe)
        except Exception as e:
            self.orchestrator.set_error(f"Light-EDA failed: {str(e)}")
            st.error(f"Light-EDA error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        # --- STAGE 4: NORMALIZER (Standardize) ---
        st.write("⚖️ **Stage 4: Normalizing data...**")
        try:
            clean_df = normalizer_agent(raw_df, eda_report, display=False)
            st.write(f"✅ Normalization complete")
            self.orchestrator.normalizer_complete(clean_df.to_json())
        except Exception as e:
            self.orchestrator.set_error(f"Normalizer failed: {str(e)}")
            st.error(f"Normalizer error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        # --- STAGE 5: VALIDATOR (Quality Check) ---
        st.write("✓ **Stage 5: Validating quality...**")
        try:
            quality_score, passed, validation_report = self.validator.validate(clean_df)
            st.json(validation_report)
            
            self.orchestrator.validator_complete(quality_score, passed)
            
            if not passed:
                if self.orchestrator.state['retry_count'] < self.orchestrator.state['max_retries']:
                    st.warning(f"Quality too low ({quality_score:.2f}), retrying search...")
                    return self.run_complete_pipeline(user_query)
                else:
                    st.error("Max retries exceeded")
                    return None, self.orchestrator.get_workflow_status()
        except Exception as e:
            self.orchestrator.set_error(f"Validator failed: {str(e)}")
            st.error(f"Validator error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        # --- STAGE 6: FINAL-EDA (Analysis & Visualization) ---
        st.write("📊 **Stage 6: Final analysis...**")
        try:
            final_report = final_eda_report(clean_df)
            self.orchestrator.final_eda_complete(final_report, [])
            st.json(final_report)
            st.write("✅ Pipeline complete!")
        except Exception as e:
            self.orchestrator.set_error(f"Final-EDA failed: {str(e)}")
            st.error(f"Final-EDA error: {e}")
            return None, self.orchestrator.get_workflow_status()
        
        return clean_df, self.orchestrator.get_workflow_status()
