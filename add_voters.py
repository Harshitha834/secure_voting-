import bcrypt
from db import get_db

# list of voters (you can add many)
users = [
    ("101", "pass"),
    ("102", "hello"),
    ("103", "secure"),
    ("104", "vote123")
]

db = get_db()
cur = db.cursor()

for user in users:
    voter_id = user[0]
    password = user[1]

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    cur.execute(
        "INSERT INTO voters (voter_id, password) VALUES (%s,%s)",
        (voter_id, hashed.decode())
    )

db.commit()
print("All voters added successfully")