import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

## load data into DF and clean up the data
df = pd.read_excel("JUST_TRACK_IT/data/food_nut_values.xlsx", header=0, decimal=",")
df.columns = df.columns.str.strip()
df["name"] = df["name"].apply(lambda x: x.strip().lower())



# Load environment variables from .env
load_dotenv()

# Read database credentials
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")


# Establish connection
connection = psycopg2.connect(
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    dbname=DBNAME
)
print("Connection successful!")

# Create cursor
cursor = connection.cursor()

# Define the INSERT query
insert_query = """
INSERT INTO foods (id, name, calories, protein, carbohydrates, fat)
VALUES (gen_random_uuid(), %s, %s, %s, %s, %s)
RETURNING id;
"""
# Run loop over each row of DF and insert into DB
success_count = 0
duplicate_count = 0
for row in df.itertuples(index=False):
    try:
        # Check if food already exists
        cursor.execute("SELECT COUNT(*) FROM foods WHERE name = %s", (row.name,))
        if cursor.fetchone()[0] > 0:
            print(f"Skipping duplicate: {row.name}")
            duplicate_count += 1
            continue
# Insert the row
        cursor.execute("""
            INSERT INTO foods (id, name, calories, protein, carbohydrates, fat)
            VALUES (gen_random_uuid(), %s, %s, %s, %s, %s)
        """, (row.name, row.calories, row.protein, row.carbohydrates, row.fat))

        print(f"Inserted: {row.name}")
        success_count += 1
    except Exception as e:
            print(f"Failed to insert {row.name}: {e}")

# Commit transaction
connection.commit()

# Close connection
cursor.close()
connection.close()
print("Connection closed.")
print(f"Done. Inserted: {success_count}, Skipped: {duplicate_count}")
