{{ config(materialized='table') }}

WITH raw_order_line_items AS (
    SELECT
        id AS sales_item_id,
        current_quantity AS sales_quantity,
        fulfillable_quantity,
        gift_card AS gift_card_used,
        grams AS sales_item_weight,
        name AS product_name,
        price AS sales_price,
        product_id,
        total_discount AS sales_discount,
        _dlt_parent_id AS order_parent_id,
        fulfillment_status
    FROM `shopify_raw_data.orders__line_items`
),

-- Deduplicate the data based on `sales_item_id`
deduplicated_order_line_items AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY sales_item_id) AS row_num
    FROM raw_order_line_items
)

-- Select only the first occurrence of each `sales_item_id`
SELECT
    *
FROM deduplicated_order_line_items
WHERE row_num = 1  -- Keep only the first occurrence
