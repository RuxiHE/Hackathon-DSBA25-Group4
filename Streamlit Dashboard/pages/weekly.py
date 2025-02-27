import os
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np

# -----------------------------
# 📌 配置部分
# -----------------------------
HISTORICAL_DATA_PATH = "/Users/kk_yang/Desktop/M2S2/Hackthon/Streamlit Dashboard/cleaned_data/merged_final_2.csv"
MERGED_7_DAYS = "/Users/kk_yang/Desktop/M2S2/Hackthon/Streamlit Dashboard/merged_df.csv"

# 时间范围
DATA_START_DATE = pd.to_datetime("2018-06-01")
DATA_END_DATE = pd.to_datetime("2022-07-26")  
FAKE_START_DATE = pd.to_datetime("2022-07-27")
FAKE_END_DATE = pd.to_datetime("2022-08-02")  

# -----------------------------
# 📌 读取数据
# -----------------------------
@st.cache_data
def load_historical_data():
    """加载历史数据"""
    if not os.path.exists(HISTORICAL_DATA_PATH):
        st.error(f"❌ Historical data file not found: {HISTORICAL_DATA_PATH}")
        return None

    df = pd.read_csv(HISTORICAL_DATA_PATH, encoding="utf-8", low_memory=False, on_bad_lines="skip")
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
    df["capacity_utilization"] = np.where(df["CAPACITY"] > 0, df["GUEST_CARRIED"] / df["CAPACITY"] * 100, 0)
    
    return df[df["date"] <= DATA_END_DATE]

@st.cache_data
def load_fake_data():
    """加载假数据"""
    if not os.path.exists(MERGED_7_DAYS):
        st.error(f"❌ 7-day fake data file not found: {MERGED_7_DAYS}")
        return None

    df = pd.read_csv(MERGED_7_DAYS)
    df.rename(columns={"Date": "date", "Attraction": "attraction", "Wait_time_max": "wait_time_max"}, inplace=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["hour", "attendance", "GUEST_CARRIED", "CAPACITY"]:
        if col not in df.columns:
            df[col] = 0

    df = df[(df["date"] >= FAKE_START_DATE) & (df["date"] <= FAKE_END_DATE)]
    df["capacity_utilization"] = np.where(df["CAPACITY"] > 0, df["GUEST_CARRIED"] / df["CAPACITY"] * 100, 0)

    return df

# -----------------------------
# 📌 计算同比变化
# -----------------------------
def compute_delta_percent(current, previous):
    """计算同比增长百分比"""
    if previous is None or previous == 0:
        return None
    return round((current - previous) / abs(previous) * 100, 2)

# -----------------------------
# 📌 Streamlit 界面
# -----------------------------
def show():
    st.title("📊 Weekly Forecast & Insights")

    df_hist = load_historical_data()
    df_fake = load_fake_data()

    if df_hist is None or df_fake is None:
        st.stop()

    df_all = pd.concat([df_hist, df_fake])

    # 📅 **日历选择日期**
    selected_date = st.date_input("📅 Select a Date", value=pd.to_datetime("2022-07-04"), min_value=DATA_START_DATE.date(), max_value=FAKE_END_DATE.date())

    selected_date = pd.to_datetime(selected_date)
    selected_week_start = selected_date - pd.Timedelta(days=selected_date.weekday())
    selected_week_end = selected_week_start + pd.Timedelta(days=6)

    # 🗂 **筛选当周数据**
    weekly_df = df_all[(df_all["date"] >= selected_week_start) & (df_all["date"] <= selected_week_end)]

    if weekly_df.empty:
        st.warning("⚠️ No data for the selected week.")
        st.stop()

    # 🎢 **选择景点**
    attractions = weekly_df["attraction"].dropna().unique().tolist()
    attraction_selected = st.selectbox("🎢 Select an Attraction", attractions)
    filtered_df = weekly_df[weekly_df["attraction"] == attraction_selected]

    # 📊 **计算 KPI**
    avg_wait_time = round(filtered_df["wait_time_max"].mean(), 2)
    peak_wait_time = round(filtered_df["wait_time_max"].max(), 2)
    daily_attendance = filtered_df.groupby("date").first()["attendance"]
    weekly_attendance = daily_attendance.sum()
    capacity_utilization = round(filtered_df["capacity_utilization"].mean(), 2)
    peak_time_row = filtered_df.loc[filtered_df["wait_time_max"].idxmax()]
    peak_hour = int(peak_time_row["hour"]) if not filtered_df.empty else None

    # 📌 **计算上一周数据**
    prev_week_start = selected_week_start - pd.Timedelta(weeks=1)
    prev_week_end = selected_week_end - pd.Timedelta(weeks=1)

    prev_week_df = df_all[(df_all["date"] >= prev_week_start) & (df_all["date"] <= prev_week_end)]
    prev_filtered = prev_week_df[prev_week_df["attraction"] == attraction_selected] if not prev_week_df.empty else pd.DataFrame()

    if not prev_filtered.empty:
        prev_avg_wait_time = round(prev_filtered["wait_time_max"].mean(), 2)
        prev_peak_wait_time = round(prev_filtered["wait_time_max"].max(), 2)
        prev_daily_attendance = prev_filtered.groupby("date").first()["attendance"]
        prev_weekly_attendance = prev_daily_attendance.sum()
        prev_capacity_utilization = round(prev_filtered["capacity_utilization"].mean(), 2)
    else:
        prev_avg_wait_time = None
        prev_peak_wait_time = None
        prev_weekly_attendance = None
        prev_capacity_utilization = None

    # 📈 **计算同比增长**
    delta_attendance = compute_delta_percent(weekly_attendance, prev_weekly_attendance)
    delta_avg_wait = compute_delta_percent(avg_wait_time, prev_avg_wait_time)
    delta_peak_wait = compute_delta_percent(peak_wait_time, prev_peak_wait_time)
    delta_cap_util = compute_delta_percent(capacity_utilization, prev_capacity_utilization)

    # 🚀 **展示 KPI**
    col1, col2, col3 = st.columns(3)
    col1.metric("📊 Total Attendance", int(weekly_attendance), f"{delta_attendance}%")
    col2.metric("🛎️ Avg Wait Time (min)", avg_wait_time, f"{delta_avg_wait}%")
    col3.metric("📈 Peak Wait Time (min)", peak_wait_time, f"{delta_peak_wait}%")

    colA, colB, colC = st.columns(3)
    colA.metric("🎢 Capacity Utilization (%)", capacity_utilization, f"{delta_cap_util}%")
    colB.metric("⏰ Peak Hour", f"{peak_hour}:00")
    
    busy_level = "🟢 Low" if avg_wait_time < 15 else "🟡 Medium" if avg_wait_time < 30 else "🔴 High"
    colC.metric("🚦 Busy Level", busy_level)

    # 📉 **绘制趋势图**
    st.write("### ⏳ Daily Avg Wait Time Trends")
    # 计算每日平均等待时间
    daily_trend = filtered_df.groupby("date")["wait_time_max"].mean().reset_index()

    # **确保 date 只包含日期，不包含时间**
    daily_trend["date"] = pd.to_datetime(daily_trend["date"]).dt.date

    # **只保留数据范围内的日期**
    daily_trend = daily_trend[daily_trend["date"] <= FAKE_END_DATE.date()]

    # 重新转换回 `datetime`，以便 plotly 识别
    daily_trend["date"] = pd.to_datetime(daily_trend["date"])

    fig = px.line(daily_trend, x="date", y="wait_time_max", 
                title=f"{attraction_selected} - Daily Wait Time (Weekly View)", 
                labels={"wait_time_max": "Avg Wait Time (min)", "date": "Date"})
    st.plotly_chart(fig)


# 启动 Streamlit
if __name__ == "__main__":
    show()
