
With orders as(
    select *
    from {{ ref('int_order_line_items') }}
)

select *
from orders

