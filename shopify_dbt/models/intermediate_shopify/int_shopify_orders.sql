
With orders as(
    select *
    from {{ ref('stg_shopify_orders') }}
    --where id = 1
)

select *
from orders

