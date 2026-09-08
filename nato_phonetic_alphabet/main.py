import os
import sys
import pandas

CSV_FILE = "nato_phonetic_alphabet.csv"


def load_nato_dict(file_path: str) -> dict[str, str]:
    """
    CSVファイルを読み込み、辞書内包表記を用いて
    {letter: code} 形式の辞書を生成する。
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"データファイル '{file_path}' が見つかりません。")

    df = pandas.read_csv(file_path)
    # TODO 1. Create a dictionary in this format: {"A": "Alfa", "B": "Bravo"}
    return {row.letter: row.code for (_, row) in df.iterrows()}


def convert_word_to_phonetic(word: str, nato_dict: dict[str, str]) -> list[str]:
    """
    入力文字列を大文字化し、スペースを除外しながら
    NATOフォネティックコードのリストを生成する。
    辞書に存在しない文字が含まれる場合は KeyError を送出。
    """
    # TODO 2. Create a list of the phonetic code words from a word that the user inputs.
    return [nato_dict[letter] for letter in word.upper() if letter != " "]


def main() -> None:
    try:
        nato_dict = load_nato_dict(CSV_FILE)
    except FileNotFoundError as e:
        print(f"[Error] {e}")
        return

    print("=== NATO Phonetic Alphabet Converter ===")
    print("変換したい単語を入力してください (終了するには 'exit' または 'quit')\n")

    try:
        while True:
            user_input = input("Enter a word: ").strip()

            # 1. 終了コマンドの判定
            if user_input.upper() in ["EXIT", "QUIT"]:
                print("プログラムを終了します。")
                break

            # 2. 空入力のガード
            if not user_input:
                continue

            # 3. 変換と例外処理 (Day 30: try-except による KeyError 捕捉)
            try:
                phonetic_code_list: list[str] = convert_word_to_phonetic(
                    user_input, nato_dict
                )
            except KeyError:
                print("Sorry, only letters in the alphabet please.\n")
            else:
                print(f"{phonetic_code_list}\n")

    except KeyboardInterrupt:
        # Ctrl+C による安全終了
        print("\n\nプログラムが中断されました。終了します。")
        sys.exit(0)


if __name__ == "__main__":
    main()
