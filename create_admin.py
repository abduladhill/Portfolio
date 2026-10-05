from werkzeug.security import generate_password_hash
from database import get_db_connection


username = input("Enter admin username: ").strip()
password = input("Enter admin password: ")


connection = get_db_connection()

existing_user = connection.execute(
    "SELECT * FROM admin WHERE username = ?",
    (username,)
).fetchone()

if existing_user:
    print("Admin user already exists.")
else:
    hashed_password = generate_password_hash(password)

    connection.execute(
        "INSERT INTO admin (username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    connection.commit()

    print("Admin user created successfully!")


connection.close()