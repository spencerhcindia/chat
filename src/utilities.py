import sqlite3
import time
from typing import Union

import bcrypt
from constants import DB_FILENAME


def get_db_connection():
    return sqlite3.connect("/home/spencer/Desktop/programming/chat/chat.db")


def get_userid(username: str) -> int:
    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT
        username
        , password
        , banned
        , mod
        , id
        , color
        FROM users
        WHERE username = ?
        """,
        (username,),
    ).fetchone()
    if user:
        return user[4]
    else:
        return None


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()

    hash_ = bcrypt.hashpw(password=password.encode(), salt=salt)

    return hash_.decode("utf-8")


def login(user: dict) -> Union[dict, None]:

    user_pass = user["password"]
    userid = get_userid(username=user["username"])
    db_user = get_user(userid=userid)
    if db_user:
        user_pass = user["password"]
        db_pass = db_user["password"]

        if bcrypt.checkpw(user_pass.encode("utf-8"), db_pass.encode("utf-8")):
            return db_user

    return None


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


def get_user(userid: str) -> dict:
    conn = get_db_connection()

    user = conn.execute(
        """
        SELECT
        username
        , password
        , banned
        , mod
        , id
        , color
        FROM users
        WHERE id = ?
        """,
        (userid,),
    ).fetchone()
    if user:
        return {
            "userid": user[4],
            "username": user[0],
            "password": user[1],
            "banned": bool(user[2]),
            "mod": bool(user[3]),
            "color": user[5],
        }
    else:
        return None


def create_message(userid: str, message: str):

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO messages(userid, createdtime, message)
        VALUES(?, datetime('now'), ?)
        """,
        (userid, message),
    )
    conn.commit()


def get_messages():
    conn = get_db_connection()

    messages = conn.execute(
        """
            SELECT 
            users.username
            , users.color
            , messages.userid
            , messages.createdtime
            , messages.message
            FROM messages
            JOIN users ON messages.userid = users.id
            ORDER BY messages.createdtime ASC
            LIMIT 100
        """
    ).fetchall()

    conn.commit()

    messages_conversion = [
        {
            "username": message[0],
            "color": message[1],
            "userid": message[2],
            "createdtime": message[3],
            "message": message[4],
        }
        for message in messages
    ]

    return messages_conversion
