from dataclasses import dataclass

from imperfect.draw import BitBlt, CombinationRule, Form


@dataclass
class Pen(BitBlt):
    def __init__(self, destination, color, width, height):
        brush = Form(0, 0, width, height)
        brush.fill(color)

        super().__init__(
            destination=destination,
            source=brush,
            fill=None,
            combination_rule=CombinationRule.SOURCE_ONLY,
            destination_x=0,
            destination_y=0,
            source_x=0,
            source_y=0,
            width=brush.w,
            height=brush.h,
            clip_x=0,
            clip_y=0,
            clip_w=destination.w,
            clip_h=destination.h,
        )

        self.color = color
        self.is_down = False

    @property
    def is_up(self):
        return not self.is_down

    def up(self):
        self.is_down = False

    def down(self):
        self.is_down = True

    def set_color(self, color):
        self.color = color
        self.source.fill(self.color)

    def scale_up(self, factor):
        self.source.w *= factor
        self.width *= factor

        self.source.h *= factor
        self.height *= factor

        self.source.fill(self.color)

    def scale_down(self, factor):
        self.source.w = max(1, self.source.w // factor)
        self.width = max(1, self.width // factor)

        self.source.h = factor
        self.height = factor

        self.source.fill(self.color)

    def line(self, from_x, from_y, to_x, to_y):
        if self.is_up:
            return

        super().draw_line(from_x, from_y, to_x, to_y)
