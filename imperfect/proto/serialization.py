import json

from .proto import Proto


class ProtoSerializer:
    def serialize(self, value):
        pass

    def deserialize(self, rawdata):
        pass

    def reference(self, identifier):
        return f'PROTOREF#:{identifier}'


class ProtoSerializerJson(ProtoSerializer):
    def serialize(self, value):
        return json.dumps(self._todict(value))

    def deserialize(self, rawdata):
        return json.loads(rawdata)

    def _todict(self, value):
        return {
            'tag': value.tag,
            'uid': value.uid,
            'protos': [f'{proto.identifier}' for proto in value.protos],
            'slots': {
                slot_name: self._serialize_slot(slot_value)
                for slot_name, slot_value
                in value.slots.items()
            }
        }

    def _serialize_slot(self, slot_value):
        if isinstance(slot_value, Proto):
            return self.reference(slot_value.uid)
        return self._serialize_primitive_slot(slot_value)

    def _serialize_primitive_slot(self, slot_value):
        match slot_value:
            case dict():
                return self._serialize_primitive_mapping(slot_value)
            case list() | tuple() | set():
                return self._serialize_primitive_sequence(slot_value)
            case _:
                return slot_value

    def _serialize_primitive_mapping(self, slot_value):
        return {key: self._serialize_slot(val) for key, val in slot_value.items()}

    def _serialize_primitive_sequence(self, slot_value):
        return [self._serialize_slot(item) for item in slot_value]
