"""
СОГ ГП-16 | ML Аналитика для прогнозирования температуры газа
Версия 1.1 - Исправлено определение столбцов
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import re
import warnings

warnings.filterwarnings('ignore')

# Путь к файлу с данными (на папку выше)
DATA_FILE = "stats.xlsx"


def clean_column_name(col):
    """Очищает название столбца от переносов строк и лишних пробелов"""
    if isinstance(col, str):
        col = col.replace('\n', ' ')
        col = re.sub(r'\s+', ' ', col).strip()
    return col


@st.cache_data
def load_data():
    """Загрузка данных из Excel файла"""
    try:
        xl = pd.ExcelFile(DATA_FILE)
        sheet_names = xl.sheet_names
        st.info(f"Найдены листы в файле: {', '.join(sheet_names)}")
        sheet_name = sheet_names[0]
        df = pd.read_excel(DATA_FILE, sheet_name=sheet_name)
        df.columns = [clean_column_name(col) for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None


def prepare_data(df):
    """Подготовка данных для ML"""
    df_clean = df.copy()

    possible_names = {
        't_air': ['Температура воздуха 8-00-14-00', 'Температура воздуха'],
        't_gas': ['Температура газа на ГИС', 'Температура газа'],
        'n_tda': ['Кол-во ТДА', 'Количество ТДА'],
        'n_fans': ['Кол-во вент.', 'Количество вентиляторов', 'Вентиляторы'],
        'gas_flow': ['Расход', 'Расход газа'],
        'pressure': ['Рвх СОГ', 'Давление на входе']
    }

    data = {}
    for key, names in possible_names.items():
        for name in names:
            if name in df_clean.columns:
                data[key] = name
                break

    if len(data) != 6:
        st.warning(f"Найдены не все столбцы. Найдено: {list(data.keys())}")
        return None

    ml_df = pd.DataFrame()
    ml_df['t_air'] = pd.to_numeric(df_clean[data['t_air']].astype(str).str.replace(',', '.'), errors='coerce')
    ml_df['t_gas'] = pd.to_numeric(df_clean[data['t_gas']].astype(str).str.replace(',', '.'), errors='coerce')
    ml_df['n_tda'] = pd.to_numeric(df_clean[data['n_tda']], errors='coerce')
    ml_df['n_fans'] = pd.to_numeric(df_clean[data['n_fans']], errors='coerce')
    ml_df['gas_flow'] = pd.to_numeric(df_clean[data['gas_flow']], errors='coerce')
    ml_df['pressure'] = pd.to_numeric(df_clean[data['pressure']], errors='coerce')

    ml_df = ml_df.dropna()
    ml_df = ml_df[
        (ml_df['t_gas'] > -10) & (ml_df['t_gas'] < 20) &
        (ml_df['n_tda'] >= 0) & (ml_df['n_tda'] <= 6) &
        (ml_df['n_fans'] >= 0) & (ml_df['n_fans'] <= 100) &
        (ml_df['gas_flow'] > 0) & (ml_df['gas_flow'] < 5000) &
        (ml_df['pressure'] > 0) & (ml_df['pressure'] < 20)
    ]

    return ml_df


def regression_formula_predict(t_air, gas_flow, n_fans, pressure, n_tda):
    """Регрессионная формула для сравнения"""
    intercept = 3.8
    coef_temp = 0.053
    coef_flow = -0.00048
    coef_fans = -0.0079
    coef_pressure = -0.61
    coef_tda = -0.15

    t_gis = (coef_temp * t_air +
             coef_flow * gas_flow +
             coef_fans * n_fans +
             coef_pressure * pressure +
             intercept +
             coef_tda * n_tda)
    return max(-10, min(15, t_gis))


def main():
    st.markdown("""
    <div class="header">
        <h1>ML Аналитика | СОГ ГП-16</h1>
        <p>Экспериментальная страница для анализа и сравнения моделей прогнозирования температуры газа</p>
    </div>
    """, unsafe_allow_html=True)

    st.info(
        "Эта страница использует методы машинного обучения для анализа данных. Результаты носят исследовательский характер.")

    with st.spinner("Загрузка данных..."):
        df_raw = load_data()

    if df_raw is None:
        st.stop()

    df = prepare_data(df_raw)

    if df is None:
        st.error("Не удалось подготовить данные для анализа")
        st.stop()

    st.success(f"Загружено {len(df)} строк данных после очистки")

    with st.expander("Просмотр загруженных данных"):
        st.dataframe(df.head(10), use_container_width=True)
        st.write("Статистика по данным:")
        st.write(df.describe())

    # ===== ОБУЧЕНИЕ МОДЕЛЕЙ =====
    st.markdown("## Сравнение моделей")

    features = ['t_air', 'n_tda', 'n_fans', 'gas_flow', 'pressure']
    target = 't_gas'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    st.markdown(f"- Обучающая выборка: {len(X_train)} строк")
    st.markdown(f"- Тестовая выборка: {len(X_test)} строк")

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    }

    results = []
    predictions = {}

    for name, model in models.items():
        with st.spinner(f"Обучение {name}..."):
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            predictions[name] = y_pred

            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            results.append({
                "Модель": name,
                "MAE (средняя ошибка)": f"{mae:.2f}°C",
                "RMSE": f"{rmse:.2f}°C",
                "R² (качество)": f"{r2:.3f}"
            })

    # Добавляем регрессионную формулу для сравнения
    y_formula = [regression_formula_predict(
        row['t_air'], row['gas_flow'], row['n_fans'], row['pressure'], row['n_tda']
    ) for _, row in X_test.iterrows()]

    mae_formula = mean_absolute_error(y_test, y_formula)
    rmse_formula = np.sqrt(mean_squared_error(y_test, y_formula))
    r2_formula = r2_score(y_test, y_formula)

    results.append({
        "Модель": "Регрессионная формула",
        "MAE (средняя ошибка)": f"{mae_formula:.2f}°C",
        "RMSE": f"{rmse_formula:.2f}°C",
        "R² (качество)": f"{r2_formula:.3f}"
    })

    results_df = pd.DataFrame(results)
    st.dataframe(results_df, use_container_width=True)

    st.caption("Таблица 1. Сравнение точности моделей прогнозирования температуры газа. MAE - средняя абсолютная ошибка, RMSE - среднеквадратичная ошибка, R² - коэффициент детерминации (чем ближе к 1, тем лучше).")

    # ===== ВИЗУАЛИЗАЦИЯ =====
    st.markdown("## Сравнение прогнозов")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(range(len(y_test))),
        y=y_test,
        mode='markers',
        name='Факт',
        marker=dict(color='blue', size=8)
    ))

    colors = {'Linear Regression': 'green', 'Random Forest': 'orange'}
    for name, y_pred in predictions.items():
        fig.add_trace(go.Scatter(
            x=list(range(len(y_test))),
            y=y_pred,
            mode='markers',
            name=name,
            marker=dict(color=colors.get(name, 'red'), size=6, symbol='x')
        ))

    fig.add_trace(go.Scatter(
        x=list(range(len(y_test))),
        y=y_formula,
        mode='markers',
        name='Регрессионная формула',
        marker=dict(color='purple', size=6, symbol='diamond')
    ))

    fig.update_layout(
        title="Сравнение прогнозов на тестовых данных",
        xaxis_title="Номер наблюдения",
        yaxis_title="Температура газа, °C",
        legend_title="Тип прогноза",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
    st.caption("Рисунок 1. Сопоставление фактических значений температуры газа с прогнозами различных моделей на тестовой выборке.")

    # ===== ВАЖНОСТЬ ПРИЗНАКОВ =====
    st.markdown("## Важность признаков (Random Forest)")

    rf_model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf_model.fit(X, y)

    feature_importance = pd.DataFrame({
        'Признак': ['Температура воздуха', 'Количество ТДА', 'Вентиляторы АВО', 'Расход газа', 'Давление на входе'],
        'Важность': rf_model.feature_importances_
    }).sort_values('Важность', ascending=False)

    fig_imp = px.bar(feature_importance, x='Признак', y='Важность',
                     title="Влияние параметров на температуру газа",
                     color='Важность', color_continuous_scale='Blues')
    fig_imp.update_layout(height=400)
    st.plotly_chart(fig_imp, use_container_width=True)
    st.caption("Рисунок 2. Относительная важность признаков в модели Random Forest. Чем выше значение, тем сильнее параметр влияет на температуру газа.")

    # ===== ПРОГНОЗИРОВАНИЕ =====
    st.markdown("## Прогнозирование температуры газа")
    st.markdown("Введите параметры для прогноза (обучаем модели на всех данных):")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        t_air_input = st.number_input("Температура воздуха, °C", value=-5.0, step=0.5)
    with col2:
        gas_flow_input = st.number_input("Расход газа, тыс.м³/ч", value=1800.0, step=50.0)
    with col3:
        n_fans_input = st.number_input("Вентиляторы АВО, шт", value=25, step=1)
    with col4:
        pressure_input = st.number_input("Давление на входе, МПа", value=5.5, step=0.1)

    col5, col6 = st.columns(2)
    with col5:
        n_tda_input = st.selectbox("Количество ТДА, шт", [0, 1, 2, 3, 4, 5, 6], index=2)
    with col6:
        st.markdown("<br>", unsafe_allow_html=True)
        predict_btn = st.button("Рассчитать прогноз", use_container_width=True)

    if predict_btn:
        input_data = pd.DataFrame([[t_air_input, n_tda_input, n_fans_input, gas_flow_input, pressure_input]],
                                  columns=features)

        st.markdown("### Результаты прогноза")

        results_pred = []
        for name, model in models.items():
            model.fit(X, y)
            pred = model.predict(input_data)[0]
            results_pred.append({"Модель": name, "Прогноз температуры": f"{pred:.1f}°C"})

        formula_pred = regression_formula_predict(
            t_air_input, gas_flow_input, n_fans_input, pressure_input, n_tda_input
        )
        results_pred.append({"Модель": "Регрессионная формула", "Прогноз температуры": f"{formula_pred:.1f}°C"})

        pred_df = pd.DataFrame(results_pred)
        st.dataframe(pred_df, use_container_width=True)

        st.markdown("### Рекомендация")
        if formula_pred > 10:
            st.warning(
                f"Прогнозируется высокая температура ({formula_pred}°C). Рекомендуется включить дополнительные ТДА.")
        elif formula_pred < 5:
            st.info(f"Прогнозируется низкая температура ({formula_pred}°C). Можно рассмотреть отключение части ТДА.")
        else:
            st.success(f"Прогнозируемая температура ({formula_pred}°C) в допустимом диапазоне.")

    # ===== ВЫВОДЫ =====
    st.markdown("---")
    st.markdown("""
    <div class="footer">
        ML Аналитика | Экспериментальная страница<br>
        Данные загружены из файла stats.xlsx<br>
        Для повседневного использования рекомендуется основная страница с регрессионной моделью.
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
    <style>
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
            padding: 1rem 1.5rem;
            border-radius: 4px;
            margin-bottom: 1.5rem;
            border-left: 4px solid #3182ce;
        }
        .header h1 {
            color: white;
            margin: 0;
            font-size: 1.3rem;
            font-weight: 600;
        }
        .header p {
            color: #a0c4e8;
            margin: 0.3rem 0 0 0;
            font-size: 0.85rem;
        }
        .footer {
            text-align: center;
            color: #718096;
            font-size: 0.7rem;
            padding: 1.5rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }
        .stButton > button {
            background: #2c5282;
            color: white;
            font-weight: 600;
            border-radius: 4px;
        }
        .stAlert {
            background-color: #f0f4f8 !important;
        }
    </style>
""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()