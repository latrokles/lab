import json
import pathlib
import re


DEFAULT_STOREDIR = '/tmp/'


class Filesystem:
    INSTANCE = None

    def __init__(self, directory, record_klass):
        self.db = pathlib.Path(directory)
        self.klass = record_klass

    def read(self, uid):
        pattern = f'.*-{uid}.p'
        matching_files = [name for name in self.db.glob(pattern)]
        return self._read_from_file(matching_files[0])

    def write(self, filename, serializable_slots):
        pathname = self.db / filename
        pathname.write_text(json.dumps(serializable_slots))

    def find_all(self, tag):
        pattern = f'{tag}-.*.p'
        return [self._read_from_file(name) for name self.db.glob(pattern)]

    def find_with_slots(self, tag, **slots):
        all_instances = self.find_all(tag)
        return [thing for thing in all_instances if thing.matches(**slots)]

    def _read_from_file(self, filename):
        pathname = self.db / filename
        loaded_data = json.loads(pathname.read_text())
        slots = {}
        for k, v in loaded_data.items():
            slots[k] = v

            if isinstance(v, str) and re.match(klass.REFERENCE, v):
                uid = v.replace(klass.REFERENCE, '')
                record = self.read(uid)
                slots[k] = record
        return klass(**slots)

    @classmethod
    def instance(cls, directory = None):
        if directory is None:
            directory = DEFAULT_STOREDIR

        if cls.INSTANCE is None:
            cls.INSTANCE = cls(directory)
        return cls.INSTANCE
