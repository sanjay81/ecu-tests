"""Minimal UDS client for the fake ECU (single frames only)."""
import time
from dataclasses import dataclass

import can

from ecu_sim.fake_ecu import REQUEST_ID, RESPONSE_ID


@dataclass
class Response:
    payload: bytes | None  # None means no response within the timeout
    elapsed: float  # seconds from send to receive (or to timeout)

    @property
    def is_negative(self) -> bool:
        return self.payload is not None and self.payload[0] == 0x7F


class UdsClient:
    def __init__(self, channel: str):
        self._bus = can.Bus(interface="virtual", channel=channel)

    def close(self) -> None:
        self._bus.shutdown()

    def send_raw(self, frame: bytes, timeout: float = 1.0) -> Response:
        """Send raw CAN data bytes exactly as given (use for malformed frames)."""
        self._bus.send(can.Message(arbitration_id=REQUEST_ID, data=frame, is_extended_id=False))
        start = time.monotonic()
        deadline = start + timeout
        while (remaining := deadline - time.monotonic()) > 0:
            msg = self._bus.recv(timeout=remaining)
            if msg is not None and msg.arbitration_id == RESPONSE_ID:
                length = msg.data[0]
                return Response(bytes(msg.data[1 : 1 + length]), time.monotonic() - start)
        return Response(None, time.monotonic() - start)

    def request(self, payload: bytes, timeout: float = 1.0) -> Response:
        """Wrap payload in a single-frame header and send it."""
        frame = (bytes([len(payload)]) + payload).ljust(8, b"\x00")
        return self.send_raw(frame, timeout)

    def read_did(self, did: int, timeout: float = 1.0) -> Response:
        return self.request(bytes([0x22]) + did.to_bytes(2, "big"), timeout)