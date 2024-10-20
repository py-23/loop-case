{{ config(materialized='table') }}

With orders as(
    select *
    from {{ ref('stg_orders') }}
)

select *
from orders

