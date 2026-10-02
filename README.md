# ecu-tests

A practice project: pytest tests for a fake ECU that answers simplified UDS requests over a virtual CAN bus.
I built it to practise **reviewing and validating AI-generated tests** (Codex in VS Code), not just generating them.
All data is synthetic.

Related project: [log-triage](https://github.com/sanjay81/log-triage), a companion project for investigating synthetic logs.

## What it shows

- Requirements-based tests with traceability (`REQ-001` to `REQ-005` in `docs/requirements.md`, referenced in each test docstring)
- Rules for the AI tool in `AGENTS.md` (no `time.sleep`, seeded tests, requirement IDs, do not change the ECU to make a test pass)
- Testing non-deterministic timing with a statistical budget instead of a single pass or fail
- Mutation testing: breaking the ECU on purpose to check whether the tests notice
- A log of where the AI went wrong: [`ai_mistakes.md`](ai_mistakes.md)

## Setup

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt
    pytest -v

Expected: 15 passed, 1 xfailed (the xfail is intentional, see below).

## Layout

    ecu_sim/            fake ECU and minimal UDS client
    tests/              requirement tests and timing tests
    exercises/          a deliberately flaky test (run on purpose: pytest exercises)
    docs/requirements.md  synthetic requirements
    conftest.py         fixtures (seeded ECU on an isolated virtual bus)
    AGENTS.md           rules for AI coding agents
    ai_mistakes.md      what the AI got wrong, and how I found and fixed it

## The fake ECU

- Simplified UDS, single CAN frames only (request ID 0x7E0, response ID 0x7E8)
- Service 0x22 (ReadDataByIdentifier) with two DIDs: 0xF190 (4 bytes), 0xF186 (1 byte)
- Negative responses: 0x11 (service not supported), 0x13 (incorrect length), 0x31 (request out of range)
- Invalid frame headers get no response
- Response time: 20-60 ms, but 10% of responses take 90-130 ms, close to the 100 ms limit in REQ-002

## Results

**Mutation testing.** I changed the ECU in three ways and checked which tests failed.

| Mutation | Caught by |
|---|---|
| Length check `!= 3` changed to `< 3` | Extra-bytes test (the AI's original tests missed it) |
| F186 value changed | F186 test |
| Slow responses made much slower (0.2-0.3 s) | Max-latency ceiling test. The rate test missed it. |

"Within 100 ms" is ambiguous (every response? 99%?). Read strictly, this ECU violates it. By design, 10% of responses are slow (90-130 ms), so about 7.5% exceed 100 ms in theory. In a 100-request sample with seed 1234 I measured 12% (a 200-request run gave 7%), so small samples are noisy.\
&#x20;I kept the strict reading as `xfail(strict=True)`, and added two regression guards (a rate budget of 15% and a 150 ms ceiling) so the behavior can't get worse. The budget is my assumption and needs confirming with the requirement owner.

## Lessons

1. Passing AI-generated tests do not prove the tests are good. Break the code and check.
2. When asked to fix a flaky test, the AI removed the randomness instead of handling it. That hid the problem.
3. One statistical check is not enough. A rate check and a ceiling check catch different failures.
4. Ambiguous requirements need a human decision, not a silent AI interpretation.
5. I made a wrong prediction about one mutation and only found out by measuring.

## Limitations

- The ECU is simulated and simple. There is no ISO-TP multi-frame, no sessions, and no security access.
- Timing numbers depend on the machine running the tests.
- The regression guard's 15% exceedance budget is an assumption, not a requirement.
- Mutations were applied by hand, not with a mutation testing tool.
