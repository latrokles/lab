"""
Read and write to the json lines format.
see: https://jsonlines.org/
"""

import json

from pathlib import Path


def load(pathname, encoding = 'utf-8'):
    """Read and deserialize the contents of filepath."""
    pathname = Path(pathname)
    return [
        json.loads(line)
        for line
        in pathname.read_text(encoding=encoding).split('\n')
        if line != ''
    ]


def dump(contents, pathname, encoding = 'utf-8'):
    """Serialize and write contents to filepath."""
    content = '\n'.join([json.dumps(entry) for entry in contents])
    Path(pathname).write_text(content, encoding=encoding)
