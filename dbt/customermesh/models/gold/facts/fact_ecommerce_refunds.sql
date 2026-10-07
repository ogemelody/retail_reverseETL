{{ config(materialized='view') }}

select
    r.source_record_id as refund_id,
    r.order_id,
    o.canonical_customer_id,
    r.refund_amount,
    r.currency,
    r.business_event_timestamp as refunded_at,
    r.source_updated_at,
    r.ingestion_timestamp,
    r.late_arrival,
    r.batch_id,
    r.source_file,
    r.source_file_row
from {{ ref('stg_ecommerce_refunds') }} r
left join {{ ref('fact_ecommerce_orders') }} o on o.order_id = r.order_id
where r.operation <> 'delete'
