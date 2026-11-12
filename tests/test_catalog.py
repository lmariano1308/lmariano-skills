"""Regression tests for the published catalog and the demonstration contract."""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "ecosystem.json").read_text(encoding="utf-8"))
PORTFOLIO_AREAS = {"front-end", "motion", "design", "back-end", "review", "visual-qa"}
PORTFOLIO_SKILLS = {
    "investigation",
    "frontend",
    "motion",
    "design-direction",
    "backend",
    "visual-qa",
}
DEMO_SCRIPTS = (
    ROOT / "scripts" / "run_demo.py",
    ROOT / "examples" / "rounding-service" / "qa" / "check_preview.py",
)


class CatalogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.skills = MANIFEST["skills"]

    def test_portfolio_areas_are_published(self) -> None:
        covered = {entry.get("area") for entry in self.skills}
        self.assertEqual(PORTFOLIO_AREAS - covered, set())

    def test_every_skill_has_dated_evidence(self) -> None:
        for entry in self.skills:
            with self.subTest(skill=entry["name"]):
                evidence = entry.get("evidence")
                self.assertIsInstance(evidence, list)
                self.assertTrue(evidence)
                for record in evidence:
                    self.assertTrue(record["project"].strip())
                    self.assertTrue(record["ref"].strip())
                    self.assertTrue(record["result"].strip())
                    self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")

    def test_skill_descriptions_carry_discovery_wording(self) -> None:
        for entry in self.skills:
            with self.subTest(skill=entry["name"]):
                text = (ROOT / entry["path"] / "SKILL.md").read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"name: {entry['name']}", text)
                self.assertIn("license: MIT", text)

    def test_demo_documents_the_demonstrated_chain(self) -> None:
        demo = (ROOT / "docs" / "workflow-demo.md").read_text(encoding="utf-8")
        published = {entry["name"] for entry in self.skills}
        chain = {
            "dev-workflow",
            "repo-context",
            "investigation",
            "backend",
            "review-gate",
            "visual-qa",
            "completion-gate",
        }
        self.assertEqual(chain - published, set())
        for name in chain:
            self.assertIn(f"`{name}`", demo)

    def test_published_skills_name_no_tool(self) -> None:
        published = {entry["name"] for entry in self.skills}
        self.assertEqual(PORTFOLIO_SKILLS - published, set())
        forbidden = (
            "playwright", "puppeteer", "cypress", "selenium", "webdriver",
            "chromium", "firefox", "safari", "gsap", "scrolltrigger", "framer",
            "lenis", "tailwind", "figma", "lighthouse", "jest", "vitest",
            "pytest", "react", "vue", "svelte", "angular", "vite", "webpack",
            "nuxt", "golang", "postgres", "mysql", "mongodb", "redis", "sqlite",
            "python3",
        )
        pattern = re.compile(r"\b(" + "|".join(forbidden) + r")\b", re.IGNORECASE)
        for name in sorted(PORTFOLIO_SKILLS):
            for path in (ROOT / "skills" / name).rglob("*.md"):
                with self.subTest(skill=name, file=path.name):
                    text = path.read_text(encoding="utf-8")
                    self.assertEqual(
                        [token for token in pattern.findall(text)],
                        [],
                        f"{path} names a specific tool or stack",
                    )

    def test_demo_scripts_use_the_standard_library_only(self) -> None:
        allowed = set(getattr(__import__("sys"), "stdlib_module_names", ()))
        for script in DEMO_SCRIPTS:
            with self.subTest(script=script.name):
                tree = ast.parse(script.read_text(encoding="utf-8"))
                imported: set[str] = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported.add(node.module.split(".")[0])
                self.assertEqual(imported - allowed, set())


if __name__ == "__main__":
    unittest.main()
