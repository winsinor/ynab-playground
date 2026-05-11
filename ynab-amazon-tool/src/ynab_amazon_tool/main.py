"""Orchestration entry point — wires together mail, parse, ynab, match, and notify.

Exposes the `cli` function registered as the `ynab-amazon-tool` console script.
Accepts --apply flag (dry-run is default). Loads config.yaml and .env, then runs
the full pipeline: fetch emails → parse → fetch YNAB txns → match → patch → notify.

Implemented in Session 6.
"""
