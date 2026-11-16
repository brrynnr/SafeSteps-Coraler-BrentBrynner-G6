import re
from django.core.exceptions import ValidationError


class LetterAndDigitValidator:
    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one letter and one digit.")

    def get_help_text(self):
        return "Your password must contain at least one letter and one digit."