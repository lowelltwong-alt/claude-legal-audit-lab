#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('inventory')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--out', default='results/worklists')
    args = ap.parse_args()
    inv = json.loads(Path(args.inventory).read_text())['files']
    items = [r for r in inv if r.get('text')]
    items.sort(key=lambda r: (-r['lines'], r['path']))
    bins = [{'lines':0,'items':[]} for _ in range(args.workers)]
    for item in items:
        b = min(bins, key=lambda x: x['lines'])
        b['items'].append(item); b['lines'] += item['lines']
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    summary=[]
    for i,b in enumerate(bins,1):
        p = out / f'worker-{i}.csv'
        with p.open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=['path','sha256','lines','status','notes']); w.writeheader()
            for r in sorted(b['items'], key=lambda x:x['path']):
                w.writerow({'path':r['path'],'sha256':r['sha256'],'lines':r['lines'],'status':'assigned','notes':''})
        summary.append({'worker':i,'files':len(b['items']),'lines':b['lines'],'path':str(p)})
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
