import sqlite3

def add_ath_at_column(db_name, table_name):
    """Add the 'ath_at' column if it does not exist and update existing rows with timestamps."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if 'ath_at' column exists
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "ath_at" not in existing_columns:
        # Add column WITHOUT DEFAULT (SQLite restriction)
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN ath_at TEXT")
        # Update existing rows with CURRENT_TIMESTAMP
        #cursor.execute(f"UPDATE {table_name} SET ath_at = CURRENT_TIMESTAMP WHERE ath_at IS NULL")
        cursor.execute(f"UPDATE {table_name} SET ath_at = NULL WHERE ath_at IS NULL")
        
        conn.commit()
        print(f"✅ Column 'ath_at' added successfully and existing rows updated.")
    else:
        print(f"⚠️ Column 'ath_at' already exists. No changes made.")

    conn.close()

# Example usage
add_ath_at_column("tokens.db", "tokens")
