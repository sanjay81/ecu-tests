import uuid

import can
import pytest

from fake_ecu import FakeECU, REQUEST_ID, RESPONSE_ID


@pytest.fixture
def tester_bus():
    channel = f"ecu-tests-{uuid.uuid4().hex}"
    with can.Bus(interface="virtual", channel=channel) as ecu_bus:
        with can.Bus(interface="virtual", channel=channel) as tester:
            ecu = FakeECU(ecu_bus)
            ecu.start()
            yield tester
            ecu.stop()


def send_read(bus, did=b"\xF1\x90"):
    bus.send(
        can.Message(
            arbitration_id=REQUEST_ID,
            data=b"\x03\x22" + did,
            is_extended_id=False,
        )
    )


def test_read_f190_returns_positive_response(tester_bus):
    send_read(tester_bus)

    response = tester_bus.recv(timeout=1)

    assert response is not None
    assert response.arbitration_id == RESPONSE_ID
    assert bytes(response.data) == b"\x07\x62\xF1\x90ECU1"


def test_first_f190_response_has_deliberate_delay(tester_bus):
    send_read(tester_bus)

    assert tester_bus.recv(timeout=0.03) is None
    response = tester_bus.recv(timeout=1)

    assert response is not None
    assert bytes(response.data)[1:4] == b"\x62\xF1\x90"


def test_unknown_did_returns_negative_response(tester_bus):
    send_read(tester_bus, did=b"\xF1\x99")

    response = tester_bus.recv(timeout=1)

    assert response is not None
    assert bytes(response.data) == b"\x03\x7F\x22\x31"
