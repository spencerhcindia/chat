import sqlite3
import time

import bcrypt
from constants import DB_FILENAME


def get_db_connection():
    return sqlite3.connect(DB_FILENAME)


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()

    hash_ = bcrypt.hashpw(password=password.encode(), salt=salt)

    return hash_.decode("utf-8")


def create_user(
    username: str, password: str, color: str, banned: bool = False, mod: bool = False
) -> bool:
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO users(username, password, color, banned, mod)
            VALUES(?, ?, ?, ?, ?)
            """,
            (username, password, color, banned, mod),
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
        """
        INSERT INTO messages(userid, createdtime, message)
        VALUES(?, datetime('now'), ?)
        """,
        (id, message),
    )
    conn.commit()
