import sqlite3

DATABASE = "portfolio.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    # Projects table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            technologies TEXT,
            github_url TEXT,
            demo_url TEXT,
            status TEXT DEFAULT 'Completed'
        )
    """)
        # Add image_url to existing projects table if it does not exist
    project_columns = connection.execute(
        "PRAGMA table_info(projects)"
    ).fetchall()

    column_names = [column["name"] for column in project_columns]

    if "image_url" not in column_names:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN image_url TEXT"
        )

        # Add features to existing projects table if it does not exist
    project_columns = connection.execute(
        "PRAGMA table_info(projects)"
    ).fetchall()

    column_names = [column["name"] for column in project_columns]

    if "features" not in column_names:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN features TEXT"
        )
    # Add category to existing projects table if it does not exist
    project_columns = connection.execute(
        "PRAGMA table_info(projects)"
    ).fetchall()

    column_names = [column["name"] for column in project_columns]

    if "category" not in column_names:
        connection.execute(
            "ALTER TABLE projects ADD COLUMN category TEXT"
        )

    # Admin table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Site settings table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS site_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            headline TEXT,
            hero_description TEXT,
            about TEXT,
            email TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            resume_url TEXT
        )
    """)

    # Skills table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT
        )
    """)

    # Experience table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree TEXT NOT NULL,
            institution TEXT NOT NULL,
            location TEXT,
            start_date TEXT,
            end_date TEXT,
            description TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            issuer TEXT NOT NULL,
            issue_date TEXT,
            credential_url TEXT,
            description TEXT
        )
    """)
    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    connection.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")