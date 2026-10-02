# ECU requirements (synthetic, for practice)

- REQ-001: The ECU shall answer a ReadDataByIdentifier (0x22) request for a supported DID with a positive response (0x62 + DID + data).
- REQ-002: The ECU shall respond to a diagnostic request within 100 ms.
- REQ-003: The ECU shall answer a request for an unsupported DID with negative response code 0x31.
- REQ-004: The ECU shall answer a 0x22 request with an incorrect message length with negative response code 0x13.
- REQ-005: The ECU shall answer an unsupported service with negative response code 0x11.

Supported DIDs: 0xF190 (identification, 4 bytes), 0xF186 (active session, 1 byte).