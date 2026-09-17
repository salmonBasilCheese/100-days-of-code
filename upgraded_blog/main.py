import json
import os
import smtplib
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, abort

# .env ファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# 環境変数から安全に取得
OWN_EMAIL = os.environ.get("OWN_EMAIL")
OWN_PASSWORD = os.environ.get("OWN_PASSWORD")

DATA_FILE_PATH = Path(__file__).resolve().parent / "blog-data.txt"


def get_posts_data():
    """ローカルファイルからブログ記事データを読み込む。失敗時は空リストを返却。"""
    try:
        with open(DATA_FILE_PATH, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def send_email(name, email, phone, message):
    """お問い合わせ内容を管理者のGmailへ送信する。"""
    email_message = f"Subject:New Message from Blog\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{message}"
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=OWN_EMAIL, password=OWN_PASSWORD)
        connection.sendmail(
            from_addr=OWN_EMAIL, to_addrs=OWN_EMAIL, msg=email_message.encode("utf-8")
        )


@app.route("/")
def get_all_posts():
    posts = get_posts_data()
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")

        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Phone: {phone}")
        print(f"Message: {message}")

        try:
            send_email(name=name, email=email, phone=phone, message=message)
        except Exception as e:
            print(f"メール送信エラー: {e}")

        return render_template("contact.html", msg_sent=True)

    return render_template("contact.html", msg_sent=False)


@app.route("/post/<int:index>")
def show_post(index):
    posts = get_posts_data()
    requested_post = next((post for post in posts if post.get("id") == index), None)
    if requested_post is None:
        abort(404)
    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(debug=True)
