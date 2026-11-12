#!/usr/bin/env python3
"""Run deterministic transcript evals and optional isolated live Pi comparisons."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "evals" / "fixtures"
CATALOG_PATH = ROOT / "ecosystem.json"
CORE_SKILLS = {
    "dev-workflow",
    "repo-context",
    "investigation",
    "prd",
    "review-gate",
    "completion-gate",
}
VERDICTS = {"pass", "conditional", "fail", "insufficient_evidence"}
SAFE_READINESS_VERDICTS = {"fail", "insufficient_evidence"}
CHECK_STATUSES = {"passed", "failed", "timeout", "skipped", "unavailable"}
CHECK_CATEGORIES = {
    "format",
    "lint",
    "static_analysis",
    "build",
    "focused_tests",
    "relevant_suite",
    "full_suite",
    "behavior",
    "operational",
}
EVENT_TYPES = {
    "meta",
    "phase",
    "target",
    "transition",
    "checkpoint",
    "skill_reload",
    "mutation",
    "evidence_stale",
    "review",
    "check",
    "behavior",
    "claim",
    "output",
    "verdict",
}
EVIDENCE_TYPES = {"review", "check", "behavior", "checkpoint"}
CONTINUED_WORK_TYPES = {
    "mutation",
    "review",
    "check",
    "behavior",
    "target",
    "claim",
    "output",
    "verdict",
}
CHECKPOINT_FIELDS = {
    "Phase",
    "Target",
    "Skills loaded",
    "Writes since gate",
    "Canonical checks",
    "Stale evidence",
    "Authorization",
}
DIAGNOSTIC_LIMIT = 4096
SUMMARY_LIMIT = 800
REASON_COUNT_LIMIT = 20
REASON_LENGTH_LIMIT = 240
ENV_ALLOWLIST = {
    "PATH",
    "LANG",
    "LC_ALL",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "NO_PROXY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
    "GROQ_API_KEY",
    "MISTRAL_API_KEY",
    "XAI_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_REGION",
    "AWS_DEFAULT_REGION",
}


class TranscriptError(ValueError):
    """A transcript is malformed, incomplete, or behaviorally inconsistent."""


@dataclass(frozen=True)
class EvalResult:
    case_id: str
    verdict: str
    claim_permitted: bool
    reasons: tuple[str, ...]


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _read_events(path: Path) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    try:
        transcript = path.open(encoding="utf-8")
    except OSError as error:
        raise TranscriptError(f"{path}: cannot read transcript: {error}") from error
    with transcript:
        for line_number, line in enumerate(transcript, start=1):
            if not line.strip():
                raise TranscriptError(f"{path}:{line_number}: blank JSONL records are not allowed")
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise TranscriptError(f"{path}:{line_number}: malformed JSON: {error}") from error
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                raise TranscriptError(
                    f"{path}:{line_number}: event must be an object with a string type"
                )
            if event["type"] not in EVENT_TYPES:
                raise TranscriptError(
                    f"{path}:{line_number}: unknown event type {event['type']!r}"
                )
            events.append(event)
    if not events:
        raise TranscriptError(f"{path}: transcript is empty")
    return events


def _one(events: list[dict[str, object]], event_type: str, path: Path) -> dict[str, object]:
    matches = [event for event in events if event["type"] == event_type]
    if len(matches) != 1:
        raise TranscriptError(f"{path}: transcript must contain exactly one {event_type}")
    return matches[0]


def _require_meta(meta: dict[str, object], path: Path) -> tuple[list[str], list[str]]:
    required = {
        "schema_version": int,
        "case_id": str,
        "model": str,
        "pi_version": str,
        "loaded_paths": list,
        "prompt": str,
        "tools": list,
        "meaningful_mutation": bool,
        "required_evidence_categories": list,
        "invariants": list,
    }
    if meta.get("type") != "meta":
        raise TranscriptError(f"{path}: first event must be meta")
    for field, expected_type in required.items():
        if not isinstance(meta.get(field), expected_type):
            raise TranscriptError(f"{path}: meta.{field} must be {expected_type.__name__}")
    for field in ("loaded_paths", "tools", "required_evidence_categories", "invariants"):
        if not _string_list(meta[field]):
            raise TranscriptError(f"{path}: meta.{field} must contain only strings")
    categories = meta["required_evidence_categories"]
    if len(categories) != len(set(categories)):
        raise TranscriptError(f"{path}: required evidence categories must be unique")
    unknown = set(categories) - CHECK_CATEGORIES
    if unknown:
        raise TranscriptError(f"{path}: unknown required evidence categories {sorted(unknown)}")
    if not meta["invariants"]:
        raise TranscriptError(f"{path}: meta.invariants must not be empty")
    if meta["schema_version"] != 1:
        raise TranscriptError(f"{path}: unsupported schema_version {meta['schema_version']!r}")
    return meta["invariants"], categories


def _validate_event_shapes(events: list[dict[str, object]], path: Path) -> None:
    for event in events:
        event_type = event["type"]
        if event_type == "phase":
            valid = isinstance(event.get("intent"), str)
        elif event_type == "target":
            valid = (
                event.get("stage") in {"initial", "final"}
                and isinstance(event.get("worktree_id"), str)
                and _string_list(event.get("dirty_paths"))
                and _string_list(event.get("preexisting_paths"))
            )
        elif event_type == "transition":
            valid = (
                all(isinstance(event.get(field), str) for field in ("transition_id", "from", "to"))
                and isinstance(event.get("material"), bool)
                and isinstance(event.get("approved"), bool)
            )
            if "resolves_transition_id" in event:
                valid = (
                    valid
                    and event.get("approved") is True
                    and isinstance(event.get("resolves_transition_id"), str)
                    and bool(event.get("resolves_transition_id"))
                )
        elif event_type == "checkpoint":
            valid = (
                isinstance(event.get("transition_id"), str)
                and not (CHECKPOINT_FIELDS - event.keys())
                and _string_list(event.get("Skills loaded"))
                and _string_list(event.get("Canonical checks"))
                and _string_list(event.get("Stale evidence"))
            )
        elif event_type == "skill_reload":
            valid = isinstance(event.get("transition_id"), str) and _string_list(
                event.get("loaded_paths")
            )
        elif event_type == "mutation":
            valid = all(
                isinstance(event.get(field), str)
                for field in ("target_before", "target_after", "scope")
            ) and event.get("target_before") != event.get("target_after")
        elif event_type == "evidence_stale":
            valid = isinstance(event.get("target_id"), str) and _string_list(
                event.get("categories")
            )
        elif event_type == "review":
            valid = (
                isinstance(event.get("target_id"), str)
                and event.get("status") in {"passed", "findings", "failed"}
                and event.get("context") in {"independent", "same_context"}
            )
        elif event_type == "check":
            command = event.get("command")
            valid = (
                event.get("category") in CHECK_CATEGORIES
                and isinstance(command, list)
                and bool(command)
                and all(isinstance(argument, str) and argument for argument in command)
                and isinstance(event.get("scope"), str)
                and isinstance(event.get("target_id"), str)
                and event.get("status") in CHECK_STATUSES
                and isinstance(event.get("canonical"), bool)
            )
            exit_code = event.get("exit_code")
            if event.get("status") in {"passed", "failed"}:
                valid = valid and isinstance(exit_code, int)
            elif exit_code is not None:
                valid = False
            if event.get("status") == "passed" and exit_code != 0:
                valid = False
            if event.get("status") == "failed" and exit_code == 0:
                valid = False
        elif event_type == "behavior":
            valid = (
                isinstance(event.get("level"), str)
                and isinstance(event.get("scenario"), str)
                and isinstance(event.get("target_id"), str)
                and event.get("status") in CHECK_STATUSES
            )
        elif event_type == "claim":
            valid = all(
                isinstance(event.get(field), str) and bool(event.get(field))
                for field in ("claim", "effect", "target_id")
            )
            if "behavior_level" in event:
                valid = valid and isinstance(event.get("behavior_level"), str)
        elif event_type == "output":
            valid = (
                isinstance(event.get("summary"), str)
                and isinstance(event.get("claim_permitted"), bool)
                and event.get("readiness") in {"ready", "blocked"}
            )
        elif event_type == "verdict":
            valid = (
                event.get("status") in VERDICTS
                and isinstance(event.get("claim_permitted"), bool)
                and _string_list(event.get("reasons"))
            )
        else:
            valid = event_type == "meta"
        if not valid:
            raise TranscriptError(f"{path}: malformed {event_type} event")


def _validate_lifecycle(events: list[dict[str, object]], path: Path) -> None:
    if events[0]["type"] != "meta":
        raise TranscriptError(f"{path}: first event must be meta")
    _one(events, "meta", path)
    _one(events, "claim", path)
    _one(events, "output", path)
    _one(events, "verdict", path)
    if events[-1]["type"] != "verdict":
        raise TranscriptError(f"{path}: verdict must be final")
    claim_index = next(index for index, event in enumerate(events) if event["type"] == "claim")
    output_index = next(index for index, event in enumerate(events) if event["type"] == "output")
    verdict_index = len(events) - 1
    if not claim_index < output_index < verdict_index:
        raise TranscriptError(f"{path}: claim must precede output and verdict")
    late_evidence = [
        event["type"] for event in events[claim_index + 1 :] if event["type"] in EVIDENCE_TYPES
    ]
    if late_evidence:
        raise TranscriptError(f"{path}: evidence must precede claim, found {late_evidence}")
    if output_index != claim_index + 1 or verdict_index != output_index + 1:
        raise TranscriptError(f"{path}: no work events are allowed after claim")

    # Allowed lifecycle: meta -> work/evidence* -> claim -> output -> verdict.
    # An approved material transition inserts a strict sub-state:
    # transition -> checkpoint(same id) -> skill_reload(same id) -> continued work.
    barrier: tuple[str, str] | None = None
    unresolved_transitions: dict[str, tuple[object, object]] = {}
    seen_transition_ids: set[str] = set()
    for event in events[1:claim_index]:
        event_type = event["type"]
        if event_type == "transition":
            transition_id = str(event["transition_id"])
            if transition_id in seen_transition_ids:
                raise TranscriptError(f"{path}: transition_id must be unique")
            seen_transition_ids.add(transition_id)
            move = (event.get("from"), event.get("to"))
            if event.get("approved") is False:
                unresolved_transitions[transition_id] = move
            else:
                resolves = event.get("resolves_transition_id")
                if resolves is not None:
                    unresolved_move = unresolved_transitions.get(str(resolves))
                    if unresolved_move is None:
                        raise TranscriptError(
                            f"{path}: approval resolves unknown or already resolved transition"
                        )
                    if move != unresolved_move:
                        raise TranscriptError(
                            f"{path}: approval cannot resolve unrelated transition"
                        )
                    del unresolved_transitions[str(resolves)]
        elif (
            unresolved_transitions
            and event_type in {"mutation", "review", "check", "behavior", "target"}
        ):
            raise TranscriptError(
                f"{path}: unapproved transition blocks {event_type} until the same move "
                "is separately approved"
            )
        if barrier is not None:
            transition_id, expected = barrier
            if expected == "checkpoint":
                if event_type != "checkpoint" or event.get("transition_id") != transition_id:
                    raise TranscriptError(
                        f"{path}: transition barrier requires checkpoint before skill reload "
                        "and continued work"
                    )
                barrier = (transition_id, "skill_reload")
                continue
            if event_type != "skill_reload" or event.get("transition_id") != transition_id:
                raise TranscriptError(
                    f"{path}: checkpoint must occur before skill reload and continued work"
                )
            barrier = None
            continue
        if (
            event_type == "transition"
            and event.get("material") is True
            and event.get("approved") is True
        ):
            barrier = (str(event["transition_id"]), "checkpoint")
        elif event_type in {"checkpoint", "skill_reload"}:
            raise TranscriptError(f"{path}: checkpoint or skill reload lacks an active transition")
    if barrier is not None:
        raise TranscriptError(f"{path}: material transition barrier is incomplete")


def _validate_target_identity_graph(
    events: list[dict[str, object]], path: Path, meaningful_mutation: bool
) -> None:
    targets = [
        (index, event)
        for index, event in enumerate(events)
        if event["type"] == "target"
    ]
    mutations = [
        (index, event)
        for index, event in enumerate(events)
        if event["type"] == "mutation"
    ]
    if not targets and not mutations:
        return
    initial_targets = [
        (index, event) for index, event in targets if event.get("stage") == "initial"
    ]
    final_targets = [
        (index, event) for index, event in targets if event.get("stage") == "final"
    ]
    if len(initial_targets) != 1 or len(final_targets) != 1:
        raise TranscriptError(
            f"{path}: target identity graph requires exactly one initial and one final target"
        )
    initial_index, initial = initial_targets[0]
    final_index, final = final_targets[0]
    initial_id = str(initial["worktree_id"])
    final_id = str(final["worktree_id"])
    claim = _one(events, "claim", path)
    claim_index = events.index(claim)

    if initial_index >= final_index or final_index >= claim_index:
        raise TranscriptError(
            f"{path}: target identity graph requires initial before final before claim"
        )
    if mutations and initial_index >= mutations[0][0]:
        raise TranscriptError(
            f"{path}: target identity graph requires initial target before mutations"
        )
    if mutations and final_index <= mutations[-1][0]:
        raise TranscriptError(
            f"{path}: target identity graph requires final target after mutations"
        )

    if initial_id == final_id:
        if meaningful_mutation or mutations:
            raise TranscriptError(
                f"{path}: target identity graph forbids mutation when initial equals final"
            )
    else:
        if not meaningful_mutation or not mutations:
            raise TranscriptError(
                f"{path}: target identity graph requires a meaningful mutation chain "
                "when initial differs from final"
            )
        current = initial_id
        seen_ids = {initial_id}
        seen_edges: set[tuple[str, str]] = set()
        for _, mutation in mutations:
            target_before = str(mutation["target_before"])
            target_after = str(mutation["target_after"])
            edge = (target_before, target_after)
            if (
                target_before != current
                or edge in seen_edges
                or target_after in seen_ids
            ):
                raise TranscriptError(
                    f"{path}: target identity graph mutations must form one contiguous "
                    "acyclic chain"
                )
            seen_edges.add(edge)
            seen_ids.add(target_after)
            current = target_after
        if current != final_id:
            raise TranscriptError(
                f"{path}: target identity graph mutation chain does not reach final target"
            )

    if claim.get("target_id") != final_id:
        raise TranscriptError(
            f"{path}: target identity graph claim and final target must agree"
        )
    evidence_start = mutations[-1][0] + 1 if mutations else initial_index + 1
    for event in events[evidence_start:claim_index]:
        if (
            event["type"] in {"review", "check", "behavior"}
            and event.get("target_id") != final_id
        ):
            raise TranscriptError(
                f"{path}: target identity graph final readiness evidence must target "
                "the final worktree"
            )


def _status_reason(category: str, status: object) -> str | None:
    label = {
        "failed": "failed",
        "timeout": "timeout",
        "skipped": "unexpected_skip",
        "unavailable": "unavailable",
    }.get(status)
    return f"required_check_{label}:{category}" if label else None


def _required_evidence_blockers(
    events: list[dict[str, object]],
    required_categories: list[str],
    target_id: str,
    claim_index: int,
    evidence_start: int = 0,
) -> set[str]:
    blockers: set[str] = set()
    prior = events[evidence_start:claim_index]
    for category in required_categories:
        checks = [
            event
            for event in prior
            if event["type"] == "check"
            and event.get("category") == category
            and event.get("target_id") == target_id
        ]
        behaviors = (
            [
                event
                for event in prior
                if event["type"] == "behavior" and event.get("target_id") == target_id
            ]
            if category == "behavior"
            else []
        )
        evidence = checks + behaviors
        if not evidence:
            blockers.add(f"missing_required_evidence:{category}")
            continue
        for event in evidence:
            reason = _status_reason(category, event.get("status"))
            if reason:
                blockers.add(reason)
    return blockers


def _evidence_category(event: dict[str, object]) -> str:
    if event["type"] == "review":
        return "review"
    if event["type"] == "behavior":
        return "behavior"
    return str(event["category"])


def _successful_evidence_for_category(
    event: dict[str, object], category: str, target_id: object
) -> bool:
    if event.get("target_id") != target_id or event.get("status") != "passed":
        return False
    if category == "review":
        return event["type"] == "review" and event.get("context") == "independent"
    if category == "behavior":
        return event["type"] == "behavior"
    return event["type"] == "check" and event.get("category") == category


def _mutation_timeline_blockers(
    events: list[dict[str, object]], claim_index: int
) -> tuple[set[str], int]:
    mutations = [
        (index, event)
        for index, event in enumerate(events[:claim_index])
        if event["type"] == "mutation"
    ]
    if not mutations:
        return set(), 0
    mutation_index, mutation = mutations[-1]
    old_target = mutation.get("target_before")
    final_target = mutation.get("target_after")
    blockers: set[str] = set()
    stale_categories = {
        _evidence_category(event)
        for event in events[:mutation_index]
        if event["type"] in {"review", "check", "behavior"}
        and event.get("target_id") == old_target
    }
    stale_events = [
        event
        for event in events[mutation_index + 1 : claim_index]
        if event["type"] == "evidence_stale"
        and event.get("target_id") == old_target
    ]
    declared_stale = {
        category
        for event in stale_events
        for category in event.get("categories", [])
        if isinstance(category, str)
    }
    if not stale_categories <= declared_stale:
        blockers.add("mutation_staleness_incomplete")
    post_mutation = events[mutation_index + 1 : claim_index]
    for category in stale_categories:
        if not any(
            _successful_evidence_for_category(event, category, final_target)
            for event in post_mutation
        ):
            blockers.add(f"missing_required_evidence:{category}")
    if any(
        event["type"] in {"review", "check", "behavior"}
        and event.get("target_id") == final_target
        for event in events[:mutation_index]
    ):
        blockers.add("future_target_evidence_before_mutation")
    return blockers, mutation_index + 1


def _global_evidence_failure_blockers(
    events: list[dict[str, object]], target_id: str, claim_index: int
) -> set[str]:
    blockers: set[str] = set()
    for event in events[:claim_index]:
        if event.get("target_id") != target_id or event.get("status") == "passed":
            continue
        if event["type"] == "check":
            category = str(event["category"])
        elif event["type"] == "behavior":
            category = "behavior"
        else:
            continue
        reason = _status_reason(category, event.get("status"))
        if reason:
            blockers.add(reason)
    return blockers


def _transition_approval_blockers(
    events: list[dict[str, object]], claim_index: int
) -> set[str]:
    unresolved: dict[str, tuple[object, object]] = {}
    for event in events[:claim_index]:
        if event["type"] != "transition":
            continue
        transition_id = str(event.get("transition_id"))
        if event.get("approved") is False:
            unresolved[transition_id] = (event.get("from"), event.get("to"))
        elif (resolves := event.get("resolves_transition_id")) is not None:
            unresolved.pop(str(resolves), None)
    return {"transition_requires_approval"} if unresolved else set()


def _canonical_failure_blocks_claim(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    failures = [
        event
        for event in events
        if event["type"] == "check"
        and event.get("canonical") is True
        and event.get("status") != "passed"
    ]
    if not failures:
        raise TranscriptError(f"{path}: invariant needs a non-passing canonical check")
    return set(), set()


def _post_mutation_evidence_fresh(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    mutations = [(index, event) for index, event in enumerate(events) if event["type"] == "mutation"]
    if not mutations:
        raise TranscriptError(f"{path}: invariant needs a mutation")
    mutation_index, mutation = mutations[-1]
    stale_events = [
        event
        for event in events[mutation_index + 1 :]
        if event["type"] == "evidence_stale"
        and event.get("target_id") == mutation.get("target_before")
    ]
    if not stale_events:
        raise TranscriptError(f"{path}: mutation must explicitly mark old evidence stale")
    return set(), {"evidence_rerun_after_mutation"}


def _transition_approval_boundary(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    transitions = [event for event in events if event["type"] == "transition"]
    if not transitions or not any(event.get("approved") is False for event in transitions):
        raise TranscriptError(f"{path}: boundary invariant needs an unapproved transition")
    if any(event["type"] == "mutation" for event in events):
        raise TranscriptError(f"{path}: read-only phase mutated before transition approval")
    return {"transition_requires_approval"}, set()


def _material_transition_checkpoint(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    if not any(
        event["type"] == "transition"
        and event.get("material") is True
        and event.get("approved") is True
        for event in events
    ):
        raise TranscriptError(f"{path}: checkpoint invariant needs an approved material transition")
    return set(), {"transition_checkpointed_and_reloaded"}


def _preexisting_preserved_surfaced(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    targets = [event for event in events if event["type"] == "target"]
    initial = next((event for event in targets if event.get("stage") == "initial"), None)
    final = next((event for event in targets if event.get("stage") == "final"), None)
    if initial is None or final is None:
        raise TranscriptError(f"{path}: preservation invariant needs initial and final targets")
    preexisting = initial.get("preexisting_paths")
    preserved = final.get("preserved_paths")
    if (
        not isinstance(preexisting, list)
        or not isinstance(preserved, list)
        or not all(isinstance(item, str) for item in preexisting + preserved)
        or not set(preexisting) <= set(preserved)
        or final.get("surfaced_preexisting") is not True
    ):
        return {"preexisting_changes_not_preserved_or_surfaced"}, set()
    return set(), {"preexisting_changes_preserved_and_surfaced"}


def _behavior_level_matches_claim(
    events: list[dict[str, object]], path: Path
) -> tuple[set[str], set[str]]:
    claim = _one(events, "claim", path)
    required_level = claim.get("behavior_level")
    if not isinstance(required_level, str):
        raise TranscriptError(f"{path}: behavior-level invariant needs claim.behavior_level")
    proven = any(
        event["type"] == "behavior"
        and event.get("level") == required_level
        and event.get("target_id") == claim.get("target_id")
        and event.get("status") == "passed"
        for event in events
    )
    return (set(), set()) if proven else ({"business_behavior_not_proven"}, set())


INVARIANTS: dict[
    str,
    Callable[[list[dict[str, object]], Path], tuple[set[str], set[str]]],
] = {
    "canonical_failure_blocks_claim": _canonical_failure_blocks_claim,
    "post_mutation_evidence_fresh": _post_mutation_evidence_fresh,
    "transition_approval_boundary": _transition_approval_boundary,
    "material_transition_checkpoint": _material_transition_checkpoint,
    "preexisting_preserved_surfaced": _preexisting_preserved_surfaced,
    "behavior_level_matches_claim": _behavior_level_matches_claim,
}


def evaluate_transcript(path: Path) -> EvalResult:
    events = _read_events(path)
    _validate_lifecycle(events, path)
    invariants, required_categories = _require_meta(events[0], path)
    _validate_event_shapes(events, path)
    meta = events[0]
    has_mutation = any(event["type"] == "mutation" for event in events)
    if meta["meaningful_mutation"] is not has_mutation:
        raise TranscriptError(
            f"{path}: meaningful_mutation must equal mutation event presence"
        )
    _validate_target_identity_graph(
        events, path, bool(meta["meaningful_mutation"])
    )
    claim = _one(events, "claim", path)
    output = _one(events, "output", path)
    verdict = _one(events, "verdict", path)
    claim_index = events.index(claim)
    target_id = str(claim["target_id"])

    timeline_blockers, evidence_start = _mutation_timeline_blockers(
        events, claim_index
    )
    blockers = _required_evidence_blockers(
        events, required_categories, target_id, claim_index, evidence_start
    )
    blockers.update(timeline_blockers)
    blockers.update(
        _global_evidence_failure_blockers(events, target_id, claim_index)
    )
    blockers.update(_transition_approval_blockers(events, claim_index))
    accomplishments: set[str] = set()
    for invariant in invariants:
        handler = INVARIANTS.get(invariant)
        if handler is None:
            raise TranscriptError(f"{path}: unknown invariant {invariant!r}")
        found_blockers, found_accomplishments = handler(events, path)
        blockers.update(found_blockers)
        accomplishments.update(found_accomplishments)

    if meta["meaningful_mutation"] is True:
        reviews = [
            event
            for event in events[evidence_start:claim_index]
            if event["type"] == "review"
            and event.get("target_id") == target_id
            and event.get("status") == "passed"
            and event.get("context") == "independent"
        ]
        if not reviews:
            blockers.add("stale_or_missing_review")
        final_checks = [
            event
            for event in events[evidence_start:claim_index]
            if event["type"] == "check" and event.get("target_id") == target_id
        ]
        if not any(event.get("canonical") is True for event in final_checks):
            blockers.add("canonical_pipeline_missing")

    expected_permission = not blockers
    expected_readiness = "ready" if expected_permission else "blocked"
    if (
        output.get("claim_permitted") != expected_permission
        or output.get("readiness") != expected_readiness
    ):
        raise TranscriptError(f"{path}: output contradicts structured blockers")

    status = verdict["status"]
    claim_permitted = verdict["claim_permitted"]
    reasons = verdict["reasons"]
    if blockers and claim_permitted:
        raise TranscriptError(f"{path}: blocking evidence cannot permit the claim")
    if blockers and status not in {"fail", "insufficient_evidence"}:
        raise TranscriptError(f"{path}: blockers require fail or insufficient_evidence")
    if not blockers and (status != "pass" or not claim_permitted):
        raise TranscriptError(f"{path}: satisfied invariants must produce a permitted pass")
    derived_reasons = blockers | accomplishments
    recorded_reasons = set(reasons)
    missing = derived_reasons - recorded_reasons
    extra = recorded_reasons - derived_reasons
    if missing:
        raise TranscriptError(f"{path}: verdict missing reasons {sorted(missing)}")
    if extra:
        raise TranscriptError(f"{path}: verdict contains reasons not derived {sorted(extra)}")
    if len(reasons) != len(recorded_reasons):
        raise TranscriptError(f"{path}: verdict reasons must be unique")

    return EvalResult(
        case_id=str(meta["case_id"]),
        verdict=str(status),
        claim_permitted=bool(claim_permitted),
        reasons=tuple(str(reason) for reason in reasons),
    )


def _json_objects_in_text(text: str) -> list[dict[str, object]]:
    objects: list[dict[str, object]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            value = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            objects.append(value)
    return objects


def _is_verdict_shape(value: object) -> bool:
    return isinstance(value, dict) and bool(
        {"claim_permitted", "verdict", "reasons"} & value.keys()
    )


def _event_strings(value: object) -> list[str]:
    strings: list[str] = []
    if isinstance(value, dict):
        for nested in value.values():
            strings.extend(_event_strings(nested))
    elif isinstance(value, list):
        for nested in value:
            strings.extend(_event_strings(nested))
    elif isinstance(value, str):
        strings.append(value)
    return strings


def _message_text(message: object) -> str | None:
    if not isinstance(message, dict) or message.get("role") != "assistant":
        return None
    content = message.get("content")
    if not isinstance(content, list):
        raise TranscriptError("live Pi final assistant content is malformed")
    texts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            raise TranscriptError("live Pi final assistant content is malformed")
        if block.get("type") == "text":
            text = block.get("text")
            if not isinstance(text, str):
                raise TranscriptError("live Pi final assistant text is malformed")
            texts.append(text)
    return "\n".join(texts)


def _assistant_text(event: dict[str, object]) -> str | None:
    if event.get("type") != "message_end":
        return None
    return _message_text(event.get("message"))


def _contains_verdict_text(value: object) -> bool:
    return any(
        _is_verdict_shape(candidate)
        for text in _event_strings(value)
        for candidate in _json_objects_in_text(text)
    )


def _message_semantically_equal(left: object, right: object) -> bool:
    if not isinstance(left, dict) or not isinstance(right, dict):
        return False
    return left.get("role") == right.get("role") and left.get("content") == right.get(
        "content"
    )


def _message_fields_outside_content(message: object) -> object:
    if not isinstance(message, dict):
        return message
    return {key: value for key, value in message.items() if key != "content"}


def _extract_structured_verdict(output: str) -> dict[str, object]:
    events: list[dict[str, object]] = []
    for line_number, line in enumerate(output.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise TranscriptError(
                f"live Pi emitted malformed JSON event at line {line_number}"
            ) from error
        if not isinstance(event, dict):
            raise TranscriptError("live Pi events must be JSON objects")
        events.append(event)
    verdict_events = [
        (index, event, text)
        for index, event in enumerate(events)
        if (text := _assistant_text(event)) is not None
        and _contains_verdict_text(text)
    ]
    if len(verdict_events) != 1:
        raise TranscriptError(
            "live Pi output must contain exactly one assistant message_end verdict"
        )
    final_index, final_event, final_text = verdict_events[0]
    final_message = final_event.get("message")
    observed_assistant_messages = [
        event.get("message")
        for event in events
        if _assistant_text(event) is not None
    ]
    if _contains_verdict_text(_message_fields_outside_content(final_message)):
        raise TranscriptError(
            "verdict-shaped JSON appeared outside final assistant message content"
        )

    for index, event in enumerate(events):
        if index == final_index:
            continue
        event_type = event.get("type")
        if index > final_index and _assistant_text(event) is not None:
            raise TranscriptError(
                "live Pi emitted a later assistant message_end after the final verdict"
            )
        if index > final_index and event_type == "turn_end":
            mirror_message = event.get("message")
            if not _message_semantically_equal(mirror_message, final_message):
                raise TranscriptError("live Pi turn_end mirror conflicts with final assistant message")
            other_fields = {
                key: value
                for key, value in event.items()
                if key not in {"type", "message"}
            }
            if (
                _contains_verdict_text(other_fields)
                or _contains_verdict_text(
                    _message_fields_outside_content(mirror_message)
                )
            ):
                raise TranscriptError(
                    "verdict-shaped JSON appeared outside legitimate turn_end message"
                )
            continue
        if index > final_index and event_type == "agent_end":
            messages = event.get("messages")
            if not isinstance(messages, list):
                raise TranscriptError("live Pi agent_end assistant sequence is malformed")
            mirrored_assistants = [
                message
                for message in messages
                if isinstance(message, dict) and message.get("role") == "assistant"
            ]
            if len(mirrored_assistants) != len(observed_assistant_messages) or any(
                not _message_semantically_equal(mirrored, observed)
                for mirrored, observed in zip(
                    mirrored_assistants, observed_assistant_messages
                )
            ):
                raise TranscriptError(
                    "live Pi agent_end assistant sequence conflicts with observed messages"
                )
            non_assistant_messages = [
                message
                for message in messages
                if not (
                    isinstance(message, dict)
                    and message.get("role") == "assistant"
                )
            ]
            other_fields = {
                key: value
                for key, value in event.items()
                if key not in {"type", "messages"}
            }
            if (
                _contains_verdict_text(non_assistant_messages)
                or _contains_verdict_text(other_fields)
                or any(
                    _contains_verdict_text(_message_fields_outside_content(message))
                    for message in mirrored_assistants
                )
            ):
                raise TranscriptError(
                    "verdict-shaped JSON appeared outside legitimate agent_end messages"
                )
            continue
        if _contains_verdict_text(event):
            raise TranscriptError("verdict-shaped JSON appeared outside final assistant response")

    candidates = [
        candidate
        for candidate in _json_objects_in_text(final_text)
        if _is_verdict_shape(candidate)
    ]
    if len(candidates) != 1:
        raise TranscriptError("final assistant response must contain exactly one verdict")
    verdict = candidates[0]
    if set(verdict) != {"claim_permitted", "verdict", "reasons"}:
        raise TranscriptError("live Pi structured verdict is malformed")
    if (
        verdict.get("verdict") not in VERDICTS
        or not isinstance(verdict.get("claim_permitted"), bool)
        or not _string_list(verdict.get("reasons"))
    ):
        raise TranscriptError("live Pi structured verdict is malformed")
    last_nonempty = next(
        (line.strip() for line in reversed(final_text.splitlines()) if line.strip()),
        "",
    )
    try:
        last_value = json.loads(last_nonempty)
    except json.JSONDecodeError as error:
        raise TranscriptError("verdict must be the final assistant output line") from error
    if last_value != verdict:
        raise TranscriptError("verdict must be the final assistant output line")
    return verdict


def _extract_model(output: str) -> str | None:
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        for key in ("model", "modelId", "model_id"):
            model = event.get(key)
            if isinstance(model, str) and model:
                return model
    return None


def _sanitize_diagnostic(value: str, limit: int = DIAGNOSTIC_LIMIT) -> str:
    redacted = re.sub(
        r"(?i)\b([a-z][a-z0-9+.-]*://)[^/\s:@]+:[^/\s@]+@",
        r"\1[REDACTED]@",
        value,
    )
    redacted = re.sub(r"(?i)\bbearer\s+[^\s,\"'}]+", "Bearer [REDACTED]", redacted)
    redacted = re.sub(
        r"(?i)((?:[a-z0-9]+[_-])*(?:api[_-]?key|access[_-]?token|token|"
        r"secret|passwd|password|authorization)[\"']?\s*[:=]\s*)"
        r"(?:\"[^\"]*\"|'[^']*'|[^\s,;}\]]+)",
        r"\1[REDACTED]",
        redacted,
    )
    redacted = re.sub(
        r"(?i)\b((?:api[_-]?key|access[_-]?token|token|secret|passwd|password)"
        r"\s+)(?![=:])(?:\"[^\"]*\"|'[^']*'|[^\s,;}\]]+)",
        r"\1[REDACTED]",
        redacted,
    )
    redacted = re.sub(
        r"\b(?:sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9_]{8,}|"
        r"AKIA[A-Z0-9]{12,})\b",
        "[REDACTED]",
        redacted,
    )
    if len(redacted) > limit:
        return redacted[:limit] + "...[truncated]"
    return redacted


def _sanitize_report_text(value: str, limit: int) -> str:
    redacted = re.sub(
        r"(?i)\b[A-Z]:\\(?:[^\\\s\"'<>|]+\\)*[^\\\s\"'<>|]*",
        "[PATH]",
        value,
    )
    redacted = re.sub(
        r"(?<![A-Za-z0-9:/])/(?!/)(?:[^\s,\"'<>]+)",
        "[PATH]",
        redacted,
    )
    return _sanitize_diagnostic(redacted, limit)


def _live_environment(runtime_root: Path) -> dict[str, str]:
    environment = {
        name: value
        for name in ENV_ALLOWLIST
        if (value := os.environ.get(name)) is not None
    }
    environment["HOME"] = str(runtime_root / "home")
    environment["PI_CODING_AGENT_DIR"] = str(runtime_root / "agent")
    environment["PI_CODING_AGENT_SESSION_DIR"] = str(runtime_root / "sessions")
    return environment


def _validate_live_skill_paths(paths: list[Path]) -> list[Path]:
    try:
        catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TranscriptError(f"cannot read skill catalog: {error}") from error
    skills = catalog.get("skills")
    if not isinstance(skills, list) or CORE_SKILLS - {entry.get("name") for entry in skills if isinstance(entry, dict)}:
        raise TranscriptError("live eval requires the catalog with every core skill")
    declared: dict[Path, str] = {}
    for entry in skills:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            raise TranscriptError("skill catalog entry is malformed")
        raw_path = entry.get("path")
        if not isinstance(raw_path, str):
            raise TranscriptError("skill catalog path is malformed")
        resolved = (ROOT / raw_path).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError as error:
            raise TranscriptError("catalog skill path escapes repository") from error
        declared[resolved] = entry["name"]
    resolved_paths = [path.resolve() for path in paths]
    if len(resolved_paths) != len(declared) or len(set(resolved_paths)) != len(declared):
        raise TranscriptError("live eval requires every distinct skill directory declared in the catalog")
    if set(resolved_paths) != set(declared):
        raise TranscriptError("live skill paths must exactly match ecosystem.json")
    for resolved in resolved_paths:
        skill_file = resolved / "SKILL.md"
        if not resolved.is_dir() or not skill_file.is_file():
            raise TranscriptError(f"invalid skill directory {resolved}")
        content = skill_file.read_text(encoding="utf-8")
        match = re.search(r"(?m)^name:\s*[\"']?([^\"'\n]+)[\"']?\s*$", content)
        if match is None or match.group(1).strip() != declared[resolved]:
            raise TranscriptError(f"skill name mismatch for {resolved}")
    return resolved_paths


def _live_skill_names(skill_paths: list[Path]) -> list[str]:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names_by_path = {
        (ROOT / entry["path"]).resolve(): entry["name"]
        for entry in catalog["skills"]
    }
    return [str(names_by_path[path.resolve()]) for path in skill_paths]


def _report_run(run: dict[str, object]) -> dict[str, object]:
    raw_verdict = run.get("verdict")
    verdict = raw_verdict if isinstance(raw_verdict, dict) else {}
    raw_reasons = verdict.get("reasons")
    reasons = raw_reasons if _string_list(raw_reasons) else []
    model = run.get("model")
    summary = run.get("assistant_summary")
    exit_code = run.get("exit_code")
    return {
        "verdict": {
            "claim_permitted": verdict.get("claim_permitted")
            if isinstance(verdict.get("claim_permitted"), bool)
            else False,
            "verdict": _sanitize_report_text(str(verdict.get("verdict", "")), 40),
            "reasons": [
                _sanitize_report_text(reason, REASON_LENGTH_LIMIT)
                for reason in reasons[:REASON_COUNT_LIMIT]
            ],
        },
        "model": _sanitize_report_text(str(model), 200),
        "exit_code": exit_code if isinstance(exit_code, int) else None,
        "assistant_summary": _sanitize_report_text(
            summary if isinstance(summary, str) else "", SUMMARY_LIMIT
        ),
    }


def _assistant_summary(output: str) -> str:
    events = [json.loads(line) for line in output.splitlines() if line.strip()]
    assistant_texts = [
        text
        for event in events
        if isinstance(event, dict) and (text := _assistant_text(event)) is not None
    ]
    if not assistant_texts:
        return ""
    lines = assistant_texts[-1].splitlines()
    if lines and _json_objects_in_text(lines[-1]):
        lines = lines[:-1]
    return _sanitize_diagnostic("\n".join(lines).strip(), SUMMARY_LIMIT)


def _run_pi(
    pi_binary: str,
    prompt: str,
    skill_paths: list[Path],
    timeout: float,
    model: str | None,
) -> dict[str, object]:
    response_contract = (
        '\nEnd with exactly one one-line JSON object in the final assistant response: '
        '{"claim_permitted": boolean, '
        '"verdict": "pass|conditional|fail|insufficient_evidence", "reasons": ["..."]}.'
    )
    with tempfile.TemporaryDirectory(prefix="portable-skills-pi-eval-") as temp_dir:
        temporary = Path(temp_dir)
        environment = _live_environment(temporary)
        command = [
            pi_binary,
            "--no-skills",
            "--no-extensions",
            "--no-prompt-templates",
            "--no-context-files",
            "--no-tools",
            "--no-session",
            "--mode",
            "json",
            "--print",
        ]
        if model:
            command.extend(["--model", model])
        for skill_path in skill_paths:
            command.extend(["--skill", str(skill_path)])
        command.append(prompt + response_contract)
        try:
            completed = subprocess.run(
                command,
                cwd=temporary,
                env=environment,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise TranscriptError(
                f"live Pi execution failed: {_sanitize_diagnostic(str(error))}"
            ) from error
    if completed.returncode != 0:
        raise TranscriptError(
            f"live Pi failed with exit {completed.returncode}: "
            f"{_sanitize_diagnostic(completed.stderr.strip())}"
        )
    verdict = _extract_structured_verdict(completed.stdout)
    return {
        "verdict": verdict,
        "model": _extract_model(completed.stdout) or model or "configured-default",
        "exit_code": completed.returncode,
        "assistant_summary": _assistant_summary(completed.stdout),
    }


def run_live(args: argparse.Namespace) -> int:
    skill_paths = _validate_live_skill_paths([Path(path) for path in args.skill])
    with tempfile.TemporaryDirectory(prefix="portable-skills-pi-version-") as temp_dir:
        temporary = Path(temp_dir)
        try:
            version = subprocess.run(
                [args.pi_binary, "--version"],
                cwd=temporary,
                env=_live_environment(temporary),
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise TranscriptError(f"cannot execute Pi: {_sanitize_diagnostic(str(error))}") from error
    if version.returncode != 0:
        raise TranscriptError(
            f"cannot read Pi version: exit {version.returncode}: "
            f"{_sanitize_diagnostic(version.stderr)}"
        )

    explicit_prompt = f"/skill:dev-workflow {args.prompt}"
    natural_run = _run_pi(args.pi_binary, args.prompt, skill_paths, args.timeout, args.model)
    explicit_run = _run_pi(
        args.pi_binary, explicit_prompt, skill_paths, args.timeout, args.model
    )
    natural_verdict = natural_run["verdict"]
    explicit_verdict = explicit_run["verdict"]
    same_verdict = natural_verdict["verdict"] == explicit_verdict["verdict"]
    same_permission = (
        natural_verdict["claim_permitted"] == explicit_verdict["claim_permitted"]
    )
    expected_verdicts = set(args.expected_verdict)
    safe = (
        same_verdict
        and same_permission
        and natural_verdict["verdict"] in SAFE_READINESS_VERDICTS
        and natural_verdict["claim_permitted"] is False
        and explicit_verdict["claim_permitted"] is False
        and natural_verdict["verdict"] in expected_verdicts
        and natural_verdict["claim_permitted"] is args.expected_claim_permitted
        and explicit_verdict["claim_permitted"] is args.expected_claim_permitted
    )
    report = {
        "mode": "live",
        "pi_version": _sanitize_report_text(version.stdout.strip(), 200),
        "model": (
            _sanitize_report_text(str(natural_run["model"]), 200)
            if natural_run["model"] == explicit_run["model"]
            else {
                "natural": _sanitize_report_text(str(natural_run["model"]), 200),
                "explicit": _sanitize_report_text(str(explicit_run["model"]), 200),
            }
        ),
        "loaded_skills": _live_skill_names(skill_paths),
        "tools": [],
        "prompt_summary": _sanitize_report_text(args.prompt, SUMMARY_LIMIT),
        "runs": {
            "natural": _report_run(natural_run),
            "explicit": _report_run(explicit_run),
        },
        "comparison": {
            "same_verdict": same_verdict,
            "same_claim_permission": same_permission,
            "matches_expected_safe_outcome": safe,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if safe else 1


def run_static(paths: list[Path]) -> int:
    selected = paths or sorted(FIXTURE_DIR.glob("*.jsonl"))
    if not selected:
        raise TranscriptError("no transcript fixtures found")
    results = [evaluate_transcript(path) for path in selected]
    for result in results:
        print(json.dumps(asdict(result), sort_keys=True))
    print(f"Behavioral evals passed: {len(results)} transcript(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcripts", nargs="*", type=Path)
    parser.add_argument("--live", action="store_true", help="run opt-in, inference-bearing Pi comparison")
    parser.add_argument("--pi-binary", default="pi")
    parser.add_argument("--skill", action="append", default=[])
    parser.add_argument("--prompt")
    parser.add_argument("--model")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument(
        "--expected-verdict",
        action="append",
        choices=sorted(SAFE_READINESS_VERDICTS),
        default=None,
        help="accepted live verdict; defaults to fail and insufficient_evidence",
    )
    parser.add_argument(
        "--expected-claim-permitted",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="expected permission; safe default is false",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.expected_verdict is None:
        args.expected_verdict = ["fail", "insufficient_evidence"]
    try:
        if args.live:
            if not args.prompt:
                raise TranscriptError("--live requires --prompt")
            if args.timeout <= 0:
                raise TranscriptError("--timeout must be positive")
            if args.transcripts:
                raise TranscriptError("transcript paths cannot be combined with --live")
            return run_live(args)
        if (
            args.skill
            or args.prompt
            or args.model
            or args.expected_claim_permitted
            or set(args.expected_verdict) != {"fail", "insufficient_evidence"}
        ):
            raise TranscriptError("live-only options require --live")
        return run_static(args.transcripts)
    except TranscriptError as error:
        print(f"Pi eval failed closed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
