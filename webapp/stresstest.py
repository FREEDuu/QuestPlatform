import psycopg2
import random
import time

# Database connection parameters
DB_NAME = "questapplication"
DB_USER = "carl"
DB_PASSWORD = "mZT4Uo9u2aB7Y2ApZB3ZP45VwN5zmRlG"
DB_HOST = "dpg-cnnihula73kc739tq2lg-a.frankfurt-postgres.render.com"
DB_PORT = "5432"

# Number of objects to create
NUM_OBJECTS = 1000  # Adjust as needed

def measure_insertion_time():
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Record start time
        start_time = time.time()

        # Execute 1000 insertions
        for _ in range(NUM_OBJECTS):
            # Generate random data
            nr_test = random.randint(1, 100)
            nr_gruppo = random.randint(1, 100)
            tipo = random.choice(["manuale", "automatico"])
            in_sequenza = random.choice([True, False])
            secondi_ritardo = random.randint(1, 10)
            data_ora_inizio = time.strftime('%Y-%m-%d %H:%M:%S')

            # Construct the SQL INSERT statement
            sql_insert = f"""
                INSERT INTO "webapp_testsgroup" ("utente_id", "nrTest", "nrGruppo", "tipo", "inSequenza", "secondiRitardo", "dataOraInizio", "dataOraInserimento")
                VALUES (1, {nr_test}, {nr_gruppo}, '{tipo}', {in_sequenza}, {secondi_ritardo}, '{data_ora_inizio}', CURRENT_TIMESTAMP)
            """

            # Execute the INSERT query
            cursor.execute(sql_insert)

        # Commit the transaction
        #conn.commit()

        # Record end time
        end_time = time.time()

        # Calculate and return the total execution time
        total_execution_time = end_time - start_time

        # Close cursor and connection
        cursor.close()
        conn.close()

        return total_execution_time
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Measure insertion time
    total_time = measure_insertion_time()

    # Print the total insertion time
    if total_time is not None:
        print(f"Total time taken to insert {NUM_OBJECTS} objects: {total_time} seconds")
