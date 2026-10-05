from database import get_db_connection


connection = get_db_connection()

connection.execute("""
    INSERT INTO projects
    (title, description, technologies, github_url, demo_url, status)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    "Portfolio CMS",
    "A full-stack portfolio management system built using Python and Flask.",
    "Python, Flask, SQLite, HTML, CSS, JavaScript",
    "https://github.com/",
    "",
    "In Progress"
))

connection.commit()
connection.close()

print("Project added successfully!")