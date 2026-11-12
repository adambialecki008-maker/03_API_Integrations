from webhooks.duplication import EventRegistry


def test_event_registry():
    registry = EventRegistry()

    assert registry.register("evt_001") is True
    assert registry.register("evt_001") is False
    assert registry.register("evt_002") is True
