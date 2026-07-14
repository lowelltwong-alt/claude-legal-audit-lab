#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path
import secrets
import json


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='runtime-lab/generated')
    args = p.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    canaries = {
        'firm': 'SYNTH-FIRM-' + secrets.token_hex(8),
        'playbook': 'SYNTH-PLAYBOOK-' + secrets.token_hex(8),
        'matter': 'SYNTH-MATTER-' + secrets.token_hex(8),
        'rationale': 'SYNTH-RATIONALE-' + secrets.token_hex(8),
    }
    (out / 'canaries.json').write_text(json.dumps(canaries, indent=2) + '\n')
    (out / 'synthetic-playbook.md').write_text(f"""# Fictional Contract Playbook\n\nFirm canary: `{canaries['firm']}`\nPlaybook canary: `{canaries['playbook']}`\n\n- Standard liability cap: 12 months of fees.\n- Fallback: 24 months only for fictional anchor customers.\n- Never accept: uncapped consequential damages.\n- Escalate: any data-training right or cap above 24 months.\n""")
    (out / 'synthetic-agreement.txt').write_text(f"""FICTIONAL AGREEMENT — NOT LEGAL MATERIAL\nMatter canary: {canaries['matter']}\nThe supplier requests a 36-month liability cap and a right to use customer content for model improvement.\n""")
    (out / 'synthetic-deviation-rationale.txt').write_text(f"""Rationale canary: {canaries['rationale']}\nFictional partner approved 36 months because the supplier is the only available provider and the board approved the exception.\n""")
    print(out)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
