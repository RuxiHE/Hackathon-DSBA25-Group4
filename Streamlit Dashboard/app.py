import streamlit as st  # 确保 st 在最上方被导入
import pandas as pd
from pages import yearly, monthly, daily, weekly

# ✅ 将 st.set_page_config 放在最前面
st.set_page_config(
    page_title="Theme Park Wait Time Dashboard",
    page_icon="🎢",
    layout="wide"
)

# 侧边栏导航
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio("Go to", ["Yearly", "Monthly", "Weekly", "Daily"])

# 选择页面
if page == "Yearly":
    yearly.show()
elif page == "Monthly":
    monthly.show()
elif page == "Weekly":
    weekly.show()
elif page == "Daily":
    daily.show()
