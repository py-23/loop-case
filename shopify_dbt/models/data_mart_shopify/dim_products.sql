{{ config(
    materialized='incremental',
    unique_key='product_id'
) }}

With products as(
    select
        product_id,
        title,
        product_type,
        created_at,
        handle,
        status
    from {{ ref('int_products') }}
)

select *
from products

