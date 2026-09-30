from django.core.exceptions import ValidationError
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BaseQuestion(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    text = models.TextField()

    class Meta:
        abstract = True

    def __str__(self):
        return self.text


class ChoiceQuestion(BaseQuestion):
    REQUIRED_OPTION_COUNT = 4
    REQUIRED_CORRECT_COUNT = 1

    class Meta:
        verbose_name = "Choice question"
        verbose_name_plural = "Choice questions"

    def clean(self):
        """Validate that the question has exactly four options, one correct.

        Answer options are related objects, so they only exist once the
        question itself has been saved. An unsaved question is therefore
        skipped here and validated after its options are created.
        """
        super().clean()

        if self.pk is None:
            return

        options = list(self.answer_options.all())

        if len(options) != self.REQUIRED_OPTION_COUNT:
            raise ValidationError(
                {
                    "answer_options": (
                        f"A choice question must have exactly "
                        f"{self.REQUIRED_OPTION_COUNT} answer options, "
                        f"got {len(options)}."
                    )
                }
            )

        correct_count = sum(1 for option in options if option.is_correct)

        if correct_count != self.REQUIRED_CORRECT_COUNT:
            raise ValidationError(
                {
                    "answer_options": (
                        f"A choice question must have exactly "
                        f"{self.REQUIRED_CORRECT_COUNT} correct answer, "
                        f"got {correct_count}."
                    )
                }
            )

    @property
    def correct_option(self):
        return self.answer_options.filter(is_correct=True).first()


class NumericQuestion(BaseQuestion):
    correct_answer = models.IntegerField()

    class Meta:
        verbose_name = "Numeric question"
        verbose_name_plural = "Numeric questions"


class AnswerOption(models.Model):
    question = models.ForeignKey(
        ChoiceQuestion,
        on_delete=models.CASCADE,
        related_name="answer_options",
    )
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Answer option"
        verbose_name_plural = "Answer options"

    def __str__(self):
        return self.text
