# What the AI got wrong

Add a rough entry as soon as you notice a problem; tidy it later. Include the date and project when logging across projects. Keep each entry factual and specific. If the problem is not fixed yet, say so plainly.

| # | Date | Project | Task | What the AI did | What was wrong / missing | How I found it | How I fixed it |
|---|------|---------|------|-----------------|--------------------------|----------------|----------------|
| 1 | 2026-10-02 | ecu-tests | Fix the flaky timing exercise (`exercises/test_timing_flaky.py`) | The conversation does not record a specific AI-proposed fix. | The exercise uses `seed=None` and makes 20 requests with a hard `< 100 ms` assertion; it says 10% of responses take 90–130 ms. Without the proposed change, we cannot say whether the AI fixed the cause or hid the failure. | Read the exercise instructions and test; they recommend repeated runs with `pytest exercises/ -v`. | Not yet fixed: the AI's actual proposal and the human's final correction were not recorded. |
| 2 | 2026-10-02 | ecu-tests | Review test count | The AI initially repeated the README's expected count without running the suite. | The documented count was not verified; the suite later collected 16 tests, not the count implied by the earlier review. | Ran `pytest -v` via the project virtual environment and observed 15 passed, 1 xfailed. | Updated the README expected count to the observed result. |
| 3 | 2026-10-02 | ecu-tests | Explain REQ-002 latency measurements | The AI treated the 7.5% and 12% exceedance figures as conflicting measurements and replaced the README explanation with a claim that 7.5% came from a different measurement. | It did not establish that explanation. The figures are consistent with the user's theory/sample figures: 7.5% theoretical and 12% in a 100-request sample; the README should preserve that distinction. | The user supplied the intended wording and clarified that small samples are noisy (200 requests measured 7%). | Replaced the paragraph with the supplied explanation. |

## What the AI did well

Add specific examples here too, so the log reflects both useful work and mistakes.

## What scripts can generate

Tests can generate some of the review, but not the most valuable part.

| What | Can a script generate it? | How |
|---|---|---|
| Which requirements have tests | Yes | Read the `REQ-xxx` IDs from test docstrings and compare them with `docs/requirements.md`. Any requirement with no test is a gap. |
| Which bugs the tests miss | Yes | Mutation testing changes the ECU code one small way at a time, runs `pytest`, and records which mutations were caught and which survived. |
| Weak assertions | Partly | A script can flag patterns like `assert response.payload is not None`, `assert response`, or a test with no assertion. |
| Tests that can't fail | Partly | Mutation testing can reveal this: if a test never fails under any mutation, it's suspect. |
| Flaky tests | Yes | Run the suite 20 times and report which tests changed result. |
| What the AI did and why it was wrong | No | “It said it didn't run the tests” and “it disabled the spikes to get stability” describe the AI's behavior and judgment. A test result can't show that. |
