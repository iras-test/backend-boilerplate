import datetime

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