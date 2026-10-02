import uuid

import pytest

from ecu_sim.client import UdsClient
from ecu_sim.fake_ecu import FakeEcu


@pytest.fixture
def make_ecu():
    """Factory: start a fake ECU on its own virtual bus and return a client for it."""
    created = []

    def _make(seed: int | None = 1234, spike_probability: float = 0.1) -> UdsClient:
        channel = f"vbus-{uuid.uuid4().hex}"
        ecu = FakeEcu(channel, seed=seed, spike_probability=spike_probability)
        ecu.start()
        client = UdsClient(channel)
        created.append((ecu, client))
        return client

    yield _make
    for ecu, client in created:
        client.close()
        ecu.stop()


@pytest.fixture
def client(make_ecu) -> UdsClient:
    """Default client: seeded ECU, so timing is repeatable."""
    return make_ecu(seed=1234)