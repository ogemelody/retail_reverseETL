select *
from {{ ref('stg_behavioral_events')  }}
where anonymous_id is null
    and user_id is null
