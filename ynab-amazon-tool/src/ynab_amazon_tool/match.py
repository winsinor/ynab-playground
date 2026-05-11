"""Matcher and memo builder — pure functions, no I/O.

Matches parsed shipment records to unapproved YNAB transactions by amount and date
(±match_window_days). Builds the final memo string with the 200-char hard cap,
smart truncation, and the 🤖 suffix.

Implemented in Session 5.
"""
