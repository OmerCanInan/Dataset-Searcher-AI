import streamlit as st
import pandas as pd
from .collector import DataCollector, convert_hunter_results_to_structured
from .web_fetcher import enrich_records_with_content, WebContentFetcher
from .eda import run_light_eda
from .normalizer import normalizer_agent
from .final_eda import final_eda_report


def process_all_search_results(hunter_results):
    """Process all Hunter search results, fetch content from URLs, and aggregate into structured data."""
    collector = DataCollector()
    
    structured_data = convert_hunter_results_to_structured(hunter_results)
    
    st.write("🌐 Linklerden içerik alınıyor...")
    progress_bar = st.progress(0)
    
    fetcher = WebContentFetcher(timeout=5)
    enriched_data = []
    
    for idx, record in enumerate(structured_data):
        enriched_record = dict(record)  # Copy original record
        link = record.get('link', '')
        
        if link and link.startswith('http'):
            try:
                fetched_data = fetcher.process_url(link)
                enriched_record['content'] = fetched_data['content']
                enriched_record['fetch_status'] = fetched_data['status']
            except Exception as e:
                enriched_record['content'] = ''
                enriched_record['fetch_status'] = 'error'
        else:
            enriched_record['content'] = record.get('description', '')
            enriched_record['fetch_status'] = 'local'
        
        enriched_data.append(enriched_record)
        progress_bar.progress((idx + 1) / len(structured_data))
    
    collector.add_batch(enriched_data)
    aggregated_df = collector.get_dataframe()
    
    if aggregated_df.empty:
        return None, None, None
    
    st.session_state['raw_df'] = aggregated_df
    report = run_light_eda(aggregated_df, display=False)
    clean_df = normalizer_agent(aggregated_df, report, display=False)
    st.session_state['clean_df'] = clean_df
    final_report = final_eda_report(clean_df)
    st.session_state['final_report'] = final_report
    
    return clean_df, final_report, collector.get_stats()
