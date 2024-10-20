{{ config(materialized='table') }}

With sales as(
    select
        sales_item_id,
        sales_quantity,
        created_at,
        product_id,
        customer_id,
        order_parent_id,
        fulfillable_quantity,
        sales_item_weight,
        product_name,
        currency,
        sales_price,
        sales_discount,
        total_sales_amount,
        after_discount_sales_amount,
        gift_card_used,
        fulfillment_status
    from {{ ref('int_order_line_items') }}
)

select *
from sales

