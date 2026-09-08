import sys
from tkinter import messagebox
from question_model import Question
from data import question_data
from quiz_brain import QuizBrain
from ui import QuizInterface


def main() -> None:
    if not question_data:
        print(
            "[Error] No question data available. Check network connection.",
            file=sys.stderr,
        )
        return

    question_bank: list[Question] = []
    for question in question_data:
        q_text = question.get("question", "")
        q_answer = question.get("correct_answer", "")
        question_bank.append(Question(q_text, q_answer))

    quiz = QuizBrain(question_bank)
    QuizInterface(quiz)


if __name__ == "__main__":
    main()
