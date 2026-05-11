"""YNAB API client — fetches unapproved transactions and PATCHes memo fields.

Never touches approved transactions. Respects dry-run mode (reads are always
performed; writes are gated by the --apply flag). Targets the configured
Amazon Prime Visa account inside the configured budget.

Implemented in Session 4.
"""
