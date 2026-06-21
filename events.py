# routers/events.py — Студент 1: События
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_theme(db):
    row = db.execute("SELECT value FROM settings WHERE key='theme'").fetchone()
    return row["value"] if row else "light"


@router.get("/events", response_class=HTMLResponse)
def events_page(request: Request):
    db = get_db()
    theme = get_theme(db)
    events = db.execute(
        "SELECT * FROM events ORDER BY date DESC, time_start"
    ).fetchall()
    db.close()
    return templates.TemplateResponse("events.html", {
        "request": request,
        "theme": theme,
        "events": [dict(e) for e in events],
    })


@router.get("/events/new", response_class=HTMLResponse)
def new_event_page(request: Request, date: str = ""):
    db = get_db()
    theme = get_theme(db)
    db.close()
    return templates.TemplateResponse("event_form.html", {
        "request": request,
        "theme": theme,
        "event": None,
        "prefill_date": date,
    })


@router.post("/events/new")
def create_event(
    title: str = Form(...),
    date: str = Form(...),
    time_start: str = Form(""),
    time_end: str = Form(""),
    repeat: str = Form("none"),
    reminder: str = Form("none"),
    description: str = Form(""),
    color: str = Form("#7C5CBF"),
    emoji: str = Form(""),
):
    db = get_db()
    db.execute(
        """INSERT INTO events (title, date, time_start, time_end, repeat, reminder, description, color, emoji)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (title, date, time_start, time_end, repeat, reminder, description, color, emoji)
    )
    db.commit()
    db.close()
    return RedirectResponse(url=f"/calendar?year={date[:4]}&month={int(date[5:7])}", status_code=303)


@router.get("/events/{event_id}/edit", response_class=HTMLResponse)
def edit_event_page(request: Request, event_id: int):
    db = get_db()
    theme = get_theme(db)
    event = db.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    db.close()
    if not event:
        return RedirectResponse(url="/events")
    return templates.TemplateResponse("event_form.html", {
        "request": request,
        "theme": theme,
        "event": dict(event),
        "prefill_date": "",
    })


@router.post("/events/{event_id}/edit")
def update_event(
    event_id: int,
    title: str = Form(...),
    date: str = Form(...),
    time_start: str = Form(""),
    time_end: str = Form(""),
    repeat: str = Form("none"),
    reminder: str = Form("none"),
    description: str = Form(""),
    color: str = Form("#7C5CBF"),
    emoji: str = Form(""),
):
    db = get_db()
    db.execute(
        """UPDATE events SET title=?, date=?, time_start=?, time_end=?, repeat=?, reminder=?, description=?, color=?, emoji=?
           WHERE id=?""",
        (title, date, time_start, time_end, repeat, reminder, description, color, emoji, event_id)
    )
    db.commit()
    db.close()
    return RedirectResponse(url=f"/calendar?year={date[:4]}&month={int(date[5:7])}", status_code=303)


@router.post("/events/{event_id}/delete")
def delete_event(event_id: int):
    db = get_db()
    event = db.execute("SELECT date FROM events WHERE id=?", (event_id,)).fetchone()
    db.execute("DELETE FROM events WHERE id=?", (event_id,))
    db.commit()
    db.close()
    if event:
        d = event["date"]
        return RedirectResponse(url=f"/calendar?year={d[:4]}&month={int(d[5:7])}", status_code=303)
    return RedirectResponse(url="/calendar", status_code=303)


@router.get("/api/events")
def api_get_events():
    db = get_db()
    rows = db.execute("SELECT * FROM events ORDER BY date, time_start").fetchall()
    db.close()
    return [dict(r) for r in rows]
