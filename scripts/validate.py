#!/usr/bin/env python3
"""Validate this catalog and optionally fetch pinned plugin manifests, without executing code."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def relative_file(root, value):
    require(isinstance(value,str) and value, 'Companion path must be a string')
    path=PurePosixPath(value)
    require(not path.is_absolute() and '..' not in path.parts, 'Companion path must stay inside the plugin')
    target=(root/value).resolve()
    require(target.is_relative_to(root.resolve()) and target.is_file(), f'Missing companion file: {value}')
    return target

def plugin(root, name):
    data=json.loads((root/'.codex-plugin/plugin.json').read_text())
    require(data.get('name')==name, 'Catalog and plugin names differ')
    require(re.fullmatch(r'\d+\.\d+\.\d+(?:[-+][\w.+-]+)?',data.get('version','')), 'Invalid plugin version')
    for field in ('description','license','repository','author','interface'):
        require(data.get(field),f'Missing plugin field: {field}')
    require(data['author'].get('name'), 'Missing author name')
    for field in ('displayName','shortDescription','longDescription','developerName','category','defaultPrompt'):
        require(data['interface'].get(field),f'Missing interface field: {field}')
    config=json.loads(relative_file(root,data['mcpServers']).read_text())
    require(isinstance(config.get('mcpServers'),dict) and config['mcpServers'], 'No MCP servers configured')
    for key,server in config['mcpServers'].items():
        require(isinstance(server,dict),f'Invalid MCP server: {key}')
        require(server.get('command') or server.get('url'),f'MCP server has no command or URL: {key}')
    skills=root/'skills'
    require(skills.is_dir() and any(skills.glob('*/SKILL.md')), 'No bundled usage skills')
    print(f'  {name} {data["version"]}: plugin manifest and MCP configuration valid')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fetch',action='store_true',help='Read plugin metadata at the exact pinned commit')
    args=ap.parse_args()
    data=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text())
    require(re.fullmatch(r'[A-Za-z0-9_-]+',data.get('name','')), 'Invalid marketplace name')
    require(data.get('interface',{}).get('displayName'), 'Missing marketplace display name')
    require(isinstance(data.get('plugins'),list) and data['plugins'], 'Catalog must contain plugins')
    names=set()
    for entry in data['plugins']:
        name=entry.get('name','')
        require(re.fullmatch(r'[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*',name), 'Invalid plugin name')
        require(name not in names, 'Duplicate plugin name')
        names.add(name)
        policy=entry.get('policy',{})
        require(policy.get('installation') in ('AVAILABLE','INSTALLED_BY_DEFAULT','NOT_AVAILABLE'), 'Invalid installation policy')
        require(policy.get('authentication') in ('ON_INSTALL','ON_USE'), 'Invalid authentication policy')
        require(entry.get('category'), 'Missing category')
        source=entry.get('source',{})
        require(source.get('source')=='url', 'This catalog uses explicit Git URL sources')
        url=urlparse(source.get('url',''))
        require(url.scheme=='https' and url.hostname=='github.com' and not url.username and not url.password, 'Expected public HTTPS GitHub source')
        sha=source.get('sha','')
        require(re.fullmatch(r'[0-9a-f]{40}',sha), 'Source must pin a full immutable commit')
        require(isinstance(source.get('ref'),str) and source['ref'] and not source['ref'].startswith('-'), 'Source requires a release ref')
        if args.fetch:
            with tempfile.TemporaryDirectory(prefix='catalog-check-') as tmp:
                checkout=Path(tmp)
                subprocess.run(['git','init','-q',tmp],check=True)
                subprocess.run(['git','-C',tmp,'fetch','-q','--depth','1',source['url'],source['ref']],check=True)
                actual=subprocess.check_output(['git','-C',tmp,'rev-parse','FETCH_HEAD^{commit}'],text=True).strip()
                require(actual==sha, f'Release ref does not match pinned commit for {name}')
                subprocess.run(['git','-C',tmp,'checkout','-q','--detach',sha],check=True)
                plugin(checkout,name)
    print(f'Valid catalog: {data["name"]}, {len(names)} plugin(s)')

if __name__=='__main__':
    main()
