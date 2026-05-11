"""Notifications — sends the daily summary email and immediate parse-failure emails.

Uses smtplib + Gmail SMTP (TLS on port 587). Summary email reports counts of
enriched, skipped, ambiguous, and unparseable emails. Parse-failure emails include
the subject, sender, and first 500 chars of the raw body.

Implemented in Session 6.
"""
