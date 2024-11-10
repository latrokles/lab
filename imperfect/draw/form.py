import ctypes

from dataclasses import dataclass

from imperfect.draw import Color

class OutOfBoundsError(Exception):
    """Raised when trying to access a location outside a form."""


@dataclass
class Form:
    x: int
    y: int
    w: int
    h: int
    offset_x: int|None = None
    offset_y: int|None = None
    bitmap: bytearray|None = None

    def __post_init__(self):
        if self.bitmap is None:
            self.bitmap = bytearray(self.w * self.h * self.depth * [0x00])

    @property
    def depth(self):
        return 4

    @property
    def offset(self):
        if self.offset_x is None and self.offset_y is None:
            return (0, 0)
        return (self.offset_x, self.offset_y)

    @property
    def bitmap_bytes(self):
        return (ctypes.c_char * len(self.bitmap)).from_buffer(self.bitmap)

    def color_at(self, x, y):
        _0th, _nth = self._pixel_bytes_range_at_point(x, y)
        pixel_bytes = self.bitmap[_0th:_nth]
        return Color.from_values(pixel_bytes)

    def put_color_at(self, x, y, color):
        _0th, _nth = self._pixel_bytes_range_at_point(x, y)
        self.bitmap[_0th:_nth] = color.values

    def row_bytes(self, x, y, pixel_count):
        byte_0 = (y * (self.w * self.depth)) + (x * self.depth)
        byte_n = byte_0 + (self.depth * pixel_count)
        return self.bitmap[byte_0:byte_n]

    def put_row_bytes(self, x, y, row_bytes):
        if x + (len(row_bytes) // self.depth) > self.w:
            pixel_count = len(row_bytes) // self.depth
            stop = x + pixel_count
            pixels_to_remove = stop - self.w
            bytes_to_remove = pixels_to_remove * self.depth
            row_bytes = row_bytes[:-bytes_to_remove]

        byte_0 = (y * (self.w * self.depth)) + (x * self.depth)
        byte_n = byte_0 + len(row_bytes)
        self.bitmap[byte_0:byte_n] = row_bytes

    def fill(self, color):
        self.bitmap = bytearray(self.w * self.h * color.values)

    def draw_on(self, medium, x, y, clip_x, clip_y, clip_w, clip_h, rule, fill):
        BitBlt(
            destination=medium,
            source=self,
            fill=fill,
            combination_rule=rule,
            destination_x=x,
            destination_y=y,
            source_x=self.x,
            source_y=self.y,
            extent=(self.w, self.y),
            clip_x=clip_x,
            clip_y=clip_y,
            clip_w=clip_w,
            clip_h=clip_h
        )
        bitblt.copy_bits()

    def _pixel_bytes_range_at_point(self, x, y):
        x_out_of_bounds = x < 0 or self.w <= x
        y_out_of_bounds = y < 0 or self.h <= y
        if x_out_of_bounds or y_out_of_bounds:
            raise OutOfBoundsError(f'{point} is out of bounds of {self}')

        byte_0 = (y * (self.w * self.depth)) + (x * self.depth)
        byte_n = byte_0 + self.depth
        return byte_0, byte_n

    def __str__(self):
        return f"<Form: {self.x=}, {self.y=}, {self.w=}, {self.h=}, {self.offset_x=}, {self.offset_y=}, {len(self.bitmap)=}>"

    def __repr__(self):
        return self.__str__()
