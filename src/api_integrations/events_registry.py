from api_integrations.events_repository import EventsRepository
from api_integrations.models import WebhookPayload


class EventRegistry:
    def __init__(self):
        self.path = "events_db"

    def register(self, payload: WebhookPayload) -> bool:
        self.repository = EventsRepository(self.path)
        event = self.repository.get_event_by_event_id(payload.event_id)
        if event is None:
            self.repository.save_event(payload)
            return True
        return False
