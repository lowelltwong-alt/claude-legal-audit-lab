# Runtime validation plan

## Objective

Determine what leaves the firm-controlled environment and what the provider retains or reuses. Use synthetic data only.

## Test environment

- dedicated tenant and devices;
- synthetic firm name, lawyers, clients, matters, agreements, playbooks, and deviation history;
- unique canary strings per asset and workflow step;
- instrumented local/mock connectors where technically supported;
- organization-approved proxy, DNS, endpoint, and application audit logs;
- documented configuration and product tier.

## Experiments

1. **Onboarding payload test** — capture which interview answers and seed-document portions reach the model endpoint.
2. **Connector retrieval test** — determine whether the connector streams selected content, copies it, indexes it, or creates a durable cache.
3. **Local-persistence test** — inventory all local files before and after each skill.
4. **Hosted-agent upload test** — inspect skill bundles and agent definitions uploaded to `/v1/skills` and `/v1/agents`.
5. **Telemetry test** — inspect network calls for product analytics separate from model inference.
6. **Feedback-path test** — compare data flows with and without thumbs-up/down, support tickets, shared conversations, and bug reports.
7. **Deletion/export test** — request export and deletion, then verify local, admin, and provider attestations.
8. **Model substitution test** — replace the model while preserving firm-owned workflow definitions and measure rewrite effort.
9. **Canary follow-up** — search only within the authorized tenant's exports/logs for canary propagation. Do not probe unrelated users.

## Limits

Network observation can show transmission but usually cannot prove how a provider uses retained data internally. Contract terms, audits, attestations, and provider responses remain necessary. Failure to observe leakage in a finite test is not proof of non-retention or non-training.
