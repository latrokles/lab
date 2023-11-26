from __future__ import annotations

import json

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from pprint import pformat
from re import match
from os import listdir

from nanoid import generate


SYSIMG = None


def get_system_image(pathname=None):
    global SYSIMG
    if SYSIMG is None:
        SYSIMG = SystemImage(pathname)
        Proto('Object', 1)
    return SYSIMG


@dataclass
class Slot:
    name: str
    value: Value

    def __repr__(self):
        return f'{self.name}={self.value}'

    def __str__(self):
        return self.__repr__()


@dataclass
class Proto:
    tag: str = ''
    uid: str = field(default_factory=generate)
    protos: list[Proto] = field(default_factory=list)
    slots: dict[str, Slot] = field(default_factory=dict)

    def __post_init__(self):
        self._persist()

    @property
    def fqid(self):
        return f'{self.tag}-{self.uid}'

    def set_slot(self, name, value):
        self.slots[name] = Slot(name, value)
        self._persist()
        return self

    def get_slot(self, name):
        slot = self.slots.get(name)
        if slot is not None:
            return slot.value

        for proto in self.protos:
            slot = proto.get_slot(name)
            if slot is None:
                continue
            return slot.value

        raise AttributeError(f'There is no slot `{name}` in {self.tag}!')

    def clone(self, tag=None, **with_slots):
        protos = deepcopy(self.protos)
        protos.append(self)
        slots = deepcopy(self.slots)

        if tag is None:
            tag = self.tag

        for slot_name, slot_value in with_slots.items():
            slots[slot_name] = Slot(slot_name, slot_value)

        return Proto(tag=tag, protos=protos, slots=slots)

    def matches(self, **slots):
        def is_match(other_slot):
            name, value = other_slot
            slot = self.get_slot(name)
            return slot == value
        return all(is_match(slot) for slot in slots.items())

    def todict(self):
        return {
            'tag': self.tag,
            'uid': self.uid,
            'protos': [f'{proto.fqid}' for proto in self.protos],
            'slots': {
                slot.name: self._serialize(slot.value)
                for slot
                in self.slots.values()
            }
        }

    def __repr__(self):
        object_prefix = f'{self.tag}'
        protos = ' '.join(proto.tag for proto in self.protos)
        if protos != '':
            object_prefix = f'{object_prefix} < {protos}'

        slots = ' '.join(f'{slot}' for slot in self.slots.values())
        return f'( {object_prefix} | {slots} )'

    def __str__(self):
        return self.__repr__()

    def _persist(self):
        return get_system_image().put(self)

    def _serialize(self, slot_value):
        if isinstance(slot_value, Proto):
            return f'PROTOREF#:{slot_value.fqid}'
        return self._serialize_primitive(slot_value)

    def _serialize_primitive(self, slot_value):
        match slot_value:
            case dict():
                return self._serialize_primitive_mapping(slot_value)
            case list() | tuple() | set():
                return self._serialize_primitive_sequence(slot_value)
            case _:
                return slot_value

    def _serialize_primitive_sequence(self, list_value):
        return [self._serialize(item) for item in list_value]

    def _serialize_primitive_mapping(self, mapping_value):
        return {key: self._serialize(val) for key, val in mapping_value.items()}


Primitive = str | float | int | int | list | dict | tuple | set
Value = Primitive | Proto


class SystemImage:
    def __init__(self, image_pathname=None):
        if image_pathname is None:
            image_pathname = '/tmp/'
        self.live = {}
        self.store = FileBackedStore(Path(image_pathname))

    @property
    def object(self):
        return self.get('Object-1')

    def restore(self):
        all_blobids = self.store.all_blobs()
        for blobid in all_blobids:
            self.get(blobid)

    def put(self, proto):
        self.live[proto.fqid] = proto
        self.store.write(proto)
        return self

    def get(self, fqid):
        if fqid not in self.live.keys():
            self.live[fqid] = self._load(fqid)
        return self.live.get(fqid)

    def find_all(self, tag):
        pattern = f'{tag}-*'
        return [proto for fqid, proto in self.live.items() if match(pattern, fqid)]

    def find_with_slots(self, tag, **slots):
        all = self.find_all(tag)
        return [proto for proto in all if proto.matches(**slots)]

    def _load(self, fqid):
        data = self.store.read(fqid)
        uid = data.get('uid')
        tag = data.get('tag')
        protos = [self.get(protoref) for protoref in data.get('protos', [])]
        slots = {
            slot_name: Slot(slot_name, self._load_slot(slot_value))
            for slot_name, slot_value
            in data.get('slots', {}).items()
        }
        return Proto(tag, uid, protos, slots)

    def _load_slot(self, slot_value):
        if isinstance(slot_value, str) and slot_value.startswith('PROTOREF#:'):
            fqid = slot_value.replace('PROTOREF#:', '')
            return self.get(fqid)
        if isinstance(slot_value, list) or isinstance(slot_value, set) or isinstance(slot_value, tuple):
            return [self._load_slot(item) for item in slot_value]
        if isinstance(slot_value, dict):
            return {key: self._load_slot(val) for key, val in slot_value.items()}
        return slot_value

    def __repr__(self):
        protos = ',\n '.join(f'{proto}' for proto in self.live.values())
        return f'(\n Primitive:SystemImage |\n {protos}\n)'

    def __str__(self):
        return self.__repr__()


class FileBackedStore:
    def __init__(self, directory):
        self.db = Path(directory)

    def write(self, value):
        serializable_slots = value.todict()
        pathname = self.db / f'{value.fqid}.protojson'
        pathname.write_text(json.dumps(serializable_slots))
        return f'PROTOREF#:{value.uid}'

    def read(self, fqid):
        pattern = f'{fqid}.protojson'
        matching_files = [name for name in listdir(self.db) if match(pattern, name)]
        return self._read_from_file(matching_files[0])

    def all_blobs(self):
        pattern = '.*.protojson'
        return [Path(name).stem for name in listdir(self.db) if match(pattern, name)]

    def _read_from_file(self, filename):
        pathname = self.db / filename
        return json.loads(pathname.read_text())

    def __repr__(self):
        return f'( Primitive:FileBackedStore | db={self.db} )'

    def __str__(self):
        return self.__repr__()
