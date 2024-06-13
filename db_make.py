import psycopg2

# connection establishment
conn = psycopg2.connect(
    database="postgres",
    user="bob",
    password="starcow.7889",
    host="localhost",
    port="5432",
)

conn.autocommit = True

# Creating a cursor object
cursor = conn.cursor()

# query to create a database
sql = """ CREATE database rho_test """

# executing above query
cursor.execute(sql)
print("Database has been created successfully !!")

# Closing the connection
conn.close()
