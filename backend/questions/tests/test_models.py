from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from questions.models import AnswerOption, Category, ChoiceQuestion, NumericQuestion


def create_options(question, correct_count=1, total=4):
    """Attach ``total`` answer options to ``question``, ``correct_count`` correct."""
    for index in range(total):
        AnswerOption.objects.create(
            question=question,
            text=f"Отговор {index + 1}",
            is_correct=index < correct_count,
        )


class CategoryModelTests(TestCase):
    def test_create_category_with_valid_name(self):
        category = Category.objects.create(name="География")

        category.full_clean()

        self.assertEqual(category.name, "География")
        self.assertEqual(str(category), "География")
        self.assertEqual(Category.objects.count(), 1)

    def test_category_name_must_be_unique(self):
        Category.objects.create(name="История")

        with self.assertRaises(IntegrityError):
            Category.objects.create(name="История")

    def test_duplicate_category_name_fails_validation(self):
        Category.objects.create(name="Наука")
        duplicate = Category(name="Наука")

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_category_name_cannot_be_blank(self):
        category = Category(name="")

        with self.assertRaises(ValidationError):
            category.full_clean()


class ChoiceQuestionModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Технологии")

    def test_create_valid_choice_question(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Кой създава програмния език Python?",
        )
        create_options(question)

        question.full_clean()

        self.assertEqual(question.category, self.category)
        self.assertEqual(question.text, "Кой създава програмния език Python?")
        self.assertEqual(question.answer_options.count(), 4)
        self.assertEqual(question.answer_options.filter(is_correct=True).count(), 1)

    def test_correct_option_property_returns_the_correct_answer(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Какво означава HTTP статус код 404?",
        )
        create_options(question)

        self.assertTrue(question.correct_option.is_correct)
        self.assertEqual(question.correct_option.text, "Отговор 1")

    def test_choice_question_is_reachable_from_its_category(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Кой е химичният символ на златото?",
        )

        self.assertIn(question, self.category.choicequestions.all())

    def test_too_few_answer_options_is_invalid(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Въпрос с три отговора",
        )
        create_options(question, total=3)

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("answer_options", context.exception.message_dict)

    def test_too_many_answer_options_is_invalid(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Въпрос с пет отговора",
        )
        create_options(question, total=5)

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("answer_options", context.exception.message_dict)

    def test_no_correct_answer_option_is_invalid(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Въпрос без верен отговор",
        )
        create_options(question, correct_count=0)

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("answer_options", context.exception.message_dict)

    def test_more_than_one_correct_answer_option_is_invalid(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Въпрос с два верни отговора",
        )
        create_options(question, correct_count=2)

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("answer_options", context.exception.message_dict)

    def test_choice_question_text_cannot_be_blank(self):
        question = ChoiceQuestion(category=self.category, text="")

        with self.assertRaises(ValidationError):
            question.full_clean()

    def test_deleting_choice_question_cascades_to_answer_options(self):
        question = ChoiceQuestion.objects.create(
            category=self.category,
            text="Въпрос за изтриване",
        )
        create_options(question)
        self.assertEqual(AnswerOption.objects.count(), 4)

        question.delete()

        self.assertEqual(ChoiceQuestion.objects.count(), 0)
        self.assertEqual(AnswerOption.objects.count(), 0)


class NumericQuestionModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Наука")

    def test_create_valid_numeric_question(self):
        question = NumericQuestion.objects.create(
            category=self.category,
            text="Колко хромозоми има една човешка телесна клетка?",
            correct_answer=46,
        )

        question.full_clean()

        self.assertEqual(question.category, self.category)
        self.assertEqual(question.correct_answer, 46)

    def test_numeric_question_accepts_negative_answer(self):
        question = NumericQuestion.objects.create(
            category=self.category,
            text="Каква е температурата на абсолютната нула в градуси Целзий?",
            correct_answer=-273,
        )

        question.full_clean()

        self.assertEqual(question.correct_answer, -273)

    def test_correct_answer_is_required(self):
        question = NumericQuestion(
            category=self.category,
            text="Въпрос без верен отговор",
        )

        with self.assertRaises(ValidationError) as context:
            question.full_clean()

        self.assertIn("correct_answer", context.exception.message_dict)

    def test_correct_answer_cannot_be_null_in_the_database(self):
        with self.assertRaises(IntegrityError):
            NumericQuestion.objects.create(
                category=self.category,
                text="Въпрос без верен отговор",
                correct_answer=None,
            )

    def test_numeric_question_is_reachable_from_its_category(self):
        question = NumericQuestion.objects.create(
            category=self.category,
            text="Колко кръга има олимпийският символ?",
            correct_answer=5,
        )

        self.assertIn(question, self.category.numericquestions.all())


class AnswerOptionModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Спорт")
        self.question = ChoiceQuestion.objects.create(
            category=self.category,
            text="В кой спорт думата „любов“ означава резултат нула?",
        )

    def test_answer_option_defaults_to_incorrect(self):
        option = AnswerOption.objects.create(question=self.question, text="Тенис")

        self.assertFalse(option.is_correct)
        self.assertEqual(str(option), "Тенис")

    def test_answer_option_belongs_to_its_question(self):
        option = AnswerOption.objects.create(question=self.question, text="Голф")

        self.assertEqual(option.question, self.question)
        self.assertIn(option, self.question.answer_options.all())

    def test_answer_option_text_cannot_be_blank(self):
        option = AnswerOption(question=self.question, text="")

        with self.assertRaises(ValidationError):
            option.full_clean()


class CategoryProtectionTests(TestCase):
    def test_category_with_choice_questions_cannot_be_deleted(self):
        category = Category.objects.create(name="Изкуство и литература")
        ChoiceQuestion.objects.create(
            category=category,
            text="Кой рисува „Мона Лиза“?",
        )

        with self.assertRaises(ProtectedError):
            category.delete()

        self.assertEqual(Category.objects.count(), 1)

    def test_category_with_numeric_questions_cannot_be_deleted(self):
        category = Category.objects.create(name="История")
        NumericQuestion.objects.create(
            category=category,
            text="През коя година пада Берлинската стена?",
            correct_answer=1989,
        )

        with self.assertRaises(ProtectedError):
            category.delete()

        self.assertEqual(Category.objects.count(), 1)

    def test_empty_category_can_be_deleted(self):
        category = Category.objects.create(name="Празна категория")

        category.delete()

        self.assertEqual(Category.objects.count(), 0)

    def test_category_can_be_deleted_after_its_questions_are_removed(self):
        category = Category.objects.create(name="Технологии")
        question = ChoiceQuestion.objects.create(
            category=category,
            text="Какво означава HTTP статус код 404?",
        )

        with transaction.atomic():
            question.delete()
        category.delete()

        self.assertEqual(Category.objects.count(), 0)


class AbstractBaseQuestionTests(TestCase):
    def test_base_question_has_no_database_table(self):
        """``BaseQuestion`` is abstract, so only the concrete models have tables."""
        from questions.models import BaseQuestion

        self.assertTrue(BaseQuestion._meta.abstract)

    def test_choice_and_numeric_questions_use_separate_tables(self):
        self.assertNotEqual(
            ChoiceQuestion._meta.db_table,
            NumericQuestion._meta.db_table,
        )

    def test_correct_answer_exists_only_on_numeric_question(self):
        choice_fields = [field.name for field in ChoiceQuestion._meta.get_fields()]
        numeric_fields = [field.name for field in NumericQuestion._meta.get_fields()]

        self.assertNotIn("correct_answer", choice_fields)
        self.assertIn("correct_answer", numeric_fields)
