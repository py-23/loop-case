{{ config(materialized='table') }}

WITH raw_orders AS (
    SELECT
        *
    FROM `shopify_raw_data.orders`
)

SELECT *
FROM raw_orders
where id is not null
