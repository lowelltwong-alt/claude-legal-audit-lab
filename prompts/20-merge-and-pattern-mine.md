# Merge and pattern-mining pass

Input: six completed independent worker reports plus their coverage receipts.

1. Reject malformed or incomplete reports; do not treat missing workers as negative evidence.
2. Merge candidates only when one test/remediation would resolve every merged candidate.
3. Preserve dissent: if workers disagree on what evidence proves, retain the disagreement.
4. Build a canonical source-to-sink diagram for each sensitive asset.
5. Extract recurring semantic patterns and generate new static-search patterns, including synonyms, indirect phrasing, path conventions, and combinations of otherwise benign primitives.
6. Store generated patterns in `patterns/generated-patterns.json`. Include rationale and false-positive risks.
7. Compare the new canonical inventory with prior rounds and write novelty metrics.
8. Produce a remaining-coverage worklist.

Do not upgrade a claim from Inferred to Confirmed merely because multiple agents repeated it. Correlated model outputs are not independent evidence.
