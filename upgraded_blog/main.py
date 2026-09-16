from pathlib import Path
import json
from flask import Flask, render_template, abort

app = Flask(__name__)

# プロジェクト直下の blog-data.txt を絶対パスで安全に参照
DATA_FILE_PATH = Path(__file__).resolve().parent / "blog-data.txt"


def get_posts_data():
    """ローカルファイルからブログ記事データを読み込む。失敗時は空リストを返却。"""
    try:
        with open(DATA_FILE_PATH, mode="r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


@app.route("/")
def get_all_posts():
    posts = get_posts_data()
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/post/<int:index>")
def show_post(index):
    posts = get_posts_data()
    # index (id) に合致する記事を抽出
    requested_post = next((post for post in posts if post.get("id") == index), None)

    # 存在しない記事IDへのアクセスは404エラーを返却
    if requested_post is None:
        abort(404)

    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(debug=True)
