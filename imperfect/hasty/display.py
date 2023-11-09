import json

from jinja2 import Environment
from nanoid import generate


HTML = '''
<div id="{{proto.uid}}">
    <table>
    {% for attr_name, attr_value in proto.dict().items() %}
        <tr>
            <td id="{{proto.uid}}-{{attr_name}}">{{ attr_name }}</td>
            <td id="{{proto.uid}}-{{attr_name}}-value">{{ render_value(attr_value) }}</td>
        </tr>
    {% endfor %}
    </table>
</div>
'''

def render_value(objekt):
    if isinstance(objekt, dict):
        return display_html(objekt)
    return objekt


def display_html(proto):
    funcs = {'render_value': render_value}
    environment = Environment()
    environment.globals.update(funcs)
    return environment.from_string(HTML).render(proto=proto)


def display_json(proto):
    return json.dumps(proto.dict())


def to_dict(objekt, klass=None):
    if isinstance(objekt, dict):
        return {key: to_dict(value, klass) for key, value in objekt.items()}

    if hasattr(objekt, '__iter__') and not isinstance(objekt, str):
        return [to_dict(value) for value in objekt]

    if hasattr(objekt, '__dict__'):
        data = {
            key: to_dict(value, klass)
            for key, value
            in objekt.__dict__.items()
            if not callable(value)
        }
        data['tag'] = objekt.__class__.__name__
        return data

    return objekt


# TODO make parameterized uid work
# TODO add transparent persistence
#      - save method that uses a specific persistence implementation
#        - json
#        - sqlite
#        - triplestore
#        - ddb?
def proto(cls, default_uid=True, uid_len=10):
    if default_uid:
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            self.uid = generate(size=uid_len)
            original_init(self, *args, **kwargs)

        setattr(cls, '__init__', __init__)

    def todict(self):
        return to_dict(self)

    def tohtml(self):
        return display_html(self)

    def tojson(self):
        return display_json(self)

    setattr(cls, 'dict', todict)
    setattr(cls, 'html', tohtml)
    setattr(cls, 'json', tojson)
    return cls
