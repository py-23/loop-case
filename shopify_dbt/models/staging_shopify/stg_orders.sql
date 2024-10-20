{{ config(materialized='table') }}

WITH raw_orders AS (
    SELECT
        id AS order_id,
        created_at,
        confirmed,
        currency,
        current_total_discounts AS order_total_discounts,
        current_total_price AS order_total_price,
        current_total_tax AS order_total_tax,
        order_number,
        subtotal_price,
        customer__id as customer_id,
        _dlt_id AS parent_id
    FROM `shopify_raw_data.orders`
),

-- Deduplicate the data based on `sales_item_id`
deduplicated_orders AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY order_id) AS row_num
    FROM raw_orders
)

-- Select only the first occurrence of each `sales_item_id`
SELECT
    *
FROM deduplicated_orders
WHERE row_num = 1  -- Keep only the first occurrence
