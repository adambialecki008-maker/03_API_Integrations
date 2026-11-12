class EventRegistry:
    def __init__(self):
        self.seen_ids: set[str] = set()

    def register(self, event_id: str) -> bool:
        if not event_id in self.seen_ids:
            self.seen_ids.add(event_id)
            return True
        return False
