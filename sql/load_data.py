import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import subprocess

def get_window_host():
    res = subprocess.run(
        ['ip' , 'route', 'show', 'default'],
        capture_output=True,
        text=True
    )
    return res.stdout.split()[2]

DB_CONFIG = {
    "host": get_window_host(),
    "port": 5432,
    "database": "db",
    "user": "postgres",
    "password": "benson0530"
}

COLUMNS = [
    "unit_id", "cycle",
    "setting_1", "setting_2", "setting_3",
    "sensor_1", "sensor_2", "sensor_3", "sensor_4", "sensor_5",
    "sensor_6", "sensor_7", "sensor_8", "sensor_9", "sensor_10",
    "sensor_11", "sensor_12", "sensor_13", "sensor_14", "sensor_15",
    "sensor_16", "sensor_17", "sensor_18","sensor_19", "sensor_20",
    "sensor_21"
]

df_train = pd.read_csv(
    r"/mnt/d/Python_code/NASA/data/train_FD001.txt",
    sep=r'\s+', # \s : whitespace , + : >= 1
    header=None,
    names=COLUMNS
)

df_train["rul"] = (
    df_train.groupby("unit_id")["cycle"].transform("max") - df_train["cycle"]
)

# psycopg2 + executemany : 適合筆數少，邏輯簡單的情況
# 建立連線
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# 寫入
engines = [
    (int(uid) , "FD001" , "HPC Degradation" , "Sea level") 
    for uid in df_train["unit_id"].unique()
]

cursor.executemany(
    "INSERT INTO engines (unit_id , dataset , condition , fault_mode) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
    engines
)
conn.commit()

# pandas + to_sql : 適合筆數多、欄位多的情況
# to_sql 只接受 SQLAlchemy 的 engine 物件

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

df_train.to_sql(
    name="sensor_readings",
    con=engine,
    if_exists="append", # append : 追加資料， replace : 刪除原表重建， fail : 若表存在則不執行
    index=False,
    method="multi", # multi : 一次插入多行， values : 使用 VALUES 語法， default : 預設方式
    chunksize=1000 # 每次插入的行數，適合大量資料
)

cursor.close()
conn.close()