import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import subprocess

import os
from dotenv import load_dotenv

# 自動讀取 .env 檔案中的環境變數
# override=False : 已經有環境變數就不覆蓋，避免使用的被 .env 覆蓋
load_dotenv(override=False)

DB_CONFIG ={
    "host":       os.getenv("DB_HOST"),
    # 第二個是預設值
    "port":       os.getenv("DB_PORT" , "5432"),
    "database":   os.getenv("DB_NAME"),
    "user":       os.getenv("DB_USER"),
    "password":   os.getenv("DB_PASSWORD")
}

# 每次使用者互動都會重新執行 app.py , 透過 cache 只建立一次連線，沒改變就不重新處理

# 建立資料庫連線，用 cache 避免重新連線
@st.cache_resource
def get_engine():
    engine = create_engine(
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return engine

# 讀取資料
@st.cache_data
def load_data():
    engine = get_engine()
    df_sensors = pd.read_sql("SELECT * FROM sensor_readings" , engine)
    df_alerts = pd.read_sql("SELECT * FROM alerts" , engine)
    return df_sensors , df_alerts

st.set_page_config(
    page_title="Engine Health Dashboard",
    layout="wide"
)

st.title("設備異常偵測 Dashboard")
st.markdown("基於 NASA C-MAPSS 渦輪引擎資料集")

df_sensors , df_alerts = load_data()

col1 , col2 , col3 = st.columns(3)

with col1:
    st.metric("引擎總數" , df_sensors["unit_id"].nunique())
    
with col2:
    st.metric("總警報數" , len(df_alerts))
    
with col3:
    high_alerts = len(df_alerts[df_alerts["severity"] == "HIGH"])
    st.metric("高風險警報數" , high_alerts)
    
# streamlit run app.py 

import plotly.express as px

# sidebar : 左邊側邊攔

st.sidebar.header("篩選條件")

unit_ids = sorted(df_sensors["unit_id"].unique())
selected_unit = st.sidebar.selectbox(
    "選擇引擎",
    unit_ids,
    format_func = lambda x : f"引擎 {x}"
)

df_unit = df_sensors[df_sensors["unit_id"] == selected_unit]

# anomaly_detection.py 中透過 z-score 計算出會變化的感測器
useful_sensors = [
    "sensor_2", "sensor_3", "sensor_4", "sensor_7", "sensor_8",
    "sensor_9", "sensor_11", "sensor_12", "sensor_13", "sensor_14",
    "sensor_15", "sensor_17", "sensor_20", "sensor_21"    
]

selected_sensor = st.sidebar.selectbox(
    "選擇感測器",
    useful_sensors
)

# 感測器趨勢圖

st.subheader(f"引擎 {selected_unit} | {selected_sensor} 趨勢")

fig = px.line(
    df_unit,
    x = "cycle",
    y = selected_sensor,
    title = f"引擎 {selected_unit} - {selected_sensor} 隨時間變化",
    labels = {"cycle" : "運行週期" , selected_sensor: "感測器數值"}
)

# 標記異常點

df_unit_alerts = df_alerts[
    (df_alerts["unit_id"] == selected_unit) &
    (df_alerts["sensor_name"] == selected_sensor)
]

if len(df_unit_alerts) > 0:
    df_anomaly_points = df_unit[
        df_unit["cycle"].isin(df_unit_alerts["cycle"])
    ]
    fig.add_scatter(
        x = df_anomaly_points["cycle"],
        y = df_anomaly_points[selected_sensor],
        mode = "markers",
        marker = dict(color = "red" , size = 8),
        name = "異常點"
    )
    
st.plotly_chart(fig)

# 分隔線
st.divider()

col_left , col_right = st.columns(2)

with col_left:
    st.subheader("各感測器警報分布")
    
    sensor_alert_count = (
        df_alerts.groupby("sensor_name")
        .size()
        .reset_index(name = "count")
        .sort_values("count" , ascending = False)
    )
    # pie 圓餅圖 : 各部分佔整體的比例
    fig_pie = px.pie(
        sensor_alert_count,
        names = "sensor_name",
        values = "count",
        title = "各感測器觸發警報比例"
    )
    st.plotly_chart(fig_pie)
    
with col_right:
    st.subheader("引擎危險排名")
    
    engine_alert_count = (
        df_alerts.groupby("unit_id")
        .size()
        .reset_index(name = "total_alerts")
        .sort_values("total_alerts" , ascending = False)
        .head(10)
    )
    
    # bar 長條圖 : 各類別的數值比較
    fig_bar = px.bar(
        engine_alert_count,
        x = "unit_id",
        y = "total_alerts",
        title = "警報量前 10 名引擎",
        labels = {"unit_id" : "引擎編號" , "total_alerts" : "警報數量"},
        color = "total_alerts",
        color_continuous_scale = "Reds"
    )
    st.plotly_chart(fig_bar)

# 警報明細
st.divider()
st.subheader(f"引擎{selected_unit} 警報明細")

df_unit_alerts_all = df_alerts[df_alerts["unit_id"] == selected_unit]

if(len(df_unit_alerts_all) > 0):
    st.dataframe(
        df_unit_alerts_all[["cycle" , "sensor_name" , "severity"]]
        .sort_values("cycle")
    )