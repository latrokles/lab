from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from re import match

from nanoid import generate


IMAGE = None


def init_system_image(store):
    global IMAGE
    if IMAGE is None:
        IMAGE = SystemImage(store)
        Proto('Object', 1)
    return IMAGE


@dataclass
class Proto:
    tag: str = ''
    uid: str = field(default_factory=generate)
    protos: list[Proto] = field(default_factory=list)
    slots: dict[str, Value] = field(default_factory=dict)

    def __post_init__(self):
        self._persist()

    @property
    def identifier(self):
        return f'{self.tag}-{self.uid}'

    def set_slot(self, name, value):
        self.slots[name] = value
        self._persist()
        return self

    def get_slot(self, name):
        slot = self.slots.get(name)
        if slot is not None:
            return slot

        for proto in self.protos:
            slot = proto.get_slot(name)
            if slot is None:
                continue
            return slot

        raise AttributeError(f'There is no slot `{name}` in {self.tag}!')

    def clone(self, tag=None, **with_slots):
        protos = deepcopy(self.protos)
        protos.append(self)
        slots = deepcopy(self.slots)

        if tag is None:
            tag = self.tag

        for slot_name, slot_value in with_slots.items():
            slots[slot_name] = slot_value

        return Proto(tag=tag, protos=protos, slots=slots)

    def matches(self, **slots):
        def is_match(other_slot):
            name, value = other_slot
            slot = self.get_slot(name)
            return slot == value
        return all(is_match(slot) for slot in slots.items())

    def __repr__(self):
        object_prefix = f'{self.tag}'
        protos = ' '.join(proto.tag for proto in self.protos)
        if protos != '':
            object_prefix = f'{object_prefix} < {protos}'

        slots = ' '.join(
            f'{slot_name}={slot_value}'
            for slot_name, slot_value
            in self.slots.items()
        )
        return f'( {object_prefix} | {slots} )'

    def __str__(self):
        return self.__repr__()

    def _persist(self):
        return IMAGE.put(self)


class SystemImage:
    def __init__(self, store):
        self.live = {}
        self.store = store

    @property
    def object(self):
        return self.get('Object-1')

    def restore(self):
        blobids = self.store.list_blobs()
        for blobid in blobids:
            self.get(blobid)
        return self

    def put(self, proto):
        self.live[proto.identifier] = proto
        self.store.write_blob(proto)
        return self

    def get(self, identifier):
        if identifier not in self.live.keys():
            self.live[identifier] = self._load(identifier)
        return self.live.get(identifier)

    def find_all(self, tag):
        pattern = f'{tag}-*'
        return [
            proto
            for identifier, proto
            in self.live.items()
            if match(pattern, identifier)
        ]

    def find_with_slots(self, tag, **slots):
        all = self.find_all(tag)
        print(all)
        return [proto for proto in all if proto.matches(**slots)]

    def _load(self, identifier):
        blob = self.store.read_blob(identifier)
        uid = blob.get('uid')
        tag = blob.get('tag')
        protos = [self.get(protoref) for protoref in blob.get('protos', [])]
        slots = {
            slot_name: self._load_slot(slot_value)
            for slot_name, slot_value
            in blob.get('slots', {}).items()
        }
        return Proto(tag, uid, protos, slots)

    def _load_slot(self, slot_value):
        match slot_value:
            case list() | tuple() | set():
                return [self._load_slot(item) for item in slot_value]
            case dict():
                return {key: self._load_slot(val) for key, val in slot_value.items()}
            case str():
                if slot_value.startswith('PROTOREF#:'):
                    return self.get(slot_value.replace('PROTOREF#:',''))
                return slot_value
            case _:
                return slot_value

    def __repr__(self):
        protos = ',\n '.join(f'{proto}' for proto in self.live.values())
        return f'(\n Primitive:SystemImage |\n {protos}\n)'

    def __str__(self):
        return self.__repr__()


Primitive = str | float | int | int | list | dict | tuple | set
Value = Primitive | Proto
