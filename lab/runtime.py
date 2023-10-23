import sdl2

from dataclasses import dataclass, field
from enum import Enum

from lab.draw import Form


class Mod:
    ESC = 'ESC'
    F1 = 'F1'
    F2 = 'F2'
    F3 = 'F3'
    F4 = 'F4'
    F5 = 'F5'
    F6 = 'F6'
    F7 = 'F7'
    F8 = 'F8'
    F9 = 'F9'
    F10 = 'F10'
    F11 = 'F11'
    F12 = 'F12'
    TAB = 'TAB'
    CAPS = 'CAPS'
    LSHIFT = 'LSHIFT'
    LCTRL = 'LCTRL'
    LALT = 'LALT'
    LMETA= 'LMETA'
    SPACE = 'SPACE'
    RMETA = 'RMETA'
    RALT = 'RALT'
    RCTRL = 'RCTRL'
    RSHIFT = 'RSHIFT'
    ENTER = 'ENTER'
    DEL = 'DEL'
    BACKSPACE = 'BACKSPACE'
    UP = 'UP'
    DOWN = 'DOWN'
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'


@dataclass
class MouseDevice:
    """Represents an abstract mouse device, tracking
    its x and y position on the screen and its state."""

    x: int = 0
    y: int = 0
    px: int = 0
    py: int = 0
    l: bool = False
    m: bool = False
    r: bool = False


@dataclass
class KeyboardDevice:
    """Represents an abstract keyboard device, tracking
    the state of modifier keys as well as the text input
    key most recently pressed."""

    text: str = ''
    modifiers: dict = field(init=False)

    def __post_init__(self):
        """Populate modifiers mapping."""
        self.modifiers = {
                k: 0
                for k
                in Mod.__dict__.keys()
                if not k.startswith('_')
        }

    def __str__(self):
        return f'KeyboadDevice(text={self.text}, pressed={self.pressed})'

    def down(self, modifier):
        """Set modifier key state down."""
        self.modifiers[modifier] = 1

    def up(self, modifier):
        """Set modifier key state up."""
        self.modifiers[modifier] = 0

    @property
    def pressed(self):
        """Return all pressed modifiers."""
        return {mod for mod, val in self.modifiers.items() if val == 1}

    def has_pressed(self, modifiers_to_check):
        """Return True if all modifier keys passed are pressed."""
        return all((self.modifiers[m] == 1) for m in modifiers_to_check)


class AppRuntime:
    """AppRuntime wraps all interaction with the platform's
    facilities for drawing to the screen and inputs from the
    mouse and keyboard."""

    def __init__(self, width, height, scale):
        self.w = width * scale
        self.h = height * scale
        self.scale = scale
        self.screen = Form(0, 0, width, height)

        self.mouse = MouseDevice()
        self.handle_mouse_event = None

        self.keybd = KeyboardDevice()
        self.handle_keybd_event = None

        self.running = False
        self.exiting = False

    @property
    def width_in_pixels(self):
        return self.w / self.scale

    @property
    def height_in_pixels(self):
        return self.h / self.scale

    def register_mouse_handler(self, mouse_handler):
        self.handle_mouse_event = mouse_handler

    def register_keybd_handler(self, keybd_handler):
        self.handle_keybd_event = keybd_handler

    def start(self):
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            raise MachineError(f'Canot initialize SDL: {sdl2.SDL_Geterror()}')

        window_opts = sdl2.SDL_WINDOW_BORDERLESS
        self.window = sdl2.SDL_CreateWindow(
            ''.encode('utf-8'),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            self.w,
            self.h,
            window_opts
        )

        self.renderer = sdl2.render.SDL_CreateRenderer(
            self.window,
            -1,
            sdl2.SDL_RENDERER_PRESENTVSYNC
        )

        sdl2.SDL_SetWindowMinimumSize(self.window, self.screen.w, self.screen.h)
        sdl2.render.SDL_RenderSetLogicalSize(self.renderer, self.screen.w, self.screen.h)
        sdl2.render.SDL_RenderSetIntegerScale(self.renderer, 1)

        self.texture = sdl2.SDL_CreateTexture(
            self.renderer,
            sdl2.SDL_PIXELFORMAT_RGBA8888,
            sdl2.SDL_TEXTUREACCESS_STREAMING,
            self.screen.w,
            self.screen.h,
        )
        sdl2.SDL_StartTextInput()
        self.running = True
        self.run()

    def stop(self):
        if not self.running:
            return

        self.running = False
        sdl2.SDL_StopTextInput()
        sdl2.SDL_DestroyTexture(self.texture)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def run(self):

        while self.running:
            start = sdl2.SDL_GetPerformanceCounter()

            self._handle_events()
            if self.exiting:
                break

            self._redisplay()

            end = sdl2.SDL_GetPerformanceCounter()
            elapsed = (
                (end - start) /
                (sdl2.SDL_GetPerformanceFrequency() * 1000.0)
            )

            delay = 16.666 - elapsed
            sdl2.SDL_Delay(int(delay))
        self.stop()

    def _handle_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event) != 0:
            handled, dev = self._handle(event)
            match handled, dev:
                case True, self.mouse:
                    self.handle_mouse_event(self.mouse)
                case True, self.keybd:
                    self.handle_keybd_event(self.keybd)

    def _redisplay(self):
        sdl2.SDL_UpdateTexture(
            self.texture,
            None,
            self.screen.bitmap_bytes,
            self.screen.w * self.screen.depth
        )
        sdl2.SDL_RenderClear(self.renderer)
        sdl2.SDL_RenderCopy(self.renderer, self.texture, None, None)
        sdl2.SDL_RenderPresent(self.renderer)

    def _handle(self, event):
        if event.type == sdl2.SDL_TEXTINPUT:
            self.keybd.text = event.text.text.decode('utf-8')
            return True, self.keybd

        if event.type == sdl2.SDL_KEYDOWN:
            key = MODS_BY_SDL_CODE.get(event.key.keysym.sym, 'text_key')
            self.keybd.down(key)
            return True, self.keybd

        if event.type == sdl2.SDL_KEYUP:
            key = MODS_BY_SDL_CODE.get(event.key.keysym.sym, 'text_key')
            self.keybd.text = ''
            self.keybd.up(key)
            return True, self.keybd

        if event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            button_value = event.button.button
            match button_value:
                case 1:
                    self.mouse.l = True
                case 2:
                    self.mouse.m = True
                case 3:
                    self.mouse.r = True
                case _:
                    print(f'button_value={button_value}')
            return True, self.mouse

        if event.type == sdl2.SDL_MOUSEBUTTONUP:
            button_value = event.button.button
            match button_value:
                case 1:
                    self.mouse.l = False
                case 2:
                    self.mouse.m = False
                case 3:
                    self.mouse.r = False
                case _:
                    print(f'button_value={button_value}')
            return True, self.mouse

        if event.type == sdl2.SDL_MOUSEMOTION:
            self.mouse.px = self.mouse.x
            self.mouse.py = self.mouse.y

            self.mouse.x = event.motion.x
            self.mouse.y = event.motion.y
            return True, self.mouse

        if event.type == sdl2.SDL_QUIT:
            self.exiting = True
            return True, None

        return False, None


MODS_BY_SDL_CODE = {
    sdl2.SDLK_ESCAPE: Mod.ESC,
    sdl2.SDLK_F1: Mod.F1,
    sdl2.SDLK_F2: Mod.F2,
    sdl2.SDLK_F3: Mod.F3,
    sdl2.SDLK_F4: Mod.F4,
    sdl2.SDLK_F5: Mod.F5,
    sdl2.SDLK_F6: Mod.F6,
    sdl2.SDLK_F7: Mod.F7,
    sdl2.SDLK_F8: Mod.F8,
    sdl2.SDLK_F9: Mod.F9,
    sdl2.SDLK_F10: Mod.F10,
    sdl2.SDLK_F11: Mod.F11,
    sdl2.SDLK_F12: Mod.F12,
    sdl2.SDLK_TAB: Mod.TAB,
    sdl2.SDLK_CAPSLOCK: Mod.CAPS,
    sdl2.SDLK_LSHIFT: Mod.LSHIFT,
    sdl2.SDLK_LCTRL: Mod.LCTRL,
    sdl2.SDLK_LALT: Mod.LALT,
    sdl2.SDLK_LGUI: Mod.LMETA,
    sdl2.SDLK_SPACE: Mod.SPACE,
    sdl2.SDLK_RGUI: Mod.RMETA,
    sdl2.SDLK_RALT: Mod.RALT,
    sdl2.SDLK_RCTRL: Mod.RCTRL,
    sdl2.SDLK_RSHIFT: Mod.RSHIFT,
    sdl2.SDLK_RETURN: Mod.ENTER,
    sdl2.SDLK_DELETE: Mod.DEL,
    sdl2.SDLK_BACKSPACE: Mod.BACKSPACE,
    sdl2.SDLK_UP: Mod.UP,
    sdl2.SDLK_DOWN: Mod.DOWN,
    sdl2.SDLK_LEFT: Mod.LEFT,
    sdl2.SDLK_RIGHT: Mod.RIGHT,
}
