{{ config(materialized='table') }}

WITH order_line_items AS (
    SELECT *
    FROM {{ ref('stg_order_line_items') }}
),

orders AS (
    SELECT *
    FROM {{ ref('int_orders') }}
),

sales_items AS (
    SELECT
        order_line_items.*,
        orders.created_at,
        orders.currency,
        orders.customer_id,
        order_line_items.sales_quantity * CAST(order_line_items.sales_price AS FLOAT64) AS total_sales_amount,
        (order_line_items.sales_quantity * CAST(order_line_items.sales_price AS FLOAT64) - CAST(order_line_items.sales_discount AS FLOAT64)) AS after_discount_sales_amount
    FROM order_line_items
    LEFT JOIN orders
    ON order_line_items.order_parent_id = orders.parent_id
)

SELECT *
FROM sales_items
