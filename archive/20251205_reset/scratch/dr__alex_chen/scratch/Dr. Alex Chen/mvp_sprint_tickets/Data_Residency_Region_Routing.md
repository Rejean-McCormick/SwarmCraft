# Epic: Data Residency & Region Routing

Objective
- Implement region_id routing with data residency guarantees for US/EU, with a plan to expand regions as needed.

Acceptance Criteria
- region_id is captured and surfaced in user and session creation flows.
- Data storage is region-scoped; reads/writes are directed to the regional storage instance.
- Cross-region data transfer is disabled by default; DPAs and vendor commitments documented.
- Data flow map and DPAs are documented and accessible to the team.