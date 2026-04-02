# 設備異常偵測系統

基於 NASA C-MAPSS 渦輪引擎資料集，建立一套完整的設備健康監測與異常偵測系統

## 資料說明

來源：NASA Prognostics Data Repository
資料集：FD001（100 台引擎，20,631 筆感測器記錄
特徵：21 個 sensor , 3 個 setting value

## 目標

透過感測器時序數據，偵測引擎退化異常，並以互動式 Dashboard 呈現分析結果

## Docker 執行方式
### 1. 複製環境變數範例
cp .env.example .env
### 填入自己的資料庫密碼

### 2. 啟動容器
docker compose up --build

### 3. 載入資料
docker compose exec app python sql/load_data.py

docker compose exec app python notebooks/anomaly_detection.py

### 4. 開啟瀏覽器，streamlit port 預設使用 8501 
### http://localhost:8501