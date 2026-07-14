# Synthetic runtime lab

This folder defines safe runtime experiments. It deliberately contains no real client data, credentials, or live connector configuration.

1. Generate synthetic canaries:

```bash
python3 runtime-lab/generate_synthetic_case.py --out runtime-lab/generated
```

2. Review `docs/RUNTIME_VALIDATION_PLAN.md`.
3. Obtain firm security, privacy, ethics, and vendor authorization.
4. Use a dedicated test tenant and instrumented endpoints.
5. Store immutable logs under a separate controlled evidence repository; do not commit secrets here.

The generated documents are fictional and include unique canaries to trace propagation within the authorized test environment.
