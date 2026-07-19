#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, hashlib, json, os, re
from pathlib import Path

TEXT_EXTS = {'.md','.txt','.json','.yaml','.yml','.py','.sh','.toml','.ini','.cfg','.csv','.xml','.html','.js','.ts','.gitignore',''}
SKIP_DIRS = {'.git','node_modules','vendor','.venv','venv','__pycache__'}
URL_RE = re.compile(r'https?://[^\s\]\)\>"\']+')


def is_text(path: Path) -> bool:
    if path.name in {'.gitignore','.mcp.json'}:
        return True
    if path.suffix.lower() in TEXT_EXTS:
        try:
            data = path.read_bytes()[:4096]
            return b'\x00' not in data
        except OSError:
            return False
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('target')
    ap.add_argument('--out', default='results')
    args = ap.parse_args()
    target = Path(args.target).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if not target.is_dir():
        raise SystemExit(f'target not found: {target}')
    rows, urls = [], []
    for path in sorted(target.rglob('*')):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(target).as_posix()
        data = path.read_bytes()
        record = {'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'text': False, 'lines': 0, 'extension': path.suffix.lower()}
        if is_text(path):
            text = data.decode('utf-8', errors='replace')
            record['text'] = True
            record['lines'] = len(text.splitlines())
            for i, line in enumerate(text.splitlines(), 1):
                for url in URL_RE.findall(line):
                    urls.append({'path': rel, 'line': i, 'url': url.rstrip('.,;')})
        rows.append(record)
    (out / 'inventory.json').write_text(json.dumps({'target': str(target), 'files': rows}, indent=2) + '\n')
    with (out / 'coverage.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['path','sha256','text','lines','bytes','extension','status','reviewer','notes'])
        w.writeheader()
        for r in rows:
            w.writerow({**r, 'status':'unreviewed','reviewer':'','notes':''})
    with (out / 'url-index.csv').open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['path','line','url'])
        w.writeheader(); w.writerows(urls)
    print(f'inventoried {len(rows)} files; {sum(r["lines"] for r in rows)} text lines; {len(urls)} URL occurrences')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
