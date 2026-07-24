-- Nivell 1
-- exercici 2

-- Pas 1 / MOCKING
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_silver.transactions_recent` AS
WITH nuevo_timestamp AS (
  SELECT 
    * EXCEPT(timestamp),
    TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL CAST(RAND() * 50 AS INT64) DAY) AS time,
FROM `sprint3-analytics-melina.sprint3_silver.transactions_clean`
)
SELECT * FROM nuevo_timestamp;

-- Pas 2 / PARTITION & CLUSTER
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized`
PARTITION BY DATE(time)
CLUSTER BY business_id
AS
SELECT *
FROM `sprint3-analytics-melina.sprint3_silver.transactions_recent`;

-- exercici 3
-- Pas 1
SELECT *
FROM `sprint3-analytics-melina.sprint3_silver.transactions_recent`
WHERE time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);

-- Pas 2
SELECT *
FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized`
WHERE time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY);

-- exercici 4
CREATE MATERIALIZED VIEW `sprint3-analytics-melina.sprint3_gold.mv_daily_sales` AS
SELECT 
DATE(time) AS fecha_venta, 
SUM(amount) AS total_ventas
FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized`
WHERE declined = 0
GROUP BY fecha_venta;

SELECT *
FROM `sprint3-analytics-melina.sprint3_gold.mv_daily_sales`
WHERE fecha_venta = CURRENT_DATE(); -- se filtra por fecha en la misma consulta, aqui con la fecha de hoy.

-- Nivell 2
-- exercici 1

WITH VIP_Stats AS (
  SELECT
    user_id,
    SUM(amount) AS gasto_total,
    COUNT(transaction_id) AS numero_compras,
    ROUND(AVG(amount),2) AS ticket_medio,
    MAX(amount) AS compra_maxima
  FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized`
  WHERE declined = 0
  GROUP BY user_id
  HAVING SUM(amount) > 500
)
SELECT 
  v.user_id, 
  u.name, u.surname, u.email, v.numero_compras, v.ticket_medio, v.compra_maxima, v.gasto_total
FROM VIP_Stats v
JOIN `sprint3-analytics-melina.sprint3_silver.users_combined` u 
  ON v.user_id = u.user_id
ORDER BY v.gasto_total DESC;

-- exercici 2

WITH fechas AS (
  SELECT
  fecha_venta,
  total_ventas,
  total_ventas AS ventas_hoy,
  LAG(total_ventas) OVER(ORDER BY fecha_venta) AS ventas_ayer
  FROM `sprint3-analytics-melina.sprint3_gold.mv_daily_sales`
)

SELECT 
  fecha_venta,
  ventas_hoy,
  ventas_ayer,
  ROUND((ventas_hoy - ventas_ayer/ventas_ayer) * 100,2) AS Diff_Porcentual
FROM fechas
WHERE fecha_venta = CURRENT_DATE(); -- este filtro es optional, aqui es solo si queremos ver los resultados de hoy vs ayer, en vez de recuperar todas las filas de ventas.

-- P2P feedback: Faltaría NULLIF para contemplar casos en los que "ventas_ayer" = 0 ventas, ya que daria error al intentar dividir entre 0.
-- ROUND(((ventas_hoy - ventas_ayer) / NULLIF(ventas_ayer,0)) * 100, 2)

-- Exercici 3  

SELECT
fecha_venta,
ROUND(total_ventas,2) AS ventas_dia,
ROUND(SUM(total_ventas) OVER (PARTITION BY EXTRACT (YEAR FROM fecha_venta) ORDER BY fecha_venta ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW),2) AS ventas_acumulades_YTD
FROM `sprint3-analytics-melina.sprint3_gold.mv_daily_sales`;

-- Exercici 4

WITH orden_compras AS (
  SELECT
    ROW_NUMBER() OVER (PARTITION BY t.user_id ORDER BY t.time ASC) AS orden,  -- ordena las compras por usuario por fecha ascendente, y se les asigna un numero (1 para la 1ra compra, 2 para la 2da,..)
    t.user_id,
    t.amount,
    t.time
  FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized` t
  WHERE t.declined = 0
  QUALIFY orden <= 3  -- selecciona las 3 primeras compras 
)

SELECT
  u.user_id,
  CONCAT(u.name, ' ', u.surname) AS nombre_completo,
  u.email,

  MAX(IF(o.orden = 3, DATE(o.time), NULL)) AS fecha_tercera_compra, -- IF devuelve la fecha donde orden = 3, devuelve NULL a las demás filas.
  MAX(IF(o.orden = 3, o.amount, NULL)) AS importe_tercera_compra,    -- MAX(...) recupera el único valor que no es nulo
  AVG(o.amount) AS media_3primeras_compras --  se hereda el filtro de la CTE, el amount ya solo contiene las primeras 3 compras

FROM orden_compras o
JOIN `sprint3-analytics-melina.sprint3_silver.users_combined` u
  ON o.user_id = u.user_id
GROUP BY u.user_id, nombre_completo, u.email
ORDER BY media_3primeras_compras DESC;

-- Nivell 3
-- Exercici 1

CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_gold.dim_transactions_flat` AS
SELECT
  t.transaction_id,
  card_id,
  business_id,
  declined,
  product_id,
  user_id,
  longitude,
  lat,
  time,
  p.name,
  p.price,
FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized` AS t
CROSS JOIN UNNEST(t.product_ids) AS product_id
JOIN `sprint3-analytics-melina.sprint3_gold.product_sales_ranking` AS p
ON product_id = p.product_id;

-- Exercici 2
SELECT
name,
product_id,
COUNT(product_id) AS numero_ventas
FROM `sprint3-analytics-melina.sprint3_gold.dim_transactions_flat`
GROUP BY name, product_id
ORDER BY numero_ventas DESC
LIMIT 5

-- Exercici 3
-- función para icluir el calculo de impuestos

CREATE OR REPLACE FUNCTION `sprint3-analytics-melina.sprint3_gold.calculate_tax_amount`(porcentaje FLOAT64)
RETURNS FLOAT64
AS (porcentaje * 0.21);

-- modificación de la creacion de tabla dim_transactions_flat que incluye la función calculate_tax_amount

CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_gold.dim_transactions_flat` AS
SELECT
  t.transaction_id,
  card_id,
  business_id,
  declined,
  product_id,
  user_id,
  longitude,
  lat,
  time,
  p.name,
  p.price,
  price + `sprint3-analytics-melina.sprint3_gold.calculate_tax_amount`(price) AS product_price_tax_inc
FROM `sprint3-analytics-melina.sprint3_gold.fact_transactions_optimized` AS t
CROSS JOIN UNNEST(t.product_ids) AS product_id
JOIN `sprint3-analytics-melina.sprint3_gold.product_sales_ranking` AS p
ON product_id = p.product_id;