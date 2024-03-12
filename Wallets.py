import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

# load environment variables
load_dotenv()


class Wallets:
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
                AND    table_name = 'wallets'
            );
        """
        )
        table_exists = self.cur.fetchone()[0]

        # If the table does not exist, create it
        if not table_exists:
            self.cur.execute(
                """
                CREATE TABLE wallets (
                    address VARCHAR(255),
                    privKey VARCHAR(255)
                );
            """
            )
            self.conn.commit()

    def insert(self, address, privKey):
        # date = date.strftime("%Y-%m-%d %H:%M:%S")
        self.cur.execute(
            """
            INSERT INTO wallets (address, privKey)
            VALUES (%s, %s);
        """,
            (address, privKey),
        )
        self.conn.commit()

        return True

    def get_privKey(self, address):
        self.cur.execute(
            """
            SELECT privKey
            FROM wallets
            WHERE address = %s;
        """,
            (address,),
        )
        row = self.cur.fetchone()
        if row:
            return row[0]
        else:
            print(f"No row found for address '{address}' in 'wallets' table.")
            return None

    def clear_table(self):
        self.cur.execute(
            """
            DELETE FROM wallets;
        """
        )
        self.conn.commit()
        print("All data cleared from 'queue' table.")

    def get_all_addresses(self):
        self.cur.execute(
            """
            SELECT address
            FROM wallets;
            """
        )
        rows = self.cur.fetchall()
        addresses = [row[0] for row in rows]
        return addresses

    def __del__(self):
        # Close the cursor and connection
        self.cur.close()
        self.conn.close()

    # def get_actionList(self, address):
    #     self.cur.execute(
    #         """
    #         SELECT actionList
    #         FROM wallets
    #         WHERE address = %s;
    #     """,
    #         (address,),
    #     )
    #     row = self.cur.fetchone()
    #     if row:
    #         return row[0]
    #     else:
    #         print(f"No row found for address '{address}' in 'wallets' table.")
    #         return None

    # def update_actionList(self, address, new_actionList):
    #     self.cur.execute(
    #         """
    #         UPDATE my_table
    #         SET actionList = %s
    #         WHERE address = %s;
    #     """,
    #         (Json(new_actionList), address),
    #     )
    #     self.conn.commit()
