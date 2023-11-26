from pathlib import Path

from .proto import Proto, init_system_image
from .storage import new_file_store


def bootstrap(root_path=None):
    if root_path is None:
        root_path = Path('/tmp/')
    return init_system_image(new_file_store(root_path)).restore()
