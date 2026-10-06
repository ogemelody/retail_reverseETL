{{ config(materialized='view') }}

with source_versions as (

    select
        *,
        coalesce(
            logical_version,
            concat(
                source_record_id,
                '|', to_varchar(source_updated_at),
                '|', to_varchar(business_event_timestamp)
            )
        ) as logical_source_version_key
    from {{ ref('stg_crm_contacts') }}

), ranked as (

    select
        *,
        row_number() over (
            partition by source_record_id, logical_source_version_key
            order by
                delivery_instance asc nulls last,
                source_file asc,
                source_file_row asc,
                warehouse_loaded_at asc
        ) as duplicate_delivery_rank
    from source_versions

)

select
    batch_id,
    business_event_timestamp,
    city,
    consent_status,
    delivery_instance,
    email_hash,
    first_name,
    ingestion_timestamp,
    late_arrival,
    loyalty_id,
    last_name,
    logical_source_version_key,
    logical_version,
    operation,
    phone_hash,
    previous_consent_status,
    schema_version,
    source_entity,
    source_file,
    source_file_row,
    source_record_id,
    source_system,
    source_updated_at,
    tombstone,
    warehouse_loaded_at,
    duplicate_delivery_rank
from ranked
where duplicate_delivery_rank = 1
