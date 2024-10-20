{{ config(materialized='table') }}

WITH raw_products AS (
    SELECT
        id AS product_id,
        title,
        product_type,
        created_at,
        handle,
        status
    FROM `shopify_raw_data.products`
),

deduplicated_products AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY product_id) AS row_num
    FROM raw_products
)

SELECT
    *
FROM deduplicated_products
WHERE row_num = 1
