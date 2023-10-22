from dataclasses import dataclass


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    @property
    def values(self):
        return [self.a, self.b, self.g, self.r]

    @classmethod
    def from_values(cls, values):
        alpha, blue, green, red = values
        return cls(red, green, blue, alpha)

    @staticmethod
    def from_hexstr(hexstr):
        color = int(hexstr, 16)
        red = (color & 0xff0000) >> 16
        green = (color & 0xff00) >> 8
        blue  = (color & 0xff)
        return Color(red, green, blue)
