import sqlite3

def remove_column(db_name, table_name, column_to_remove):
    """Removes a column from a SQLite table by recreating it without the specified column."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Get existing column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]

    if column_to_remove not in columns:
        print(f"⚠️ Column '{column_to_remove}' does not exist in '{table_name}'. No changes made.")
        conn.close()
        return

    # Keep all columns except the one to remove
    columns_to_keep = [col for col in columns if col != column_to_remove]
    columns_str = ", ".join(columns_to_keep)

    # Create a new table with the same structure but without the unwanted column
    cursor.execute(f"CREATE TABLE {table_name}_new AS SELECT {columns_str} FROM {table_name}")

    # Drop the old table
    cursor.execute(f"DROP TABLE {table_name}")

    # Rename the new table to the original table name
    cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")

    conn.commit()
    conn.close()

    print(f"✅ Column '{column_to_remove}' removed successfully from '{table_name}'.")

# Example usage:
remove_column("tokens.db", "tokens", "ath_at")
