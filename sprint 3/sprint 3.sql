-- Nivell 1: Entorn i Ingesta Híbrida (Code-First)
-- Exercici 1: Arquitectura de Dades

-- Dataset Físic sprint3_silver con codigo SQL
CREATE SCHEMA `sprint3-analytics-melina.sprint3_silver`
OPTIONS (
location = 'EU'
);

-- Exercici 2: Ingesta en Capa Bronze

-- tabla transactions_raw
CREATE OR REPLACE EXTERNAL TABLE `sprint3-analytics-melina.sprint3_bronze.transactions_raw`
OPTIONS (
  format = 'CSV',
  uris = ['gs://bootcamp-data-analytics-public/ERP/transactions.csv'],
  field_delimiter = ';' -- Delimitador: ; (Punt i coma)
  );

-- tabla companies_raw
CREATE OR REPLACE EXTERNAL TABLE `sprint3-analytics-melina.sprint3_bronze.companies_raw`
(
  company_id STRING,
  company_name STRING,
  phone STRING,
  email STRING,
  country STRING,
  website STRING
)
OPTIONS (
  format = 'CSV',
  uris = ['gs://bootcamp-data-analytics-public/ERP/companies.csv'],
  field_delimiter = ',',
  skip_leading_rows = 1 -- Capçalera: Ignora la 1a fila
  );

-- tabla american_users_raw
CREATE EXTERNAL TABLE `sprint3-analytics-melina.sprint3_bronze.american_users_raw`
OPTIONS (
  format = 'CSV',
  uris = ['gs://bootcamp-data-analytics-public/CRM/american_users.csv'],
  field_delimiter = ','
  );
  
 -- tabla european_users_raw
CREATE EXTERNAL TABLE `sprint3-analytics-melina.sprint3_bronze.european_users_raw`
OPTIONS (
  format = 'CSV',
  uris = ['gs://bootcamp-data-analytics-public/CRM/european_users.csv'],
  field_delimiter = ','
  );
  
-- tabla credit_cards_raw
CREATE EXTERNAL TABLE `sprint3-analytics-melina.sprint3_bronze.credit_cards_raw`
OPTIONS (
  format = 'CSV',
  uris = ['gs://bootcamp-data-analytics-public/CRM/credit_cards.csv'],
  field_delimiter = ','
  );  

-- tabla transactions_raw_native
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_bronze.transactions_raw_native` AS
SELECT * 
FROM `sprint3-analytics-melina.sprint3_bronze.transactions_raw`;

  
-- Exercici 5: els 5 dies amb més ingressos de l'any 2021.
SELECT DATE(timestamp) AS dia, ROUND(SUM(amount), 2) AS ingresos
FROM `sprint3_bronze.transactions_raw_native` t
WHERE t.declined = 0 AND EXTRACT(YEAR FROM timestamp) = 2021
GROUP BY DATE(timestamp)
ORDER BY ingresos DESC
LIMIT 5;

-- Exercici 6: Llista el nom, país i data de les transaccions realitzades per empreses que van fer operacions entre 100 i 200 euros en alguna d'aquestes dates: 29-04-2015, 20-07-2018 o 13-03-2024.
SELECT company_name, country, DATE(timestamp) AS fecha, ROUND(amount, 2) AS valor
FROM   `sprint3_bronze.companies_raw` c
INNER JOIN `sprint3_bronze.transactions_raw_native` t ON c.company_id = t.business_id
WHERE amount BETWEEN 100 AND 200 AND DATE(timestamp) IN ('2015-04-29','2018-07-20','2024-03-13')
ORDER BY amount DESC;

-- Nivell 2: Neteja i Transformació
-- Exercici 1: Neteja de Productes

CREATE TABLE `sprint3-analytics-melina.sprint3_silver.products_clean` AS
WITH datos_actualizados AS (
  SELECT 
    id AS product_id, 
    product_name AS name,
    price,
    colour,
    weight, 
    category, 
    brand, 
    launch_date,
    -- Limpieza de prefijo y conversión a entero
    SAFE_CAST(REPLACE(warehouse_id, 'WH-', '') AS INT64) AS warehouse_id,
    -- Limpieza de símbolo 
    SAFE_CAST(cost AS NUMERIC) AS cost
  FROM 
    `sprint3-analytics-melina.sprint3_bronze.products_raw`
)
SELECT * FROM datos_actualizados

-- Exercici 2: Creació de Transaccions Netes 
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_silver.transactions_clean` AS
WITH datos_actualizados AS (
  SELECT 
    id AS transaction_id,
card_id,
business_id,
timestamp,
SAFE_CAST(amount AS NUMERIC) AS amount,
declined,
ARRAY(
      SELECT SAFE_CAST(TRIM(id) AS INT64)
      FROM UNNEST(SPLIT(product_ids, ",")) AS id
    ) AS product_ids,
user_id,
SAFE_CAST(lat AS FLOAT64) AS lat,
SAFE_CAST(longitude AS FLOAT64) AS longitude,

FROM `sprint3-analytics-melina.sprint3_bronze.transactions_raw`
)
SELECT * FROM datos_actualizados



-- Exercici 3: Unificació d'Usuaris

CREATE TABLE `sprint3-analytics-melina.sprint3_silver.users_combined` AS

WITH datos_actualizados AS (
  SELECT 
    id AS user_id,
    name,
    surname,
    phone,
    email,
    birth_date,
    country,
    city,
    postal_code,
    address,
    'USA' AS origen -- Columna calculada de origen
  FROM 
    `sprint3-analytics-melina.sprint3_bronze.american_users_raw`
  
  UNION ALL
  
  SELECT 
    id AS user_id,
    name,
    surname,
    phone,
    email,
    birth_date,
    country,
    city,
    postal_code,
    address,
    'EU' AS origen   -- Columna calculada de origen
  FROM 
    `sprint3-analytics-melina.sprint3_bronze.european_users_raw`
)
SELECT * FROM datos_actualizados


-- Exercici 4: Materialització de Companyies i Targetes de Crèdit

-- tabla companies
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_silver.companies_clean` AS
SELECT *
FROM `sprint3-analytics-melina.sprint3_bronze.companies_raw`

-- tabla credit_cards
CREATE OR REPLACE TABLE `sprint3-analytics-melina.sprint3_silver.credit_cards_clean` AS
WITH datos_actualizados AS (
  SELECT 
    * EXCEPT(id),      
    id AS credit_cards_id
FROM `sprint3-analytics-melina.sprint3_bronze.credit_cards_raw`
)
SELECT * FROM datos_actualizados

-- Nivell 3: Presentació de Dades i Creació de Vistes
-- Exercici 1: La Vista de Màrqueting

CREATE VIEW `sprint3_gold.v_marketing_kpis` AS
SELECT c.company_name, c.phone, c.country, ROUND(AVG(t.amount), 2) AS media_compras,
  CASE
    WHEN AVG(t.amount) > 260 THEN 'Premium'
    ELSE 'Standard'
  END AS client_tier
FROM `sprint3-analytics-melina.sprint3_silver.companies_clean` c
INNER JOIN `sprint3-analytics-melina.sprint3_silver.transactions_clean` t
  ON c.company_id = t.business_id
GROUP BY c.company_name, c.phone, c.country
;

SELECT * FROM sprint3_gold.v_marketing_kpis        
ORDER BY media_compras DESC;


-- Exercici 2: Rànquing de Productes
CREATE TABLE `sprint3-analytics-melina.sprint3_gold.product_sales_ranking` AS
WITH aplanadas AS (
  SELECT 
    t.transaction_id,
    t_id AS product_ids_vendidos
  FROM `sprint3-analytics-melina.sprint3_silver.transactions_clean` t,
  UNNEST(t.product_ids) AS t_id
)
SELECT 
    p.product_id, p.name, p.price, p.colour, 
    COUNT(a.product_ids_vendidos) AS total_sold
FROM `sprint3-analytics-melina.sprint3_silver.products_clean` p
LEFT JOIN aplanadas a
  ON p.product_id = a.product_ids_vendidos
GROUP BY p.product_id, p.name, p.price, p.colour
ORDER BY total_sold DESC;

