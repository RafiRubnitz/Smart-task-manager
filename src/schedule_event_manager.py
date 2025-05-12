from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base, Session
from config.db import engine
from datetime import datetime

Base = declarative_base()

class ScheduleEvent(Base):
    __tablename__ = "schedule_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    event_type = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    details = Column(String, nullable=True)
    datetime_iso = Column(DateTime, nullable=False)
    extracted_from = Column(String, nullable=True)
    source_date = Column(String, nullable=True)
    is_all_day = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    is_removed = Column(Boolean, default=False)
    removed_at = Column(DateTime, nullable=True)
    '''
    loaction
    duartion_time
    is_recurring
    calender_id
    '''

class ScheduleEventDB:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    @staticmethod
    def create_table():
        ScheduleEvent.metadata.create_all(engine)
        print("Schedule events table created")

    def reset_table(self):
        ScheduleEvent.__table__.drop(engine)
        print("Schedule events table removed")
        self.create_table()

    def insert_event(self, task_wrapper: dict):
        event = task_wrapper["event"]
        new_event = ScheduleEvent(
            user_id=task_wrapper["user_id"],
            title=event["title"],
            event_type=event.get("event_type"),
            priority=event.get("priority"),
            details=event.get("details"),
            datetime_iso=datetime.fromisoformat(event["datetime_iso"]),
            extracted_from=event.get("extracted_from"),
            source_date=event.get("source_date"),
            is_all_day=event.get("is_all_day", False)
        )
        self.db_session.add(new_event)
        self.db_session.commit()
        print(f"Event added: {event['title']}")
        return True

    def get_events(self, user_id: int):
        events = self.db_session.query(ScheduleEvent).filter(
            (ScheduleEvent.user_id == user_id) &
            (ScheduleEvent.is_removed == False)
        ).all()

        return [
            {
                "id": e.id,
                "title": e.title,
                "datetime": e.datetime_iso.isoformat(),
                "event_type": e.event_type,
                "priority": e.priority,
                "is_all_day": e.is_all_day
            }
            for e in events
        ]

    def remove_event(self, task_wrapper: dict):
        title = task_wrapper["event"]["title"]
        event = self.db_session.query(ScheduleEvent).filter(
            (ScheduleEvent.user_id == task_wrapper["user_id"]) &
            (ScheduleEvent.title == title) &
            (ScheduleEvent.is_removed == False)
        ).first()

        if event:
            event.is_removed = True
            event.removed_at = task_wrapper["removed_at"]
            self.db_session.commit()
            return True, "event removed"
        else:
            return False, "event not found"
