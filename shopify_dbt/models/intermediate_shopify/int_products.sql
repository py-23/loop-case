{{ config(materialized='table') }}

With products as(
    select *
    from {{ ref('stg_products') }}
)

select *
from products

