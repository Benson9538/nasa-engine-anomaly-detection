
1. 哪幾台引擎最危險
SELECT
    unit_id,
    COUNT(*) AS total_alerts,
    SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) AS high_alerts,
    SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) AS medium_alerts,
    SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) AS low_alerts
FROM alerts
GROUP BY unit_id
ORDER BY total_alerts DESC
LIMIT 10;

2. 哪個感測器最常觸發警報
# SUM(COUNT(*)) OVER () : Total count of all groups , () 空白表示對所有資料運算 0 ，不受 GROUP BY 影響
SELECT
    sensor_name,
    COUNT(*) AS alerts_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
FROM alerts
GROUP BY sensor_name
ORDER BY alerts_count DESC

3. 引擎在 RUL 剩多少時開始出現異常
# CTE Common Table Expression : 把一段查詢的結果作為表繼續沿用

WITH first_alert AS (
    SELECT
        unit_id,
        MIN(cycle) AS first_alert_cycle
    FROM alerts
    GROUP BY unit_id
)
SELECT
    fa.unit_id,
    fa.first_alert_cycle,
    sr.rul AS rul_at_first_alert
FROM first_alert fa
JOIN sensor_readings sr ON fa.unit_id = sr.unit_id AND fa.first_alert_cycle = sr.cycle
ORDER BY rul_at_first_alert DESC
LIMIT 10;
-> 有些引擎在 RUL 還很高的時候就開始出現異常，可能會有偽陽的問題

4. 平均引擎在 RUL 剩多少時出現第一個警報
# CTE -> 將複雜的查詢拆分成多個步驟，讓每個步驟的邏輯更清晰

WITH first_alert AS (
    SELECT
        unit_id,
        MIN(cycle) AS first_alert_cycle
    FROM alerts
    GROUP BY unit_id
),
first_alert_rul AS (
    SELECT
        fa.unit_id,
        sr.rul AS rul_at_first_alert
    FROM first_alert fa
    JOIN sensor_readings sr ON fa.unit_id = sr.unit_id AND fa.first_alert_cycle = sr.CYCLE
)
SELECT
    ROUND(AVG(rul_at_first_alert) , 2) AS avg_rul_at_first_alert,
    MIN(rul_at_first_alert) AS min_rul_at_first_alert,
    MAX(rul_at_first_alert) AS max_rul_at_first_alert
FROM first_alert_rul;

-> 有些很早觸發，有些要壞了才觸發 -> z_score 方法有改善空間

