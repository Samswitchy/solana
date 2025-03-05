import sqlite3

def update_database_schema(db_name, table_name):
    """Ensure the database has the required columns and update existing records with default values."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # List of columns to add (column_name, type, default_value)
    columns = [
        ("ath", "REAL", 0),
        ("liquidity", "REAL", None),  # No default value
        ("status", "TEXT", "active"),
        ("trade", "TEXT", "HOLD")
    ]

    # Get existing columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = {row[1] for row in cursor.fetchall()}

    # Add missing columns
    for col_name, col_type, default in columns:
        if col_name not in existing_columns:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")

    # Ensure existing rows have default values
    for col_name, col_type, default in columns:
        if default is not None:
            cursor.execute(f"UPDATE {table_name} SET {col_name} = ? WHERE {col_name} IS NULL", (default,))

    conn.commit()
    conn.close()
    print(f"✅ Database '{db_name}' updated successfully!")

# Example usage:
update_database_schema("tokens.db", "tokens")
