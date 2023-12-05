

class ThingMeta(type):
    def __new__(meta, name, bases, class_dict):
        return type.__new__(meta, name, bases, class_dict)

    def __getattribute__(self, tag):
        return RecordManager(tag)


class Thing(metaclass=ThingMeta):
    pass


class RecordManager:
    def __init__(self, tag):
        self.tag = tag

    def __call__(self, **slots):
        return Record(nanoid.generate(), self.tag, **slots)

    def all(self):
        # load all records with self.tag and return them as a list
        return FileBackedStorage.instance().find_all(self.tag)

    def find_one(self, **query):
        # return the first record with self.tag that matches query
        results = self.find_many(**query)
        if not results:
            return None
        return results[0]

    def find_many(self, **query):
        # return all records with self.tag that match query
        return FileBackedStorage.instance().find_with_slots(self.tag, **query)


class Record:
    PRIVATE_SLOTS = ('uid', 'tag', 'updated_at')
    REFERENCE = '#ref#:'

    def __init__(self, uid, tag, **slots):
        self.uid = uid
        self.tag = tag
        self._initialize_slots(slots)

    @property
    def filename(self):
        return f'{self.tag}-{self.uid}.p'

    def save(self):
        serializable = {}
        for slot_name, slot_value in self.__dict__.items():
            serializable[slot_name] = slot_value

            if isinstance(slot_value, Record):
                slot_value.save()
                serializable[slot_name] = f'{Record.REFERENCE}{slot_value.uid}'
        FileBackedStorage.instance().write(self.filename, serializable)

    def matches(self, **slots):
        def is_match(slot):
            name, value = slot
            return hasattr(self, name) and getattr(self, name) == value
        return all(is_match(slot) for slot in slots.items())

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        self.__dict__['updated_at'] = int(time.time() * 1000)
        if name in Record.PRIVATE_SLOTS:
            return

        self.save()

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return self.uid == other.uid

    def __repr__(self):
        def show(slot):
            value = getattr(self, slot)
            return f'{slot}: {repr(value)}'

        slots = ', '.join(
            show(slot)
            for slot
            in self.__dict__.keys()
            if slot not in Record.PRIVATE_SLOTS)
        return f'{self.tag}.({slots})'

    def _initialize_slots(self, slots):
        for slot_name, slot_value in slots.items():
            setattr(self, slot_name, slot_value)

