{{ config(
    materialized='incremental',
    unique_key='product_id'
) }}

With products as(
    select *
    from {{ ref('stg_products') }}
)

select *
from products

