from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model for the project.

    Declared before the first migration so that AUTH_USER_MODEL can be
    extended later without recreating the database.
    """

    pass
