"""Django User Management Package - Reusable abstract models for user/profile."""

from .models import AbstractUserMixin, AbstractUserProfile
from .managers import CustomUserManager

__version__ = '0.1.0'
__all__ = [
    'AbstractUserMixin',
    'AbstractUserProfile',
    'CustomUserManager',
]

