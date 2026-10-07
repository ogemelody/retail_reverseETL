{{ config(materialized='view') }}

with intents as (
    select
        event_id as intent_event_id,
        canonical_customer_id,
        product_id,
        event_type as intent_event_type,
        event_at as intent_at
    from {{ ref('fact_customer_events') }}
    where canonical_customer_id is not null
      and event_type in ('add_to_cart', 'checkout_started')
), online_conversions as (
    select distinct o.canonical_customer_id, i.product_id
    from {{ ref('fact_ecommerce_orders') }} o
    join {{ ref('stg_ecommerce_order_items') }} i on i.order_id = o.order_id
    where o.canonical_customer_id is not null
), offline_conversions as (
    select distinct canonical_customer_id, product_id
    from {{ ref('fact_pos_transactions') }}
    where canonical_customer_id is not null
), eligible as (
    select
        i.*,
        'cart_abandoner' as audience_name,
        'resolved intent without ecommerce or qualifying POS conversion' as eligibility_reason
    from intents i
    left join online_conversions online
      on online.canonical_customer_id = i.canonical_customer_id
     and online.product_id = i.product_id
    left join offline_conversions offline
      on offline.canonical_customer_id = i.canonical_customer_id
     and offline.product_id = i.product_id
    where online.canonical_customer_id is null
      and offline.canonical_customer_id is null
)

select *
from eligible
qualify row_number() over (partition by canonical_customer_id, product_id order by intent_at desc, intent_event_id desc) = 1
