{{ config(materialized='view') }}

with intent as (
    select event_id, canonical_customer_id, product_id, event_type, event_at
    from {{ ref('fact_customer_events') }}
    where canonical_customer_id is not null
      and event_type in ('product_viewed', 'add_to_cart', 'checkout_started')
), online_orders as (
    select orders.canonical_customer_id, orders.order_id, orders.ordered_at, order_item.product_id
    from {{ ref('fact_ecommerce_orders') }} orders
    join {{ ref('stg_ecommerce_order_items') }} order_item
      on order_item.order_id = orders.order_id
    where orders.canonical_customer_id is not null
), later_pos as (
    select canonical_customer_id, transaction_id, product_id, purchased_at, amount, store_id
    from {{ ref('fact_pos_transactions') }}
    where canonical_customer_id is not null
), candidates as (
    select
        i.event_id as intent_event_id,
        i.canonical_customer_id,
        i.product_id,
        i.event_type as intent_event_type,
        i.event_at as intent_at,
        p.transaction_id,
        p.purchased_at as offline_purchase_at,
        p.store_id,
        p.amount as offline_amount,
        case when o.order_id is null then true else false end as no_online_conversion
    from intent i
    join later_pos p
      on p.canonical_customer_id = i.canonical_customer_id
     and p.product_id = i.product_id
     and p.purchased_at > i.event_at
     and p.purchased_at <= dateadd('day', 30, i.event_at)
    left join online_orders o
      on o.canonical_customer_id = i.canonical_customer_id
     and o.product_id = i.product_id
     and o.ordered_at > i.event_at
     and o.ordered_at <= dateadd('day', 30, i.event_at)
)

select *
from candidates
where no_online_conversion
qualify row_number() over (partition by intent_event_id order by offline_purchase_at, transaction_id) = 1
