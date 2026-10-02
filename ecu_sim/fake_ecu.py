"""A tiny fake ECU that speaks a simplified UDS over CAN (single frames only).

Simplifications (on purpose, to keep the exercise small):
- No ISO-TP multi-frame, so DID values are at most 4 bytes.
- Request ID 0x7E0, response ID 0x7E8.
- Only service 0x22 (ReadDataByIdentifier) is implemented.
"""
import random
import threading
import time

import can

REQUEST_ID = 0x7E0
RESPONSE_ID = 0x7E8

DATA_IDENTIFIERS = {
    0xF190: b"ECU1",  # pretend VIN (shortened)
    0xF186: b"\x01",  # active diagnostic session

}

NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_INCORRECT_LENGTH = 0x13
NRC_REQUEST_OUT_OF_RANGE = 0x31


class FakeEcu:
    """Answers diagnostic requests on a virtual CAN bus, with variable latency.

    Latency: 20-60 ms normally. With `spike_probability` a response takes
    90-130 ms instead (a 'slow' response around the 100 ms limit).
    """

    def __init__(self, channel: str, seed: int | None = None, spike_probability: float = 0.1):
        self._bus = can.Bus(interface="virtual", channel=channel)
        self._rng = random.Random(seed)
        self._spike_probability = spike_probability
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        self._bus.shutdown()

    def _run(self) -> None:
        while not self._stop.is_set():
            msg = self._bus.recv(timeout=0.05)
            if msg is None or msg.arbitration_id != REQUEST_ID:
                continue
            payload = self._parse_single_frame(bytes(msg.data))
            if payload is None:
                continue  # invalid frame header: ECU stays silent
            response = self._handle(payload)
            time.sleep(self._latency())
            self._send(response)

    def _latency(self) -> float:
        if self._rng.random() < self._spike_probability:
            return self._rng.uniform(0.09, 0.13)
        return self._rng.uniform(0.02, 0.06)

    @staticmethod
    def _parse_single_frame(data: bytes) -> bytes | None:
        if not data:
            return None
        pci_type, length = data[0] >> 4, data[0] & 0x0F
        if pci_type != 0 or length == 0 or length > len(data) - 1:
            return None
        return data[1 : 1 + length]

    @staticmethod
    def _negative(service: int, nrc: int) -> bytes:
        return bytes([0x7F, service, nrc])

    def _handle(self, payload: bytes) -> bytes:
        service = payload[0]
        if service != 0x22:
            return self._negative(service, NRC_SERVICE_NOT_SUPPORTED)
        if len(payload) != 3:
            return self._negative(service, NRC_INCORRECT_LENGTH)
        did = int.from_bytes(payload[1:3], "big")
        if did not in DATA_IDENTIFIERS:
            return self._negative(service, NRC_REQUEST_OUT_OF_RANGE)
        return bytes([0x62]) + payload[1:3] + DATA_IDENTIFIERS[did]

    def _send(self, payload: bytes) -> None:
        frame = bytes([len(payload)]) + payload
        frame = frame.ljust(8, b"\x00")
        self._bus.send(can.Message(arbitration_id=RESPONSE_ID, data=frame, is_extended_id=False))