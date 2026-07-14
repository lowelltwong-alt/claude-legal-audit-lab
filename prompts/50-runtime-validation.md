# Runtime and contractual validation plan

The source repository cannot reveal the full hosted runtime. Design an authorized, synthetic test program that can distinguish:

- local file persistence;
- inference request content;
- connector retrieval vs copying/indexing;
- provider-side retention;
- telemetry/metadata collection;
- human/support access;
- feedback submission;
- model evaluation use;
- generalized training/fine-tuning;
- cross-tenant or cross-product use.

Use a dedicated test tenant, synthetic agreements, unique canary identifiers, instrumented connector endpoints, network/DNS/proxy logs, API request capture where contractually and technically permitted, admin/audit logs, deletion requests, and export/termination tests.

Do not propose probing other customers, extracting model memorization of real data, evading controls, or placing privileged/client information into the experiment.

For each test include hypothesis, setup, evidence collected, success/failure criterion, limitations, and legal/contract approval required. State explicitly that an absence of observed leakage in a limited test does not prove absence of retention or training.
