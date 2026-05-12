import streamlit as st


def light_eda_agent(df):
    """Light-EDA Agent: Normalizasyon öncesi ilk röntgeni çeker."""
    report = {
        "sutunlar": list(df.columns),
        "tipler": df.dtypes.to_dict(),
        "eksik_veriler": df.isnull().sum().to_dict(),
        "satir_sayisi": len(df)
    }
    return report


def run_light_eda(df, display=True):
    """Verinin teknik analizini yapar ve düzeltme reçetesi hazırlar."""
    df_analysis = df.drop(columns=[col for col in df.columns if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, dict)).any()], errors='ignore')
    
    report = {
        "missing_values": df_analysis.isnull().sum().to_dict(),
        "column_types": df_analysis.dtypes.to_dict(),
        "duplicates": int(df_analysis.duplicated().sum())
    }

    if not display:
        return report

    st.subheader("🔍 Ajan Analizi: Light-EDA")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Sütun Tipleri:**")
        st.write(df_analysis.dtypes)
    with col2:
        st.write("**Eksik Veri Sayısı:**")
        st.write(df_analysis.isnull().sum())

    return report
