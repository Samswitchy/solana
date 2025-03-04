import sqlite3
from config import DATABASE_NAME
import datetime

def update_existing_timestamps():
    """Set 'updated_at' to current timestamp for existing rows."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    current_time = datetime.datetime.utcnow()  # Get current UTC time

    try:
        cursor.execute("UPDATE tokens SET updated_at = ?", (current_time,))
        conn.commit()
        print("✅ Existing rows updated with timestamps!")
    except sqlite3.OperationalError as e:
        print(f"⚠️ Error: {e}")
    
    conn.close()

update_existing_timestamps()
