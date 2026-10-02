# Project rules for AI coding agents

This repo tests a fake ECU (UDS over a virtual CAN bus) with pytest. It is a practice project with synthetic data only.

## Conventions
- Python 3.10+, type hints on all new functions.
- Use pytest. Test names: `test_<feature>_<condition>`.
- One behavior per test. Prefer several small tests over one long one.
- Never use `time.sleep` in tests. Wait with a timeout (see `UdsClient.request`).
- Use the `client` and `make_ecu` fixtures from `conftest.py`. Do not create buses by hand in tests.
- Tests must be deterministic: use a seeded ECU (`make_ecu(seed=...)`) unless the test is about randomness.
- Every test should reference a requirement ID from `docs/requirements.md` in its docstring (for traceability).

## Do not
- Do not change `ecu_sim/fake_ecu.py` behavior to make a test pass. If a test fails, report whether it is a product bug, a test bug, or flakiness.
- Do not loosen a timing limit without saying why.

## Commands
- Run tests: `pytest -v`
