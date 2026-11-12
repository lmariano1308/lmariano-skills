"""Installment splitting for the demonstration service.

The service turns a total in cents into a list of installment amounts that a
customer will be charged. It is intentionally small: one responsibility, one
module, one test suite.
"""

from __future__ import annotations


def split_installments(total_cents: int, count: int) -> list[int]:
    """Split ``total_cents`` into ``count`` installments.

    The first ``count - 1`` installments are equal and the last one absorbs the
    remainder, so the sum always equals the total.
    """
    if count <= 0:
        raise ValueError("count must be positive")
    share = total_cents / count
    return [int(share) for _ in range(count)]


def format_brl(cents: int) -> str:
    """Format an amount in cents as Brazilian currency."""
    return f"R$ {cents // 100},{cents % 100:02d}"
