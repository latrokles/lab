from lab import AppRuntime


class Tedit:
    def __init__(self, width, height, scale=1):
        self.w = width
        self.h = height
        self.win = AppRuntime(width, height, scale)
        self.win.register_keybd_handler(self.on_keybd)
        self.win.register_mouse_handler(self.on_mouse)

    def on_mouse(self, mouse):
        print(mouse)

    def on_keybd(self, keybd):
        print(keybd)

    def launch(self):
        self.win.start()


def main():
    Tedit(320, 240, 2).launch()