
With orders as(
    select *
    from {{ ref('stg_order_line_items') }}
)

select *
from orders

