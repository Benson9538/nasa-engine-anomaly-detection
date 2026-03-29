FROM python:3.12-slim

# 設定工作目錄
WORKDIR /app

# 用 COPY : 若沒改變 requirements -> Docker 會用快取，而非重新安裝
# Docker 的 layer cache ，跟下面的不同
COPY requirements.txt .

# pip 原本會將套件存進本機 cache，下次安裝就不用重新下載
# 但在 docker 中，每次建立 image 都是新的環境 -> 快取永遠用不到
# 透過 --no-cache-dir 避免 pip 使用快取
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Streamlit 預設使用 8501
EXPOSE 8501

CMD ["streamlit" , "run" , "dashboard/app.py" , "--server.address=0.0.0.0"]