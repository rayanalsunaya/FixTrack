import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "fixtrack.db")

# pretend the open prediction was made 90 days ago
old_day = str(date.today() - timedelta(days=90))

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute(
    "UPDATE predictions_log SET created_at = ? WHERE actual_date IS NULL",
    (old_day,),
)
conn.commit()
print("rows changed:", cursor.rowcount)
conn.close()