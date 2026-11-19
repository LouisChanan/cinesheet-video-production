#!/usr/bin/env python3
"""Create a local blank CineSheet JSON project. No media generation."""
import argparse, json
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--id',required=True)
ap.add_argument('--title',required=True)
ap.add_argument('--out',type=Path,required=True)
args=ap.parse_args()
tmpl=Path(__file__).resolve().parents[1]/'templates/production.template.json'
dat=json.loads(tmpl.read_text(encoding='utf-8'))
dat['project']['id']=args.id
dat['project']['title']=args.title
args.out.mkdir(parents=True,exist_ok=True)
path=args.out/'production.json'
if path.exists(): raise SystemExit(f'Refusing to overwrite existing {path}')
path.write_text(json.dumps(dat,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(args.out/'assets').mkdir(exist_ok=True)
print(f'Created draft template: {path} (incomplete until populated)')
