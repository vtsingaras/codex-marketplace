#!/usr/bin/env python3
"""Pin an existing catalog entry to a published release tag."""
import argparse
import json
from pathlib import Path
import subprocess

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('plugin')
parser.add_argument('release')
args=parser.parse_args()
path=Path(__file__).resolve().parents[1]/'.agents/plugins/marketplace.json'
catalog=json.loads(path.read_text())
entry=next((item for item in catalog['plugins'] if item['name']==args.plugin),None)
if entry is None:
    parser.error('Plugin is not in the catalog')
source=entry['source']
if source['source']!='url':
    parser.error('Only Git URL entries can be pinned by this helper')
ref='refs/tags/'+args.release
rows=subprocess.check_output(['git','ls-remote','--exit-code',source['url'],ref,ref+'^{}'],text=True)
resolved={name:sha for sha,name in (line.split() for line in rows.splitlines())}
sha=resolved.get(ref+'^{}') or resolved[ref]
source.update(ref=args.release,sha=sha)
path.write_text(json.dumps(catalog,indent=2)+'\n')
print(f'{args.plugin}: {args.release} at {sha}')
