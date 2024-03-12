import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()


class Queue:
    def __init__(self):
        host = os.getenv("PGHOST", "localhost")
        port = os.getenv("PGPORT", "5432")
        user = os.getenv("PGUSER", "postgres")
        password = os.getenv("PGPASSWORD", "")
        dbname = os.getenv("PGDATABASE", "postgres")

        self.conn = psycopg2.connect(
            dbname=dbname,
            host=host,
            user=user,
            password=password,
            port=port,
        )
        self.cur = self.conn.cursor()

        # Check if the table already exists
        self.cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM   information_schema.tables 
                WHERE  table_schema = 'public'
                AND    table_name = 'queue'
            );
        """
        )
        table_exists = self.cur.fetchone()[0]

        # If the table does not exist, create it
        if not table_exists:
            self.cur.execute(
                """
                CREATE TABLE queue (
                    txName VARCHAR(255),
                    address VARCHAR(255),
                    date TIMESTAMP,
                    param TEXT
                );
            """
            )
            self.conn.commit()

    def exists_for_address(self, address):
        self.cur.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM queue
                WHERE address = %s
            );
            """,
            (address,),
        )
        return self.cur.fetchone()[0]

    def sort(self):
        self.cur.execute(
            """
            SELECT txName, address, date, param
            FROM queue
            ORDER BY date ASC;
        """
        )
        rows = self.cur.fetchall()
        rows.sort(key=lambda x: x[2])

        for row in rows:
            self.cur.execute(
                """
                UPDATE queue
                SET txName = %s, address = %s, date = %s, param = %s
                WHERE txName = %s AND address = %s AND date = %s AND param = %s;
            """,
                (row[0], row[1], row[2], row[3], row[0], row[1], row[2], row[3]),
            )

        self.conn.commit()

        return True

    def insert(self, txName, address, date, param):
        # date = date.strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute(
            """
            INSERT INTO queue (txName, address, date, param)
            VALUES (%s, %s, %s, %s);
        """,
            (txName, address, date, param),
        )
        self.conn.commit()

        self.sort()
        return True

    def pop(self):

        self.sort()

        # Fetch the earliest record based on the date
        self.cur.execute(
            """
            SELECT txName, address, date, param
            FROM queue
            ORDER BY date ASC
            LIMIT 1;
            """
        )
        row = self.cur.fetchone()

        if row:
            self.cur.execute(
                """
                DELETE FROM queue
                WHERE txName = %s AND address = %s AND date = %s AND param = %s;
            """,
                row,
            )
            self.conn.commit()
            return row
        else:
            print("Queue is empty.")
            return None

    def clear_table(self):
        self.cur.execute(
            """
            DELETE FROM queue;
        """
        )
        self.conn.commit()
        print("All data cleared from 'queue' table.")

    def __del__(self):
        # Close the cursor and connection
        self.cur.close()
        self.conn.close()

    def drop_table(self):
        try:
            self.cur.execute("DROP TABLE IF EXISTS queue;")
            self.conn.commit()
            print("Table 'queue' has been deleted successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
