import sqlite3
from config import DATABASE_NAME

# Connect to your database
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Rename the column from "price" to "holders"
cursor.execute("ALTER TABLE tokens RENAME COLUMN price TO holders;")

# Commit changes and close the connection
conn.commit()
conn.close()