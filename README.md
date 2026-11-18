# Dynamic Scheduling Business Owner Dashboard
An asynchronous, full-stack appointment scheduling system built with **FastAPI**, **SQLite**, **Jinja2**, and **Vanilla Javascript**. With a decoupled service layer, strict double-booking prevention, parameterized SQL queries, and an autonomous background daemon for upcoming appointment alerts for clients.

## System Architecture 
* **Client & Presentation Layer ('owner-dashboard.html'):** 
  FastAPI serves the initial dashboard using Jinja2 templates. When an owner selects a date, asynchronous Javascript ('fetch') requests daily bookings and dynamically renders open or occupied time slots without reloading the page.
* **Application & Routing Layer ('main.py'):** 
  Uvicorn runs the FastAPI server, validating all incoming JSON payloads through Pydantic schemas ('AppointmentCreate', 'CancelBooking'), and routing requests to decoupled database helper functions.
* **Persistence Layer ('bookings.db'):** 
  A local SQLite database stores appointment records. All database operations use parameterized SQL queries ('?') placeholders to prevent SQL injection and check existing timestamps to block double-bookings.
* **Background Notification ('worker.py'):** 
  A standalone daemon process polls ('bookings.db') every 60 seconds, it detects appointments occurring within a 20min window, dispatches reminders, and updates a 'notified' flag to prevent duplicate alerts.



## Tech Stack
* **Backend:** Python, FastAPI, Uvicorn (ASGI), Pydantic
* **Database:** SQLite3
* **Frontend:** HTML5, CSS3,Vanilla Javascript, Jinja2 Templates



## Local Setup & Initialization 

### 1. Clone Repository
```bash
git clone https://github.com
cd single-owner-scheduler
```
### 2. Create & Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start the Web Server
```bash
uvicorn main:app --reload
```
* **Owner Dashboard:** `http://127.0.0.1:8000/`
* **Interactive API Docs (Swagger UI):** `http://127.0.0.1:8000/docs`



| Method | Endpoint | Description |
| :--- | :--- | :--- |
| 'GET' | '/' | Serves the Owner Dashboard UI ('owner-dashboard.html'). |
| 'GET' | '/owner/dashboard?date={YYYY-MM--DD}' | Fetches all booked appointments for a specific date. |
| 'GET' | '/available-slots?date={YYYY-MM-DD}' | Returns open 2hr time slots ('08:00' - '20:00') for a given date. |
| 'GET' | '/appointments' | Retrieves all stored appointments from the database. |
| 'POST' | '/book' | Validates client details and creates a new booking ('YYYY-MM-DD HH:MM'). |
| 'POST' | '/cancel-appointment' | Cancels and deletes an appointment by client_id' ('int'). |




## Planned Roadmap (Feature Branches)

* [ ] **Timezone Synchronization:** Standardize timestamps using Python's `zoneinfo` module for cloud deployments.
* [ ] **Owner Authentication:** Implement `bcrypt` password hashing and session-based route protection for dashboard access.
* [ ] **Multi-Tenant Support:** Introduce an `owners` table with foreign-key relationships to support multiple business schedules independently.
