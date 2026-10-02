from collections.abc import Callable
from pathlib import Path
import re

from ecu_sim.client import UdsClient
from ecu_sim.fake_ecu import (
    NRC_INCORRECT_LENGTH,
    NRC_REQUEST_OUT_OF_RANGE,
    NRC_SERVICE_NOT_SUPPORTED,
)


def test_read_supported_f190_returns_identification(client: UdsClient) -> None:
    """REQ-001: supported F190 reads return a positive response and four data bytes."""
    response = client.read_did(0xF190)

    assert response.payload == bytes([0x62, 0xF1, 0x90]) + b"ECU1"


def test_read_supported_f186_returns_active_session(client: UdsClient) -> None:
    """REQ-001: supported F186 reads return a positive response and one data byte."""
    response = client.read_did(0xF186)

    assert response.payload == bytes([0x62, 0xF1, 0x86, 0x01])


def test_nominal_latency_without_spikes(
    make_ecu: Callable[..., UdsClient],
) -> None:
    """Nominal latency only. Does NOT verify REQ-002, see test_timing.py."""
    client = make_ecu(seed=1234, spike_probability=0.0)

    response = client.read_did(0xF190)

    assert response.payload is not None
    assert response.elapsed <= 0.100


def test_read_unsupported_did_returns_out_of_range_nrc(client: UdsClient) -> None:
    """REQ-003: unsupported DIDs receive negative response code 0x31."""
    response = client.read_did(0x1234)

    assert response.payload == bytes([0x7F, 0x22, NRC_REQUEST_OUT_OF_RANGE])


def test_read_did_with_incorrect_length_returns_length_nrc(client: UdsClient) -> None:
    """REQ-004: 0x22 requests without exactly two DID bytes receive NRC 0x13."""
    response = client.request(bytes([0x22, 0xF1]))

    assert response.payload == bytes([0x7F, 0x22, NRC_INCORRECT_LENGTH])


def test_unsupported_service_returns_service_nrc(client: UdsClient) -> None:
    """REQ-005: unsupported diagnostic services receive negative response code 0x11."""
    response = client.request(bytes([0x10, 0x01]))

    assert response.payload == bytes([0x7F, 0x10, NRC_SERVICE_NOT_SUPPORTED])

def test_read_did_with_extra_bytes_returns_length_nrc(client):
    """REQ-004: a 0x22 request with too many bytes receives NRC 0x13."""
    response = client.request(bytes([0x22, 0xF1, 0x90, 0x00]))
    assert response.payload == bytes([0x7F, 0x22, NRC_INCORRECT_LENGTH])


def test_invalid_frame_header_gets_no_response(client):
    """No requirement: the ECU ignores frames with an invalid single-frame header."""
    response = client.send_raw(bytes([0xF3, 0x22, 0xF1, 0x90, 0, 0, 0, 0]), timeout=0.3)
    assert response.payload is None


def test_invalid_empty_frame_gets_no_response(client: UdsClient) -> None:
    """Malformed-frame behavior: an empty CAN payload gets no response."""
    response = client.send_raw(b"", timeout=0.1)
    assert response.payload is None


def test_invalid_zero_length_frame_gets_no_response(client: UdsClient) -> None:
    """Malformed-frame behavior: a zero-length single frame gets no response."""
    response = client.send_raw(bytes([0x00, 0, 0, 0, 0, 0, 0, 0]), timeout=0.1)
    assert response.payload is None


def test_invalid_declared_length_gets_no_response(client: UdsClient) -> None:
    """Malformed-frame behavior: a length larger than the data gets no response."""
    response = client.send_raw(bytes([0x08, 0x22, 0xF1, 0x90]), timeout=0.1)
    assert response.payload is None


def test_invalid_pci_type_gets_no_response(client: UdsClient) -> None:
    """Malformed-frame behavior: an unsupported PCI type gets no response."""
    response = client.send_raw(bytes([0x12, 0x22, 0xF1, 0x90, 0, 0, 0, 0]), timeout=0.1)
    assert response.payload is None


def test_requirement_ids_are_covered_by_test_docstrings() -> None:
    """Every requirement in the spec must appear in at least one test docstring."""
    root = Path(__file__).resolve().parents[1]
    requirement_text = (root / "docs" / "requirements.md").read_text(encoding="utf-8")
    requirement_ids = set(re.findall(r"\bREQ-\d{3}\b", requirement_text))
    test_docstrings = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((root / "tests").glob("test_*.py"))
    )
    covered_ids = set(re.findall(r"\bREQ-\d{3}\b", test_docstrings))
    assert requirement_ids <= covered_ids
