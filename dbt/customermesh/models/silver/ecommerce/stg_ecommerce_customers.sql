with source as (

    select *
    from {{ source('landing', 'ecommerce_customers') }}

),

renamed as (

    select
        raw_record:source_record_id::varchar as source_record_id,
        raw_record:source_system::varchar as source_system,
        raw_record:source_entity::varchar as source_entity,
        raw_record:operation::varchar as operation,
        raw_record:business_event_timestamp::timestamp_tz as business_event_timestamp,
        raw_record:source_updated_at::timestamp_tz as source_updated_at,
        raw_record:ingestion_timestamp::timestamp_tz as ingestion_timestamp,
        raw_record:late_arrival::boolean as late_arrival,
        raw_record:late_arrival_reason::varchar as late_arrival_reason,
        raw_record:batch_id::varchar as batch_id,
        raw_record:schema_version::varchar as schema_version,

        raw_record:payload:ecommerce_customer_id::varchar as ecommerce_customer_id,
        raw_record:payload:email_hash::varchar as email_hash,
        raw_record:payload:first_name::varchar as first_name,
        raw_record:payload:last_name::varchar as last_name,
        raw_record:payload:city::varchar as city,

        file_name as source_file,
        file_row_num as source_file_row,
        load_timestamp as warehouse_loaded_at
    from source

)

select *
from renamed
