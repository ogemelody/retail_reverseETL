{{ config(materialized='view') }}

with identity_map as (
    select *
    from {{ ref('int_customer_identity_map') }}
    qualify row_number() over (
        partition by source_system, source_identifier
        order by
            case when match_status = 'resolved' then 1 else 2 end,
            case when match_strength = 'strong' then 1 when match_strength = 'source_native' then 2 else 3 end,
            canonical_customer_id
    ) = 1
)

select
    e.source_record_id || '|' || coalesce(e.source_file, 'inline') || '|' || to_varchar(e.source_file_row) as event_id,
    coalesce(explicit_map.canonical_customer_id, user_map.canonical_customer_id, anonymous_map.canonical_customer_id) as canonical_customer_id,
    e.anonymous_id,
    e.user_id,
    e.ecommerce_customer_id,
    e.event_type,
    e.product_id,
    e.business_event_timestamp as event_at,
    e.ingestion_timestamp,
    e.late_arrival,
    e.batch_id,
    e.source_file,
    e.source_file_row
from {{ ref('stg_behavioral_events') }} e
left join identity_map explicit_map
  on explicit_map.source_system = 'ecommerce'
 and explicit_map.source_identifier = e.ecommerce_customer_id
left join identity_map user_map
  on user_map.source_system = 'behavioral'
 and user_map.source_identifier = e.user_id
left join identity_map anonymous_map
  on anonymous_map.source_system = 'behavioral'
 and anonymous_map.source_identifier = e.anonymous_id
where e.operation <> 'delete'
