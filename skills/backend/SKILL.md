---
name: backend
description: "Deliver a backend capability as one verifiable slice: contract, migration with rollback, store, routes, tests, and evidence. Use when the request is 'implementa no backend', 'faz a fatia', 'cria a rota', 'adiciona a migration', 'fecha o financeiro', or when a data model change must ship with a rollback path and gate evidence. Do not use for read-only investigation, for schema changes without rollback, or to deploy without approval."
license: MIT
compatibility: "Any language with versioned migrations and a native test command. The contract is language-agnostic; SQL migrations are the reference, not a requirement."
---

# Backend delivery

A slice is one capability that can be verified end to end: contract, schema, store, transport, tests, evidence. Half a slice is a liability.

## Before touching the schema

1. Confirm directory, git root, branch, and `git status`. Preserve unrelated changes; keep the slice on its own branch.
2. Read the repository invariants. They override this skill; record the ones that constrain the slice.
3. Write the contract before the code. Template and acceptance criteria: [slice-contract.md](references/slice-contract.md).
4. Establish the current migration head and the native commands for format, lint, vet, build, focused test, suite.

## Contract

The contract states, for the slice:

- the behavior in one paragraph, in the user's terms;
- schema changes with `up`, `down`, and a validation that `up → down → up` succeeds on a local database;
- each route with method, path, role, request body, response body, and error shape;
- the invariants that must not regress;
- the acceptance criteria that can be observed without reading the code;
- what is explicitly out of scope.

A route added without a contract is a route nobody can review.

## Schema

- Every migration has a reversible `down`. A destructive `down` is acceptable only for data the same slice created, and the contract must say so.
- Every business table carries its tenant or owner scope, and every query filters by it. Isolation by convention alone is a defect waiting for the first missing `WHERE`.
- Soft delete when history matters: a record deactivated today must not rewrite last month's report.
- Numbering comes from a transactional counter, never from `COUNT(*) + 1`. Counting races under concurrency and produces duplicates.
- Constraints live in the database: positive amounts, bounded text, allowed enumerations. Application validation alone drifts.

## Store and transport

- Store methods take the scope as their first argument and cannot be called without it.
- The transport layer validates the role from the session, not from the request body, and revalidates every permission the client also checks.
- Public or link-shared surfaces never expose cost, margin, tax identifiers, or internal identifiers beyond the one in the link.
- Errors are typed and mapped to status codes in one place.

## Money and time

Rules that catch most of the real defects: [money-and-time.md](references/money-and-time.md).

- No binary float for money. Integers in the smallest unit or a decimal type.
- Splitting a total into installments must sum exactly to the total; the last installment absorbs the remainder and the test asserts the sum.
- Rounding is explicit and applied once, at the edge where the value becomes display or ledger.
- Store timestamps in UTC, convert at the boundary, and keep one documented convention for the reporting window.

## Gates

Run, and report separately: format, vet or static analysis, build, focused tests, the relevant suite, and the web or client build when the slice touches it. Then run the slice's end-to-end script.

A green focused test does not prove the route works. A migration that applies does not prove it rolls back.

## Evidence

Close the slice with a short document: what changed, the migration name, the commands run with their exit results, the end-to-end observation, and the known limits. This document is what the next person reads before changing the slice.

Do not commit, push, migrate a shared database, or deploy without explicit authorization for that action.
