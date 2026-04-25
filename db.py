import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="mksHarshitha@123",
        database="voting_db"
    )
