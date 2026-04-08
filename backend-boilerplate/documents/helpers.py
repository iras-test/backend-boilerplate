from uuid import uuid4

def get_file_path(instance, filename):
    extension = filename.split(".")[-1]
    filename = f"{uuid4()}.{extension}"
    return f"{instance._meta.db_table}/{filename}"