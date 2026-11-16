import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse 
from fastapi.templating import Jinja2Templates 
from pydantic import BaseModel


#==============
# Blueprints 
#==============

# Blueprint for an appointment request
class AppointmentCreate(BaseModel):
    client_name: str
    client_phone: str
    appointment_date: str


# Blueprint for a cancel request
class CancelBooking(BaseModel):
    client_id: int


#============
#============
app = FastAPI()

templates = Jinja2Templates(directory="templates")

DB_FILE = "bookings.db"

#==================
# Helper functions
#==================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT NOT NULL,
        client_phone TEXT NOT NULL,
        appointment_date TEXT NOT NULL,
        notified BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def get_owner_schedule(date: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM appointments " \
        "WHERE appointment_date LIKE ? " \
        "ORDER BY appointment_date ASC", (f"{date}%",)
    )
    owner_schedule = cursor.fetchall()
    conn.close()
    return owner_schedule


def get_booked_hours_by_date(date: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT appointment_date FROM appointments WHERE appointment_date LIKE ?",
        (f"{date}%",))
    booked_rows = cursor.fetchall()
    conn.close()
    taken_hours = []
    for row in booked_rows:
        date_string = row[0]
        date_date, date_time = date_string.split(" ")
        taken_hours.append(date_time)

    return taken_hours


def get_bookings_by_id(user_id: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM appointments WHERE id = ?", (user_id,)
    )
    found = cursor.fetchone()
    conn.commit()
    conn.close()

    return found



#================
#================

init_db()


#=============
# Web routes 
#=============

@app.get("/", response_class = HTMLResponse)
def read_owner_dashboard(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = "owner-dashboard.html",
        context = {"request": request}
        )


@app.get("/owner/dashboard")
def owner_schedule_for_the_day(date: str):
    owner_schedule_today = get_owner_schedule(date)
    if owner_schedule_today is None:
        raise HTTPException(status_code=400, detail="No bookings found for the day")

    return {"date": date, "schedule": owner_schedule_today}


@app.post("/book")
def book_appointment(appointment: AppointmentCreate):
    date_date, date_time = appointment.appointment_date.split(" ")
    booked_hours = get_booked_hours_by_date(date_date)
    if date_time in booked_hours:
        raise HTTPException(status_code=400, detail="This time slot is alreadyb booked")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (client_name, client_phone, appointment_date) VALUES (?, ?, ?)",
        (appointment.client_name, appointment.client_phone, appointment.appointment_date)
    )
    conn.commit()
    conn.close()

    return {"status": "success", "message": f"Appointment booked for {appointment.client_name}!"}


@app.post("/cancel-appointment")
def cancel_appointment(booking_to_cancel: CancelBooking):
    checking = get_bookings_by_id(booking_to_cancel.client_id)
    if checking is None:
        raise HTTPException(status_code=404, detail= "Appointment ID not found")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM appointments WHERE id = ?", 
        (booking_to_cancel.client_id,)
    )
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Cancellation complete"}



@app.get("/appointments")
def get_all_appointments():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM appointments")

    rows = cursor.fetchall()   
    conn.commit()
    conn.close()

    return {"appointments": rows}


@app.get("/available-slots")
def get_slots(date: str):
    # The master list of possible 2-hr slots for the owner
    possible_slots = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    booked_hours = get_booked_hours_by_date(date)
    free_slots = []
    for slot in possible_slots:
        if slot not in booked_hours:
            free_slots.append(slot)

    return {"date": date, "available_slots": free_slots}
