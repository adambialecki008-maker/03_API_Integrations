import sqlite3, time
from pathlib import Path
from api_integrations.models import (
    RegisteredEvent,
    AlarmData,
    WebhookPayload,
)
from datetime import datetime
from zoneinfo import ZoneInfo


def format_timestamp(timestamp: int | datetime | str) -> str:
    if isinstance(timestamp, int):
        return datetime.fromtimestamp(timestamp, tz=ZoneInfo("UTC")).isoformat()
    if isinstance(timestamp, datetime):
        return timestamp.astimezone(ZoneInfo("UTC")).isoformat()
    return timestamp


class DuplicateEventError(Exception):
    pass


class EventsRepository:

    def __init__(self, path: str | Path = "database/events.db"):
        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.path)

    def create_table(self):
        connection = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                event TEXT NOT NULL,
                machine TEXT NOT NULL,
                alarm_code INT NOT NULL,
                timestamp TEXT NOT NULL,
                received_at TEXT NOT NULL)""")
        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            print("Error during creating events table")
            raise
        finally:
            if connection:
                connection.close()

    def save_event(self, payload: WebhookPayload) -> None:
        connection = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                """INSERT INTO events (event_id, event, machine, alarm_code, timestamp, received_at) VALUES (?,?,?,?,?,?) """,
                (
                    payload.event_id,
                    payload.event,
                    payload.data.machine,
                    payload.data.alarm_code,
                    format_timestamp(payload.timestamp),
                    format_timestamp(int(time.time())),
                ),
            )
            connection.commit()

        except sqlite3.Error as e:
            if connection:
                connection.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise DuplicateEventError(
                    f"Event {payload.event_id} already exists"
                ) from e
            print("Error during saving event to database")
            raise
        finally:
            if connection:
                connection.close()

    def get_events(
        self,
        event_id: str | None = None,
        machine: str | None = None,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[list[RegisteredEvent], int]:
        connection = None
        results = []

        if time_to is not None and time_from is not None and time_to < time_from:
            raise ValueError("time_from cannot be later than time_to")
        try:
            params = []
            conditions = []
            total = 0
            query = """SELECT event_id,event, machine, alarm_code, timestamp, received_at FROM events """
            query_total = """SELECT COUNT(*) OVER() AS total FROM events 
            """
            if event_id is not None:
                params.append(event_id)
                conditions.append("event_id=?")
            if machine is not None:
                params.append(machine)
                conditions.append("machine=?")
            connection = self.connect()
            cursor = connection.cursor()
            if time_from is not None:
                params.append(format_timestamp(time_from))
                conditions.append("timestamp >= ?")
            if time_to is not None:
                params.append(format_timestamp(time_to))
                conditions.append("timestamp < ?")

            if conditions:
                query += "WHERE " + " AND ".join(conditions)
                query_total += "WHERE " + " AND ".join(conditions)
            query += "ORDER BY timestamp DESC, id DESC "
            cursor.execute(query_total, params)
            total_row = cursor.fetchone()
            total = total_row[0] if total_row else 0
            if limit is not None:
                query += " LIMIT ? "
                params.append(int(limit))
            if offset is not None:
                query += " OFFSET ? "
                params.append(int(offset))
            cursor.execute(query, params)
            rows = cursor.fetchall()

            if rows is not None:
                for row in rows:
                    alarm_data = AlarmData(machine=row[2], alarm_code=row[3])

                    result = RegisteredEvent(
                        event_id=row[0],
                        event=row[1],
                        data=alarm_data,
                        timestamp=row[4],
                        received_at=row[5],
                    )
                    results.append(result)
            return results, total
        except sqlite3.Error as e:
            print(f"Error during getting event: {event_id}")
            raise
        finally:
            if connection:
                connection.close()
