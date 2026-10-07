{{ config(materialized='table') }}

with product_observations as (
    select product_id, unit_price as amount, cast(null as varchar) as currency, business_event_timestamp, 'ecommerce' as source_system
    from {{ ref('stg_ecommerce_order_items') }}
    where product_id is not null
    union all
    select product_id, amount, currency, business_event_timestamp, 'pos'
    from {{ ref('stg_pos_transactions') }}
    where product_id is not null
    union all
    select product_id, amount, currency, business_event_timestamp, 'pos_return'
    from {{ ref('stg_pos_returns') }}
    where product_id is not null
), ranked as (
    select *, row_number() over (partition by product_id order by case when source_system = 'ecommerce' then 1 when source_system = 'pos' then 2 else 3 end, business_event_timestamp desc) as rn
    from product_observations
)
select
    product_id,
    amount as representative_amount,
    currency as representative_currency,
    min(business_event_timestamp) over (partition by product_id) as first_seen_at,
    max(business_event_timestamp) over (partition by product_id) as last_seen_at,
    listagg(distinct source_system, ',') within group (order by source_system) over (partition by product_id) as source_systems
from ranked
where rn = 1
