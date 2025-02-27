# ---------------------------- 新增预测数据加载函数 ----------------------------
import pandas as pd
import numpy as np

def load_forecast_data(date_selected, attraction_list):
    """生成模拟预测数据（未来需替换为真实模型预测）"""
    np.random.seed(42)
    
    # 生成未来日期范围（示例：预测未来24小时，间隔15分钟）
    date_range = pd.date_range(
        start=date_selected,
        end=date_selected + pd.Timedelta(days=1),
        freq="15min"
    )
    
    # 构建模拟预测数据框架
    forecast_data = []
    for attraction in attraction_list:
        for ts in date_range:
            forecast_data.append({
                "date": ts,
                "attraction": attraction,
                "wait_time_max": np.random.randint(10, 120),  # 模拟等待时间
                "attendance": np.random.randint(50, 500),     # 模拟客流量
                "capacity_utilization": np.random.uniform(60, 100),  # 模拟容量利用率
                "hour": ts.hour,
                "time_slot": ts.strftime("%H:%M")
            })
    
    return pd.DataFrame(forecast_data)

# 更新 __all__ 以导出新函数
__all__ = ["load_forecast_data"]