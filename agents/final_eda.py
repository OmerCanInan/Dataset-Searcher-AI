import streamlit as st
import numpy as np


def final_eda_report(df):
    """Final EDA raporunu dönderir, UI olmadan da kullanılabilir."""
    report = {
        'num_rows': int(df.shape[0]),
        'num_columns': int(df.shape[1]),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'missing_values': int(df.isnull().sum().sum()),
        'duplicates': int(df.duplicated().sum())
    }
    return report


def final_eda_visualizer(df):
    """Kullanıcıya sunulacak final raporu."""
    st.header("📊 Final Analiz Raporu")

    import plotly.express as px

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if numeric_cols:
        st.write("### Sayısal Dağılımlar")
        selected_col = st.selectbox("Görselleştirmek için sütun seçin:", numeric_cols)
        fig = px.histogram(df, x=selected_col, title=f"{selected_col} Dağılım Grafiği")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Görselleştirilecek sayısal veri bulunamadı.")

    st.write("### Temizlenmiş Veri Önizleme")
    st.dataframe(df)
