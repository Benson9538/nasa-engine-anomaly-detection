CREATE TABLE IF NOT EXISTS engines (
    unit_id     INT PRIMARY KEY,
    dataset     VARCHAR(10)  NOT NULL,
    fault_mode  VARCHAR(50),
    condition   VARCHAR(50)
);

/*
FOREIGN KEY : 避免資料不一致
    1. 參照完整性 Referential Integrity : 確保外鍵的值在參照表中存在
    2. 級聯刪除 Cascade : 當參照表中的記錄被刪除時，相關的外鍵記錄也會被自動刪除
*/

CREATE TABLE IF NOT EXISTS sensor_readings (
    unit_id     INT   NOT NULL,
    cycle       INT   NOT NULL,
    setting_1   FLOAT,
    setting_2   FLOAT,
    setting_3   FLOAT,
    sensor_1    FLOAT,
    sensor_2    FLOAT,
    sensor_3    FLOAT,
    sensor_4    FLOAT,
    sensor_5    FLOAT,
    sensor_6    FLOAT,
    sensor_7    FLOAT,
    sensor_8    FLOAT,
    sensor_9    FLOAT,
    sensor_10   FLOAT,
    sensor_11   FLOAT,
    sensor_12   FLOAT,
    sensor_13   FLOAT,
    sensor_14   FLOAT,
    sensor_15   FLOAT,
    sensor_16   FLOAT,
    sensor_17   FLOAT,
    sensor_18   FLOAT,
    sensor_19   FLOAT,
    sensor_20   FLOAT,
    sensor_21   FLOAT,
    rul         INT,
    PRIMARY KEY (unit_id, cycle),
    FOREIGN KEY (unit_id) REFERENCES engines(unit_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id    SERIAL PRIMARY KEY,
    unit_id     INT   NOT NULL,
    cycle       INT   NOT NULL,
    sensor_name VARCHAR(20),
    severity    VARCHAR(10),
    FOREIGN KEY (unit_id, cycle)
        REFERENCES sensor_readings(unit_id, cycle)
);