import pandas as pd

# unit_id : 引擎編號
# cycle : 引擎運行的週期數
# setting_1 ~ setting_3 : 引擎的操作設定 -> 環境變數
# sensor_1 ~ sensor_21 : 感測器數值
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
    r"./NASA/data/train_FD001.txt",
    sep=r'\s+', # \s : whitespace , + : >= 1
    header=None,
    names=COLUMNS
)

# rul , remaining useful life : 剩幾個 cycle 會壞 -> 最後一個cycle - 當前cycle
df_train["rul"] = (
    df_train.groupby("unit_id")["cycle"].transform("max") - df_train["cycle"]
)

print(df_train.head())
print(f"len : {len(df_train)}")
print(f"engine num : {df_train['unit_id'].nunique()}")