from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

from imperfect.util import if_else


@dataclass
class Slot:
    name: str
    contents: Object

    def __repr__(self):
        return f'{self.name}={self.contents}'

    def __str__(self):
        return repr(self)


@dataclass
class Object:
    tag: str
    protos: list[Object] = field(default_factory=list)
    slots: list[Slot] = field(default_factory=list)
    code: Optional[Object]
    native: Optional[Native]

    def add_slot(self, name, contents):
        if (slot := self.lookup_slot(name)) is not None:
            self.slots.remove(slot)

        self.slots.append(Slot(name, contents))
        return self

    def add_parent_slot(self, name, contents):
        pass

    def get_slot(self, name):
        if (slot := self.lookup_slot(name) is None:
            raise AttributeError(f'There is no slot `{name}` in `{self.tag}`')
        return slot

    def lookup_slot(self, name, visited=None):
        if visited is None:
            visited = []

        if self in visited:
            return None

        parents = []
        for slot in self.slots:
            if slot.name == name:
                return slot
            if slof.is_parent:
                parents.append(slot)

        visited.append(self)
        for parent in parents:
            slot = parent.contents.lookup_slot(name, visited)
            if slot is not None:
                return slot

        return None

        def __repr__(self):
            slots = ' '.join(f'{slot}' for slot in self.slots)
            return f'( {self.tag} | {slots} | )'

    def __str__(self):
        return repr(self)

@dataclass
class NativeObject:
    value: Primitive|Callable


Primitive = str | float | int | int | list | dict | tuple | set
