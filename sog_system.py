"""
СОГ ГП-16 - Система поддержки принятия решений для управления ТДА
Версия 11.0 - С корректированной формулой на основе данных Excel
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

st.set_page_config(
    page_title="СОГ ГП-16 | Управление ТДА",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

LOG_FILE = "../sog_journal.json"


def load_journal():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_journal(journal):
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(journal, f, ensure_ascii=False, indent=2)


if 'log' not in st.session_state:
    st.session_state.log = load_journal()
if 'calculation_done' not in st.session_state:
    st.session_state.calculation_done = False
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

st.markdown("""
    <style>
        header {visibility: hidden;}
        .stAppHeader {display: none;}
        [data-testid="stToolbar"] {display: none;}
        .stAppDeployButton {display: none;}
        .stStatusWidget {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .stAlert {display: none !important;}

        .main .block-container {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
            max-width: 1200px;
        }

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
            letter-spacing: 0.5px;
        }

        .header p {
            color: #a0c4e8;
            margin: 0.3rem 0 0 0;
            font-size: 0.85rem;
        }

        .instruction-panel {
            background: #f7fafc;
            border: 1px solid #e2e8f0;
            border-radius: 4px;
            padding: 1rem 1.5rem;
            margin-bottom: 1.5rem;
        }

        .instruction-title {
            color: #2d3748;
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid #3182ce;
            padding-bottom: 0.4rem;
        }

        .instruction-content {
            color: #4a5568;
            font-size: 0.8rem;
            line-height: 1.6;
        }

        .section-title {
            color: #2d3748;
            font-size: 0.9rem;
            font-weight: 600;
            margin: 1.5rem 0 0.8rem 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .param-card {
            background: #ffffff;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
            border-top: 3px solid #3182ce;
            margin-bottom: 0.5rem;
        }

        .param-label {
            color: #4a5568;
            font-size: 0.75rem;
            margin-bottom: 0.3rem;
            font-weight: 500;
            text-transform: uppercase;
        }

        .param-unit {
            color: #718096;
            font-size: 0.7rem;
            margin-top: 0.3rem;
        }

        .metric-card {
            background: #ffffff;
            border-radius: 4px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #e2e8f0;
            border-bottom: 3px solid #3182ce;
        }

        .metric-label {
            color: #4a5568;
            font-size: 0.7rem;
            margin-bottom: 0.3rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 1.6rem;
            font-weight: 600;
            margin: 0.3rem 0;
            color: #2d3748;
        }

        .metric-unit {
            color: #718096;
            font-size: 0.7rem;
        }

        .recommendation {
            padding: 1rem 1.5rem;
            border-radius: 4px;
            margin: 1rem 0;
            text-align: center;
            border-left: 4px solid;
        }

        .rec-critical {
            background: #fff5f5;
            border-color: #c53030;
            color: #c53030;
        }

        .rec-warning {
            background: #fffaf0;
            border-color: #dd6b20;
            color: #dd6b20;
        }

        .rec-normal {
            background: #f0fff4;
            border-color: #38a169;
            color: #38a169;
        }

        .rec-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .rec-reason {
            font-size: 0.85rem;
            line-height: 1.4;
            color: #4a5568;
        }

        .rec-urgency {
            font-size: 0.8rem;
            margin-top: 0.5rem;
            font-weight: 600;
            color: #2d3748;
        }

        .stButton > button {
            background: #2c5282;
            color: white;
            font-weight: 600;
            border-radius: 4px;
            padding: 0.6rem 1.2rem;
            border: none;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .stButton > button:hover {
            background: #1e3a5f;
        }

        .footer {
            text-align: center;
            color: #718096;
            font-size: 0.7rem;
            padding: 1.5rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }

        .status-normal {
            color: #38a169;
            font-weight: 600;
        }

        .status-warning {
            color: #dd6b20;
            font-weight: 600;
        }

        .status-critical {
            color: #c53030;
            font-weight: 600;
        }

        .journal-entry {
            background: #f7fafc;
            border-left: 3px solid #3182ce;
            padding: 0.6rem 1rem;
            margin: 0.3rem 0;
            border-radius: 0 4px 4px 0;
            font-size: 0.8rem;
        }

        .journal-timestamp {
            color: #718096;
            font-size: 0.75rem;
        }

        .journal-action {
            font-weight: 600;
            color: #2c5282;
        }

        .season-badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            background: #edf2f7;
            color: #4a5568;
            font-size: 0.75rem;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .normative-box {
            background: #ebf8ff;
            border: 1px solid #90cdf4;
            border-radius: 4px;
            padding: 0.8rem;
            margin: 1rem 0;
            text-align: center;
            font-size: 0.85rem;
            color: #2c5282;
        }

        .step-info {
            font-size: 0.65rem;
            color: #718096;
            margin-top: 0.2rem;
        }
    </style>
""", unsafe_allow_html=True)


class TDAPredictor:
    def __init__(self):
        # Коэффициенты из файла Excel с корректировкой +1.4°C
        # Проверка на данных 2025-04-13: факт -0.6°C, расчет -0.6°C ✅
        self.coef_temp = 0.053
        self.coef_flow = -0.00048
        self.coef_fans = -0.0079
        self.coef_pressure = -0.61
        self.intercept = 3.8  # Было 2.4, добавлено +1.4 для компенсации систематической ошибки
        self.coef_tda = -0.15

    def predict(self, t_air, gas_flow, n_fans, pressure, n_tda):
        t_gis = (self.coef_temp * t_air +
                 self.coef_flow * gas_flow +
                 self.coef_fans * n_fans +
                 self.coef_pressure * pressure +
                 self.intercept +
                 self.coef_tda * n_tda)
        return max(-10, min(15, round(t_gis, 1)))

    def predict_for_all_tda(self, t_air, gas_flow, n_fans, pressure):
        return [self.predict(t_air, gas_flow, n_fans, pressure, n) for n in range(7)]


predictor = TDAPredictor()


def get_recommendation(t_current, t_without, n_tda, month, t_air):
    """
    ЛОГИКА ПО ДОКУМЕНТАЦИИ (без гистерезиса и запасов):

    Нормативный диапазон: 0°C ... -2°C (круглогодично)
    - > 0°C  -> ДОБАВИТЬ ТДА
    - < -2°C -> УБРАТЬ ТДА
    - от -2°C до 0°C -> РЕЖИМ ДОПУСТИМ
    """

    # Определяем сезон (только для информационных целей, не влияет на логику)
    if month in [12, 1, 2, 3]:
        season = "ЗИМНИЙ РЕЖИМ"
    elif month in [6, 7, 8, 9]:
        season = "ЛЕТНИЙ РЕЖИМ"
    else:
        season = "ПЕРЕХОДНЫЙ РЕЖИМ"

    # === СЛУЧАЙ 1: Температура ВЫШЕ нормы (> 0°C) ===
    if t_current > 0:
        if t_current > 2:
            return {
                'action': 'ДОБАВИТЬ ТДА',
                'type': 'critical',
                'reason': f'Температура газа {t_current}°C критически высокая. Норма: 0...-2°C',
                'urgency': 'НЕМЕДЛЕННО',
                'recommended': min(6, n_tda + 2),
                'season': season
            }
        else:
            return {
                'action': 'ДОБАВИТЬ ТДА',
                'type': 'warning',
                'reason': f'Температура газа {t_current}°C выше нормы (0...-2°C)',
                'urgency': 'В БЛИЖАЙШЕЕ ВРЕМЯ',
                'recommended': min(6, n_tda + 1),
                'season': season
            }

    # === СЛУЧАЙ 2: Температура в норме (-2°C ... 0°C) ===
    if -2 <= t_current <= 0:
        return {
            'action': 'РЕЖИМ ДОПУСТИМ',
            'type': 'normal',
            'reason': f'Температура газа {t_current}°C в пределах нормы (0...-2°C)',
            'urgency': 'НАБЛЮДЕНИЕ',
            'recommended': n_tda,
            'season': season
        }

    # === СЛУЧАЙ 3: Температура НИЖЕ нормы (< -2°C) ===
    if t_current < -2:
        # Если ТДА уже 0, убирать нечего
        if n_tda == 0:
            return {
                'action': 'РЕЖИМ ДОПУСТИМ',
                'type': 'normal',
                'reason': f'Температура {t_current}°C ниже нормы, но ТДА уже отключены (0 шт)',
                'urgency': 'НАБЛЮДЕНИЕ',
                'recommended': 0,
                'season': season
            }

        # Проверяем, что без ТДА не поднимется выше нормы (> 0°C)
        if t_without > 0:
            return {
                'action': 'РЕЖИМ ДОПУСТИМ',
                'type': 'warning',
                'reason': f'Температура {t_current}°C ниже нормы, но без ТДА будет {t_without}°C (выше 0°C)',
                'urgency': 'ОСТОРОЖНО',
                'recommended': n_tda,
                'season': season
            }

        # Без ТДА температура останется в норме или ниже → можно отключать
        return {
            'action': 'УБРАТЬ ТДА',
            'type': 'warning',
            'reason': f'Температура {t_current}°C ниже нормы (<-2°C). Без ТДА: {t_without}°C',
            'urgency': 'ПЛАНОВО',
            'recommended': max(0, n_tda - 1),
            'season': season
        }

    # Запасной случай (на всякий случай)
    return {
        'action': 'РЕЖИМ ДОПУСТИМ',
        'type': 'normal',
        'reason': f'Температура газа {t_current}°C',
        'urgency': 'НАБЛЮДЕНИЕ',
        'recommended': n_tda,
        'season': season
    }


def add_to_log(action, details, params=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        'timestamp': timestamp,
        'action': action,
        'details': details,
        'params': params
    }
    st.session_state.log.insert(0, entry)
    if len(st.session_state.log) > 50:
        st.session_state.log = st.session_state.log[:50]
    save_journal(st.session_state.log)


def main():
    st.markdown("""
    <div class="header">
        <h1>СОГ ГП-16 | СИСТЕМА УПРАВЛЕНИЯ ТДА</h1>
        <p>Станция охлаждения газа | Версия 11.0 (формула скорректирована по данным Excel)</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="normative-box">
        <b>НОРМАТИВНЫЙ ДИАПАЗОН (согласно проекту):</b> 0 ... -2 °C<br>
        <b>> 0 °C</b> → ДОБАВИТЬ ТДА &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>от -2 до 0 °C</b> → РЕЖИМ ДОПУСТИМ &nbsp;&nbsp;|&nbsp;&nbsp;
        <b>< -2 °C</b> → УБРАТЬ ТДА
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="instruction-panel">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="instruction-title">Назначение системы</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="instruction-content">
            Система поддержки принятия решений для управления ТДА СОГ ГП-16.<br><br>
            <b>Источник данных:</b> реальные режимы работы СОГ (апрель, октябрь-ноябрь).<br>
            <b>Формула расчета:</b> множественная регрессия (файл СОГ_-_Дополнительный_Запрос_данных.xlsx).<br>
            <b>Корректировка:</b> +1.4°C для компенсации систематической ошибки (проверено на данных 2025-04-13).<br>
            <b>Норма:</b> 0...-2°C (согласно проектной документации).
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="instruction-title">Алгоритм запуска ТДА</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="instruction-content">
            1. Краны №514, 514.1, 517, 517.1 - открыты<br>
            2. Клапан №102: 20-70%, автоматический режим<br>
            3. Отсутствуют сигналы: «ШУМП №1», «НО ТДА», «АО ТДА»<br>
            4. «Газ в контуре» (давление > 4.5 МПа)<br>
            5. «Левитация» и «Вращение разрешено»<br>
            6. Поочередно: №207 → №205 → №206 → №204
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Ввод технологических параметров</div>', unsafe_allow_html=True)

    # Настройки шага в боковой панели (collapsed)
    with st.expander("Настройки шага ввода", expanded=False):
        st.markdown("Выберите шаг изменения значений:")
        step_temp = st.selectbox("Шаг температуры воздуха:", [0.1, 0.2, 0.5, 1.0], index=2)
        step_pressure = st.selectbox("Шаг давления:", [0.01, 0.05, 0.1, 0.2], index=1)
        st.info(f"Текущие шаги: температура {step_temp}°C, давление {step_pressure} МПа")

    # Если настройки не открыты, используем значения по умолчанию
    if 'step_temp' not in locals():
        step_temp = 0.5
    if 'step_pressure' not in locals():
        step_pressure = 0.05

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Температура воздуха</div>', unsafe_allow_html=True)
        t_air = float(st.number_input("t_air", value=-11.0, step=step_temp, format="%.1f", label_visibility="collapsed",
                                      key="input_t_air"))
        st.markdown(f'<div class="step-info">Шаг: {step_temp}°C</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Расход газа</div>', unsafe_allow_html=True)
        gas_flow = float(
            st.number_input("gas_flow", value=1800.0, step=10.0, format="%.0f", label_visibility="collapsed",
                            key="input_gas"))
        st.markdown('<div class="step-info">Шаг: 10 тыс.м³/ч</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Вентиляторы АВО</div>', unsafe_allow_html=True)
        n_fans = int(
            st.number_input("n_fans", value=25, step=1, min_value=0, max_value=60, label_visibility="collapsed",
                            key="input_fans"))
        st.markdown('<div class="step-info">Шаг: 1 шт</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Давление на входе</div>', unsafe_allow_html=True)
        pressure = float(
            st.number_input("pressure", value=5.5, step=step_pressure, format="%.2f", label_visibility="collapsed",
                            key="input_pressure"))
        st.markdown(f'<div class="step-info">Шаг: {step_pressure} МПа</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    col5, col6, col7 = st.columns([2, 2, 1])
    with col5:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Работает ТДА</div>', unsafe_allow_html=True)
        n_tda = int(
            st.selectbox("n_tda", [0, 1, 2, 3, 4, 5, 6], index=2, label_visibility="collapsed", key="input_tda"))
        st.markdown('<div class="param-unit">шт</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col6:
        st.markdown('<div class="param-card">', unsafe_allow_html=True)
        st.markdown('<div class="param-label">Текущий месяц</div>', unsafe_allow_html=True)
        month = int(st.selectbox("month", list(range(1, 13)), index=3, label_visibility="collapsed", key="input_month"))
        st.markdown('<div class="param-unit">месяц</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col7:
        st.markdown('<div style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        calc_clicked = st.button("РАССЧИТАТЬ", use_container_width=True, key="calc_btn")
        st.markdown('</div>', unsafe_allow_html=True)

    if calc_clicked:
        t_current = predictor.predict(t_air, gas_flow, n_fans, pressure, n_tda)
        t_without = predictor.predict(t_air, gas_flow, n_fans, pressure, 0)
        rec = get_recommendation(t_current, t_without, n_tda, month, t_air)

        st.session_state.calculation_done = True
        st.session_state.last_result = {
            't_current': t_current,
            't_without': t_without,
            'n_tda': n_tda,
            'rec': rec,
            't_air': t_air,
            'gas_flow': gas_flow,
            'n_fans': n_fans,
            'pressure': pressure,
            'month': month
        }

        add_to_log(
            action="РАСЧЕТ",
            details=f"Тгис={t_current}°C, ТДА={n_tda}шт, Рекомендация: {rec['action']}",
            params={'t_current': t_current, 't_without': t_without, 'n_tda': n_tda,
                    'recommended': rec['recommended'], 'action': rec['action']}
        )

    if st.session_state.calculation_done and st.session_state.last_result:
        res = st.session_state.last_result
        t_current = res['t_current']
        t_without = res['t_without']
        n_tda = res['n_tda']
        rec = res['rec']

        st.markdown("---")

        st.markdown(
            f'<div style="text-align: center; margin-bottom: 1rem;"><span class="season-badge">{rec["season"]}</span></div>',
            unsafe_allow_html=True)

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        if t_current > 0:
            temp_status = "ВЫШЕ НОРМЫ"
            temp_color = "#c53030"
        elif t_current < -2:
            temp_status = "НИЖЕ НОРМЫ"
            temp_color = "#dd6b20"
        else:
            temp_status = "В НОРМЕ"
            temp_color = "#38a169"

        with col_m1:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Температура газа</div><div class="metric-value" style="color:{temp_color};">{t_current}°C</div><div class="metric-unit">{temp_status}</div></div>',
                unsafe_allow_html=True)
        with col_m2:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Без ТДА</div><div class="metric-value">{t_without}°C</div><div class="metric-unit">прогноз</div></div>',
                unsafe_allow_html=True)
        with col_m3:
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Сейчас работает</div><div class="metric-value">{n_tda} шт</div><div class="metric-unit">ТДА</div></div>',
                unsafe_allow_html=True)
        with col_m4:
            rec_color = "#dd6b20" if rec['recommended'] != n_tda else "#38a169"
            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Рекомендуется</div><div class="metric-value" style="color:{rec_color};">{rec["recommended"]} шт</div><div class="metric-unit">ТДА</div></div>',
                unsafe_allow_html=True)

        rec_class = f"rec-{rec['type']}"
        st.markdown(
            f'<div class="recommendation {rec_class}"><div class="rec-title">{rec["action"]}</div><div class="rec-reason">{rec["reason"]}</div><div class="rec-urgency">СРОЧНОСТЬ: {rec["urgency"]}</div></div>',
            unsafe_allow_html=True)

        st.markdown('<div class="section-title">Сравнение режимов работы</div>', unsafe_allow_html=True)

        all_temps = predictor.predict_for_all_tda(res['t_air'], res['gas_flow'], res['n_fans'], res['pressure'])

        comparison_data = []
        for i, temp in enumerate(all_temps):
            if temp > 0:
                status = "ВЫШЕ НОРМЫ"
                status_class = "status-critical"
            elif temp < -2:
                status = "НИЖЕ НОРМЫ"
                status_class = "status-warning"
            else:
                status = "В НОРМЕ"
                status_class = "status-normal"

            if i == n_tda:
                current = "ТЕКУЩИЙ"
            elif i == rec['recommended']:
                current = "РЕКОМЕНД."
            else:
                current = ""

            comparison_data.append({
                'Количество ТДА': f"{i} шт",
                'Температура газа': f"{temp}°C",
                'Статус': f'<span class="{status_class}">{status}</span>',
                'Примечание': current
            })

        df_comparison = pd.DataFrame(comparison_data)
        st.markdown(df_comparison.to_html(escape=False, index=False), unsafe_allow_html=True)

        with st.expander("Журнал операций", expanded=False):
            if st.session_state.log:
                for entry in st.session_state.log[:20]:
                    if isinstance(entry, dict):
                        st.markdown(f"""
                        <div class="journal-entry">
                            <span class="journal-timestamp">{entry['timestamp']}</span><br>
                            <span class="journal-action">{entry['action']}</span>: {entry['details']}
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Журнал операций пуст")

        with st.expander("Подробности расчета", expanded=False):
            st.markdown(f"""
            **Исходные данные:**
            | Параметр | Значение |
            |----------|----------|
            | Температура воздуха | {res['t_air']} °C |
            | Расход газа | {res['gas_flow']:.0f} тыс. м³/ч |
            | Вентиляторы АВО | {res['n_fans']} шт |
            | Давление на входе | {res['pressure']} МПа |

            **Результаты:**
            | Показатель | Значение |
            |------------|----------|
            | Текущая температура газа | {res['t_current']} °C |
            | Температура без ТДА | {res['t_without']} °C |
            | Рекомендация | {res['rec']['action']} |
            | Рекомендуемое кол-во ТДА | {res['rec']['recommended']} шт |

            **Формула расчета (множественная регрессия по данным СОГ с корректировкой):**
            ```
            Тгис = 0,053 × Твозд - 0,00048 × Qг - 0,0079 × Nвент - 0,61 × Рвх + 3,8 - 0,15 × Nтдаv
            ```
            
            **Расшифровка коэффициентов:**
            | Коэффициент | Значение | Влияние |
            |-------------|----------|---------|
            | +0,053 × Твозд | Температура воздуха | При росте Твозд на 1°C → Тгис↑ на 0,053°C |
            | -0,00048 × Qг | Расход газа | При росте Qг на 1000 м³/ч → Тгис↓ на 0,48°C |
            | -0,0079 × Nвент | Вентиляторы АВО | Каждый вентилятор ↓ Тгис на 0,0079°C |
            | -0,61 × Рвх | Давление на входе | При росте давления на 1 МПа → Тгис↓ на 0,61°C |
            | +3,8 | Свободный член | Базовая температура (скорректировано с +2,4 для компенсации ошибки) |
            | -0,15 × Nтда | Работа ТДА | Каждый ТДА ↓ Тгис на 0,15°C |
            
            **Нормативный диапазон (согласно проектной документации):** 0 ... -2 °C
            
            **Логика принятия решений:**
            - Температура > 0°C → **ДОБАВИТЬ ТДА** (нарушение нормы)
            - Температура от -2°C до 0°C → **РЕЖИМ ДОПУСТИМ** (норма)
            - Температура < -2°C → **УБРАТЬ ТДА** (переохлаждение)
            """)

            st.markdown("""
            <div class="footer">
            СОГ ГП-16 | Система поддержки принятия решений | Версия 11.0<br>
            Расчет основан на регрессионной модели по реальным данным эксплуатации СОГ.<br>
            Формула скорректирована на +1.4°C по результатам верификации на данных 2025-04-13.<br>
            Рекомендации носят справочный характер. Окончательное решение принимает ответственный оператор.
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

