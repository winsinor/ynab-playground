# ynab-amazon-tool

A Raspberry Pi 4 service that enriches unapproved YNAB transactions on your Amazon Prime Visa
with item-level memos parsed from Amazon order and shipment confirmation emails stored in a
dedicated Gmail account. It runs daily via systemd timer, patches matching unapproved transactions
with a structured memo (e.g. `AirPods Pro, USB-C Cable (#114-1234567) 🤖`), and emails you a
summary after each run.

---

## Prerequisites

- Raspberry Pi 4 running a recent Raspberry Pi OS (64-bit recommended)
- Python 3.11+ (`python3 --version`)
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed (`uv --version`)

---

## YNAB Sandbox Setup

Before touching your real budget, test against a sandbox budget.

1. Log in to [app.ynab.com](https://app.ynab.com) and create a new budget named something like
   `Amazon Tool Test`.
2. Add a checking/credit account named `Amazon Prime Visa (Test)`.
3. Create a few manually-entered transactions with realistic Amazon amounts (e.g. $23.47) and
   leave them **unapproved** (do not click the green checkmark).
4. Grab the budget ID from the URL: `app.ynab.com/budgets/<BUDGET_ID>/...`
5. Navigate to the account and grab the account ID from the URL:
   `.../accounts/<ACCOUNT_ID>`
6. Generate a Personal Access Token at
   [app.ynab.com/settings/developer](https://app.ynab.com/settings/developer).
7. Put these three values in your `.env` as `YNAB_BUDGET_ID`, `YNAB_AMAZON_ACCOUNT_ID`, and
   `YNAB_TOKEN`.

---

## Gmail Dedicated Account Setup

This tool needs a Gmail account that receives only forwarded Amazon emails.

1. Create a new Google account (e.g. `yourname-amazon-ynab@gmail.com`).
2. Enable 2-Step Verification on the new account
   (Account → Security → 2-Step Verification).
3. Generate an App Password: Account → Security → 2-Step Verification → App passwords.
   - App name: `ynab-amazon-tool`
   - Copy the 16-character password — you won't see it again.
4. Put the address in `.env` as `IMAP_USER` and the app password as `IMAP_APP_PASSWORD`.

---

## Gmail Forwarding Setup

Forward Amazon emails from your main account to the dedicated account.

1. In your **main** Gmail account, go to Settings → See all settings → Filters and Blocked
   Addresses → Create a new filter.
2. In the **From** field enter: `amazon.com`
   (this catches `ship-confirm@amazon.com`, `auto-confirm@amazon.com`, etc.)
3. Click **Create filter** → check **Forward it to** → add the dedicated Gmail address.
4. Confirm the forwarding address via the verification email sent to the dedicated account.
5. Optionally also filter on `@amazon.com` subject keywords to catch edge cases.

---

## Install on the Pi

```bash
# Clone the repo
git clone https://github.com/youruser/ynab-amazon-tool.git
cd ynab-amazon-tool

# Install dependencies
uv sync

# Configure secrets
cp .env.example .env
nano .env   # fill in all values
```

---

## Manual Test Run

```bash
# Dry-run (default) — reads emails and YNAB, prints what it would do, writes nothing
uv run ynab-amazon-tool

# Apply against the sandbox budget
uv run ynab-amazon-tool --apply
```

Review the output. Confirm memos look correct on the sandbox YNAB transactions before
proceeding to production.

---

## systemd Installation

Install as a user-level service so it runs without root and respects your local timezone.

```bash
# Copy unit files
mkdir -p ~/.config/systemd/user
cp systemd/ynab-amazon-tool.service ~/.config/systemd/user/
cp systemd/ynab-amazon-tool.timer   ~/.config/systemd/user/

# Reload and enable
systemctl --user daemon-reload
systemctl --user enable --now ynab-amazon-tool.timer

# Check status
systemctl --user status ynab-amazon-tool.timer
journalctl --user -u ynab-amazon-tool.service -f
```

The timer fires daily at 06:00 local time. If the Pi was off at that time, systemd will
run the service shortly after next boot (`Persistent=true`).

---

## Going Live

Once you're satisfied with sandbox results:

1. In [YNAB](https://app.ynab.com), find your **real** Amazon Prime Visa account ID and your
   **real** budget ID using the same URL method described above.
2. Update `.env` with the production `YNAB_BUDGET_ID` and `YNAB_AMAZON_ACCOUNT_ID`.
3. Run one more dry-run to confirm the real unapproved transactions are found correctly:
   ```bash
   uv run ynab-amazon-tool
   ```
4. Run with `--apply` to write the first real memos:
   ```bash
   uv run ynab-amazon-tool --apply
   ```
5. Check YNAB — enriched transactions will have memos ending in 🤖.
