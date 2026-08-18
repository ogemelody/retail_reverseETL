# RetailLoop
Customer intelligence & ad-activation platform for multi-location retail 
built to demonstrate end-to-end data engineering: 
multi-source ingestion, orchestration,
medallion-architecture transformation,
CI/CD for schema change, and reverse ETL activation.
 
---
## The challenge
 
A multi-location retail chain has its data trapped in
disconnected systems: GA4 knows what people browse, 
Shopify knows who buys, Klaviyo knows who engages with email,
and Google/Meta Ads know what's spent,but none of it is joined. 
The result: marketing spends the same acquisition budget on existing
loyal customers as on genuinely new prospects, nobody can say which 
store or channel drives long-term value, and upstream schema changes
(a new GA4 dimension, a renamed Shopify field) silently break downstream
dashboards.
 
## Proposed Solution
 
1. **Ingests** GA4, Shopify, Klaviyo, and ad-spend data through both scheduled Airflow DAGs and real-time FastAPI webhooks.
2. **Transforms** it through dbt's medallion architecture (bronze → silver → gold) into a unified customer, location, and marketing-attribution model in Snowflake.
3. **Enforces schema-change safety** through a GitHub Actions CI/CD pipeline with slim CI and automated drift detection.
4. **Closes the loop** with reverse ETL — pushing gold-layer audience segments (high-LTV, lapsed, cart-abandoners) directly back into Google Ads and Meta Custom Audiences.
5. Runs on infrastructure fully defined in Terraform, with autoscaling, least-privilege IAM, and cost guardrails built in from the start.


## Data sources
 
- **GA4** — `bigquery-public-data.ga4_obfuscated_sample_ecommerce` (public sample export)
- **Shopify** — Partners development store, seeded with 12 months of realistic order data
- **Klaviyo** — free-tier account for email engagement events
- **Google Ads / Meta Ads** — developer sandbox accounts for spend data and audience activation


## Tools
 
| Layer | Tool |
|---|---|
| Ingestion / orchestration | Apache Airflow (Cloud Composer 2) |
| Event-driven ingestion & activation | FastAPI, Docker, Cloud Run |
| Landing / bronze | BigQuery (GA4 native export), Snowflake |
| Transformation | dbt Core |
| Warehouse (silver/gold) | Snowflake |
| CI/CD | GitHub Actions, dbt slim CI, Elementary |
| Reverse ETL | Custom FastAPI services + Google Ads / Meta Marketing APIs |
| Infrastructure as code | Terraform (GCP + Snowflake providers) |
| Observability | Elementary, OpenLineage, Snowflake resource monitors |
 

## Project phases
 

| Phase | Focus                                                      |
|---|------------------------------------------------------------|
| 0 | Environment & IaC (Terraform)                              |
| 1 | Data source setup (Shopify, Klaviyo, Google/Meta Ads, GA4) |
| 2 | Batch ingestion (Airflow)                                  |
| 2.5 | Event-driven ingestion & activation (FastAPI + Docker)     |
| 3 | Transformation (dbt bronze → silver → gold)                |
| 4 | CI/CD & schema-change safety                               |
| 5 | Reverse ETL activation                                     |
| 6 | Observability                                              |
| 7 | Documentation                                              |