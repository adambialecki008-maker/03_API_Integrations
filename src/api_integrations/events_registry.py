from api_integrations.events_repository import EventsRepository, DuplicateEventError
from api_integrations.models import WebhookPayload


class EventRegistry:
    def __init__(self):
        self.path = "events_db"

    def register(self, payload: WebhookPayload) -> bool:
        self.repository = EventsRepository(self.path)
        try:
            self.repository.save_event(payload)
            return True
        except DuplicateEventError as e:
            return False
