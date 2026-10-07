{{ config(materialized='table') }}

with identity as (
    select *
    from {{ ref('int_customer_identity_map') }}
    where canonical_customer_id is not null
), crm_profiles as (
    select
        i.canonical_customer_id,
        c.first_name,
        c.last_name,
        c.city,
        c.email_hash,
        c.phone_hash,
        c.consent_status,
        c.source_updated_at,
        2 as source_priority
    from identity i
    join {{ ref('crm_contacts_current') }} c
      on i.source_system = 'crm'
     and i.source_identifier = c.source_record_id
), ecommerce_profiles as (
    select
        i.canonical_customer_id,
        e.first_name,
        e.last_name,
        e.city,
        e.email_hash,
        cast(null as varchar) as phone_hash,
        cast(null as varchar) as consent_status,
        e.source_updated_at,
        1 as source_priority
    from identity i
    join {{ ref('stg_ecommerce_customers') }} e
      on i.source_system = 'ecommerce'
     and i.source_identifier = e.ecommerce_customer_id
), profile_ranked as (
    select *, row_number() over (
        partition by canonical_customer_id
        order by source_priority desc, source_updated_at desc, email_hash asc nulls last
    ) as rn
    from (
        select * from crm_profiles
        union all
        select * from ecommerce_profiles
    ) profiles
), consent_ranked as (
    select canonical_customer_id, consent_status,
           row_number() over (partition by canonical_customer_id order by source_updated_at desc, source_identifier asc) as rn
    from (
        select i.canonical_customer_id, c.consent_status, c.source_updated_at, c.source_record_id as source_identifier
        from identity i
        join {{ ref('crm_contacts_current') }} c
          on i.source_system = 'crm' and i.source_identifier = c.source_record_id
    ) crm
), coverage as (
    select
        canonical_customer_id,
        count(distinct source_system) as source_system_count,
        listagg(distinct source_system, ',') within group (order by source_system) as source_systems,
        min(source_seen_at) as first_seen_at,
        max(source_seen_at) as last_seen_at,
        count_if(identity_type = 'anonymous_session') > 0 as has_anonymous_behavior,
        count_if(identity_type = 'authenticated_behavioral_user') > 0 as has_authenticated_behavior,
        count_if(source_system = 'ecommerce') > 0 as has_ecommerce,
        count_if(source_system = 'crm') > 0 as has_crm,
        count_if(source_system = 'pos') > 0 as has_pos
    from identity
    group by canonical_customer_id
)

select
    c.canonical_customer_id,
    p.first_name,
    p.last_name,
    p.city,
    p.email_hash,
    p.phone_hash,
    coalesce(cr.consent_status, 'unknown') as consent_status,
    c.source_system_count,
    c.source_systems,
    c.first_seen_at,
    c.last_seen_at,
    c.has_anonymous_behavior,
    c.has_authenticated_behavior,
    c.has_ecommerce,
    c.has_crm,
    c.has_pos
from coverage c
join profile_ranked p on p.canonical_customer_id = c.canonical_customer_id and p.rn = 1
left join consent_ranked cr on cr.canonical_customer_id = c.canonical_customer_id and cr.rn = 1
