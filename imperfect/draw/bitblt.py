from __future__ import annotations

import ctypes

from dataclasses import dataclass
from enum import IntEnum, auto

from .color import Color

"""Exploring some of smalltalk's graphics primitives here"""


def sign(val):
    if val > 0:
        return 1
    if val < 0:
        return -1
    return 0


class CombinationRule(IntEnum):
    ALL_ZEROS                            = 0
    SOURCE_AND_DESTINATION               = 1
    SOURCE_AND_DESTINATION_INVERT        = 2
    SOURCE_ONLY                          = 3
    SOURCE_INVERT_AND_DESTINATION        = 4
    DESTINATION_ONLY                     = 5
    SOURCE_XOR_DESTINATION               = 6
    SOURCE_OR_DESTINATION                = 7
    SOURCE_INVERT_AND_DESTINATION_INVERT = 8
    SOURCE_INVERT_XOR_DESTINATION        = 9
    DESTINATION_INVERT                   = 10
    SOURCE_OR_DESTINATION_INVERT         = 11
    SOURCE_INVERT                        = 12
    SOURCE_INVERT_OR_DESTINATION         = 13
    SOURCE_INVERT_OR_DESTINATION_INVERT  = 14
    ALL_ONES                             = 15


class BitBltError(Exception):
    """Raised for an issue trying to execute a bitblt operation."""


@dataclass
class BitBlt:
    destination: Form
    source: Form
    fill: Color
    combination_rule: CombinationRule
    destination_x: int
    destination_y: int
    source_x: int
    source_y: int
    width: int
    height: int
    clip_x: int = 0
    clip_y: int = 0
    clip_w: int|None = None
    clip_h: int|None = None

    def __post_init__(self):
        if self.destination.depth != self.source.depth:
            raise BitBltError(
                f'There is no support for forms with different color formats. source={self.source.color_format}, destination={self.destination.color_format}'
            )

        self.clip_w = (self.clip_w or self.destination.w)
        self.clip_h = (self.clip_h or self.destination.h)

        self.vertical_direction = 0
        self.horizontal_direction = 0

    def draw_line(self, from_x, from_y, to_x, to_y):
        # draw down or left to right
        # so we check both points and if from point is to the right
        # we swap start and stop

        print(f'drawing from ({from_x},{from_y}) to ({to_x},{to_y})')
        is_forward = ((from_y == to_y) and (from_x < to_x)) or (from_y < to_y)
        if not is_forward:
            print('not forward, swaping points')
            from_x, to_x = to_x, from_x
            from_y, to_y = to_y, from_y

        if self.source is None:
            self.destination_x = from_x
            self.destination_y = from_y
        else:
            self.width = self.source.w
            self.height = self.source.h
            offset_x, offset_y = self.source.offset
            self.destination_x = from_x + offset_x
            self.destination_y = from_y + offset_y

        x_delta = to_x - from_x
        y_delta = to_y - from_y
        self.draw_loop_xy(x_delta, y_delta)

    def draw_loop_xy(self, x_delta, y_delta):
        dx = sign(x_delta)
        dy = sign(y_delta)
        px = abs(y_delta)
        py = abs(x_delta)

        if py > px:
            # more horizontal
            p = py // 2
            for i in range(0, py):
                self.destination_x += dx
                p = p - px
                if p < 0:
                    self.destination_y += dy
                    p += py
                if i < py:
                    # print(f'drawing at x={self.destination_x},y={self.destination_y}')
                    self.copy_bits()
        else:
            # more vertical
            p = px // 2
            for i in range(0, px):
                self.destination_y += dy
                p = p - py
                if p < 0:
                    self.destination_x += dx
                    p += px
                if i < px:
                    # print(f'drawing at x={self.destination_x},y={self.destination_y}')
                    self.copy_bits()

    def copy_bits(self):
        self.clip_range()
        self.check_overlap()
        self.copy_loop()

    def clip_range(self):
        # if clipping rectangle is outside the destination image (left)
        # we discard the region to the left of the destination
        if self.clip_x < 0:
            self.clip_w += self.clip_x
            self.clip_x = 0

        # if the clipping rectangle is outside destination image (top)
        # we discard the the region above the top of destination.
        if self.clip_y < 0:
            self.clip_h += self.clip_y
            self.clip_y = 0

        # we do the same as above, but for right and bottom
        if self.clip_x + self.clip_w > self.destination.w:
            self.clip_w = self.destination.w - self.clip_x

        if self.clip_y + self.clip_h > self.destination.h:
            self.clip_h = self.destination.h - self.clip_y

        ## clip and adjust source origing and extent
        # in X
        if self.destination_x >= self.clip_x:
            self.sx = self.source_x
            self.dx = self.destination_x
            self.w  = self.width
        else:
            self.sx = self.source_x + (self.clip_x - self.destination_x)
            self.w  = self.width - (self.clip_x - self.destination_x)
            self.dx = self.clip_x

        if (self.dx + self.w) > (self.clip_x + self.clip_w):
            self.w = self.w - ((self.dx - self.w) - (self.clip_x + self.clip_w))

        # in Y
        if self.destination_y >= self.clip_y:
            self.sy = self.source_y
            self.dy = self.destination_y
            self.h  = self.height
        else:
            self.sy = self.source_y + (self.clip_y - self.destination_y)
            self.h  = self.height - (self.clip_y - self.destination_y)
            self.dy = self.clip_y

        if (self.dy + self.h) > (self.clip_y + self.clip_h):
            self.h = self.h - ((self.dy + self.h) - (self.clip_y + self.clip_h))

        if self.source is None:
            return

        if self.sx < 0:
            self.dx = self.dx - self.sx
            self.w = self.w + self.sx
            self.sx = 0

        if (self.sx + self.w) > self.source.w:
            self.w = self.w - (self.sx + self.w - self.source.w)

        if self.sy < 0:
            self.dy = self.dy - self.sy
            self.h = self.h + self.sy
            self.sy = 0

        if (self.sy + self.h) > self.source.h:
            self.h = self.h - (self.sy + self.h - self.source.h)

    def check_overlap(self):
        # set copying directions to defaults
        self.vertical_direction = 1
        self.horizontal_direction = 1

        # guaranteed no overlap between source and destination
        # return early!
        if self.source != self.destination:
            return

        # otherwise, there could be an overlap and we want to set
        # things up so that we don't destroy the data as it's moved.
        #
        # data moving down: copy starts at bottom and move up
        if self.dy > self.sy:
            self.vertical_direction = -1
            self.sy = self.sy + self.h - 1
            self.dy = self.dy + self.h - 1
        # data moving up:   copy starts at top and move down (uses default vert dir)

        # data moving right: copy starts from the right and move left.
        if self.dx > self.sx:
            self.horizontal_direction = -1
            self.sx = self.sx + self.w - 1
            self.dx = self.dx + self.w - 1
        # data moving left:  copy starts from the left and move right (uses default hor dir)

    def copy_loop(self):
        # TODO support copying data inside the same image using vertical and horizontal direction

        # sx, sy, w, h
        # dx, dy, w, h
        sy_stop = self.sy + self.h
        while self.sy < sy_stop:
            self.merge()
            self.sy += 1
            self.dy += 1

    def merge(self):
        # TODO support other combination rules
        # TODO support color attribute
        source_bytes = self.source.row_bytes(self.sx, self.sy, self.w)
        destination_bytes = self.destination.row_bytes(self.dx, self.dy, self.w)

        match self.combination_rule:
            case CombinationRule.ALL_ZEROS:
                self.destination.put_row_bytes(self.dx, self.dy, bytes(len(destination_bytes)*[0x00]))
            case CombinationRule.ALL_ONES:
                self.destination.put_row_bytes(self.dx, self.dy, bytes(len(destination_bytes)*[0xff]))
            case CombinationRule.SOURCE_ONLY:
                self.destination.put_row_bytes(self.dx, self.dy, source_bytes)
            case CombinationRule.SOURCE_INVERT:
                result = (~int.from_bytes(source_bytes)).to_bytes(self.w * self.source.depth)
                self.destination.put_row_bytes(self.dx, self.dy, result)
            case CombinationRule.DESTINATION_INVERT:
                result = (~int.from_bytes(destination_bytes)).to_bytes(self.w * self.destination.depth)
                self.destination.put_row_bytes(self.dx, self.dy, result)
            case _:
                raise BitBltError(f'unsupported combination rule={self.combination_rule}')

    def _merge_pixel_bytes(self, source_bytes, destination_bytes):
        if len(source_bytes) != len(destination_bytes):
            raise BitBltError("source and destination length do not match!")

        match self.combination_rule:
            case CombinationRule.ALL_ZEROS:
                return bytearray(len(source_bytes) * [0x00])
            case CombinationRule.SOURCE_AND_DESTINATION:
                return bytearray(s & d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_AND_DESTINATION_INVERT:
                return bytearray(s & ~d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_ONLY:
                return source_bytes
            case CombinationRule.SOURCE_INVERT_AND_DESTINATION:
                return bytearray(~s & d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.DESTINATION_ONLY:
                return destination_bytes
            case CombinationRule.SOURCE_XOR_DESTINATION:
                return bytearray(s ^ d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_OR_DESTINATION:
                return bytearray(s | d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_INVERT_AND_DESTINATION_INVERT:
                return bytearray(s & ~d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_INVERT_XOR_DESTINATION:
                return bytearray(~s ^ d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.DESTINATION_INVERT:
                return bytearray(~d for d in destination_bytes)
            case CombinationRule.SOURCE_OR_DESTINATION_INVERT:
                return bytearray(s | ~d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_INVERT:
                return bytearray(~s for s in source_bytes)
            case CombinationRule.SOURCE_INVERT_OR_DESTINATION:
                return bytearray(~s | d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.SOURCE_INVERT_OR_DESTINATION_INVERT:
                return bytearray(~s | ~d for s, d in zip(source_bytes, destination_bytes))
            case CombinationRule.ALL_ONES:
                return bytearray(len(source_bytes) * [0x01])
