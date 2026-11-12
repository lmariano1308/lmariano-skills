# Money and time

Defects found in real ledgers, in the order they usually appear.

## Rounding

- Binary float cannot represent cents. `0.1 + 0.2` is not `0.3`, and a ledger built on floats drifts by one cent per few thousand rows.
- Represent money as integer minor units at the boundary, or as a decimal type in the database. Convert once on input, format once on output.
- Round explicitly: half away from zero for display, banker's rounding when the accounting rule demands it. Pick one and write it in the contract.
- Round once. Rounding at input, again in the store, and again in the view produces three different totals for the same invoice.

## Splitting a total

A total of `10000` cents across three installments is `3334 + 3333 + 3333`. The naive `total / n` loses a cent and never fails loudly.

```text
base = total // n
remainder = total - base * n
installments = [base] * n
installments[-1] += remainder
```

The test asserts `sum(installments) == total` for a set of totals that includes primes and values below `n`, not only the round number from the ticket.

## Negative values

- Truncation toward zero makes a negative margin look smaller than it is. Compute margin with an explicit rounding helper, then assert the sign in a test.
- Percentage discounts on negative amounts invert. Decide whether the domain allows negatives before writing the formula.
- Division by zero on an empty cost produces infinity, which serializes as `null` or panics depending on the encoder. Guard the denominator.

## Time

- Store UTC. Convert at the boundary that displays or reports.
- A reporting window defined as "the month" must state its timezone, or the first and last day disagree with the ledger.
- Date-only values are not timestamps. Storing a birthday or a due date as an instant creates off-by-one-day defects across a timezone boundary.
- DST transitions add and remove an hour. A daily aggregation that assumes 24 hours is wrong twice a year.

## Verification

- Property test the split: random total, random `n`, sum equals the total.
- Assert the formatted string for at least one value with a trailing zero and one with rounding at the half.
- Keep one fixture with a negative margin and one with zero cost; both are the cases that historically shipped broken.
