{% set delete_hook = [] %}
{% if is_incremental() %}
    {% set delete_hook = [
        "delete from " ~ this ~ " where source_record_id in (select source_record_id from (select source_record_id, operation, row_number() over (partition by source_record_id order by source_updated_at desc, ingestion_timestamp desc, warehouse_loaded_at desc, source_file desc, source_file_row desc) as rn from " ~ ref('int_crm_contacts_deduplicated') ~ ") latest where rn = 1 and operation = 'delete')"
    ] %}
{% endif %}

{{ config(
    materialized='incremental',
    unique_key='source_record_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns',
    pre_hook=delete_hook
) }}

with source_versions as (

    select *
    from {{ ref('int_crm_contacts_deduplicated') }}
    {% if is_incremental() %}
    where warehouse_loaded_at >= (
        select dateadd('day', -7, max(warehouse_loaded_at))
        from {{ this }}
    )
    {% endif %}

), latest_source_state as (

    select
        *,
        row_number() over (
            partition by source_record_id
            order by
                source_updated_at desc,
                ingestion_timestamp desc,
                warehouse_loaded_at desc,
                source_file desc,
                source_file_row desc
        ) as source_state_rank
    from source_versions

)

select
    batch_id,
    business_event_timestamp,
    city,
    consent_status,
    email_hash,
    first_name,
    ingestion_timestamp,
    late_arrival,
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
    warehouse_loaded_at
from latest_source_state
where source_state_rank = 1
  and operation <> 'delete'
