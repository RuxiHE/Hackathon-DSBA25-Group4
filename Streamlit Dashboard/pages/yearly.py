import os
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# -----------------------------
# 配置部分
# -----------------------------
HISTORICAL_DATA_PATH = "/Users/kk_yang/Desktop/M2S2/Hackthon/Streamlit Dashboard/cleaned_data/merged_final_2.csv"
DATA_START_DATE = pd.to_datetime("2018-06-01")
DATA_END_DATE = pd.to_datetime("2022-07-26")

@st.cache_data
def load_historical_data():
    """
    加载历史数据 (CSV)
    """
    if not os.path.exists(HISTORICAL_DATA_PATH):
        st.error(f"❌ Historical data file not found: {HISTORICAL_DATA_PATH}")
        return None
    
    df = pd.read_csv(
        HISTORICAL_DATA_PATH,
        encoding="utf-8",
        low_memory=False,
        on_bad_lines="skip"
    )
    df.rename(columns={
        "WORK_DATE": "date",
        "ENTITY_DESCRIPTION_SHORT": "attraction",
        "WAIT_TIME_MAX": "wait_time_max",
        "attendance": "attendance",
        "GUEST_CARRIED": "GUEST_CARRIED",
        "CAPACITY": "CAPACITY",
        "DEB_TIME_HOUR": "hour"
    }, inplace=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df.fillna({"wait_time_max": 0, "attendance": 0, "GUEST_CARRIED": 0, "CAPACITY": 1, "hour": 0}, inplace=True)
    df = df[df["date"] <= DATA_END_DATE]
    df["capacity_utilization"] = df["GUEST_CARRIED"] / df["CAPACITY"] * 100
    return df

def show():
    st.title("📊 Yearly Forecast & Insights")
    df_hist = load_historical_data()
    if df_hist is None:
        st.stop()
    
    # 选择年份，默认2019年
    selected_year = st.selectbox("📅 Select Year", sorted(df_hist["date"].dt.year.unique()), index=list(df_hist["date"].dt.year.unique()).index(2019))
    
    # 过滤数据
    yearly_df = df_hist[df_hist["date"].dt.year == selected_year]
    
    if yearly_df.empty:
        st.warning("No data for the selected year.")
        st.stop()
    
    # 选择景点
    attractions = yearly_df["attraction"].dropna().unique().tolist()
    attraction_selected = st.selectbox("🎢 Select an Attraction", attractions)
    filtered_df = yearly_df[yearly_df["attraction"] == attraction_selected]
    
    if filtered_df.empty:
        st.warning("No data for the selected year/attraction.")
        st.stop()
    
    # 计算 KPI
    avg_wait_time = round(filtered_df["wait_time_max"].mean(), 2)
    peak_wait_time = filtered_df["wait_time_max"].max()  # 取全年最大等待时间
    total_attendance = filtered_df.groupby("date")["attendance"].first().sum()
    capacity_utilization = round(filtered_df["capacity_utilization"].mean(), 2)
    peak_hour = filtered_df.loc[filtered_df["wait_time_max"].idxmax(), "hour"]  # 取全年最大等待时间对应的小时数
    
    # 计算 Busy Level
    if avg_wait_time < 15 and peak_wait_time < 30:
        busy_level = "🟢 Low"
    elif avg_wait_time < 30 and peak_wait_time < 60:
        busy_level = "🟡 Medium"
    else:
        busy_level = "🔴 High"
    
    # 计算前一年数据
    prev_year = selected_year - 1
    prev_year_df = df_hist[df_hist["date"].dt.year == prev_year]
    prev_filtered = prev_year_df[prev_year_df["attraction"] == attraction_selected] if not prev_year_df.empty else pd.DataFrame()
    
    def compute_delta_percent(today_val, prev_val):
        if prev_val is None or prev_val == 0:
            return None
        change = (today_val - prev_val) / abs(prev_val) * 100.0
        return round(change, 2)
    
    prev_attendance = prev_filtered.groupby("date")["attendance"].first().sum() if not prev_filtered.empty else None
    prev_avg_wait = round(prev_filtered["wait_time_max"].mean(), 2) if not prev_filtered.empty else None
    prev_peak_wait = prev_filtered["wait_time_max"].max() if not prev_filtered.empty else None  # 取前一年最大等待时间
    prev_cap_util = round(prev_filtered["capacity_utilization"].mean(), 2) if not prev_filtered.empty else None
    
    delta_attendance = compute_delta_percent(total_attendance, prev_attendance)
    delta_avg_wait = compute_delta_percent(avg_wait_time, prev_avg_wait)
    delta_peak_wait = compute_delta_percent(peak_wait_time, prev_peak_wait)
    delta_cap_util = compute_delta_percent(capacity_utilization, prev_cap_util)
    
    # KPI 显示
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Attendance", int(total_attendance), f"{delta_attendance}%" if delta_attendance is not None else None)
    col2.metric("🛎️ Avg Wait Time (min)", avg_wait_time, f"{delta_avg_wait}%" if delta_avg_wait is not None else None)
    col3.metric("📈 Peak Wait Time (min)", peak_wait_time, f"{delta_peak_wait}%" if delta_peak_wait is not None else None)
    
    colA, colB, colC = st.columns(3)
    colA.metric("🎢 Capacity Utilization (%)", capacity_utilization, f"{delta_cap_util}%" if delta_cap_util is not None else None)
    colB.metric("⏰ Peak Hour", f"{int(peak_hour):02d}:00")
    colC.metric("🚦 Busy Level", busy_level)
    
    # 趋势图
    st.write("### 📈 Yearly Wait Time Trends")
    trend_df = filtered_df.groupby(filtered_df["date"].dt.month)["wait_time_max"].mean().reset_index()
    trend_df["month"] = trend_df["date"].apply(lambda x: pd.to_datetime(f"2022-{x:02d}-01").strftime('%B'))
    trend_df.drop(columns=["date"], inplace=True)
    fig = px.line(trend_df, x="month", y="wait_time_max", title=f"{attraction_selected} - Monthly Avg Wait Time in {selected_year}", labels={"wait_time_max": "Monthly Average Waiting Time"})
    st.plotly_chart(fig)

if __name__ == "__main__":
    show()
