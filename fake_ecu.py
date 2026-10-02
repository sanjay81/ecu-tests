"""A tiny ECU responder for virtual-CAN tests; not a full UDS/ISO-TP stack."""

import threading
import time

import can

REQUEST_ID = 0x7E0
RESPONSE_ID = 0x7E8
VIN_DID = b"\xF1\x90"


class FakeECU:
    """Answer single-frame ReadDataByIdentifier requests on a CAN bus."""

    def __init__(self, bus: can.BusABC, first_read_delay: float = 0.15):
        self.bus = bus
        self.first_read_delay = first_read_delay
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._first_read_seen = False

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=1)

    def _serve(self) -> None:
        while not self._stop.is_set():
            message = self.bus.recv(timeout=0.05)
            if message is None or message.arbitration_id != REQUEST_ID:
                continue
            data = bytes(message.data)
            if len(data) < 4 or data[:2] != b"\x03\x22":
                continue
            did = data[2:4]
            if did == VIN_DID:
                response = b"\x07\x62" + did + b"ECU1"
                if not self._first_read_seen:
                    self._first_read_seen = True
                    time.sleep(self.first_read_delay)  # deliberate first-read quirk
            else:
                response = b"\x03\x7F\x22\x31"  # requestOutOfRange
            self.bus.send(
                can.Message(arbitration_id=RESPONSE_ID, data=response, is_extended_id=False)
            )
