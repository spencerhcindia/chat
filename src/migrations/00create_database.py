import sqlite3

DB_FILENAME = "chat.db"


def get_db_connection():
    return sqlite3.connect(DB_FILENAME)


def create_users_table():

    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE 
            users(
            id integer PRIMARY KEY UNIQUE
            , username text UNIQUE
            , password text
            , banned bool
            , mod bool
            )
        
        """
    )


def create_messages_table():
    conn = get_db_connection()

    conn.execute(
        """
        CREATE TABLE
          messages(
            id integer PRIMARY KEY UNIQUE
            , userid int
            , createdtime timestamp
            , message
            )
        """
    )


create_messages_table()

create_users_table()
