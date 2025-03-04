import sqlite3

def init_db():
    conn = sqlite3.connect("trading_analysis.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wash_trading_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            suspicious_wallets TEXT,
            suspicious_times TEXT,
            suspicious_pairs TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def log_suspicious_activity(contract_address, suspicious_wallets, suspicious_times, suspicious_pairs):
    conn = sqlite3.connect("trading_analysis.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO wash_trading_log (contract_address, suspicious_wallets, suspicious_times, suspicious_pairs)
        VALUES (?, ?, ?, ?)
    """, (contract_address, str(suspicious_wallets), str(suspicious_times), str(suspicious_pairs)))

    conn.commit()
    conn.close()

init_db()
