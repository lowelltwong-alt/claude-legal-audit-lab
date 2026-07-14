#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

SKIP_DIRS = {'.git','node_modules','.venv','venv','__pycache__'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--patterns', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    target = Path(args.target).resolve()
    patterns = json.loads(Path(args.patterns).read_text())
    compiled = [(p, re.compile(p['regex'])) for p in patterns]
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with out.open('w', encoding='utf-8') as dest:
        for path in sorted(target.rglob('*')):
            if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                continue
            rel = path.relative_to(target).as_posix()
            for line_no, line in enumerate(text.splitlines(), 1):
                for p, rx in compiled:
                    if rx.search(line):
                        rec = {'pattern_id':p['id'],'category':p['category'],'name':p['name'],'path':rel,'line':line_no,'text':line[:1000],'rationale':p['rationale'],'false_positive':p['false_positive']}
                        dest.write(json.dumps(rec, ensure_ascii=False) + '\n')
                        count += 1
    print(f'wrote {count} heuristic matches to {out}')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
