# ecu-tests

A tiny, hardware-free CAN exercise: a fake ECU answers a UDS-like
`ReadDataByIdentifier` request for DID `0xF190` on `python-can`'s virtual bus.
The first supported read deliberately waits 150 ms; later reads respond without
that extra delay. The tests cover the positive response, timing quirk, and an
unknown-DID negative response.

This is a teaching fixture, not a standards-complete UDS implementation. It
uses a simplified ISO-TP single-frame layout and a short fake identifier value
(`ECU1`); it does not implement real VIN data, multi-frame transport, or a real
ECU interface. Both virtual-bus endpoints run in one Python process, so no CAN
hardware is needed.

## Run

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest
```

Each test uses a unique virtual channel, keeping the examples isolated.
