import streamlit as st
from datasets import load_dataset
from .eda import run_light_eda
from .normalizer import normalizer_agent
from .final_eda import final_eda_report


def process_search_dataset(dataset_id):
    """Load a HuggingFace dataset, run EDA + normalization in the background, and return cleaned output."""
    with st.spinner(f"Dataset '{dataset_id}' yükleniyor ve işleniyor..."):
        dataset = load_dataset(dataset_id)
        if 'train' in dataset:
            df = dataset['train'].to_pandas()
        elif len(dataset) > 0:
            df = list(dataset.values())[0].to_pandas()
        else:
            raise ValueError('Dataset içinde kullanılabilir bir split bulunamadı.')

        st.session_state['raw_df'] = df
        report = run_light_eda(df, display=False)
        clean_df = normalizer_agent(df, report, display=False)
        st.session_state['clean_df'] = clean_df
        final_report = final_eda_report(clean_df)
        st.session_state['final_report'] = final_report

    return clean_df, final_report
