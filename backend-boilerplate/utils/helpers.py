import datetime
import secrets
import string
from django.contrib.auth import get_user_model
from django.conf import settings
from django.dispatch.dispatcher import Signal

post_nested_save = Signal()

import secrets
import string

def generate_unique_number(instance, custom=None):
    """
    Generate unique number.
    Format: <First three initials>/<Iterative counter>/<year>/<month>
    Example: FAR/00001/2025/09
    """
    if custom:
        initials = custom
    else:
        initials = instance.__class__.__name__[:3].upper()

    # Handle both integer and UUID primary keys
    if hasattr(instance.id, "int"):
        # For UUID fields, use the integer representation
        counter = str(instance.id.int % 100000).zfill(5)
    else:
        # For integer fields, use the ID directly
        counter = str(instance.id).zfill(5)

    # Current year & month
    now = datetime.datetime.now()
    year = now.year
    month = now.month

    return f"{initials}/{counter}/{year}/{month}"


def generate_random_password(length: int = 12) -> str:
    """
    Generate a strong, cryptographically secure random password.

    Args:
        length: Password length (recommended: 12–20)

    Returns:
        Random password string containing letters, digits, and symbols
    """
    if length < 8:
        raise ValueError("Password length must be at least 8 characters")

    chars = (
            string.ascii_uppercase
            + string.ascii_lowercase
            + string.digits
            + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    )

    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"),
    ]

    password += [secrets.choice(chars) for _ in range(length - 4)]

    secrets.SystemRandom().shuffle(password)

    return ''.join(password)
def get_external_user():
    user, _ = get_user_model().objects.get_or_create(
        email=settings.EXTERNAL_USER_EMAIL,
        defaults={
            "phone_number": getattr(settings, 'EXTERNAL_USER_PHONE', '0000000000'),
            "first_name": settings.EXTERNAL_USER_FIRST_NAME,
            "last_name": settings.EXTERNAL_USER_LAST_NAME,
            "is_active": True,
        },
    )
    return user
