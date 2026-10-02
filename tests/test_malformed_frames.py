import pytest

MALFORMED_FRAMES = [
    pytest.param(b"", id="empty-data"),
    pytest.param(bytes([0x00, 0x22, 0xF1, 0x90]), id="zero-length-single-frame"),
    pytest.param(bytes([0x07, 0x22, 0xF1, 0x90]), id="declared-length-longer-than-frame"),
    pytest.param(bytes([0x10, 0x03, 0x22, 0xF1, 0x90]), id="first-frame-pci-not-supported"),
    pytest.param(bytes([0x20, 0x22, 0xF1, 0x90]), id="consecutive-frame-pci-not-supported"),
    pytest.param(bytes([0x30, 0x00, 0x00]), id="flow-control-pci-not-supported"),
]


@pytest.mark.parametrize("frame", MALFORMED_FRAMES)
def test_malformed_frame_gets_no_response(client, frame):
    """No requirement: the ECU ignores frames with an invalid single-frame header."""
    response = client.send_raw(frame, timeout=0.3)
    assert response.payload is None


def test_ecu_still_answers_after_malformed_frame(client):
    """REQ-001: a malformed frame must not break the next valid request."""
    client.send_raw(bytes([0x30, 0x00, 0x00]), timeout=0.2)
    assert client.read_did(0xF190).payload == bytes([0x62, 0xF1, 0x90]) + b"ECU1"