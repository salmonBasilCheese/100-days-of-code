import html
from question_model import Question


class QuizBrain:
    def __init__(self, q_list: list[Question]):
        self.question_number: int = 0
        self.score: int = 0
        self.question_list: list[Question] = q_list
        self.current_question: Question | None = None

    def still_has_questions(self) -> bool:
        """残問が存在するか判定し、IndexErrorを防止する。"""
        return self.question_number < len(self.question_list)

    def next_question(self) -> str:
        """
        次問の Question オブジェクトをセットし、
        HTMLデコード済みの出題テキストを生成して返す。
        """
        self.current_question = self.question_list[self.question_number]
        self.question_number += 1
        q_text = html.unescape(self.current_question.text)
        return f"Q.{self.question_number}: {q_text}"

    def check_answer(self, user_answer: str) -> bool:
        """回答の正誤を判定し、正解ならスコアを加算して真偽値を返す。"""
        if self.current_question is None:
            return False

        correct_answer = self.current_question.answer
        if user_answer.lower() == correct_answer.lower():
            self.score += 1
            return True
        return False
