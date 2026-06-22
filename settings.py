# routers/settings.py — Студент 2: Настройки
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_all_settings(db):
    rows = db.execute("SELECT key, value FROM settings").fetchall()
    return {r["key"]: r["value"] for r in rows}


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request):
    db = get_db()
    s = get_all_settings(db)
    db.close()
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "theme": s.get("theme", "light"),
        "settings": s,
    })


@router.post("/settings")
def save_settings(
    theme: str = Form("light"),
    first_day: str = Form("monday"),
    timezone: str = Form("UTC+03:00"),
    time_format: str = Form("24"),
    event_reminder: str = Form("30min"),
    reminder_notify: str = Form("attime"),
):
    db = get_db()
    updates = {
        "theme": theme,
        "first_day": first_day,
        "timezone": timezone,
        "time_format": time_format,
        "event_reminder": event_reminder,
        "reminder_notify": reminder_notify,
    }
    for key, value in updates.items():
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    db.commit()
    db.close()
    return RedirectResponse(url="/settings?saved=1", status_code=303)


@router.get("/api/settings")
def api_get_settings():
    db = get_db()
    s = get_all_settings(db)
    db.close()
    return s


@router.post("/api/settings/theme")
def api_set_theme(theme: str = Form(...)):
    db = get_db()
    db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('theme', ?)", (theme,))
    db.commit()
    db.close()
    return {"theme": theme}
