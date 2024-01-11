import psycopg2 as psyc
import bcrypt
import Shop4allfunctions as saf

# Connect to the database
try:
    connection = psyc.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password"
    )
    
    cursor = connection.cursor()
    
    print("Connection successful.\n")


except (Exception, psyc.Error) as error:
    print("Error while connecting to PostgreSQL.")
    quit()

print("Connected to the PostgreSQL database.")

saf.fill_tables(cursor)