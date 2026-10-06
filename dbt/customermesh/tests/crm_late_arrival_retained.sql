select source_record_id
from {{ ref('crm_contacts_current') }}
where source_record_id = 'CRM-LATE-29386'
  and not (late_arrival and business_event_timestamp < ingestion_timestamp)

union all

select 'CRM-LATE-29386'
where not exists (
    select 1
    from {{ ref('crm_contacts_current') }}
    where source_record_id = 'CRM-LATE-29386'
)
