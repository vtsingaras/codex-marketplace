# Vyron's Codex Plugins

[![Validate catalog](https://github.com/vtsingaras/codex-marketplace/actions/workflows/validate.yml/badge.svg)](https://github.com/vtsingaras/codex-marketplace/actions/workflows/validate.yml)

A small, maintained catalog of Codex plugins. Each entry points to a specific
tested commit in its source repository, with clear ownership and setup guidance.

## Install

```sh
codex plugin marketplace add vtsingaras/codex-marketplace
codex plugin add ida-pro-mcp@vtsingaras
```

Start a new Codex task or reconnect the plugin after installing, so the new
tools and skills are loaded.

| Plugin | What it provides | Requirements |
| --- | --- | --- |
| [IDA Pro MCP](https://github.com/vtsingaras/ida-pro-mcp) | Headless idalib and desktop IDA analysis, with generic decompiler-provider support | Licensed IDA Pro 9.4, Python 3.11+, [uv](https://docs.astral.sh/uv/) |

**Lua bytecode:** install [Lua RE](https://github.com/vtsingaras/lua-re/tree/master/lua/ida)
separately into IDA. It supplies one loader and plugin for Lua 5.1–5.4, including
unluac source recovery through the ordinary MCP `decompile` tool. Java is optional
for analysis and required only for source recovery. Lua RE's
`python3 install.py --configure-java` provides terminal onboarding.

Lua RE is an IDA plugin, not an entry in this Codex marketplace.

## Updating

```sh
codex plugin marketplace upgrade vtsingaras
codex plugin add ida-pro-mcp@vtsingaras
```

The catalog pins both a release ref and an immutable Git commit. Updating a source
repository does not silently move an installed catalog entry to untested code.
A catalog update selects the new release; reinstall the plugin and start a new task
to use it.

## Maintenance

- The catalog lives at `.agents/plugins/marketplace.json`, following
  [OpenAI's plugin packaging guidance](https://developers.openai.com/plugins/build/plugins).
- Plugin code, licenses, manifests, skills and MCP configuration live in each
  plugin's own source repository.
- This is an independent marketplace repository, created from scratch.
  Fork provenance belongs to the individual code repositories.
- A change is validated locally with `python3 scripts/validate.py --fetch` and in
  CI. The validator checks names, policy, immutable source pins, required plugin
  metadata and companion file paths without executing plugin code.
- To add or update an entry, select a tested release, update its `ref` and `sha`,
  validate it, and document meaningful changes. Keep entries focused and preserve
  upstream attribution.
- This repository contains no credentials, IDA licenses, analyzed binaries or
  analysis databases.

## Remove

```sh
codex plugin remove ida-pro-mcp@vtsingaras
codex plugin marketplace remove vtsingaras
```

Catalog content is MIT-licensed. Plugins retain their own licenses; IDA Pro MCP
is MIT, and the separately installed Lua RE extension is AGPL-3.0.
