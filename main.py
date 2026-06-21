from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import init_db
from routers import calendar, events, reminders, settings

app = FastAPI(title="Электронный Календарь")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(calendar.router)
app.include_router(events.router)
app.include_router(reminders.router)
app.include_router(settings.router)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
def root():
    return RedirectResponse(url="/calendar")
