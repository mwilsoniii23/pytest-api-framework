import re
from pathlib import Path

BUGS_PATH = Path(__file__).resolve().parents[2] / "docs" / "bugs-found.md"
ROOT_PATH = Path(__file__).resolve().parents[2]


def test_every_logged_defect_has_a_resolvable_test() -> None:
    """Coverage links in bugs-found.md must point at tests that exist."""

    refs = re.findall(r"`(tests/[^`]+::[^`]*)`", BUGS_PATH.read_text())
    assert refs, "No test coverage references found in bugs-found.md"

    for ref in refs:
        path, _, name = ref.partition("::")

        assert name, f"{ref}: test name missing"
        assert (ROOT_PATH / path).exists(), f"{ref}: file missing"
        assert f"def {name}(" in (ROOT_PATH / path).read_text(), f"{ref}: test missing: {name}"
