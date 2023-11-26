from pathlib import Path
from re import match
from os import listdir

from .serialization import ProtoSerializerJson


def new_file_store(root_path=None, proto_serializer=None):
    if root_path is None:
        root_path = Path('/tmp/')

    if proto_serializer is None:
        proto_serializer = ProtoSerializerJson()

    return FileStore(root_path, proto_serializer)


class FileStore:
    def __init__(self, directory_pathname, proto_serializer):
        self.root_path = Path(directory_pathname)
        self.serializer = proto_serializer

    def write_blob(self, value):
        serializable_slots = self.serializer.serialize(value)
        pathname = self.root_path / f'{value.identifier}.proto'
        pathname.write_text(self.serializer.serialize(value))
        return self.serializer.reference(value.uid)

    def read_blob(self, identifier):
        pattern = f'{identifier}.proto'
        matching_files = [f for f in self._find_matching(pattern)]
        pathname = self.root_path / Path(matching_files[0])
        return self.serializer.deserialize(pathname.read_text())

    def list_blobs(self):
        pattern = '.*.proto'
        return [Path(match).stem for match in self._find_matching(pattern)]

    def _find_matching(self, pattern):
        matching = [name for name in listdir(self.root_path) if match(pattern, name)]
        return matching

    def __repr__(self):
        return f'( Primitive:FileStore | db={self.db} )'

    def __str__(self):
        return self.__repr__()
