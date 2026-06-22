# routers/reminders.py — Студент 2: Напоминания
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_theme(db):
    row = db.execute("SELECT value FROM settings WHERE key='theme'").fetchone()
    return row["value"] if row else "light"


@router.get("/reminders", response_class=HTMLResponse)
def reminders_page(request: Request, filter: str = "upcoming"):
    db = get_db()
    theme = get_theme(db)

    if filter == "done":
        rows = db.execute(
            "SELECT * FROM reminders WHERE is_done=1 ORDER BY datetime"
        ).fetchall()
    elif filter == "all":
        rows = db.execute(
            "SELECT * FROM reminders ORDER BY is_done, datetime"
        ).fetchall()
    else:  # upcoming
        rows = db.execute(
            "SELECT * FROM reminders WHERE is_done=0 ORDER BY datetime"
        ).fetchall()

    db.close()
    return templates.TemplateResponse("reminders.html", {
        "request": request,
        "theme": theme,
        "reminders": [dict(r) for r in rows],
        "filter": filter,
    })


@router.get("/reminders/new", response_class=HTMLResponse)
def new_reminder_page(request: Request):
    db = get_db()
    theme = get_theme(db)
    db.close()
    return templates.TemplateResponse("reminder_form.html", {
        "request": request,
        "theme": theme,
        "reminder": None,
    })


@router.post("/reminders/new")
def create_reminder(
    title: str = Form(...),
    datetime: str = Form(...),
    category: str = Form("Личное"),
    color: str = Form("#22C55E"),
    emoji: str = Form(""),
):
    db = get_db()
    db.execute(
        "INSERT INTO reminders (title, datetime, category, color, emoji) VALUES (?, ?, ?, ?, ?)",
        (title, datetime, category, color, emoji)
    )
    db.commit()
    db.close()
    return RedirectResponse(url="/reminders", status_code=303)


@router.get("/reminders/{rid}/edit", response_class=HTMLResponse)
def edit_reminder_page(request: Request, rid: int):
    db = get_db()
    theme = get_theme(db)
    reminder = db.execute("SELECT * FROM reminders WHERE id=?", (rid,)).fetchone()
    db.close()
    if not reminder:
        return RedirectResponse(url="/reminders")
    return templates.TemplateResponse("reminder_form.html", {
        "request": request,
        "theme": theme,
        "reminder": dict(reminder),
    })


@router.post("/reminders/{rid}/edit")
def update_reminder(
    rid: int,
    title: str = Form(...),
    datetime: str = Form(...),
    category: str = Form("Личное"),
    color: str = Form("#22C55E"),
    emoji: str = Form(""),
):
    db = get_db()
    db.execute(
        "UPDATE reminders SET title=?, datetime=?, category=?, color=?, emoji=? WHERE id=?",
        (title, datetime, category, color, emoji, rid)
    )
    db.commit()
    db.close()
    return RedirectResponse(url="/reminders", status_code=303)


@router.post("/reminders/{rid}/toggle")
def toggle_reminder(rid: int):
    db = get_db()
    db.execute(
        "UPDATE reminders SET is_done = CASE WHEN is_done=1 THEN 0 ELSE 1 END WHERE id=?",
        (rid,)
    )
    db.commit()
    db.close()
    return RedirectResponse(url="/reminders", status_code=303)


@router.post("/reminders/{rid}/delete")
def delete_reminder(rid: int):
    db = get_db()
    db.execute("DELETE FROM reminders WHERE id=?", (rid,))
    db.commit()
    db.close()
    return RedirectResponse(url="/reminders", status_code=303)


@router.get("/api/reminders")
def api_get_reminders():
    db = get_db()
    rows = db.execute("SELECT * FROM reminders ORDER BY datetime").fetchall()
    db.close()
    return [dict(r) for r in rows]
