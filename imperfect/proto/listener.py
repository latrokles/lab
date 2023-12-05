import code

from .scan import Scanner


class Listener(code.InteractiveConsole):
    def runsource(self, source, filename='<input>', symbol='single'):
        if source != '' and source[-1] not in ('.', ']'):
            return True

        expr = self._read(source)
        out  = self._eval(expr)
        self._print(out)

    def _read(self, source):
        return Scanner(source).scan()

    def _eval(self, expression):
        return expression

    def _print(self, output):
        print(output)


def start_listener():
    Listener().interact(banner='', exitmsg='bye!')
