import sqlite3

DB_PATH = "signalements.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:

        # Table des signalements (utilisateurs)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS signalements (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie         TEXT NOT NULL,
                description       TEXT NOT NULL,
                lieu              TEXT NOT NULL,
                solution_proposee TEXT,
                statut            TEXT DEFAULT 'en attente',
                date_creation     DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table des admins
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                nom              TEXT NOT NULL UNIQUE,
                mot_de_passe     TEXT NOT NULL,
                date_inscription DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("Base de données initialisée avec succès !")

if __name__ == "__main__":
    init_db()