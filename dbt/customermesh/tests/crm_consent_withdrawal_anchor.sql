select source_record_id
from {{ ref('crm_contacts_current') }}
where source_record_id = 'CRM-29382'
  and coalesce(consent_status, '') <> 'withdrawn'

union all

select 'CRM-29382'
where not exists (
    select 1
    from {{ ref('crm_contacts_current') }}
    where source_record_id = 'CRM-29382'
)
