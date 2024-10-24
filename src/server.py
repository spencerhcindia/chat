import json
import pathlib

import jwt
from flask import Flask, request, abort


import utilities
import datetime
from uuid import uuid4

app = Flask(__name__)


def load_secret():
    # Open a file called .secret adjecent to server.py
    working_directory = pathlib.Path(__file__).parent.resolve()

    # Load the data from the file and return it
    file = working_directory / ".secret"

    # If file doesn't exist, throw a FileNotFound error
    if file.exists():
        return file.read_text()

    raise FileNotFoundError


def encryption(payload: dict):

    return jwt.encode(payload=payload, key=load_secret(), algorithm="HS256")


def decryption(message: str):
    res = jwt.decode(message, key=load_secret(), algorithms=["HS256"])
    return res


def create_token(userid: str) -> str:
    # Create the dict with necessary keys for token
    token_dict = {
        "uuid": str(uuid4()),
        "session_start": datetime.datetime.now().timestamp(),
        "userid": userid,
    }
    print(token_dict)
    # Encrypt json str and return
    encrypted_token = encryption(token_dict)

    return encrypted_token


def validate_token(toeken: str):
    # Tries to decrypt token
    try:
        decrypted_token = decryption(toeken)
        if (
            datetime.datetime.now().timestamp() - decrypted_token["session_start"]
            > 7200
        ):
            abort(401, "Token expired. And you will be too.")
        if utilities.get_user(decrypted_token["userid"]):
            return decrypted_token["userid"]
        abort(
            404,
            "I'm thinking probably this user doesn't exist, or perhaps we deleted your parents.",
        )
    except jwt.exceptions.DecodeError:
        abort(400, "Unable to decrypt token.")


@app.route("/health_check", methods=["GET"])
def health_check():
    return "200 OK", 200


@app.route("/register", methods=["POST"])
def register():
    """
    We need to parse a payload of user
    We need to check if user already exists
    And if they do, deny the request
    We need to hash the password
    Insert the user
    and read our write
    """

    user = request.json

    if utilities.get_userid(username=user["username"]):
        return "Sorry, this username is taken."
    else:

        utilities.create_user(
            username=user["username"],
            password=utilities.hash_password(user["password"]),
            color=user["color"],
            banned=False,
            mod=user["mod"],
        )
        return utilities.get_user(userid=user["userid"])


@app.route("/login", methods=["POST"])
def login():
    user_input = request.json

    if user := utilities.login(user=user_input):
        return create_token(userid=user["userid"]), 200

    return {"response": "Login failed."}, 403


@app.route("/get_messages", methods=["GET"])
def get_messages():
    token = request.authorization.token

    validate_token(token)

    messages = utilities.get_messages()

    return messages


@app.route("/create_message", methods=["PUT"])
def create_message():
    message = request.json["message"]
    token = request.authorization.token

    userid = validate_token(toeken=token)

    utilities.create_message(userid=userid, message=message)

    return "Good job re tard", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6666")
