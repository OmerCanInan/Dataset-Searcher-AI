import streamlit as st
import pandas as pd
import numpy as np
from agents.hunter import hunter_agent
from agents.eda import run_light_eda, light_eda_agent
from agents.langgraph import LangGraphManager, init_langgraph_state
from agents.normalizer import normalizer_agent
from agents.final_eda import final_eda_visualizer
from agents.pipeline import process_search_dataset
from agents.aggregator import process_all_search_results
from agents.workflow import ADMARWorkflow

# --- AYARLAR ---
st.set_page_config(page_title="ADMAR | AI Dataset Refinery", layout="wide")

langgraph = init_langgraph_state(st.session_state)

# Initialize top-level agent states
langgraph.update_agent_state('hunter', 'ready')
langgraph.update_agent_state('parser', 'ready')
langgraph.update_agent_state('normalizer', 'ready')
langgraph.update_agent_state('final_eda', 'ready')

# --- UI (STREAMLIT) ---

st.sidebar.title("🤖 ADMAR Kontrol Paneli")
menu = ["Ana Sayfa", "1. Hunter (Avcı)", "2. Parser (Dönüşüm)", "3. Normalizer", "4. Final EDA"]
choice = st.sidebar.radio("Modül Seçin", menu)

with st.sidebar.expander('LangGraph Durumu', expanded=True):
    st.write('### Agent States')
    st.json(langgraph.get_states())
    st.write('### Aktif Dataset')
    st.write(st.session_state.get('current_dataset', 'Henüz seçilmedi'))
    st.write('### Graph Özeti')
    graph = langgraph.get_graph()
    st.write(f"Düğüm: {len(graph['nodes'])}, Kenar: {len(graph['edges'])}")

if choice == "Ana Sayfa":
    st.title("🤖 ADMAR: AI-Driven Dataset Refinery")
    st.markdown("""
    Bu sistem 5 aşamalı otonom bir akışla çalışır:
    1. **Hunter:** İnterneti tarar.
    2. **Parser:** Yapısal olmayanı tabloya çevirir.
    3. **Light-EDA:** Hataları saptar (İçsel süreç).
    4. **Normalizer:** Veriyi standartlaştırır.
    5. **Final EDA:** Analiz raporu sunar.
    """)

elif choice == "1. Hunter (Avcı)":
    st.header("🔍 Dataset Avcısı")
    user_query = st.text_input("Konu:", placeholder="Örn: Global Weather 2024")
    
    if st.button("Avlan"):
        langgraph.update_agent_state('hunter', 'processing')
        
        workflow = ADMARWorkflow()
        clean_df, workflow_status = workflow.run_complete_pipeline(user_query)
        
        if clean_df is not None:
            langgraph.update_agent_state('hunter', 'completed')
            langgraph.update_agent_state('normalizer', 'completed')
            langgraph.update_agent_state('final_eda', 'completed')
            
            st.success("✅ Pipeline başarıyla tamamlandı!")
            
            st.write("### Temizlenmiş Yapısal Veri")
            st.dataframe(clean_df.head(20))
            
            st.write("### Veri İndirme")
            csv = clean_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV olarak indir",
                data=csv,
                file_name="clean_dataset.csv",
                mime="text/csv"
            )
        else:
            langgraph.update_agent_state('hunter', 'failed')
            st.error(f"Pipeline başarısız: {workflow_status.get('error', 'Unknown error')}")


# --- DİĞER MENÜLER (ŞİMDİLİK BOŞ) ---
# --- UI GÜNCELLEME ---

elif choice == "2. Parser (Dönüşüm)":
    st.header("🔄 Veri Dönüşüm Merkezi")
    st.info("Tüm kaynak veriler Hunter çalıştırıldığında otomatik olarak yapısal formata dönüştürülür.")

elif choice == "3. Normalizer":
    st.header("⚖️ Normalizasyon ve İyileştirme")
    st.info("Normalizer arka planda çalışır. Temizleme işlemi Hunter üzerinden başlatıldığında sonuçları görebilirsiniz.")

elif choice == "4. Final EDA":
    st.header("📊 Final EDA")
    if 'final_report' in st.session_state:
        st.write("### Final EDA Özeti")
        st.json(st.session_state['final_report'])
        if 'clean_df' in st.session_state:
            st.write("### Temizlenmiş Veri Önizleme")
            st.dataframe(st.session_state['clean_df'].head(10))
    else:
        st.info("Henüz bir temizleme işlemi yapılmadı. Lütfen Hunter modülünden bir dataset seçin.")