import uuid
from pathlib import Path


def generate_upload_path():
    return Path("uploads/raw/") / str(uuid.uuid4())
