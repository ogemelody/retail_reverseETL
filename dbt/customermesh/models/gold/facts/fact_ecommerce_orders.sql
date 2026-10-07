{{ config(materialized='view') }}

select
    o.source_record_id as order_id,
    o.ecommerce_customer_id,
    i.canonical_customer_id,
    o.status,
    o.currency,
    o.total_amount,
    o.business_event_timestamp as ordered_at,
    o.source_updated_at,
    o.ingestion_timestamp,
    o.late_arrival,
    o.batch_id,
    o.source_file,
    o.source_file_row
from {{ ref('stg_ecommerce_orders') }} o
left join {{ ref('int_customer_identity_map') }} i
  on i.source_system = 'ecommerce'
 and i.source_identifier = o.ecommerce_customer_id
where o.operation <> 'delete'
