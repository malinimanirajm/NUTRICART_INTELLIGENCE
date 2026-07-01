import sqlite3
from datetime import datetime


class MemoryAgent:

    def __init__(self, db_path="database/memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):

        cursor = self.conn.cursor()

        # --------------------------
        # Customer Profile
        # --------------------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_profile(

            customer_id TEXT PRIMARY KEY,

            diabetic INTEGER DEFAULT 0,

            hypertension INTEGER DEFAULT 0,

            allergies TEXT,

            favourite_categories TEXT,

            favourite_brands TEXT,

            nutrition_goal TEXT

        )
        """)

        # --------------------------
        # Search History
        # --------------------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id TEXT,

            query TEXT,

            category TEXT,

            search_time TEXT

        )
        """)

        # --------------------------
        # Purchase History
        # --------------------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id TEXT,

            product_name TEXT,

            category TEXT,

            protein REAL,

            sugar REAL,

            calories REAL,

            purchase_time TEXT

        )
        """)

        # --------------------------
        # Feedback
        # --------------------------

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id TEXT,

            product_name TEXT,

            feedback TEXT,

            feedback_time TEXT

        )
        """)

        self.conn.commit()

    # ---------------------------------------------------
    # Customer Profile
    # ---------------------------------------------------

    def create_customer(self, customer_id):

        cursor = self.conn.cursor()

        cursor.execute("""

        INSERT OR IGNORE INTO customer_profile(customer_id)

        VALUES(?)

        """,(customer_id,))

        self.conn.commit()

    # ---------------------------------------------------

    def update_medical_condition(self,
                                 customer_id,
                                 diabetic=False,
                                 hypertension=False):

        cursor=self.conn.cursor()

        cursor.execute("""

        UPDATE customer_profile

        SET diabetic=?,
            hypertension=?

        WHERE customer_id=?

        """,(int(diabetic),
             int(hypertension),
             customer_id))

        self.conn.commit()

    # ---------------------------------------------------

    def update_allergies(self,
                         customer_id,
                         allergies):

        cursor=self.conn.cursor()

        cursor.execute("""

        UPDATE customer_profile

        SET allergies=?

        WHERE customer_id=?

        """,(allergies,
             customer_id))

        self.conn.commit()

    # ---------------------------------------------------

    def update_goal(self,
                    customer_id,
                    goal):

        cursor=self.conn.cursor()

        cursor.execute("""

        UPDATE customer_profile

        SET nutrition_goal=?

        WHERE customer_id=?

        """,(goal,
             customer_id))

        self.conn.commit()

    # ---------------------------------------------------
    # Search Memory
    # ---------------------------------------------------

    def save_search(self,
                    customer_id,
                    query,
                    category):

        cursor=self.conn.cursor()

        cursor.execute("""

        INSERT INTO search_history(

            customer_id,

            query,

            category,

            search_time

        )

        VALUES(?,?,?,?)

        """,

        (

            customer_id,

            query,

            category,

            datetime.now().isoformat()

        ))

        self.conn.commit()

    # ---------------------------------------------------
    # Purchase Memory
    # ---------------------------------------------------

    def save_purchase(self,
                      customer_id,
                      product_name,
                      category,
                      protein,
                      sugar,
                      calories):

        cursor=self.conn.cursor()

        cursor.execute("""

        INSERT INTO purchase_history(

            customer_id,

            product_name,

            category,

            protein,

            sugar,

            calories,

            purchase_time

        )

        VALUES(?,?,?,?,?,?,?)

        """,

        (

            customer_id,

            product_name,

            category,

            protein,

            sugar,

            calories,

            datetime.now().isoformat()

        ))

        self.conn.commit()

    # ---------------------------------------------------
    # Feedback Memory
    # ---------------------------------------------------

    def save_feedback(self,
                      customer_id,
                      product_name,
                      feedback):

        cursor=self.conn.cursor()

        cursor.execute("""

        INSERT INTO feedback(

            customer_id,

            product_name,

            feedback,

            feedback_time

        )

        VALUES(?,?,?,?)

        """,

        (

            customer_id,

            product_name,

            feedback,

            datetime.now().isoformat()

        ))

        self.conn.commit()

    # ---------------------------------------------------
    # Retrieve Customer Profile
    # ---------------------------------------------------

    def get_profile(self,
                    customer_id):

        cursor=self.conn.cursor()

        cursor.execute("""

        SELECT *

        FROM customer_profile

        WHERE customer_id=?

        """,(customer_id,))

        return cursor.fetchone()

    # ---------------------------------------------------
    # Retrieve Search History
    # ---------------------------------------------------

    def get_search_history(self,
                           customer_id):

        cursor=self.conn.cursor()

        cursor.execute("""

        SELECT *

        FROM search_history

        WHERE customer_id=?

        ORDER BY search_time DESC

        """,(customer_id,))

        return cursor.fetchall()

    # ---------------------------------------------------
    # Retrieve Purchase History
    # ---------------------------------------------------

    def get_purchase_history(self,
                             customer_id):

        cursor=self.conn.cursor()

        cursor.execute("""

        SELECT *

        FROM purchase_history

        WHERE customer_id=?

        ORDER BY purchase_time DESC

        """,(customer_id,))

        return cursor.fetchall()

    # ---------------------------------------------------

    def close(self):

        self.conn.close()