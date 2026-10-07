{{ config(materialized='view') }}

select
    p.source_record_id as transaction_id,
    p.loyalty_id,
    i.canonical_customer_id,
    p.product_id,
    p.store_id,
    p.amount,
    p.currency,
    p.business_event_timestamp as purchased_at,
    p.source_updated_at,
    p.ingestion_timestamp,
    p.late_arrival,
    p.batch_id,
    p.source_file,
    p.source_file_row
from {{ ref('stg_pos_transactions') }} p
left join {{ ref('int_customer_identity_map') }} i
  on i.source_system = 'pos'
 and i.source_identifier = p.loyalty_id
where p.operation <> 'delete'
