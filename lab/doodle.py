from lab import AppRuntime, Mod
from lab.draw import Palette
from lab.draw import Pen


class Doodle:
    def __init__(self, width, height, scale=1):
        self.w = width
        self.h = height
        self.win = AppRuntime(width, height, scale)
        self.win.register_keybd_handler(self.on_keybd)
        self.win.register_mouse_handler(self.on_mouse)
        self.pen = Pen(self.win.screen, Palette.WHITE, 5, 5)
        self.drawui()

    def drawui(self):
        self.pen.down()
        self.pen.line(0, 20, self.w - 4, 20)
        self.pen.up()

    def on_mouse(self, mouse):
        if mouse.l:
            self.pen.down()
        else:
            self.pen.up()

        self.pen.line(mouse.px, mouse.py, mouse.x, mouse.y)

    def on_keybd(self, keybd):
        if keybd.has_pressed([Mod.LSHIFT, Mod.UP]):
            self.pen.scale_up(2)

        if keybd.has_pressed([Mod.LSHIFT, Mod.DOWN]):
            self.pen.scale_down(2)

        if keybd.has_pressed([Mod.LSHIFT, Mod.RIGHT]):
            self.pen.set_color(Palette.random())

        if keybd.has_pressed([Mod.ESC]):
            self.win.stop()

    def launch(self):
        self.win.start()


def main():
    Doodle(640, 280, 2).launch()
