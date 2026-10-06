select source_record_id
from {{ ref('crm_contacts_current') }}
where source_record_id = 'CRM-DUP-29387'
group by source_record_id
having count(*) > 1
