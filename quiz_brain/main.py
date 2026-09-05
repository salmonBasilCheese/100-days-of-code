from question_model import Question
from data import question_data
from quiz_brain import QuizBrain


def main():
    question_bank = []
    for question in question_data:
        # data.py のキーが 'text'/'answer' でも 'question'/'correct_answer' でも対応可能にする
        q_text = question.get("question")
        q_answer = question.get("correct_answer")

        new_question = Question(q_text, q_answer)
        question_bank.append(new_question)

    quiz = QuizBrain(question_bank)

    while quiz.still_has_questions():
        quiz.next_question()

    print("You've completed the quiz!")
    print(f"Your final score was: {quiz.score}/{len(question_bank)}")


if __name__ == "__main__":
    main()
