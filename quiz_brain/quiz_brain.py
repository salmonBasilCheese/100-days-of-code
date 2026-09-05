import html


class QuizBrain:
    def __init__(self, q_list: list):
        self.question_number = 0
        self.score = 0
        self.question_list = q_list

    def still_has_questions(self) -> bool:
        """残りの問題が存在するか判定し、IndexErrorを未然に防ぐ。"""
        return self.question_number < len(self.question_list)

    def _get_valid_user_answer(self, prompt_text: str) -> str:
        """有効な回答（True/False または t/f）が入力されるまで再帰的に要求する。"""
        valid_true = {"true", "t"}
        valid_false = {"false", "f"}

        while True:
            raw_input = input(prompt_text).strip().lower()
            if raw_input in valid_true:
                return "True"
            if raw_input in valid_false:
                return "False"
            print("Invalid input. Please enter 'True' ('t') or 'False' ('f').")

    def next_question(self) -> None:
        """次の問題文をデコードして出題し、回答を取得・判定する。"""
        current_question = self.question_list[self.question_number]
        self.question_number += 1

        # HTMLエンティティ（&quot; や &#039; など）をデコード
        formatted_question = html.unescape(current_question.text)

        prompt = f"Q.{self.question_number}: {formatted_question} (True/False)?: "
        user_answer = self._get_valid_user_answer(prompt)
        self.check_answer(user_answer, current_question.answer)

    def check_answer(self, user_answer: str, correct_answer: str) -> None:
        """回答の成否を判定し、スコアの更新および結果表示を行う。"""
        if user_answer.lower() == correct_answer.lower():
            self.score += 1
            print("You got it right!")
        else:
            print("That's wrong.")
        print(f"The correct answer was: {correct_answer}.")
        print(f"Your current score is: {self.score}/{self.question_number}\n")
