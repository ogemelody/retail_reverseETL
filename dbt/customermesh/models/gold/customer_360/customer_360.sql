{{ config(materialized='view') }}

with orders as (
    select canonical_customer_id, count(*) as ecommerce_order_count, sum(total_amount) as ecommerce_revenue, max(ordered_at) as last_ecommerce_order_at
    from {{ ref('fact_ecommerce_orders') }}
    where canonical_customer_id is not null
    group by canonical_customer_id
), pos as (
    select canonical_customer_id, count(*) as pos_transaction_count, sum(amount) as pos_revenue, max(purchased_at) as last_pos_purchase_at
    from {{ ref('fact_pos_transactions') }}
    where canonical_customer_id is not null
    group by canonical_customer_id
), events as (
    select canonical_customer_id, count(*) as behavioral_event_count, min(event_at) as first_behavioral_event_at, max(event_at) as last_behavioral_event_at
    from {{ ref('fact_customer_events') }}
    where canonical_customer_id is not null
    group by canonical_customer_id
), refunds as (
    select canonical_customer_id, count(*) as refund_count, sum(refund_amount) as refund_amount
    from {{ ref('fact_ecommerce_refunds') }}
    where canonical_customer_id is not null
    group by canonical_customer_id
)

select
    c.canonical_customer_id,
    c.first_name,
    c.last_name,
    c.city,
    c.consent_status,
    coalesce(o.ecommerce_order_count, 0) as ecommerce_order_count,
    coalesce(o.ecommerce_revenue, 0) as ecommerce_revenue,
    coalesce(p.pos_transaction_count, 0) as pos_transaction_count,
    coalesce(p.pos_revenue, 0) as pos_revenue,
    coalesce(o.ecommerce_revenue, 0) + coalesce(p.pos_revenue, 0) as total_revenue,
    coalesce(r.refund_count, 0) as refund_count,
    coalesce(r.refund_amount, 0) as refund_amount,
    coalesce(e.behavioral_event_count, 0) as behavioral_event_count,
    least(c.first_seen_at, coalesce(e.first_behavioral_event_at, c.first_seen_at)) as first_activity_at,
    greatest(c.last_seen_at, coalesce(o.last_ecommerce_order_at, c.last_seen_at), coalesce(p.last_pos_purchase_at, c.last_seen_at), coalesce(e.last_behavioral_event_at, c.last_seen_at)) as last_activity_at,
    iff(o.canonical_customer_id is not null, true, false) as participated_in_ecommerce,
    iff(p.canonical_customer_id is not null, true, false) as participated_in_pos,
    iff(e.canonical_customer_id is not null, true, false) as participated_in_behavioral
from {{ ref('dim_customer') }} c
left join orders o on o.canonical_customer_id = c.canonical_customer_id
left join pos p on p.canonical_customer_id = c.canonical_customer_id
left join events e on e.canonical_customer_id = c.canonical_customer_id
left join refunds r on r.canonical_customer_id = c.canonical_customer_id
