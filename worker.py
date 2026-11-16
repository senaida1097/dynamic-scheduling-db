import sqlite3
import time
from datetime import  datetime, timedelta

DB_FILE = "scheduler.db"

print("Watchman Worker is alive and tracking the clock...")

# Every 60 seconds checks our database to calculate and check 
# every client whos appointment is 20 minutes from current time to notify/remind about appmnt
while True:
    # Target time (Current time + 20 min)
    target_time = (datetime.now() + timedelta(minutes = 20)).strftime("%T-%m-%d %H:^M")
    # Open database file
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, client_name, client_phone, appointment_time " \
        "FROM appointment" \
        "WHERE appointment_time = ? AND notified = 0", (target_time,)
    )
    matching_appointments = cursor.fetchall()

    for appt in matching_appointments:
        appt_id = appt[0]
        name = appt[1]
        phone = appt[2]
        appt_time = appt[3]
        # Simulation for sending the text message over through an API
        print(f"[REMINDER SENT] Texting {name} at {phone}: 'Your appointment is in 20 min at : ({appt_time})!")
        # Update notified value
        cursor.execute(
            "UPDATE appointment" \
            "SET notified = 1" \
            "WHERE id = ?",
            (appt_id,)
        )
        conn.commit()
        conn.close()

        time.sleep(60)
