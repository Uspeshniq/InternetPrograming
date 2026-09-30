import json
from pathlib import Path

from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


FIXTURE_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "questions"
    / "question_bank.json"
)

EXPECTED_CATEGORIES = 6
EXPECTED_CHOICE_QUESTIONS = 12
EXPECTED_ANSWER_OPTIONS = 48
EXPECTED_NUMERIC_QUESTIONS = 12


class QuestionBankFixtureFileTests(TestCase):
    """Checks that run against the JSON file itself, before it is loaded."""

    def test_fixture_file_exists(self):
        self.assertTrue(FIXTURE_PATH.is_file(), f"Missing fixture: {FIXTURE_PATH}")

    def test_fixture_file_is_valid_json(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            records = json.load(fixture_file)

        self.assertIsInstance(records, list)
        self.assertTrue(records)

    def test_fixture_file_declares_the_expected_record_counts(self):
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            records = json.load(fixture_file)

        counts = {}
        for record in records:
            counts[record["model"]] = counts.get(record["model"], 0) + 1

        self.assertEqual(counts["questions.category"], EXPECTED_CATEGORIES)
        self.assertEqual(counts["questions.choicequestion"], EXPECTED_CHOICE_QUESTIONS)
        self.assertEqual(counts["questions.answeroption"], EXPECTED_ANSWER_OPTIONS)
        self.assertEqual(
            counts["questions.numericquestion"], EXPECTED_NUMERIC_QUESTIONS
        )


class QuestionBankFixtureLoadTests(TestCase):
    """Checks that run against the database after ``loaddata``."""

    fixtures = ["questions/question_bank.json"]

    def test_fixture_loads_expected_number_of_categories(self):
        self.assertEqual(Category.objects.count(), EXPECTED_CATEGORIES)

    def test_fixture_loads_expected_number_of_choice_questions(self):
        self.assertEqual(ChoiceQuestion.objects.count(), EXPECTED_CHOICE_QUESTIONS)

    def test_fixture_loads_expected_number_of_answer_options(self):
        self.assertEqual(AnswerOption.objects.count(), EXPECTED_ANSWER_OPTIONS)

    def test_fixture_loads_expected_number_of_numeric_questions(self):
        self.assertEqual(NumericQuestion.objects.count(), EXPECTED_NUMERIC_QUESTIONS)

    def test_every_choice_question_has_exactly_four_answer_options(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertEqual(question.answer_options.count(), 4)

    def test_every_choice_question_has_exactly_one_correct_answer(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertEqual(
                    question.answer_options.filter(is_correct=True).count(), 1
                )

    def test_every_choice_question_passes_model_validation(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                question.full_clean()

    def test_every_numeric_question_has_an_integer_correct_answer(self):
        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertIsInstance(question.correct_answer, int)

    def test_every_numeric_question_passes_model_validation(self):
        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.text):
                question.full_clean()

    def test_every_question_belongs_to_a_category(self):
        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertIsNotNone(question.category)

        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertIsNotNone(question.category)

    def test_every_answer_option_belongs_to_a_choice_question(self):
        for option in AnswerOption.objects.all():
            with self.subTest(option=option.text):
                self.assertIsNotNone(option.question)

    def test_category_names_are_unique(self):
        names = list(Category.objects.values_list("name", flat=True))

        self.assertEqual(len(names), len(set(names)))

    def test_every_category_has_at_least_one_question(self):
        for category in Category.objects.all():
            with self.subTest(category=category.name):
                total = (
                    category.choicequestions.count() + category.numericquestions.count()
                )
                self.assertGreater(total, 0)

    def test_questions_are_written_in_bulgarian(self):
        cyrillic = set("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЬЮЯабвгдежзийклмнопрстуфхцчшщъьюя")

        for question in ChoiceQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertTrue(cyrillic & set(question.text))

        for question in NumericQuestion.objects.all():
            with self.subTest(question=question.text):
                self.assertTrue(cyrillic & set(question.text))
