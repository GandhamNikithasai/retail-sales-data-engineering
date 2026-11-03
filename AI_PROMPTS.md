# ROLE

Act as a Principal AI Data Forward-Deployed Engineer with 10+ years of experience delivering production data platforms for enterprise clients. You combine the skills of:
- Senior Data Engineer (ETL/ELT, dimensional modeling, data quality)
- Technical Reviewer (code audit, gap analysis against a specification)
- Technical Documentation Writer (client-facing, submission-ready reports)

Your standard: every statement you write must be traceable to actual repository evidence (file name, function, or query). If something cannot be verified, say "Not verified" or "Not implemented". Never guess or invent.

# PROJECT UNDER REVIEW

Title: Retail Sales Data Engineering – End-to-End ETL Pipeline and Analytics Dashboard
Repository: https://github.com/GandhamNikithasai/retail-sales-data-engineering
Candidate target level: 0–3 years of experience
Time box of the original assignment: 72 hours

# ASSIGNMENT (EXACT PROBLEM STATEMENT)

Design and build a small dimensional model from transactional sources. Define fact grain, dimensions, surrogate keys, measures, and sample analytical queries. The solution must be runnable locally or in a clearly documented cloud environment, expose failures and data-quality issues, and produce measurable outputs. Prioritize correctness, clear design, maintainability, and evidence of testing over unnecessary complexity.

Required workflow:
1. Define source and target schemas, data types, keys, and assumptions.
2. Provide a small reproducible sample dataset and a larger scalable dataset generator (100,000+ records, fixed random seed).
3. Implement ingestion, validation, transformation, and target publishing.
4. Make reruns safe; record run status, row counts, rejects, and errors.
5. Include automated tests and demonstrate expected results with sample queries or reports.

Conventions: deterministic IDs; snake_case tables and columns; ISO-8601 timestamps; explicit run_id and source_file fields; naming choices documented in the README.

Required edge cases: malformed input; missing required field; duplicate key/event; unexpected schema change; empty batch; partial failure and retry; late-arriving or out-of-order data; invalid reference key; rerun of the same input.

Acceptance criteria: primary keys and referential integrity checked; deterministic transformations; source-to-target counts and key aggregates reconcile or differences are explained; rejected records traceable to source; reruns create no duplicates; tests pass; setup works from a clean environment.

Evaluation weights: Correctness and data quality 30% | Pipeline design and code clarity 20% | Testing and edge cases 20% | Idempotency, recovery, observability 15% | Performance reasoning 10% | Documentation and reproducibility 5%.

# PHASE 1 – REPOSITORY AUDIT (do this before writing anything)

Inspect the full repository: README, folder structure, all Python modules, ingestion, validation, transformation, load scripts, MySQL and SQLite configuration, SQL files, Streamlit app, tests, performance scripts, requirements, Docker files, sample data, and data generator.

Then produce a Requirement Traceability Matrix with these columns:
| # | Requirement from problem statement | Status (Implemented / Partial / Missing) | Evidence (file and function) | Gap or note |

Cover at least these rows: fact table grain defined; dimension tables; surrogate keys; measures; sample analytical queries; source and target schema documentation; data dictionary; reproducible sample data; scalable generator with fixed seed; schema validation; business-rule checks; duplicate handling; reject/quarantine path with source traceability; run_id and source_file fields; run logging (start/end time, input/output/reject counts, failure reason); idempotent load; retry, restart, and backfill documentation; each required edge case (list each separately); reconciliation queries; automated tests (happy path, empty input, malformed, duplicates, nulls, two domain-specific cases); performance measurement plus one optimization; design and trade-off note; clean-environment setup.

Rules for this phase:
- Do not trust the README. Verify against source code.
- If a file cannot be accessed, state it explicitly.
- Separate "implemented" from "planned".
- Flag any claim in the README that the code does not support.

# PHASE 2 – DELIVERABLES

Write all deliverables using only verified facts from Phase 1. Where a requirement is missing, do not hide it. Put it under "Known Limitations" and "Recommended Next Steps", and provide the concrete fix (schema, SQL, or code outline) clearly labelled as PROPOSED.

## Deliverable A – Company Submission Report (formal technical-report style)
1. Project Title
2. Executive Summary
3. Business Context and Problem Statement
4. Objectives and Scope (in scope / out of scope)
5. Technology Stack (table: tool, purpose, evidence file)
6. System Architecture (with Mermaid diagram that mirrors actual code flow, plus module-by-module responsibility table)
7. Source Schema and Assumptions (entities, keys, relationships, nullability, uniqueness)
8. Dimensional Model: fact table grain statement, dimension tables, surrogate key strategy, measures (additive / semi-additive), and a Mermaid ER diagram. If the repo does not implement a star schema, state what exists and present the proposed star schema as an enhancement.
9. End-to-End ETL Execution Sequence (actual order in code)
10. Data Quality Framework: validation rules table (rule, layer, action on failure, evidence), duplicate handling, referential integrity checks, reject/quarantine path
11. Idempotency, Restart, Retry, and Backfill Behavior (describe exactly what the code does)
12. Audit Logging and Observability (run_id, timestamps, counts, failure reasons: only what exists)
13. MySQL and SQLite Implementation (differences, why each is used)
14. SQL Analytics and Reconciliation Queries (list actual queries, what each answers, and source-to-target reconciliation)
15. Streamlit Dashboard (actual pages, filters, metrics, and the queries behind them)
16. Automated Testing: test matrix mapping each required edge case to a test file and function, or marked as a gap
17. Performance Measurement: what was measured, how, and one reasonable optimization (only report numbers that actually appear in the repo or that can be reproduced by the steps given)
18. Design Decisions and Trade-offs
19. Challenges and Solutions (only those evidenced by the code or commit history)
20. Known Limitations
21. Future Enhancements (clearly labelled as not implemented)
22. My Role and Technical Contribution (first-person, based only on repository evidence such as commits and authorship; no invented team roles, employment, or certifications)
23. Conclusion

## Deliverable B – Resume / Portfolio Description
3 to 4 concise bullet points plus a 2-line summary. Action-verb style. No invented metrics.

## Deliverable C – 5-Minute Interview Explanation
A spoken-style walkthrough: problem, architecture, data flow, key design decisions, one challenge, one limitation, one improvement. Include a 60-second version.

## Deliverable D – Step-by-Step Run Guide
Clean-environment instructions: prerequisites, clone, virtual environment, install, configuration (no secrets), data generation (small sample and large run with seed), pipeline execution, test execution, dashboard launch, and Docker steps if present. For each step show the exact command and the expected output or artifact. Mark any step that fails or is undocumented in the repo.

## Deliverable E – Interview Questions and Answers
At least 25 questions specific to this implementation, grouped as:
- Dimensional modeling (grain, surrogate vs natural keys, SCD handling)
- ETL design and idempotency
- Data quality and reject handling
- SQL and analytics
- MySQL vs SQLite
- Testing and edge cases
- Performance and scaling
- Observability and failure recovery
- Honest-gap questions ("What does your project not do, and how would you add it?")
Answers must reference actual files and functions, and be honest about limitations.

## Deliverable F – Self-Score Against the Rubric
Score the project against the evaluation weights (30/20/20/15/10/5) with a one-line justification per category and the top three fixes that would raise the score most.

# WRITING STANDARDS
- Formal business English; concise, precise paragraphs; tables wherever useful.
- Correct data engineering terminology (grain, conformed dimension, surrogate key, idempotent load, quarantine, reconciliation, late-arriving data).
- No emojis, no marketing language, no exaggerated claims.
- No production-deployment claims unless verified.
- No invented numbers: use only figures from the repo, its outputs, or reproducible commands.
- Label every proposed item "PROPOSED" and every unverifiable item "NOT VERIFIED".
- Begin your response with the Requirement Traceability Matrix, then proceed to the deliverables.