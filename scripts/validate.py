#!/usr/bin/env python3
"""Validate the portable engineering Agent Skills foundation using stdlib only."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "ecosystem.json"
REQUIRED_FIELDS = {"name", "description", "license"}
ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata"}
PROHIBITED_FIELDS = {"allowed" + "-tools", "disable" + "-model-invocation"}
REQUIRED_LEAD_REFERENCES = {
    "intent-routing.md",
    "definitions-by-intent.md",
    "skill-selection.md",
    "safety-gates.md",
    "cli-connectors-contract.md",
    "tracer-bullet-decomposition.md",
    "capability-routing.md",
}
INTENTS = {
    "investigation",
    "hotfix",
    "bugfix",
    "feature",
    "refactor",
    "migration",
    "spike",
    "review",
}
MAX_SKILL_LINES = 220
MIN_DESCRIPTION_LENGTH = 120
PLACEHOLDERS = ("TO" + "DO", "T" + "BD", "FIX" + "ME")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
VALID_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def report(self) -> int:
        if self.errors:
            print(f"Validation failed with {len(self.errors)} error(s):")
            for error in self.errors:
                print(f"- {error}")
            return 1
        print("Validation passed: manifest, 6 skills, frontmatter, links, references, fixtures, placeholders, and size limits.")
        return 0


def load_json(path: Path, validation: Validation) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        validation.error(f"missing JSON file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as error:
        validation.error(f"invalid JSON in {path.relative_to(ROOT)}: {error}")
    return None


def parse_frontmatter(path: Path, validation: Validation) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        validation.error(f"missing opening frontmatter delimiter: {path.relative_to(ROOT)}")
        return {}, text
    try:
        closing = lines.index("---", 1)
    except ValueError:
        validation.error(f"missing closing frontmatter delimiter: {path.relative_to(ROOT)}")
        return {}, text

    fields: dict[str, Any] = {}
    current_mapping: str | None = None
    for number, line in enumerate(lines[1:closing], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if current_mapping != "metadata" or ":" not in line:
                validation.error(f"unsupported frontmatter syntax at {path.relative_to(ROOT)}:{number}")
            continue
        if ":" not in line:
            validation.error(f"invalid frontmatter field at {path.relative_to(ROOT)}:{number}")
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key in fields:
            validation.error(f"duplicate frontmatter field {key!r} in {path.relative_to(ROOT)}")
        if value.startswith('"') and value.endswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                validation.error(f"invalid quoted value for {key!r} in {path.relative_to(ROOT)}")
        fields[key] = value
        current_mapping = key if not value else None
    return fields, text


def validate_manifest(validation: Validation) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = load_json(MANIFEST_PATH, validation)
    if not isinstance(manifest, dict):
        return {}, []
    skills = manifest.get("skills")
    if not isinstance(skills, list):
        validation.error("ecosystem.json must contain a skills array")
        return manifest, []
    if len(skills) != 6:
        validation.error(f"ecosystem.json must declare exactly 6 skills, found {len(skills)}")
    return manifest, [entry for entry in skills if isinstance(entry, dict)]


def validate_skills(skills: list[dict[str, Any]], validation: Validation) -> None:
    names: list[str] = []
    declared_dirs: set[Path] = set()
    for entry in skills:
        name = entry.get("name")
        relative_path = entry.get("path")
        if not isinstance(name, str) or not isinstance(relative_path, str):
            validation.error("every skill entry needs string name and path values")
            continue
        names.append(name)
        skill_dir = ROOT / relative_path
        declared_dirs.add(skill_dir.resolve())
        skill_path = skill_dir / "SKILL.md"
        if not skill_path.is_file():
            validation.error(f"manifest skill does not exist: {skill_path.relative_to(ROOT)}")
            continue

        fields, text = parse_frontmatter(skill_path, validation)
        missing = REQUIRED_FIELDS - fields.keys()
        if missing:
            validation.error(f"missing frontmatter fields {sorted(missing)} in {skill_path.relative_to(ROOT)}")
        unknown = fields.keys() - ALLOWED_FIELDS
        if unknown:
            validation.error(f"non-portable frontmatter fields {sorted(unknown)} in {skill_path.relative_to(ROOT)}")
        prohibited = fields.keys() & PROHIBITED_FIELDS
        if prohibited:
            validation.error(f"prohibited frontmatter fields {sorted(prohibited)} in {skill_path.relative_to(ROOT)}")
        if fields.get("name") != name or fields.get("name") != skill_dir.name:
            validation.error(f"skill name must match manifest and directory for {skill_path.relative_to(ROOT)}")
        if not VALID_NAME.fullmatch(name) or len(name) > 64:
            validation.error(f"invalid Agent Skills name: {name!r}")
        description = fields.get("description")
        if not isinstance(description, str) or len(description.strip()) < MIN_DESCRIPTION_LENGTH:
            validation.error(f"description is empty or shorter than {MIN_DESCRIPTION_LENGTH} characters in {skill_path.relative_to(ROOT)}")
        if isinstance(description, str) and len(description) > 1024:
            validation.error(f"description exceeds 1024 characters in {skill_path.relative_to(ROOT)}")
        if fields.get("license") != "MIT":
            validation.error(f"license must be MIT in {skill_path.relative_to(ROOT)}")
        line_count = len(text.splitlines())
        if line_count > MAX_SKILL_LINES:
            validation.error(f"main skill is too large ({line_count} > {MAX_SKILL_LINES} lines): {skill_path.relative_to(ROOT)}")

    duplicate_names = sorted({name for name in names if names.count(name) > 1})
    if duplicate_names:
        validation.error(f"duplicate skill names: {duplicate_names}")

    discovered = {path.parent.resolve() for path in (ROOT / "skills").glob("*/SKILL.md")}
    extra = discovered - declared_dirs
    if extra:
        validation.error(f"skills exist outside the manifest: {[str(path.relative_to(ROOT)) for path in sorted(extra)]}")


def validate_lead_references(validation: Validation) -> None:
    reference_dir = ROOT / "skills" / "dev-workflow" / "references"
    existing = {path.name for path in reference_dir.glob("*.md")}
    missing = REQUIRED_LEAD_REFERENCES - existing
    if missing:
        validation.error(f"missing required lead references: {sorted(missing)}")


def validate_markdown_links(validation: Validation) -> None:
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts or "logs" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (path.parent / local_target).resolve().exists():
                validation.error(f"broken local Markdown link in {path.relative_to(ROOT)}: {target}")


def validate_placeholders(validation: Validation) -> None:
    checked_extensions = {".md", ".json", ".py"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in checked_extensions:
            continue
        if ".git" in path.parts or "logs" in path.parts or path == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in PLACEHOLDERS:
            if re.search(rf"\b{re.escape(marker)}\b", text, flags=re.IGNORECASE):
                validation.error(f"placeholder marker {marker!r} in {path.relative_to(ROOT)}")


def validate_routing(validation: Validation) -> None:
    data = load_json(ROOT / "tests" / "routing-cases.json", validation)
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        validation.error("routing fixture must contain a cases array")
        return
    cases = data["cases"]
    covered = {case.get("expected_intent") for case in cases if isinstance(case, dict)}
    missing = INTENTS - covered
    if missing:
        validation.error(f"routing fixtures do not cover intents: {sorted(missing)}")
    kinds = {case.get("kind") for case in cases if isinstance(case, dict)}
    required_kinds = {"positive", "negative", "conflict"}
    if not required_kinds <= kinds:
        validation.error(f"routing fixtures need positive, negative, and conflict cases; found {sorted(kinds)}")
    if not any(
        case.get("kind") == "conflict"
        and case.get("expected_intent") == "investigation"
        and "implement" in str(case.get("prompt", "")).lower()
        and "failing test" in str(case.get("prompt", "")).lower()
        for case in cases
        if isinstance(case, dict)
    ):
        validation.error("routing fixtures need the implement plus failing-test conflict starting in investigation")


def validate_composition(manifest: dict[str, Any], validation: Validation) -> None:
    data = load_json(ROOT / "tests" / "composition-cases.json", validation)
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        validation.error("composition fixture must contain a cases array")
        return
    cases = [case for case in data["cases"] if isinstance(case, dict)]
    if not any("report" in str(case.get("scenario", "")).lower() for case in cases):
        validation.error("composition fixtures need the approved reports scenario")
    if not any("fallback" in str(case.get("expected_capability_action", "")).lower() for case in cases):
        validation.error("composition fixtures need an explicit capability fallback")
    optional = manifest.get("optional_capabilities", {})
    if not isinstance(optional, dict) or not optional:
        validation.error("ecosystem.json needs optional capability declarations")
    elif any(not isinstance(value, dict) or not value.get("fallback") for value in optional.values()):
        validation.error("every optional capability needs an explicit fallback")


def validate_all_json(validation: Validation) -> None:
    for path in ROOT.rglob("*.json"):
        if ".git" not in path.parts and "logs" not in path.parts:
            load_json(path, validation)


def main() -> int:
    validation = Validation()
    manifest, skills = validate_manifest(validation)
    validate_skills(skills, validation)
    validate_lead_references(validation)
    validate_markdown_links(validation)
    validate_placeholders(validation)
    validate_routing(validation)
    validate_composition(manifest, validation)
    validate_all_json(validation)
    return validation.report()


if __name__ == "__main__":
    sys.exit(main())
