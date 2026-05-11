# ynab-amazon-tool — Claude Code Context

## Project Goal

A Raspberry Pi 4 service that enriches unapproved YNAB transactions on my Amazon Prime Visa
with item-level memos parsed from Amazon order/shipment emails in a dedicated Gmail account.
It runs daily via systemd timer and sends a summary email after each run.

## Sacred Invariants

These are non-negotiable. Every design decision must respect them.

1. **Only touches unapproved YNAB transactions.** Approved transactions are never modified.
2. **Idempotent** — safe to re-run any number of times with no harmful effects.
3. **No database.** YNAB's approved/unapproved flag is the only state.
4. **Dry-run mode is the default.** Requires `--apply` CLI flag to actually write to YNAB.
5. **Parse failures email me the raw email** and do NOT touch YNAB.
6. **Sandbox YNAB budget for all initial testing.**

## Architecture / Data Flow

```
Amazon → Gmail forwarding → dedicated Gmail mailbox (IMAP)
    → mail.py (fetch unread emails)
    → parse.py (classify + extract order/shipment data)
    → ynab.py (fetch unapproved transactions)
    → match.py (match shipments to transactions)
    → ynab.py (PATCH memo on matched transactions, unless dry-run)
    → notify.py (send daily summary email + parse failure emails)
```

## Stack

- Python 3.11+
- `uv` for dependency management
- `imaplib` (stdlib) for Gmail IMAP
- `requests` for YNAB API
- `pydantic` v2 for data models
- `pyyaml` for config
- `pytest` for tests
- `smtplib` (stdlib) for sending the summary email
- systemd timer for scheduling (daily at 6 AM local time)

## Memo Format

Final memo on enriched transactions: `Item 1, Item 2, Item 3 (#114-1234567) 🤖`

Rules:
- Hard cap at 200 characters
- Order number is sacred — never truncated
- Add `(x2)` quantity suffixes only if there's room
- If over 200 chars, smart-truncate each item name to ~30 chars first
- If still over, truncate items list with `...` before the order number
- 🤖 emoji always at the end — marks transactions enriched by this script

Multi-shipment memo (amounts sum to transaction): `Item A, Item B | Item C (#X, #Y) 🤖`

## Matching Rules

For each unapproved Amazon transaction on the configured account:
- Find shipments with exact amount match within ±5 days of transaction date
- 0 matches → skip silently
- 1 match → enrich the memo
- Multiple shipments whose amounts sum to the transaction amount → combine into one memo
- Multiple independent shipments that each match the amount → skip and log as ambiguous

## Email Classification

Classify every email as one of:

| Class | Action |
|---|---|
| `order_confirmation` | Join with shipment by order ID; provides item details |
| `shipment_notification` | Join with order by order ID; provides charge amount + ship date |
| `refund` | Match negative YNAB transactions (handled in v1) |
| `digital` | Log and skip |
| `whole_foods` | Log and skip |
| `fresh` | Log and skip |
| `unknown` | Log and skip |

Parse failures: email me the subject, sender, and first 500 chars of body. Never touch YNAB.

## Edge Cases

- 0 shipment matches for a transaction → skip silently
- Multiple shipments matching same amount on same date → ambiguous, skip and log
- Multi-shipment order whose amounts sum to transaction → combine memo
- Quantity > 1 → append `(x2)` suffix if memo fits within 200 chars
- Memo over 200 chars → truncate item names to ~30 chars first; if still over, use `...`
- Order number always preserved — never truncated
- `digital`, `whole_foods`, `fresh`, `unknown` email types → logged and skipped (no YNAB touch)

## 6-Session Build Plan

| Session | Description |
|---|---|
| 1 | **Scaffolding** — structure, config, docs, no feature code ✅ |
| 2 | **IMAP fetch** — read unread Amazon emails, save .eml fixtures |
| 3 | **Email parser** — classify and extract, pytest against fixtures |
| 4 | **YNAB client** — fetch unapproved txns, PATCH memos (against sandbox) |
| 5 | **Matcher + memo builder** — pure functions, fully unit tested |
| 6 | **Orchestration + notifications + systemd** — main.py, summary email, unit files |

## Do NOT Do

- **No database** — do not introduce SQLite, Redis, files, or any other persistence layer
- **No auto-approve** — never set `approved: true` on any YNAB transaction
- **No auto-categorize** — never change the YNAB category of any transaction
- **No historical backfill in v1** — only process emails and transactions from the lookback window
- **No splits** — do not split YNAB transactions into sub-transactions
- **Never touch approved transactions** — the `approved` flag gates all writes
- **Do not touch YNAB on parse failure** — send the failure email and move on

## Configuration

All tunables live in `config.yaml`. Secrets live in `.env` (never committed).
See `.env.example` for all required environment variables.

## Running Locally

```bash
# Dry run (default, safe)
uv run ynab-amazon-tool

# Apply changes to YNAB sandbox
uv run ynab-amazon-tool --apply
```
