import psycopg2
import os
from dotenv import load_dotenv
 
# Load environment variables from .env
load_dotenv()
# Read database credentials
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

try:
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

    # Data to insert - Chicken Breast
    food_data = ("Chicken Breast", 165, 31, 0, 3.6)

    # Execute the query
    cursor.execute(insert_query, food_data)

    # Fetch the new food ID
    new_food_id = cursor.fetchone()[0]
    print(f"'Chicken Breast' added successfully! Food ID: {new_food_id}")

    # Commit transaction
    connection.commit()

    # Close connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to insert food: {e}")
