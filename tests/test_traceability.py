import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQ_PATTERN = re.compile(r"REQ-\d{3}")


def _ids(text: str) -> set[str]:
    return set(REQ_PATTERN.findall(text))


def test_every_requirement_has_at_least_one_test():
    """Traceability: every REQ in docs/requirements.md is referenced by a test."""
    required = _ids((ROOT / "docs" / "requirements.md").read_text())
    tested = set()
    for path in (ROOT / "tests").glob("test_*.py"):
        if path.name != Path(__file__).name:
            tested |= _ids(path.read_text())
    assert required - tested == set(), f"Requirements without tests: {sorted(required - tested)}"


def test_tests_only_reference_existing_requirements():
    """Traceability: no test references a requirement that does not exist."""
    required = _ids((ROOT / "docs" / "requirements.md").read_text())
    referenced = set()
    for path in (ROOT / "tests").glob("test_*.py"):
        if path.name != Path(__file__).name:
            referenced |= _ids(path.read_text())
    assert referenced - required == set(), f"Unknown requirements: {sorted(referenced - required)}"