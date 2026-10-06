select current_state.source_record_id
from {{ ref('crm_contacts_current') }} as current_state
join (
    select source_record_id
    from {{ ref('int_crm_contacts_deduplicated') }}
    qualify row_number() over (
        partition by source_record_id
        order by source_updated_at desc, ingestion_timestamp desc,
                 warehouse_loaded_at desc, source_file desc, source_file_row desc
    ) = 1
    and operation = 'delete'
) as latest_delete
    on latest_delete.source_record_id = current_state.source_record_id
