"""
СОГ ГП-16 - Система поддержки принятия решений для управления ТДА
Версия 2.0 - С навигацией в боковой панели (Drawer)
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="СОГ ГП-16 | Управление ТДА",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Навигация")
    st.markdown("---")

    page = st.radio(
        "Выберите раздел",
        ["Регрессионная модель (основная)", "ML Аналитика (экспериментальная)"],
        index=0
    )

    st.markdown("---")
    st.markdown("**О системе:**")
    st.markdown("- Регрессионная модель — для повседневного использования")
    st.markdown("- ML Аналитика — для исследования и сравнения точности")
    st.markdown("- Версия 2.0")
    st.markdown("---")

    from datetime import datetime
    st.markdown(f"{datetime.now().strftime('%d.%m.%Y')}")

    st.markdown("---")
    st.markdown("Совет: Нажмите на стрелку в левом верхнем углу, чтобы свернуть панель")

if page == "Регрессионная модель (основная)":
    from sog_system_main import main as main_regression
    main_regression()
else:
    from ml_analytics import main as main_ml
    main_ml()