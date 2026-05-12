import streamlit as st
import requests
from duckduckgo_search import DDGS
from huggingface_hub import HfApi

SOURCES = {
    "HuggingFace": "https://huggingface.co/datasets",
    "OpenLibrary": "https://openlibrary.org/search.json",
    "RestCountries": "https://restcountries.com/v3.1/name/",
    "DuckDuckGo": "API_NOT_REQUIRED"
}


def hunter_agent(query):
    st.info(f"🕵️‍♂️ Ajanlar {len(SOURCES)} farklı kaynağı tarıyor...")
    all_results = []

    try:
        api = HfApi()
        hf_hits = api.list_datasets(search=query, limit=5)
        for h in hf_hits:
            all_results.append({
                "tip": "Dataset (HF)",
                "baslik": h.id,
                "link": f"https://huggingface.co/datasets/{h.id}",
                "ozet": "Yapay zeka modelleri için hazır veri seti."
            })
    except Exception:
        pass

    try:
        lib_res = requests.get(f"{SOURCES['OpenLibrary']}?q={query}").json()
        for doc in lib_res.get('docs', [])[:3]:
            all_results.append({
                "tip": "Textual (Library)",
                "baslik": doc.get('title'),
                "link": f"https://openlibrary.org{doc.get('key')}",
                "ozet": f"Yazar: {doc.get('author_name', ['Bilinmiyor'])[0]}"
            })
    except Exception:
        pass

    with DDGS() as ddgs:
        web_hits = ddgs.text(f"{query} public data api", max_results=3)
        for w in web_hits:
            all_results.append({
                "tip": "Web/API Documentation",
                "baslik": w['title'],
                "link": w['href'],
                "ozet": w['body']
            })

    return all_results
