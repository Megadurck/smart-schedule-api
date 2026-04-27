from datetime import date as date_type, datetime, time, timedelta

from agent.config import AGENT_COMPANY_NAME
from app.database.session import Base, SessionLocal, engine
from app.models.working_hours_model import WorkingHours
from app.repositories import company_repository, schedule_repository
from app.services import schedule_service


def get_db_session():
	Base.metadata.create_all(bind=engine)
	return SessionLocal()


def get_agent_company_id(db) -> int:
	company = company_repository.find_or_create_company(db, AGENT_COMPANY_NAME)
	return company.id


def parse_date(value: str) -> date_type:
	return datetime.strptime(value, "%d/%m/%Y").date()


def parse_time(value: str) -> time:
	if len(value) == 5:
		value = f"{value}:00"
	return time.fromisoformat(value)


def list_available_slots(
	db,
	start_date: str | None,
	days_ahead: int = 7,
	limit: int = 8,
) -> list[dict]:
	base_date = parse_date(start_date) if start_date else datetime.now().date()
	max_date = base_date + timedelta(days=max(days_ahead, 1))
	company_id = get_agent_company_id(db)

	working_hours_map = {
		item.weekday: item
		for item in db.query(WorkingHours)
		.filter(WorkingHours.company_id == company_id, WorkingHours.is_active == True)
		.all()
	}

	slots: list[dict] = []
	current_date = base_date
	while current_date <= max_date and len(slots) < limit:
		day_working_hours = working_hours_map.get(current_date.weekday())
		if day_working_hours:
			for slot in _build_daily_slots(day_working_hours):
				if not schedule_repository.check_conflict(db, company_id, current_date, slot):
					slots.append({"date": current_date, "time": slot})
					if len(slots) >= limit:
						break

		current_date += timedelta(days=1)

	return slots


def create_schedule_offline(db, customer_name: str, schedule_date: str, schedule_time: str):
	company_id = get_agent_company_id(db)
	return schedule_service.create_schedule(
		db,
		company_id=company_id,
		customer_name=customer_name,
		date_str=schedule_date,
		time_str=schedule_time,
	)


def _build_daily_slots(working_hours: WorkingHours) -> list[time]:
	if working_hours.slot_duration_minutes <= 0:
		return []

	start = _time_to_minutes(working_hours.start_time)
	end = _time_to_minutes(working_hours.end_time)
	lunch_start = _time_to_minutes(working_hours.lunch_start) if working_hours.lunch_start else None
	lunch_end = _time_to_minutes(working_hours.lunch_end) if working_hours.lunch_end else None

	slots: list[time] = []
	current = start
	while current <= end:
		in_lunch_break = (
			lunch_start is not None
			and lunch_end is not None
			and lunch_start <= current < lunch_end
		)
		if not in_lunch_break:
			slots.append(_minutes_to_time(current))
		current += working_hours.slot_duration_minutes

	return slots


def _time_to_minutes(value: time) -> int:
	return value.hour * 60 + value.minute


def _minutes_to_time(value: int) -> time:
	return time(hour=value // 60, minute=value % 60)
