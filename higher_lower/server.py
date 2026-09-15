import random
from flask import Flask

app = Flask(__name__)

# サーバー起動時に 0〜9 の正解の数値を1つ生成
CORRECT_NUMBER = random.randint(0, 9)
print(f"[DEBUG] Correct Number: {CORRECT_NUMBER}")


@app.route("/")
def home():
    return (
        "<h1>Guess a number between 0 and 9</h1>"
        '<img src="https://media.giphy.com/media/3o7aCSPqXE5C6T8tBC/giphy.gif" width="350" alt="Thinking GIF">'
    )


@app.route("/<int:guess>")
def check_guess(guess):
    if guess > CORRECT_NUMBER:
        return (
            '<h1 style="color: purple;">Too high, try again!</h1>'
            '<img src="https://media.giphy.com/media/3o6ZtaO9BZHcOjmErm/giphy.gif" width="350" alt="Too High">'
        )
    elif guess < CORRECT_NUMBER:
        return (
            '<h1 style="color: red;">Too low, try again!</h1>'
            '<img src="https://media.giphy.com/media/jD4DwBtqPXRXa/giphy.gif" width="350" alt="Too Low">'
        )
    else:
        return (
            '<h1 style="color: green;">You found me!</h1>'
            '<img src="https://media.giphy.com/media/4T7e4DmcrP9du/giphy.gif" width="350" alt="Correct">'
        )


if __name__ == "__main__":
    app.run(debug=True)
