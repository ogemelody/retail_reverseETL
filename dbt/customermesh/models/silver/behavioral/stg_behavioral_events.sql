 with source as (

    select *
    from {{ source('landing' , 'behavioral_events') }}

 ),

 renamed as (

        select
            raw_record:source_record_id::varchar as source_record_id,
            raw_record:source_system::varchar as source_system,
            raw_record:source_entity::varchar as source_entity,

            raw_record:payload:anonymous_id::varchar as anonymous_id,
            raw_record:payload:event_type::varchar as event_type,
            raw_record:payload:user_id::varchar as user_id,
            raw_record:payload:product_id::varchar as product_id,

            raw_record:operation::varchar as operation,
            raw_record:business_event_timestamp::timestamp_TZ as business_event_timestamp,
            raw_record:ingestion_timestamp::timestamp_TZ as ingestion_timestamp,
            raw_record:late_arrival::boolean as late_arrival,
            raw_record:batch_id::varchar as batch_id,
            raw_record:schema_version::varchar as schema_version,


            file_name as source_file,
            file_row_num as source_file_row,
            load_timestamp as warehouse_loaded_at
        from  source

 )


select *
from renamed
