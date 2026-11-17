import sqlite3, time
from pathlib import Path
from api_integrations.models import RegisteredEvent, AlarmData, WebhookPayload
from datetime import datetime


def format_timestamp(timestamp: int) -> str:
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%d-%m-%Y %H:%M:%S")


class EventsRepository:
    def __init__(self, database_name: str | Path):
        self.database_name = database_name
        self.create_table()

    def connect(self):
        return sqlite3.connect(self.database_name)

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
            print("Error during saving event to database")
            raise
        finally:
            if connection:
                connection.close()

    def get_event_by_event_id(self, event_id: str) -> RegisteredEvent | None:
        connection = None
        result = None
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                """ SELECT  event, machine, alarm_code, timestamp, received_at FROM events WHERE event_id=?""",
                (event_id,),
            )
            row = cursor.fetchone()
            if row is not None:
                alarm_data = AlarmData(machine=row[1], alarm_code=row[2])
                result = RegisteredEvent(
                    event_id=event_id,
                    event=row[0],
                    data=alarm_data,
                    timestamp=row[3],
                    received_at=row[4],
                )
            return result
        except sqlite3.Error as e:
            print(f"Error during getting event: {event_id}")
            raise
        finally:
            if connection:
                connection.close()
