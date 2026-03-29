import pandas as pd
import subprocess

import os
from dotenv import load_dotenv
load_dotenv(override=False)

COLUMNS = [
    "unit_id", "cycle",
    "setting_1", "setting_2", "setting_3",
    "sensor_1", "sensor_2", "sensor_3", "sensor_4", "sensor_5",
    "sensor_6", "sensor_7", "sensor_8", "sensor_9", "sensor_10",
    "sensor_11", "sensor_12", "sensor_13", "sensor_14", "sensor_15",
    "sensor_16", "sensor_17", "sensor_18","sensor_19", "sensor_20",
    "sensor_21"
]

df = pd.read_csv(
    r"/mnt/d/Python_code/NASA/data/train_FD001.txt",
    sep=r'\s+', # \s : whitespace , + : >= 1
    header=None,
    names=COLUMNS
)

df["rul"] = (
    df.groupby("unit_id")["cycle"].transform("max") - df["cycle"]
)

sensor_cols = [f"sensor_{i}" for i in range(1,22)]
sensor_std = df[sensor_cols].std()

THRESHOLD = 0.01

# boolean indexing : 透過 T/F 過濾資料
# index() : 取出 index -> 'sensor_i'
# Index : 欄位名稱的集合 
useful_sensors = sensor_std[sensor_std > THRESHOLD].index.tolist()

def z_score(group , sensors , threshold=3.0):
    result = group.copy()
    
    for sensor in sensors:
        mean = group[sensor].mean()
        std = group[sensor].std()
        
        if std == 0:
            result[f"{sensor}_z_score"] = 0
            result[f"{sensor}_anomaly"] = False
        else:
            result[f"{sensor}_z_score"] = (group[sensor] - mean) / std
            result[f"{sensor}_anomaly"] = result[f"{sensor}_z_score"].abs() > threshold
        
    return result
    
# groupby : 預設會把 unit_id 加進 index -> 重複
# group_keys=False : 不把 unit_id 加進 index 
# apply : 對每個 group 執行 z_score 函式
# include_groups=False : 不把 group_keys 加進結果 -> 把 unit_id 排除 
df_result = df.groupby("unit_id" , group_keys=False).apply(
    lambda g: z_score(g , useful_sensors),
    include_groups=False
)
# 0 : 最左邊第一欄
df_result.insert(0, "unit_id", df["unit_id"].values)

anomaly_cols = [f"{sensor}_anomaly" for sensor in useful_sensors]
df_result["anomaly"] = df_result[anomaly_cols].any(axis=1)

print(f"Number of anomalies detected: {df_result['anomaly'].sum()}")
print(f"Percentage of anomalies detected: {df_result['anomaly'].mean():.2%}")

# 一筆異常可能有多個感測器同時異常
df_anomaly = df_result[df_result["anomaly"] == True].copy()

alert_record = []

for _ , row in df_anomaly.iterrows():
    for sensor in useful_sensors:
        if row[f"{sensor}_anomaly"]:
            
            z = abs(row[f"{sensor}_z_score"])
            if z > 5:
                severity = "HIGH"
            elif z > 4:
                severity = "MEDIUM"
            else:
                severity = "LOW"
                
            alert_record.append({
                "unit_id": int(row["unit_id"]),
                "cycle": int(row["cycle"]),
                "sensor_name": sensor,
                "severity": severity
            })
            
df_alert = pd.DataFrame(alert_record)

import psycopg2

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cursor = conn.cursor()

records = [
    (row["unit_id"] , row["cycle"] , row["sensor_name"] , row["severity"])
    for _ , row in df_alert.iterrows()
]

# 寫入前先檢查
cursor.execute("SELECT COUNT(*) FROM alerts;")
count = cursor.fetchone()[0]

if(count == 0):
    cursor.executemany(
        "INSERT INTO alerts (unit_id , cycle , sensor_name , severity) VALUES (%s , %s , %s , %s)",
        records
    )
    conn.commit()
    
print(f"Inserted {len(records)} alert records into the database.")

cursor.close()
conn.close()