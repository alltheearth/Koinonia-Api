from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Usuário customizado, para permitir extensões futuras sem migração disruptiva."""
