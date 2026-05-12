import streamlit as st
import pandas as pd


def normalizer_agent(df, eda_report, display=True):
    """EDA raporuna göre veriyi standartlaştırır."""
    df_clean = df.copy()

    if display:
        st.subheader("⚖️ Ajan İşlemi: Normalizer")

    for col in df_clean.columns:
        if df_clean[col].isnull().any():
            if df_clean[col].dtype in ['int64', 'float64']:
                df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                if display:
                    st.write(f"✅ {col}: Boş değerler ortalama ile dolduruldu.")
            else:
                df_clean[col] = df_clean[col].fillna("Bilinmiyor")
                if display:
                    st.write(f"✅ {col}: Boş değerler 'Bilinmiyor' ile dolduruldu.")

    for col, dtype in eda_report['column_types'].items():
        if dtype == 'object':
            converted = pd.to_numeric(df_clean[col], errors='coerce')
            if not converted.isnull().all():
                df_clean[col] = converted
                if display:
                    st.write(f"⚙️ {col}: Metinden sayısal formata dönüştürüldü.")

    return df_clean
