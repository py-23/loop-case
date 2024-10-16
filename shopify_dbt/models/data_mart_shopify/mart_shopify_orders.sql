
With orders as(
    select *
    from {{ ref('int_shopify_orders') }}
    --where id = 1
)

select *
from orders

