#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

REQUIRED = {
    'pattern-match': {'pattern_id','category','name','path','line','text'},
    'coverage-receipt': {'path','sha256','lines_reviewed','status'},
}

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('path'); ap.add_argument('--kind',choices=REQUIRED,required=True); args=ap.parse_args()
    p=Path(args.path); errors=[]; n=0
    for i,line in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if not line.strip(): continue
        n+=1
        try: obj=json.loads(line)
        except json.JSONDecodeError as e: errors.append(f'line {i}: invalid JSON: {e}'); continue
        missing=REQUIRED[args.kind]-set(obj)
        if missing: errors.append(f'line {i}: missing {sorted(missing)}')
    if errors:
        print('\n'.join(errors)); return 1
    print(f'validated {n} {args.kind} records')
    return 0

if __name__=='__main__': raise SystemExit(main())
