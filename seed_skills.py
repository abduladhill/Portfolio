from database import get_db_connection

skills = [
    # Programming
    ("Python", "Programming"),
    ("Java", "Programming"),
    ("C", "Programming"),

    # Machine Learning
    ("Scikit-learn", "Machine Learning"),
    ("Regression", "Machine Learning"),
    ("Classification", "Machine Learning"),
    ("Clustering", "Machine Learning"),
    ("KNN", "Machine Learning"),
    ("Decision Trees", "Machine Learning"),
    ("Random Forest", "Machine Learning"),
    ("K-Means", "Machine Learning"),
    ("PCA", "Machine Learning"),

    # Data Science
    ("NumPy", "Data Science"),
    ("Pandas", "Data Science"),
    ("Matplotlib", "Data Science"),
    ("Seaborn", "Data Science"),
    ("Data Preprocessing", "Data Science"),
    ("Exploratory Data Analysis", "Data Science"),

    # Web Development
    ("Flask", "Web Development"),
    ("Django", "Web Development"),
    ("React.js", "Web Development"),

    # Databases
    ("SQL", "Databases"),
    ("SQLite", "Databases"),

    # AI & Embedded Systems
    ("Embedded AI", "AI & Embedded Systems"),
    ("ESP32", "AI & Embedded Systems"),
    ("Raspberry Pi", "AI & Embedded Systems"),
    ("Arduino IDE", "AI & Embedded Systems"),

    # Tools
    ("Git", "Tools"),
    ("GitHub", "Tools"),
    ("VS Code", "Tools"),
    ("Jupyter Notebook", "Tools"),
]

connection = get_db_connection()

added = 0
skipped = 0

for name, category in skills:

    existing = connection.execute(
        "SELECT id FROM skills WHERE name = ?",
        (name,)
    ).fetchone()

    if existing:
        skipped += 1
        continue

    connection.execute(
        "INSERT INTO skills (name, category) VALUES (?, ?)",
        (name, category)
    )

    added += 1

connection.commit()
connection.close()

print(f"Skills added: {added}")
print(f"Skills already existed: {skipped}")
print("Skill database updated successfully!")