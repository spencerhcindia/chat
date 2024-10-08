from flask import Flask, request
import json
import utilities


app = Flask(__name__)


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

    if utilities.get_user(username=user["username"]):
        return "Sorry, this username is taken."
    else:

        utilities.create_user(
            username=user["username"],
            password=utilities.hash_password(user["password"]),
            color=user["color"],
            banned=False,
            mod=user["mod"],
        )
        return utilities.get_user(username=user["username"])


@app.route("/login", methods=["POST"])
def login():
    user_input = request.json

    if user := utilities.login(user=user_input):
        return user, 200

    return {"response": "Login failed."}, 403


@app.route("/get_messages", methods=["GET"])
def get_messages():
    messages = utilities.get_messages()
    return messages


@app.route("/create_message", methods=["PUT"])
def create_message():
    message = request.json

    utilities.create_message(message=message)

    return "Good job re tard", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6666")
