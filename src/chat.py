"""
Textual is a library for making "TUI" ( Terminal User Interface ) applications. It uses
a "Widget" model, where a central "App" object uses its "compose" method to place widgets
in the terminal.
In this textual app, we make a simple "chat interface". It has two widgets:
- The message box, where messages are displayed
- The input box, where you can type
We should use textual for the chat app we're building. Before we do so, we should understand
some of the concepts that make it work. To get started, create a virtual environment and
python3 -m pip install textual
You can then run this sample app with python. Make sure your terminal is somewhat large before
you begin, so that you can see what's going on. Use the app and get a feel for what it does.
Then, follow up by answering the questions.
Questions are outlined in comments throughout. Answer them all. Any time you see a QUESTION,
you can follow on the next line with an ANSWER in a new comment. You can find the documentation
for textual here:
    https://textual.textualize.io/guide/
"""

import argparse
import hashlib
import json
import random
import string
from functools import lru_cache
from typing import List, Union

import jwt
import requests
from rich.color import Color
from rich.console import RenderableType
from rich.style import Style
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.widgets import Button, Input, RichLog

import utilities

USER = ""
SERVER_URL = ""
LINE_BREAK = "\n" + "#" * 40
HELP = (
    LINE_BREAK
    + "\nHere are the available command options:\n/login <username> <password>\n/register <username> <password>\n/help"
    + LINE_BREAK
    + "\n"
)
SECRET = ""


def health_check(url):
    return requests.get(url=url + "/health_check").status_code


def register(user: dict) -> str:
    result = requests.post(f"{SERVER_URL}/register", json=user)

    return result.text


def login(username: str, password: str) -> Union[dict, None]:

    global USER

    user = {"username": username, "password": password}

    result = requests.post(f"{SERVER_URL}/login", json=user)

    if result.status_code == 200:

        USER = result.text

        return USER

    return None


def logout():

    global USER

    USER = ""


@lru_cache  # QUESTION: What does lru_cache do, and why would I use it here?
def name2hex(name: str) -> str:
    """
    Render a name as a hex color string by hashing it and taking the last
    six characters.
    """
    # QUESTION: What is a sha256 hash?
    # QUESTION: Why would I use [:6] here?
    name_hash = hashlib.sha256(name.encode()).hexdigest()[:6]
    return f"#{name_hash}"


# QUESTION: What is an App in textual?
class Chat(App):
    """
    A chat. Consists of a message box and an input box.
    """

    # QUESTION: What does *args do? **kwargs?
    # QUESTION: Why would __init__ need *args and **kwargs?
    def __init__(self, *args, **kwargs) -> None:
        """
        In this init, we add a few things to instances of Chat:
        - An input box widget
        - A message log widget
        - A list to host our messages
        """
        self.current_user = {"username": ""}
        super().__init__(*args, **kwargs)
        # Sauce it up! We want the input box:
        self.input_box = Input(placeholder="...")
        # A list for messages:
        # QUESTION: What is a 'RenderableType' in textual?
        self.messages: list[RenderableType] = []
        # QUESTION: What does wrap=True do when RichLog is called this way?
        self.message_log = RichLog(wrap=True)

    # QUESTION: When is an App's on_mount method called?
    def on_mount(self) -> None:
        """
        Things to do once the app is setup maybe
        """
        # QUESTION: What does set_interval do in this context?
        # self.set_interval(1, self.rerender_messages)

        # QUESTION: Why do I call my input box's focus method? What does it do?
        self.input_box.focus()

    def new_user(self, username: str) -> str:
        color = name2hex(username)

        if not utilities.get_user(username=username):
            utilities.create_user(username=username, color=color)
            return utilities.get_user(username=username)
        else:
            return False

    def get_messages(self):
        global USER
        try:
            if not USER:
                return []
            headers = {"Authorization": f"Bearer {USER}"}
            response = requests.get(f"{SERVER_URL}/get_messages", headers=headers)

            messages = response.json()
            return messages
        except:
            return []

    def create_message(self, message: dict):
        global USER
        if not USER:
            return
        headers = {"Authorization": f"Bearer {USER}"}
        result = requests.put(
            f"{SERVER_URL}/create_message", json=message, headers=headers
        )

        if result.status_code == 200:
            self.rerender_messages()

    def fake_messenger(self) -> None:
        """
        Send some fake messages into our message queue
        """
        # We should make some fake messages out of like...
        # random text.
        # How long should they be?
        length = random.randint(8, 256)
        # What should the message body contain?
        message_body = "".join(
            random.choices(
                # What characters can make up our message body?
                # QUESTION: What's the type of string.ascii_uppercase?
                # QUESTION: As a follow-on, what does multiplying it by 2 do?
                (string.ascii_uppercase * 2)
                + (string.ascii_lowercase * 2)
                + (" " * 10),
                k=length,
            )
        ).strip()
        # Make up a fake user.
        username = f"User {random.randint(1, 10)}"
        # This is what the message text should look like:
        message = f"[{username}] {message_body}"
        # Let's style it.
        # QUESTION: Where does Text come from?
        # QUESTION: What does the 'style' keyword argument do?
        # QUESTION: What does _my usage_ of the 'style' keyword argument do, here?
        styled_message = Text(
            message, style=Style(color=Color.parse(name2hex(username)))
        )
        # We can now append it to our messages list,
        self.messages.append(styled_message)
        # And re-render the log.
        # QUESTION: Why do I re-render here?
        self.rerender_messages()

    def rerender_messages(self) -> None:
        """
        Clear and rerender the messages in the log.
        """
        # Clear the message log,
        if messages := self.get_messages():
            self.message_log.clear()
            # And rewrite our current messages
            for message in messages:
                formatted_message = f"[{message['username']}] {message['message']}"
                styled_message = Text(
                    formatted_message, style=Style(color=Color.parse(message["color"]))
                )
                self.message_log.write(styled_message)

    # QUESTION: What is this pattern called, where I put @something on a function?
    # QUESTION: When is this method called?
    @on(Input.Submitted)
    def submit_text_from_input(self, event: Input.Submitted) -> None:
        """
        What happens when we press "enter" in our input box.
        """

        commands = ["login", "help", "register", "logout"]
        # Don't let us submit blank messages
        # QUESTION: From a usability standpoint, why no blank messages?

        if not (message_value := event.value):
            return
        if message_value.startswith("/"):
            command = message_value.lstrip("/").split(" ")
            self.input_box.clear()
            if command[0] in commands:
                if command[0] == "help":
                    self.messages.append(HELP)
                    return
                elif command[0] == "register":
                    if not len(command) == 3:
                        self.messages.append(HELP)
                        return
                    else:
                        user = {
                            "username": command[1],
                            "password": command[2],
                            "color": name2hex(command[1]),
                            "banned": False,
                            "mod": False,
                        }
                        self.messages.append("Welcome " + register(user=user) + "!")
                        return
                elif command[0] == "login":
                    login_res = login(username=command[1], password=command[2])
                    self.input_box.clear()
                    if login_res:
                        self.current_user = login_res
                        self.messages.append("\nLogin successful!\n")
                        self.rerender_messages()
                        return
                    else:
                        self.messages.append("Login failed, try again.\n")
                        return
                elif command[0] == "logout":
                    logout()
                    self.message_log.clear()
                    return

            else:
                self.messages.append(
                    LINE_BREAK
                    + "\n\nUnrecognized command: /"
                    + command
                    + "\n"
                    + LINE_BREAK
                )
                return

        # Otherwise...
        # Clear the input box.
        self.input_box.clear()

        self.create_message({"message": message_value})

    # QUESTION: When is an App's 'compose' method called?
    def compose(self) -> ComposeResult:
        """
        Build the app.
        """
        # QUESTION: In Python, what does the 'yield' keyword do?
        yield self.message_log
        yield self.input_box


def main() -> None:
    """
    Run our app :)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server-url",
        help="The server of which we will attempt to connect.",
        required=True,
    )
    args = parser.parse_args()
    url = args.server_url

    if health_check(url=url):
        global SERVER_URL
        SERVER_URL = url
        app = Chat()
        app.run()
    else:
        print("Unable to connect to server: " + url)
        exit()


if __name__ == "__main__":
    main()
