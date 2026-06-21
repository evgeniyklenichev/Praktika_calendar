# routers/calendar.py — Студент 1: Календарь
from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database import get_db
import calendar as cal_lib
from datetime import date, datetime, timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_theme(db):
    row = db.execute("SELECT value FROM settings WHERE key='theme'").fetchone()
    return row["value"] if row else "light"


@router.get("/calendar", response_class=HTMLResponse)
def calendar_page(
    request: Request,
    year: int = None,
    month: int = None,
    day: int = None,
    view: str = "month"
):
    today = date.today()
    year = year or today.year
    month = month or today.month

    # Выбранный день: из параметра ?day=, либо сегодня (если попадает в текущий месяц), либо 1-е число месяца
    if day:
        selected_day = date(year, month, day)
    elif today.year == year and today.month == month:
        selected_day = today
    else:
        selected_day = date(year, month, 1)

    db = get_db()
    theme = get_theme(db)

    # Build month grid
    first_weekday, days_in_month = cal_lib.monthrange(year, month)
    # Adjust: Monday=0
    start_offset = first_weekday  # Monday already 0

    # Previous / next month
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1

    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # Get events for this month
    month_str = f"{year}-{month:02d}"
    events = db.execute(
        "SELECT * FROM events WHERE date LIKE ? ORDER BY date, time_start",
        (f"{month_str}%",)
    ).fetchall()

    # Map events by day
    events_by_day = {}
    for e in events:
        event_day_num = int(e["date"].split("-")[2])
        events_by_day.setdefault(event_day_num, []).append(dict(e))

    # For week view
    week_events = []
    weekday_names_ru = [
        "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"
    ]
    if view == "week":
        # Находим неделю, содержащую выбранный день
        week_start = selected_day - timedelta(days=selected_day.weekday())
        week_days = [(week_start + timedelta(days=i)) for i in range(7)]
        for d in week_days:
            day_events = db.execute(
                "SELECT * FROM events WHERE date=? ORDER BY time_start",
                (d.strftime("%Y-%m-%d"),)
            ).fetchall()
            week_events.append({
                "date": d,
                "weekday_label": f"{weekday_names_ru[d.weekday()]}, {d.strftime('%d.%m')}",
                "events": [dict(e) for e in day_events]
            })

    # For day view
    day_events = []
    if view == "day":
        day_events = db.execute(
            "SELECT * FROM events WHERE date=? ORDER BY time_start",
            (selected_day.strftime("%Y-%m-%d"),)
        ).fetchall()
        day_events = [dict(e) for e in day_events]

    db.close()

    month_names_ru = [
        "", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]

    return templates.TemplateResponse("calendar.html", {
        "request": request,
        "theme": theme,
        "year": year,
        "month": month,
        "month_name": month_names_ru[month],
        "days_in_month": days_in_month,
        "start_offset": start_offset,
        "today": today,
        "events_by_day": events_by_day,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "view": view,
        "week_events": week_events,
        "day_events": day_events,
        "selected_day": selected_day,
    })


@router.get("/api/calendar/events")
def get_events_for_date(date_str: str = Query(..., alias="date")):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM events WHERE date=? ORDER BY time_start",
        (date_str,)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]
