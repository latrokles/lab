import sdl2

from lab.draw import Form


class AppRuntime:
    """AppRuntime wraps all interaction with the platform's
    facilities for drawing to the screen and inputs from the
    mouse and keyboard."""

    def __init__(self, width, height, scale):
        self.w = width * scale
        self.h = height * scale
        self.scale = scale
        self.screen = Form(0, 0, width, height)

        self.running = False
        self.exiting = False

    @property
    def width_in_pixels(self):
        return self.w / self.scale

    @property
    def height_in_pixels(self):
        return self.h / self.scale

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
        self.running = True
        self.run()

    def stop(self):
        if not self.running:
            return

        self.running = False
        sdl2.SDL_DestroyTexture(self.texture)
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def run(self):
        while self.running:
            self._handle_events()
            if self.exiting:
                break

            self._redisplay()
        self.stop()

    def _handle_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(event) != 0:
            self._handle(event)

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
        if event.type == sdl2.SDL_QUIT:
            self.exiting = True
            return
