import sys
import os
import pandas as pd
import torch
import streamlit as st
import plotly.express as px
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# -----------------------------
# 配置部分：根据自己实际情况修改
# -----------------------------
HISTORICAL_DATA_PATH = "/Users/kk_yang/Desktop/M2S2/Hackthon/Streamlit Dashboard/cleaned_data/merged_final_2.csv"
MERGED_7_DAYS = "/Users/kk_yang/Desktop/M2S2/Hackthon/Streamlit Dashboard/merged_df.csv"

# 原始数据/闭园信息时间范围
DATA_START_DATE = pd.to_datetime("2018-06-01")
DATA_END_DATE = pd.to_datetime("2022-07-26")   # 历史数据截至
CLOSED_START = pd.to_datetime("2020-03-14")
CLOSED_END = pd.to_datetime("2021-06-14")
FAKE_START_DATE = pd.to_datetime("2022-07-27") # 假数据开始
FAKE_END_DATE = pd.to_datetime("2022-08-02")   # 假数据结束


@st.cache_data
def load_historical_data():
    """
    加载历史数据 (CSV)，仅包括 2018-06-01 ~ 2022-07-26
    """
    if not os.path.exists(HISTORICAL_DATA_PATH):
        st.error(f"❌ Historical data file not found: {HISTORICAL_DATA_PATH}")
        return None
    
    try:
        df = pd.read_csv(
            HISTORICAL_DATA_PATH,
            encoding="utf-8",
            low_memory=False,
            on_bad_lines="skip"
        )
        # 重命名列
        df.rename(columns={
            "WORK_DATE": "date",
            "ENTITY_DESCRIPTION_SHORT": "attraction",
            "WAIT_TIME_MAX": "wait_time_max",
            "attendance": "attendance",
            "DEB_TIME_HOUR": "hour",
            "DEB_TIME_ONLY": "time_slot",
            "GUEST_CARRIED": "GUEST_CARRIED",
            "CAPACITY": "CAPACITY"
        }, inplace=True)

        # 转成 datetime
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # 填缺失
        df.fillna({
            "wait_time_max": 0,
            "attendance": 0,
            "GUEST_CARRIED": 0,
            "CAPACITY": 1
        }, inplace=True)

        # 只保留 2022-07-26 及之前的记录
        df = df[df["date"] <= DATA_END_DATE]

        # capacity utilization
        df["capacity_utilization"] = (
            df["GUEST_CARRIED"] / df["CAPACITY"] * 100
        )
        return df

    except Exception as e:
        st.error(f"❌ Error loading historical CSV: {e}")
        return None

@st.cache_data
def load_fake_7days_data():
    """
    加载 7 天假数据 (Excel)，仅包括 2022-07-27 ~ 2022-08-02
    """
    if not os.path.exists(MERGED_7_DAYS):
        st.error(f"❌ 7-day fake data file not found: {MERGED_7_DAYS}")
        return None

    try:
        df_pred = pd.read_csv(MERGED_7_DAYS)

        # 根据实际列名做重命名
        df_pred.rename(columns={
            "Date": "date",
            "Attraction": "attraction",
            "Wait_time_max": "wait_time_max"
        }, inplace=True)

        # 转成 datetime
        df_pred["date"] = pd.to_datetime(df_pred["date"], errors="coerce")

        # 如果某些列不存在，则补上默认值
        if "hour" not in df_pred.columns:
            df_pred["hour"] = 12
        if "attendance" not in df_pred.columns:
            df_pred["attendance"] = 0
        if "GUEST_CARRIED" not in df_pred.columns:
            df_pred["GUEST_CARRIED"] = 0
        if "CAPACITY" not in df_pred.columns:
            df_pred["CAPACITY"] = 1

        # 只保留 2022-07-27 ~ 2022-08-02 之间的数据
        df_pred = df_pred[
            (df_pred["date"] >= FAKE_START_DATE) &
            (df_pred["date"] <= FAKE_END_DATE)
        ]

        # 计算capacity_utilization
        df_pred["capacity_utilization"] = (
            df_pred["GUEST_CARRIED"] / df_pred["CAPACITY"] * 100
        )

        return df_pred

    except Exception as e:
        st.error(f"❌ Error loading 7-day fake data Excel: {e}")
        return None


def show():
    st.title("📊 Daily Forecast & Recommendations")

    # -------------------------
    # 1) 读取并缓存两份数据
    # -------------------------
    df_hist = load_historical_data()  # 2018-06-01 ~ 2022-07-26
    df_fake = load_fake_7days_data()  # 2022-07-27 ~ 2022-08-02

    if df_hist is None or df_fake is None:
        st.stop()

    # -------------------------
    # 2) 用户选日期，限制在 2018-06-01 ~ 2022-08-02
    # -------------------------
    date_selected = pd.Timestamp(st.date_input(
        "📅 Select a Date",
        value=pd.to_datetime("2022-06-15"),
        min_value=DATA_START_DATE.date(),
        max_value=FAKE_END_DATE.date()
    ))

    # 如果在闭园期
    if CLOSED_START <= date_selected <= CLOSED_END:
        st.warning(
            f"⚠️ The park was closed from {CLOSED_START.date()} to {CLOSED_END.date()}. No data available."
        )
        st.stop()

    # 根据日期选择对应表
    if date_selected <= DATA_END_DATE:
        daily_df = df_hist[df_hist["date"] == date_selected]
    elif date_selected <= FAKE_END_DATE:
        daily_df = df_fake[df_fake["date"] == date_selected]
    else:
        st.warning("Selected date is out of range.")
        st.stop()

    if daily_df.empty:
        st.warning("No data for the selected date.")
        st.stop()

    # -------------------------
    # 3) 选择特定景点
    # -------------------------
    attractions_today = daily_df["attraction"].dropna().unique().tolist()
    if not attractions_today:
        st.warning(f"No attractions available on {date_selected.date()}.")
        st.stop()

    # 设置默认选项的索引
    default_index = attractions_today.index("Roller Coaster") if "Roller Coaster" in attractions_today else 0

    attraction_selected = st.selectbox("🎢 Select an Attraction", attractions_today, index=default_index)
    filtered_df = daily_df[daily_df["attraction"] == attraction_selected]


    if filtered_df.empty:
        st.warning("No data for the selected date/attraction.")
        st.stop()

    # -------------------------
    # 额外提示信息
    # -------------------------
    if date_selected <= DATA_END_DATE:
        st.markdown("> **👵🏼 Tips:** This data is calculated based on historical actual data.")
    elif date_selected <= FAKE_END_DATE:
        st.markdown("> **🔮 Tips:** This data is predicted based on models and historical data.")

    # -------------------------
    # 4) 计算当日核心指标
    # -------------------------
    avg_wait_time = round(filtered_df["wait_time_max"].mean(), 2)
    peak_wait_time = round(filtered_df["wait_time_max"].max(), 2)
    attendance = filtered_df["attendance"].iloc[0] if "attendance" in filtered_df.columns else 0
    capacity_utilization = round(filtered_df["capacity_utilization"].mean(), 2)

    # 峰值小时
    # 计算峰值小时
    grouped_peak = filtered_df.groupby("hour")["wait_time_max"].mean()

    if not grouped_peak.empty:
        peak_hour = grouped_peak.idxmax()
        if isinstance(peak_hour, str) and ":" in str(peak_hour):
            peak_hour = int(str(peak_hour).split(":")[0])  # 取出小时部分
        peak_hour_str = f"{int(peak_hour):02d}:00"
    else:
        peak_hour_str = "No data"


    # -------------------------
    # 5) 计算前一天数据 => 用于显示 delta%
    # -------------------------
    prev_date = date_selected - pd.Timedelta(days=1)

    # 判定前一天是否在有效区间
    if prev_date < DATA_START_DATE or prev_date > FAKE_END_DATE:
        prev_attendance = None
        prev_avg_wait = None
        prev_peak_wait = None
        prev_cap_util = None
    else:
        if prev_date <= DATA_END_DATE:
            prev_df = df_hist[df_hist["date"] == prev_date]
        else:
            prev_df = df_fake[df_fake["date"] == prev_date]

        prev_filtered = prev_df[prev_df["attraction"] == attraction_selected] if not prev_df.empty else pd.DataFrame()
        if prev_filtered.empty:
            prev_attendance = None
            prev_avg_wait = None
            prev_peak_wait = None
            prev_cap_util = None
        else:
            prev_attendance = prev_filtered["attendance"].iloc[0] if "attendance" in prev_filtered.columns else 0
            prev_avg_wait = round(prev_filtered["wait_time_max"].mean(), 2)
            prev_peak_wait = round(prev_filtered["wait_time_max"].max(), 2)
            prev_cap_util = round(prev_filtered["capacity_utilization"].mean(), 2)

    def compute_delta_percent(today_val, prev_val):
        # 若前一天无数据或 0，返回 None 不显示
        if prev_val is None or prev_val == 0:
            return None
        change = (today_val - prev_val) / abs(prev_val) * 100.0
        return round(change, 2)

    delta_attendance = compute_delta_percent(attendance, prev_attendance)
    delta_avg_wait = compute_delta_percent(avg_wait_time, prev_avg_wait)
    delta_peak_wait = compute_delta_percent(peak_wait_time, prev_peak_wait)
    delta_cap_util = compute_delta_percent(capacity_utilization, prev_cap_util)

    attendance_str = str(int(attendance))  # 整数格式

    # -------------------------
    # 6) 布局: 2 行 KPI
    #    第一行: Attendance / Avg Wait / Peak Wait
    #    第二行: Capacity Util / Peak Hour / Busy Level
    # -------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label="📊 Total Attendance",
        value=attendance_str,
        delta=f"{delta_attendance}%" if delta_attendance is not None else None
    )
    col2.metric(
        label="🛎️ Avg Wait Time (min)",
        value=avg_wait_time,
        delta=f"{delta_avg_wait}%" if delta_avg_wait is not None else None
    )
    col3.metric(
        label="📈 Peak Wait Time (min)",
        value=peak_wait_time,
        delta=f"{delta_peak_wait}%" if delta_peak_wait is not None else None
    )

    colA, colB, colC = st.columns(3)
    colA.metric(
        label="🎢 Capacity Utilization (%)",
        value=capacity_utilization,
        delta=f"{delta_cap_util}%" if delta_cap_util is not None else None
    )
    colB.metric("⏰ Peak Hour", peak_hour_str)

    # Busy Level 示例
    if avg_wait_time < 15 and peak_wait_time < 30:
        busy_level = "🟢 Low"
    elif avg_wait_time < 30 and peak_wait_time < 60:
        busy_level = "🟡 Medium"
    else:
        busy_level = "🔴 High"
    colC.metric("🚦 Busy Level", busy_level)

    # -------------------------
    # 7) 趋势图: 按小时
    # -------------------------
    st.write("### ⏳ Hourly Wait Time Trends")
    hourly_df = filtered_df.groupby("hour", as_index=False)["wait_time_max"].mean()
    hourly_df["daily_avg_wait_time"] = hourly_df["wait_time_max"].mean()

    fig = px.line(
        hourly_df,
        x="hour",
        y=["wait_time_max", "daily_avg_wait_time"],
        labels={
            "hour": "Hour of Day",
            "value": "Wait Time (min)",
            "variable": "Metric"
        },
        title=f"{attraction_selected} - Hourly Wait Time Trend on {date_selected.date()}"
    )
    st.plotly_chart(fig)

    # -------------------------
    # 8) Recommendations
    # -------------------------
    st.subheader("🪄 **Recommendation:**")
    st.markdown("#### Ideal Units & Average Wait Time by 3-Hour Segments (09:00 ~ 21:00)")
    time_segments = [(9, 12), (12, 15), (15, 18), (18, 21)]
    table_data = []

    max_avg_wait_time = 0
    busiest_time_range = None  # 记录平均等待时间最长的时间段

        # 确保 hour 列是整数类型
    filtered_df["hour"] = pd.to_numeric(filtered_df["hour"], errors="coerce").astype("Int64")

    # 计算时间段数据
    for (start_h, end_h) in time_segments:
        segment_label = f"{start_h:02d}:00-{end_h:02d}:00"
        
        # 现在 hour 列已经是整数，不会再报类型错误
        sub_df = filtered_df[(filtered_df["hour"] >= start_h) & (filtered_df["hour"] < end_h)]

        if sub_df.empty:
            recommended_units = "/"
            avg_wait_time_segment = 0  # 避免 None 影响比较
        else:
            # 1. 计算本时段累计载客数
            guests_carried_seg = sub_df["GUEST_CARRIED"].sum()
            
            # 2. 从本时段数据中取出总容量、最大单元数（假设这两个值在时段内一致，取第一条记录）
            total_capacity = sub_df["CAPACITY"].iloc[0]
            nb_unit_max = sub_df["NB_MAX_UNIT"].iloc[0]

            # 3. 计算每个单元的容量（若需要的话），这里暂时保留，但实际没用到
            #    capacity_per_unit = total_capacity / nb_unit_max if nb_unit_max > 0 else 0

            # 4. 计算平均等待时间（取整数）
            avg_wait_time_segment = int(round(sub_df["wait_time_max"].mean()))

            # 5. 根据新逻辑计算推荐的单位数：
            #    recommended_units = guests_carried_seg / total_capacity
            if total_capacity <= 0:
                recommended_units = "/"
            else:
                # 用 ceil 向上取整
                ideal_units_seg = np.ceil(guests_carried_seg / total_capacity)

                # 约束：不能超过 NB_MAX_UNIT
                if ideal_units_seg > nb_unit_max:
                    ideal_units_seg = nb_unit_max

                recommended_units = str(int(ideal_units_seg))

        table_data.append({
            "Time Range": segment_label,
            "Recommended Ideal Units": recommended_units,
            "Avg Wait Time (min)": avg_wait_time_segment
        })
        
        if avg_wait_time_segment > max_avg_wait_time:
            max_avg_wait_time = avg_wait_time_segment
            busiest_time_range = segment_label

    table_df = pd.DataFrame(table_data)
    st.dataframe(table_df, hide_index=True)

    st.markdown(
        "> **Tips**: `/` indicates that the attraction is closed or no data is available in that time period."
    )

    # -------------------------
    # 额外推荐策略: 部署 Food/Merchandise Carts
    # -------------------------
    if max_avg_wait_time > 30 and busiest_time_range:
        
        st.write(
            f"🚨 The busiest time range is **{busiest_time_range}**, with an average wait time of **{max_avg_wait_time}** minutes. "
            "Consider deploying **Food/Merchandise Carts** to improve guest experience."
        )
    