{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

With orders as(
    select *
    from {{ ref('stg_orders') }}
)

select *
from orders

