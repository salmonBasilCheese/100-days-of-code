import json
import os
import random
import tkinter as tk
from tkinter import messagebox

# クリップボード連携の安全なインポート (未インストール環境へのフォールバック)
try:
    import pyperclip
except ImportError:
    pyperclip = None

DATA_FILE = "data.json"
IMAGE_FILE = "logo.png"
DEFAULT_EMAIL = "user@example.com"


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate_password():
    """
    英文字、数字、記号をランダムに組み合わせてセキュアなパスワードを生成。
    生成後はパスワード入力欄に挿入し、クリップボードへ自動コピーする。
    """
    letters = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    symbols = ["!", "#", "$", "%", "&", "(", ")", "*", "+"]

    password_letters = [random.choice(letters) for _ in range(random.randint(8, 10))]
    password_symbols = [random.choice(symbols) for _ in range(random.randint(2, 4))]
    password_numbers = [random.choice(numbers) for _ in range(random.randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers
    random.shuffle(password_list)

    password = "".join(password_list)

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)

    if pyperclip:
        try:
            pyperclip.copy(password)
        except Exception:
            pass


# ---------------------------- SEARCH WEBSITE ------------------------------- #
def search_website():
    """
    Website名をキーとして data.json を検索し、登録済みの Email と Password を表示。
    """
    website = website_entry.get().strip()
    if not website:
        messagebox.showwarning(
            title="Oops", message="Please enter a Website name to search."
        )
        return

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    except json.JSONDecodeError:
        messagebox.showinfo(title="Error", message="Data file is empty or corrupted.")
    else:
        if website in data:
            email = data[website]["email"]
            password = data[website]["password"]
            messagebox.showinfo(
                title=website, message=f"Email: {email}\nPassword: {password}"
            )
        else:
            messagebox.showinfo(
                title="Error", message=f"No details for '{website}' exists."
            )


# ---------------------------- SAVE PASSWORD ------------------------------- #
def save_password():
    """
    入力値の検証後、辞書構造に変換して data.json へ永続化。
    """
    website = website_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    # 1. 空文字バリデーション
    if len(website) == 0 or len(password) == 0:
        messagebox.showwarning(
            title="Oops", message="Please make sure you haven't left any fields empty!"
        )
        return

    new_data = {
        website: {
            "email": email,
            "password": password,
        }
    }

    # 2. JSONファイル読み込みと追記更新 (例外安全)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data.update(new_data)

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # 3. 入力欄の初期化とフォーカス復帰
    website_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    website_entry.focus()


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

# 1. Canvas (Logo)
canvas = tk.Canvas(width=200, height=200, highlightthickness=0)
if os.path.exists(IMAGE_FILE):
    logo_img = tk.PhotoImage(file=IMAGE_FILE)
    canvas.create_image(100, 100, image=logo_img)
else:
    # 画像ファイル不在時のフォールバック描画
    canvas.create_rectangle(20, 20, 180, 180, fill="gray", outline="")
    canvas.create_text(
        100, 100, text="Logo Missing", fill="white", font=("Arial", 12, "bold")
    )
canvas.grid(column=1, row=0)

# 2. Labels
website_label = tk.Label(text="Website:")
website_label.grid(column=0, row=1)

email_label = tk.Label(text="Email/Username:")
email_label.grid(column=0, row=2)

password_label = tk.Label(text="Password:")
password_label.grid(column=0, row=3)

# 3. Entries
website_entry = tk.Entry(width=21)
website_entry.grid(column=1, row=1)
website_entry.focus()

email_entry = tk.Entry(width=38)
email_entry.grid(column=1, row=2, columnspan=2)
email_entry.insert(0, DEFAULT_EMAIL)

password_entry = tk.Entry(width=21)
password_entry.grid(column=1, row=3)

# 4. Buttons
search_button = tk.Button(text="Search", width=13, command=search_website)
search_button.grid(column=2, row=1)

generate_password_button = tk.Button(
    text="Generate Password", width=13, command=generate_password
)
generate_password_button.grid(column=2, row=3)

add_button = tk.Button(text="Add", width=36, command=save_password)
add_button.grid(column=1, row=4, columnspan=2)

if __name__ == "__main__":
    window.mainloop()
