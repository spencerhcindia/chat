from flask import Flask, request
import json
import utilities


app = Flask(__name__)


@app.route("/health_check", methods=["GET"])
def health_check():
    return "200 Ok", 200


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="6666")
