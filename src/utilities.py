import sqlite3
import time

import bcrypt
from constants import DB_FILENAME


def get_db_connection():
    return sqlite3.connect(DB_FILENAME)


def create_user(
    username: str, password: str, banned: bool = False, mod: bool = False
) -> bool:
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO users(username, password, banned, mod)
            VALUES(?, ?, ?, ?)
            """,
            (username, password, banned, mod),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_user(username: str) -> dict:
    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT
        username
        , password
        , banned
        , mod
        , id
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()
    if user:
        return {
            "id": user[4],
            "username": user[0],
            "password": user[1],
            "banned": bool(user[2]),
            "mod": bool(user[3]),
        }
    else:
        return None


def create_message(username: str, message: str):
    id = get_user(username=username)["id"]
    conn = get_db_connection()

    conn.execute(
        f"""
        INSERT INTO messages(userid, createdtime, message)
        VALUES(?, datetime('now'), ?)
        """,
        (id, message),
    )
    conn.commit()
